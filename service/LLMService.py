from openai import OpenAI
import os
from dotenv import load_dotenv
from config.Prompts import ANALYSIS_PROMPT_TEMPLATE
from service.TranscriptionService import Transcripcion_Audio
from config.mongodb import get_mongo_client
import json

def Analizar_LLM(audio):
    try:
        transcripcion_json = Transcripcion_Audio(f"Audios/{audio}")
        transcripcion = transcripcion_json["transcripcion"]

        ANALYSIS_PROMPT = ANALYSIS_PROMPT_TEMPLATE.format(transcription=transcripcion,call_id=audio)
        client = OpenAI(api_key=os.getenv("OPENAITOKEN"))

        respuesta = client.chat.completions.create(
            model="gpt-",
            messages=[{"role": "user", "content": ANALYSIS_PROMPT}],
            temperature=0.8
        )
        json_response_text = respuesta.choices[0].message.content
        print(json_response_text)
        
        try:
            analisis_dict = json.loads(json_response_text)
        except Exception as e:
            print(f"ERROR: El modelo devolvió un JSON inválido. Detalle: {e}")
            return None
        _id=os.path.splitext(audio)[0]  # Extraer el nombre del archivo sin extensión
        analisis_dict["_id"] = _id
        Mongo_Insertar_Analisis(analisis_dict)
        return analisis_dict
    except Exception as e:
        print(f"Error en la llamada a LLM: {e}")
        return None

def Mongo_Insertar_Analisis(analisis):
    try:
        client = get_mongo_client()
        db = client["CALLCENTER-MONGODB"]
        collection = db["ANALISIS-LLMS"]

        result = collection.insert_one(analisis)
        print(f"Análisis insertado con id: {result.inserted_id}")
        client.close()
    except Exception as e:
        print(f"Error al insertar análisis en MongoDB: {e}")
