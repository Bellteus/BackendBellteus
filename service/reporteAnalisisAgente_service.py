import json
from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException
from config.OpenAI import get_openai_client
from config.mongodb import get_mongo_client
import re
import pandas as pd
from collections import Counter
from statistics import mean, stdev
from config.Prompts import AGENT_ANALYSIS_PROMPT
from models.reporteAnalisisAgenteModel import AnalisisAgenteSchema

def extraer_json(texto):
    match = re.search(r'\{[\s\S]*\}', texto)
    if match:
        return match.group()
    return None

def calcular_metricas_agente(llamadas: List[dict]) -> dict:
    llm_data = [x["ANALISIS_LLM"] for x in llamadas if "ANALISIS_LLM" in x]
    if not llm_data:
        return {}

    performance_scores = [x.get("performance_score", 0) for x in llm_data]
    satisfacciones = [x.get("satisfaccion_cliente", 0) for x in llm_data]
    duraciones = []
    for l in llamadas:
        try:
            inicio = pd.to_datetime(l["FechaHoraInicio"])
            fin = pd.to_datetime(l["FechaHoraFin"])
            duracion = (fin - inicio).total_seconds() / 60
            duraciones.append(duracion)
        except:
            continue

    sentimientos = [x.get("sentimiento_cliente", "desconocido") for x in llm_data]
    casos_resueltos = [x.get("caso_resuelto", "no") for x in llm_data]
    escalados = [x.get("escalado", "no") for x in llm_data]
    followups = [x.get("necesita_followup", "no") for x in llm_data]
    protocolos = [x.get("protocolo_cumplido", "no") for x in llm_data]
    alertas = [x.get("alerta_calidad") for x in llm_data]

    total_llamadas = len(llm_data)
    def porcentaje(lista, valor):
        return round(100 * sum(1 for x in lista if x == valor) / total_llamadas, 1)

    sentimiento_counts = Counter(sentimientos)
    sentimiento_distribucion = {
        "positivo": sentimiento_counts.get("positivo", 0),
        "neutral": sentimiento_counts.get("neutral", 0),
        "negativo": sentimiento_counts.get("negativo", 0)
    }

    return {
        "numero_llamadas": total_llamadas,
        "duracion_promedio_min": round(mean(duraciones), 2) if duraciones else None,
        "duracion_std_min": round(stdev(duraciones), 2) if len(duraciones) > 1 else None,
        "performance_score_promedio": round(mean(performance_scores), 2),
        "performance_score_std": round(stdev(performance_scores), 2) if len(performance_scores) > 1 else None,
        "satisfaccion_promedio": round(mean(satisfacciones), 2),
        "tasa_resueltos_pct": porcentaje(casos_resueltos, "sí"),
        "tasa_escalados_pct": porcentaje(escalados, "sí"),
        "tasa_followup_pct": porcentaje(followups, "sí"),
        "tasa_protocolo_cumplido_pct": porcentaje(protocolos, "sí"),
        "sentimiento_distribucion": sentimiento_distribucion,
        "alertas_promedio_por_llamada": round(mean(len(a) if isinstance(a, list) else 0 for a in alertas), 2)
    }

