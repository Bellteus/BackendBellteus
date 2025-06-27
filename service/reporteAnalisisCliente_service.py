from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException
from pymongo.collection import Collection
from models.reporteAnalisisClienteModel import ReporteAnalisisSchema
from config.mongodb import get_mongo_client
import re
import pandas as pd
from config.Prompts import AGGREGATE_ANALYSIS_PROMPT
from config.OpenAI import get_openai_client
import json


def buscar_Todos_ReporteAnalisis_service(
) -> List[ReporteAnalisisSchema]:
    try:
        client = get_mongo_client()
        db = client["CALLCENTER-MONGODB"]
        collection = db["Cliente-Performance"]
        # Obtener todos los reportes de la colección
        reportes = list(collection.find())
        
        if not reportes:
            return []
        
        resultados = []
        for reporte in reportes:
            try:
                # Convertir ObjectId a string                
                # Crear el schema para cada documento
                print(reporte)
                resultado = ReporteAnalisisSchema(**reporte)
                resultados.append(resultado)
                
            except Exception as e:
                # Si hay error con un documento, continuar con los demás
                print(f"Error procesando documento {reporte.get('_id')}: {str(e)}")
                continue
        
        return resultados
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener reportes: {str(e)}"
        )


def extraer_json(texto):
    # Busca el primer '{' y el último '}'
    match = re.search(r'\{[\s\S]*\}', texto)
    if match:
        return match.group()
    return None

def Analizar_llamada_por_Area(Area,fecha_inicio,fecha_fin) -> ReporteAnalisisSchema:
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
        if not json_response_text:
            raise HTTPException(status_code=400, detail="No se recibió respuesta de la IA")

        # 1) Parsear JSON
        try:
            analisis_dict = json.loads(json_response_text)
        except json.JSONDecodeError as e:
            print(f"ERROR: JSON inválido: {e}")
            raise HTTPException(status_code=400, detail="La IA devolvió un JSON inválido")

        # 2) Preparar documento
        # Asegúrate de que 'Area', 'fecha_inicio' y 'fecha_fin' estén en scope
        area_nombre = Area if 'Area' in locals() else analisis_dict.get("area", "Desconocido")
        fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')
        fecha_fin_str   = fecha_fin.strftime('%Y-%m-%d %H:%M:%S')

        doc = {
            **analisis_dict,
            "_id": f"{area_nombre}_{datetime.now():%Y%m%d%H%M%S}",
            "fecha_inicio_busqueda": fecha_inicio_str,
            "fecha_fin_busqueda":   fecha_fin_str,
            "DateTime_realizado":    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        # 3) Insertar en MongoDB
        try:
            collectionAnalisisResultado = db["Cliente-Performance"]
            result = collectionAnalisisResultado.insert_one(doc)
            print(f"Análisis agregado con id de Mongo: {result.inserted_id}")
        except Exception as e:
            print(f"ERROR al insertar en MongoDB: {e}")
            raise HTTPException(status_code=500, detail="No se pudo guardar el análisis en la base de datos")

        # 4) Devolver el Pydantic Schema
        try:
            return ReporteAnalisisSchema(**doc)
        except Exception as e:
            print(f"ERROR al mapear al esquema: {e}")
            # Si todos los campos del schema son Optional, podrías devolver uno vacío:
            # return ReporteAnalisisSchema()
            raise HTTPException(status_code=500, detail="Error al formatear la respuesta")

           
            
        else:
            print("No se pudo extraer un JSON válido de la respuesta de la IA.")
    finally:
        client.close()
