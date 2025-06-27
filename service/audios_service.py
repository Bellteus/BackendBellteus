from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException
from pymongo.collection import Collection
from models.audiosModel import AudioMongoSchema, MetadataAudioReporteriaMongoSchema
from config.mongodb import get_mongo_client
client = get_mongo_client()
db = client["CALLCENTER-MONGODB"]
collection = db["ANALISIS-LLMS"]

def buscar_audios_service(
    FechaHoraInicio: datetime,  # Sin valor por defecto = obligatorio
    fechafin: datetime,         # Sin valor por defecto = obligatorio
    Cliente: Optional[str] = None,
    NombreArea: Optional[str] = None,
    IdEmpleado: Optional[str] = None,
) -> List[AudioMongoSchema]:
    """
    Busca audios en MongoDB filtrando por rango de fechas (obligatorio) y otros criterios opcionales.
    
    Args:
        FechaHoraInicio (datetime): Fecha de inicio del rango (requerido)
        fechafin (datetime): Fecha de fin del rango (requerido)
        Cliente (Optional[str]): Filtro por cliente
        NombreArea (Optional[str]): Filtro por área
        IdEmpleado (Optional[str]): Filtro por ID de empleado
    
    Returns:
        List[AudioMongoSchema]: Lista de audios que coinciden con los criterios
    
    Raises:
        HTTPException: 404 si no se encuentran resultados
    """
    
    # Construcción del query
    query = {
        "FechaHoraInicio": {
            "$gte": FechaHoraInicio,
            "$lte": fechafin
        }
    }
    
    # Añadir filtros opcionales
    if Cliente is not None:
        query["Cliente"] = Cliente
    if NombreArea is not None:
        query["NombreArea"] = NombreArea
    if IdEmpleado is not None:
        query["IdEmpleado"] = IdEmpleado
    
    # Ejecutar consulta
    audios = list(collection.find(query))
    if not audios:
        raise HTTPException(
            status_code=404, 
            detail="No se encontraron audios con los criterios especificados"
        )
    
    # Procesar resultados
    resultados = []
    for audio in audios:
        try:
            resultados.append(AudioMongoSchema(**audio))
        except Exception as e:
            print(f"Error procesando documento: {e}")
            continue
    
    return resultados
def buscar_audios_por_id(id: str) -> Optional[AudioMongoSchema]:
    audio = collection.find_one({"_id": id})
    if audio:
        return AudioMongoSchema(**audio)
    return  HTTPException(status_code=404, detail="Audio no encontrado")

def reporteria_service(
    FechaHoraInicio: datetime,  # Sin valor por defecto = obligatorio
    fechafin: datetime,         # Sin valor por defecto = obligatorio
    Cliente: Optional[str] = None,
    NombreArea: Optional[str] = None,
    IdEmpleado: Optional[str] = None,
) -> List[MetadataAudioReporteriaMongoSchema]:
    print("Reporteria----")
     # Construcción del query
    query = {
        "FechaHoraInicio": {
            "$gte": FechaHoraInicio,
            "$lte": fechafin
        }
    }
    
    # Añadir filtros opcionales
    if Cliente is not None:
        query["Cliente"] = Cliente
    if NombreArea is not None:
        query["NombreArea"] = NombreArea
    if IdEmpleado is not None:
        query["IdEmpleado"] = IdEmpleado

    # Ejecutar consulta
    audios = list(collection.find(query) )
    print(audios)

    if not audios:
        raise HTTPException(
            status_code=404, 
            detail="No se encontraron audios con los criterios especificados"
        )
    
    # Procesar resultados
    resultados = []
    for audio in audios:
        try:
            resultados.append(MetadataAudioReporteriaMongoSchema(**audio))
        except Exception as e:
            print(f"Error procesando documento: {e}")
            continue
    
    return resultados
