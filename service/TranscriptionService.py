import os
from dotenv import load_dotenv
from deepgram.utils import verboselogs
from datetime import datetime
import httpx

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    PrerecordedOptions,
    FileSource
)

# Carga las variables de entorno desde el archivo .env
load_dotenv()


def Transcripcion_Audio(ARCHIVO_AUDIO):
    try:
        # PASO 1: Crear cliente Deepgram usando la API key y configuración detallada
        configuracion: DeepgramClientOptions = DeepgramClientOptions(
            verbose=verboselogs.SPAM,
        )
        deepgram: DeepgramClient = DeepgramClient(os.getenv("DEEPGRANTOKEN"), configuracion)

        # PASO 2: Leer el archivo de audio como binario
        with open(ARCHIVO_AUDIO, "rb") as archivo:
            datos_audio = archivo.read()

        fuente: FileSource = {
            "buffer": datos_audio,
        }

        # PASO 3: Configurar las opciones de transcripción
        opciones: PrerecordedOptions = PrerecordedOptions(
            model="base",
            language="es",
            diarize=True,
            paragraphs=True,
            #smart_format=True, 
            #punctuate=True # Añadir puntuación
        )

        # PASO 4: Enviar a Deepgram y medir tiempo de respuesta
        antes = datetime.now()
        respuesta = deepgram.listen.rest.v("1").transcribe_file(
            fuente, opciones, timeout=httpx.Timeout(300.0, connect=10.0)
        )
        despues = datetime.now()

        resultado = respuesta.to_dict()

        # Procesar resultados
        transcripcion_limpia = "\n--- TRANSCRIPCIÓN POR SPEAKER ---\n\n"
        if "paragraphs" in resultado["results"]["channels"][0]["alternatives"][0]:
            parrafos = resultado["results"]["channels"][0]["alternatives"][0]["paragraphs"]["paragraphs"]

            for parrafo in parrafos:
                speaker = parrafo.get("speaker", "Desconocido")
                # Extraer y unir textos de todas las sentences
                textos = [sentence["text"] for sentence in parrafo["sentences"]]
                texto = " ".join(textos).strip()
                linea = f"Speaker {speaker}: {texto}\n"
                #print(linea)
                transcripcion_limpia += linea + "\n"
        else:
            mensaje = "No se encontraron párrafos en la transcripción.\n"
            #print(mensaje)
            transcripcion_limpia += mensaje



        # Tiempo total
        duracion = despues - antes
        transcripcion_limpia=transcripcion_limpia
        print(f"\nTiempo de transcripción: {duracion.seconds} segundos")
        
        # Guardar la transcripción en UN JSON PARA RETORNAR EN LA FUNCION
        transcripcion_json = {
            "transcripcion": transcripcion_limpia,
            "duracion": duracion.seconds
        }
        print(f"\nTranscripción JSON:\n{transcripcion_json}")
        return transcripcion_json

    except Exception as error:
        print(f"❌ Excepción: {error}")

