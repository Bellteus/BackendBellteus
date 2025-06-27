from db.connection import get_connection
from fastapi import HTTPException

def ObtenerMetadata(limit=10):
    try:
        connection = get_connection()
        if not connection:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
        with connection.cursor() as cursor:
            sql = "SELECT * FROM call_data_records LIMIT %s"
            cursor.execute(sql,(limit))
            return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener metadata: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener metadata de la base de datos")
    finally:
        connection.close()



""""
Voy a extraer unos campos de la  metadata para pasarlos a la llm que se encarga de analizar la transcripcion de audio
al momento de devolver el analisis del audio, la llm va a devolver un json con los campos que necesio y anexa los campos extraido de la base dadtos
# que son:
CallId,MediaFileName,FechaHoraInicio,FechaHoraFin,ANI,CallDirection,Cliente,NombreArea,IdEmpleado,NombreEmpleado
"""















