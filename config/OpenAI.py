import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

client=os.getenv("OPENAITOKEN")

def get_openai_client(Promp):
    if not client:
        raise Exception("No OPENAITOKEN configurado")
    

import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

def get_openai_client(ANALYSIS_PROMPT):
    client = OpenAI(api_key=os.getenv("OPENAITOKEN"))
    if not client:
        raise Exception("No OPENAITOKEN configurado")
        # Llamada a la LLM
    respuesta = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": ANALYSIS_PROMPT}],
            temperature=0.2
        )
    return respuesta.choices[0].message.content







































