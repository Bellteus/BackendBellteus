from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException
from pymongo.collection import Collection
from models.ReporteAnalisisModel import ReporteAnalisisSchema
from config.mongodb import get_mongo_client
client = get_mongo_client()
db = client["CALLCENTER-MONGODB"]
collection = db["Cliente-Performance"]

def buscar_Todos_ReporteAnalisis_service(
) -> List[ReporteAnalisisSchema]:
    try:
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
