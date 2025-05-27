from openai import OpenAI
import os
from dotenv import load_dotenv
from config.Prompts import ANALYSIS_PROMPT_TEMPLATE
from service.TranscriptionService import Transcripcion_Audio

load_dotenv()

def Analizar_LLM(ARCHIVO_AUDIO):
    try:
        # Cargar la transcripción
        transcripcion = Transcripcion_Audio(ARCHIVO_AUDIO)

        ANALYSIS_PROMPT = ANALYSIS_PROMPT_TEMPLATE.format(transcription=transcripcion)

        client = OpenAI(api_key=os.getenv("OPENAITOKEN"))

        respuesta = client.chat.completions.create(
            model="gpt-4",
            messages=[
            {"role": "user", "content": ANALYSIS_PROMPT}
        ],
        temperature=0.8)
        print(respuesta.choices[0].message.content)
        json_response ={
            
        }
        return respuesta.choices[0].message.content
    except Exception as e:
        print(f"Error en la llamada a LLM: {e}")