def Analizar_llamada_por_Agente(Agente, fecha_inicio, fecha_fin) -> AnalisisAgenteSchema:
    try:
        CAMPOS_PERFORMANCE = [
            "CallId", "NombreEmpleado", "NombreArea", "IdEmpleado",
            "FechaHoraInicio", "FechaHoraFin",
            "ANALISIS_LLM.performance_score", "ANALISIS_LLM.sentimiento_cliente",
            "ANALISIS_LLM.satisfaccion_cliente", "ANALISIS_LLM.sentimiento_inicio",
            "ANALISIS_LLM.sentimiento_fin", "ANALISIS_LLM.caso_resuelto",
            "ANALISIS_LLM.escalado", "ANALISIS_LLM.complejidad_caso",
            "ANALISIS_LLM.acciones_acordadas", "ANALISIS_LLM.necesita_followup",
            "ANALISIS_LLM.fortalezas", "ANALISIS_LLM.oportunidades_mejora",
            "ANALISIS_LLM.protocolo_cumplido", "ANALISIS_LLM.alerta_calidad",
            "ANALISIS_LLM.evidencia_frases", "ANALISIS_LLM.personas_mencionadas",
            "ANALISIS_LLM.palabras_clave", "ANALISIS_LLM.topicos_principales",
            "ANALISIS_LLM.resumen", "ANALISIS_LLM.observaciones_llm"
        ]

        client = get_mongo_client()
        db = client["CALLCENTER-MONGODB"]
        collection = db["ANALISIS-LLMS"]

        proyeccion = {campo: 1 for campo in CAMPOS_PERFORMANCE}
        analisis_llm_list = list(collection.find({
            "NombreEmpleado": Agente,
            "FechaHoraInicio": {"$gte": fecha_inicio, "$lte": fecha_fin}
        }, proyeccion))

        if not analisis_llm_list:
            print(f"No se encontraron análisis para el agente '{Agente}' en el rango de fechas proporcionado.")
            return
        IdEmpleado = analisis_llm_list[0].get("IdEmpleado")
        data = calcular_metricas_agente(analisis_llm_list)
        prompt_final = AGENT_ANALYSIS_PROMPT.format(nombre_empleado=Agente,id_empleado=IdEmpleado,numero_llamadas=len(analisis_llm_list),metricas_agregadas=json.dumps(data, indent=2),llamadas_llm=analisis_llm_list)
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
        fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')
        fecha_fin_str   = fecha_fin.strftime('%Y-%m-%d %H:%M:%S')

        doc = {
            **analisis_dict,
            "_id": f"{IdEmpleado}_{datetime.now():%Y%m%d%H%M%S}",
            "fecha_inicio_busqueda": fecha_inicio_str,
            "fecha_fin_busqueda":   fecha_fin_str,
            "DateTime_realizado":    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        # 3) Insertar en MongoDB
        try:
            collectionAnalisisResultado = db["Agente-Performance"]
            result = collectionAnalisisResultado.insert_one(doc)
            print(f"Análisis agregado con id de Mongo: {result.inserted_id}")
        except Exception as e:
            print(f"ERROR al insertar en MongoDB: {e}")
            raise HTTPException(status_code=500, detail="No se pudo guardar el análisis en la base de datos")

        # 4) Devolver el Pydantic Schema
        try:
            return AnalisisAgenteSchema(**doc)
        except Exception as e:
            print(f"ERROR al mapear al esquema: {e}")
            # Si todos los campos del schema son Optional, podrías devolver uno vacío:
            # return ReporteAnalisisSchema()
            raise HTTPException(status_code=500, detail="Error al formatear la respuesta")

    except Exception as e:
        print(f"Error al analizar por agente: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al procesar análisis por agente")

def Mostrar_AnalisisAgente(Agente: str, fecha_inicio: datetime, fecha_fin: datetime) -> List[AnalisisAgenteSchema]:
    try:
        client = get_mongo_client()
        db = client["CALLCENTER-MONGODB"]
        collection = db["Agente-Performance"]

        fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')
        fecha_fin_str = fecha_fin.strftime('%Y-%m-%d %H:%M:%S')

        filtro = {
            "DateTime_realizado": {
                "$gte": fecha_inicio_str,
                "$lte": fecha_fin_str
            }
        }
        if Agente and Agente != "TODOS":
            filtro["nombre_empleado"] = Agente

        print(f"[DEBUG] Filtro usado:", filtro)

        analisis_list = list(collection.find(filtro))

        print(f"[DEBUG] Resultados encontrados: {len(analisis_list)}")

        if not analisis_list:
            print(f"No se encontraron análisis para el agente '{Agente}' en el rango de fechas proporcionado.")
            return []

        return [AnalisisAgenteSchema(**item) for item in analisis_list]

    except Exception as e:
        print(f"Error al mostrar análisis del agente: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud de análisis del agente.")




    


def ObtenerReporteAnalisisAgenteporID(id:str) ->AnalisisAgenteSchema:
    try:
        client = get_mongo_client()
        db = client["CALLCENTER-MONGODB"]
        collection = db["Agente-Performance"]

        resultado = list(collection.find({
            "_id": id}))
        if not resultado:
            print(f"No se encontraron registors con ese id")
            raise HTTPException(status_code=404,detail="Error al procesar la solicitud de analisis del agente.")
        return AnalisisAgenteSchema(**resultado[0])
    except Exception as e:
        print(f"Error al mostrar análisis del agente: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud de análisis del agente.")