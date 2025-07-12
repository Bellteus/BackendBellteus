import os
import json
from dotenv import load_dotenv
from config.mongodb import get_mongo_client
from config.Prompts import ANALYSIS_PROMPT_TEMPLATE
from service.TranscriptionService import Transcripcion_Audio
from openai import OpenAI
from pymongo.errors import DuplicateKeyError
from db.connection import get_connection
import re

load_dotenv()

def extraer_json(texto):
    # Busca el primer '{' y el último '}'
    match = re.search(r'\{[\s\S]*\}', texto)
    if match:
        return match.group()
    return None

def Mongo_Insertar_Analisis(analisis):
    try:
        client = get_mongo_client()
        db = client["CALLCENTER-MONGODB"]
        collection = db["ANALISIS-LLMS"]
        result = collection.insert_one(analisis)
        print(f"Insertado: {analisis['_id']}")
        client.close()
    except DuplicateKeyError:
        print(f"Ya existe: {analisis['_id']}")
    except Exception as e:
        print(f"Error Mongo: {e}")


def Consulta_Mysql(startTime,endTime):
    try:
        connection = get_connection()
        if not connection:
            print("Error de conexión a la base de datos")
        with connection.cursor() as cursor:
            sql = """
                SELECT CallId, MediaFileName, FechaHoraInicioDT, FechaHoraFinDT, ANI, CallDirection, Cliente, NombreArea, IdEmpleado, NombreEmpleado
                FROM call_data_records
                where FechaHoraInicioDT BETWEEN %s AND %s;
            """
            cursor.execute(sql, (startTime, endTime))
            registros = cursor.fetchall()
            return registros
    except Exception as e:
        print(f"Error al obtener metadata: {e}")
    finally:
        connection.close()

def listar_todos_los_ids(db_name="CALLCENTER-MONGODB", collection_name="ANALISIS-LLMS"):
    try:
        client = get_mongo_client()
        db = client[db_name]
        collection = db[collection_name]
        ids = collection.find({}, {"_id": 1})
        lista_ids = [doc["_id"] for doc in ids]
        client.close()
        return list(lista_ids)
    except Exception as e:
        print(f"Error al consultar MongoDB: {e}")
    finally:
        client.close()


def Analizar_LLM(startTime, endTime,pathAudios=r"C:\Users\Administrator\Documents\AUDIOS\27-30"):
    #Consulta a la base de datos para obtener los registros de llamadas
    if not startTime or not endTime:
        print("Los parámetros de tiempo no pueden estar vacíos.")
        return None
    data= Consulta_Mysql(startTime, endTime)
    print(f"Total de registros obtenidos: {len(data)}")
    if not data:
        print("No se encontraron registros en la base de datos.")
        return None
    ListIdsMongos= listar_todos_los_ids()
    print(ListIdsMongos)
    print(f"Total de registros encontrados: {len(ListIdsMongos)}")
    #Verificat si la lista de mongo se encuentra en la consulta de mysql. y solo dejar los que no estan.
    data = [registro for registro in data if str(registro["CallId"]) not in ListIdsMongos]
    print(f"Registros a procesar: {len(data)}")
    # Iterar sobre cada registro de llamada
    for registro in data:
        audio_filename = registro["MediaFileName"] if "MediaFileName" in registro else None
        if not audio_filename:
            print("No se encontró el nombre del archivo de audio en el registro.")
            continue
        local_audio_path = os.path.join(pathAudios, audio_filename)
        if not os.path.exists(local_audio_path):
            print(f"Falta audio: {local_audio_path}")
            continue
        #Transcripcion de audios
        transcripcion_json = Transcripcion_Audio(local_audio_path)
        transcripcion = transcripcion_json["transcripcion"]

        #PROMPT en LLM
        ANALYSIS_PROMPT = ANALYSIS_PROMPT_TEMPLATE.format(transcription=transcripcion,metadata=registro)

        # Llamada a la LLM
        client = OpenAI(api_key=os.getenv("OPENAITOKEN"))
        respuesta = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": ANALYSIS_PROMPT}],
            temperature=0.3
        )
        json_response_text = respuesta.choices[0].message.content
        json_response_text = extraer_json(json_response_text)

        print(json_response_text)
        try:
            analisis_llm = json.loads(json_response_text)
        except Exception as e:
            print(f"LLM devolvió JSON inválido para {audio_filename}: {e}")
            continue

        # Guarda el análisis + metadata en Mongo
        doc_id = os.path.splitext(audio_filename)[0]  # Solo el nombre sin extensión
        registro = {
            "_id": doc_id,
            "audio_file": audio_filename,
            "CallId": registro["CallId"],
            "FechaHoraInicio": registro["FechaHoraInicioDT"],
            "FechaHoraFin": registro["FechaHoraFinDT"],
            "ANI": registro["ANI"],
            "CallDirection": registro["CallDirection"],
            "Cliente": registro["Cliente"],
            "NombreArea": registro["NombreArea"],
            "IdEmpleado": registro["IdEmpleado"],
            "NombreEmpleado": registro["NombreEmpleado"],
            "TRANSCRIPCION": transcripcion,
            "ANALISIS_LLM": analisis_llm
        }
        Mongo_Insertar_Analisis(registro)
        print(f"✔️ Procesado y guardado: {doc_id}")
    
if __name__ == "__main__":
    Analizar_LLM('2025-05-27', '2025-05-31')

