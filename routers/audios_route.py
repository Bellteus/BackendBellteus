from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from datetime import datetime, timezone  # Añade timezone al import
from service.audios_service import buscar_audios_por_id,reporteria_service, buscar_audios_service
from models.audiosModel import AudioMongoSchema, MetadataAudioReporteriaMongoSchema

router = APIRouter()



# ✅ Función para convertir string a datetime
def convertir_fecha(fecha_str: Optional[str]) -> Optional[datetime]:
    if fecha_str:
        try:
            dt = datetime.strptime(fecha_str, "%d-%m-%Y")
            # Ajustar para incluir todo el día y añadir timezone UTC
            return dt.replace(
                hour=0, 
                minute=0, 
                second=0, 
                microsecond=0, 
                tzinfo=timezone.utc
            )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Formato de fecha inválido: {fecha_str}. Usa formato DD-MM-YYYY"
            )
    return None

@router.get("/audios/buscar", response_model=List[AudioMongoSchema])
def buscar_audios(
    FechaHoraInicio: Optional[str] = Query(description="Formato DD-MM-YYYY"),
    fechafin: Optional[str] = Query(description="Formato DD-MM-YYYY"),
    Cliente: Optional[str] = Query(None),
    NombreArea: Optional[str] = Query(None),
    IdEmpleado: Optional[str] = Query(None),
):
    
   # ✅ Convertir fechas aquí
    fecha_inicio_dt = convertir_fecha(FechaHoraInicio)
    fecha_fin_dt = convertir_fecha(fechafin)

    # ✅ Ajustar fin del día
    if fecha_fin_dt:
        fecha_fin_dt = fecha_fin_dt.replace(hour=23, minute=59, second=59, microsecond=999999)

    return buscar_audios_service(
        FechaHoraInicio=fecha_inicio_dt,
        fechafin=fecha_fin_dt,
        Cliente=Cliente,
        NombreArea=NombreArea,
        IdEmpleado=IdEmpleado,
    )

@router.get("/audios/{id}", response_model=AudioMongoSchema)
def buscar_audio_por_id(id: str):
    return buscar_audios_por_id(id)
    
@router.get("/audios/Reporteria", response_model=List[MetadataAudioReporteriaMongoSchema])
def reporteria_audios(
    FechaHoraInicio: str,  # Sin valor por defecto = obligatorio
    fechafin: str,         # Sin valor por defecto = obligatorio
    Cliente: Optional[str] = None,
    NombreArea: Optional[str] = None,
    IdEmpleado: Optional[str] = None,
):
    print("✅ INICIANDO ENDPOINT DE REPORTERÍA")  # <- Asegura que entra aquí

    """
    Endpoint para obtener reportes de audios.
    """
    # ✅ Convertir fechas aquí
    fecha_inicio_dt = convertir_fecha(FechaHoraInicio)
    fecha_fin_dt = convertir_fecha(fechafin)

    resultados=reporteria_service(
        FechaHoraInicio=fecha_inicio_dt,
        fechafin=fecha_fin_dt,
        Cliente=Cliente,
        NombreArea=NombreArea,
        IdEmpleado=IdEmpleado
    )
    print("ENTRÓ AL ENDPOINT")  # Esto debería imprimirse

    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron audios")
    return resultados