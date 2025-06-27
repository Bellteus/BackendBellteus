from datetime import datetime
import re
from config.mongodb import get_mongo_client
from config.Prompts import AGGREGATE_ANALYSIS_PROMPT
from config.OpenAI import get_openai_client
import pandas as pd
import json

def extraer_json(texto):
    # Busca el primer '{' y el último '}'
    match = re.search(r'\{[\s\S]*\}', texto)
    if match:
        return match.group()
    return None

def Analizar_llamada_por_Area(Area,fecha_inicio,fecha_fin):
    try:
        CAMPOS_PERFORMANCE = [
    "CallId",
    "NombreArea",
    "IdEmpleado",
    "NombreEmpleado",
    "ANALISIS_LLM.performance_score",
    "ANALISIS_LLM.sentimiento_cliente",
    "ANALISIS_LLM.satisfaccion_cliente",
    "ANALISIS_LLM.caso_resuelto",
    "ANALISIS_LLM.escalado",
    "ANALISIS_LLM.complejidad_caso",
    "ANALISIS_LLM.acciones_acordadas",
    "ANALISIS_LLM.necesita_followup",
    "ANALISIS_LLM.fortalezas",
    "ANALISIS_LLM.oportunidades_mejora",
    "ANALISIS_LLM.protocolo_cumplido",
    "ANALISIS_LLM.alerta_calidad"
]

        client = get_mongo_client()
        db = client["CALLCENTER-MONGODB"]
        collection = db["ANALISIS-LLMS"]
        proyeccion = {campo: 1 for campo in CAMPOS_PERFORMANCE}

        # Filtrar por area y traer solo los campos requeridos
        analisis_llm_list = list(collection.find({"Cliente": Area,"FechaHoraInicio":{
            "$gte": fecha_inicio,
            "$lte": fecha_fin
        }}, proyeccion))
        # Si no hay análisis, retornar un mensaje
        if not analisis_llm_list:
            print(f"No se encontraron análisis para el área '{Area}' en el rango de fechas proporcionado.")
            return

        # Extraer análisis
        df_analysis = pd.DataFrame([d['ANALISIS_LLM'] for d in analisis_llm_list])
        
        # KPIs
        kpis = {}
        kpis['performance_score_avg'] = float(df_analysis['performance_score'].mean())
        kpis['sentimiento_cliente_counts'] = df_analysis['sentimiento_cliente'].value_counts().to_dict()
        kpis['satisfaccion_cliente_avg'] = float(df_analysis['satisfaccion_cliente'].mean())
        kpis['casos_resueltos'] = df_analysis['caso_resuelto'].value_counts().to_dict()
        kpis['porcentaje_escalado'] = float((df_analysis['escalado'] == 'sí').mean() * 100)
        kpis['necesita_followup_pct'] = float((df_analysis['necesita_followup'] == 'sí').mean() * 100)
        kpis['casos_alerta_calidad'] = float(df_analysis['alerta_calidad'].apply(lambda x: isinstance(x, list) and len(x) > 0).sum())
        kpis['protocolo_cumplido_counts'] = df_analysis['protocolo_cumplido'].value_counts().to_dict()
        
        print(kpis)
        
        prompt_final = AGGREGATE_ANALYSIS_PROMPT.format(cliente=Area,analisis_llm_list=analisis_llm_list,numero_llamadas=len(analisis_llm_list),metricas_agregadas=json.dumps(kpis, indent=2))
        ClientOpenAi = get_openai_client(prompt_final)
        json_response_text = extraer_json(ClientOpenAi)

        #Agregar LA RESPUESTA DE LA IA  EN UN COLECCION 
        if json_response_text:
            try:
                analisis_dict = json.loads(json_response_text)
            except json.JSONDecodeError as e:
                print(f"ERROR: El modelo devolvió un JSON inválido. Detalle: {e}")
                return None
            
            # Insertar análisis en MongoDB
            # Quiero generar un id que incremente
            collectionAnalisisResultado = db["Cliente-Performance"]
            analisis_dict["_id"]= f"{Area}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            analisis_dict["fecha_inicio_busqueda"]= fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')
            analisis_dict["fecha_fin_busqueda"]= fecha_fin.strftime('%Y-%m-%d %H:%M:%S')
            analisis_dict["DateTime_realizado"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            result = collectionAnalisisResultado.insert_one(analisis_dict)
            print(f"Análisis agregado con id: {result.inserted_id}")
        else:
            print("No se pudo extraer un JSON válido de la respuesta de la IA.")
    finally:
        client.close()

if __name__ == "__main__":
    Area = "NATURA COLOMBIA"
    fecha_inicio = datetime(2025, 5, 1)
    fecha_fin = datetime(2025, 5, 30)
    Analizar_llamada_por_Area(Area, fecha_inicio, fecha_fin)