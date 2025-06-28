from datetime import datetime, timezone
from fastapi import APIRouter,HTTPException
from typing import List
from models.reporteAnalisisAgenteModel import AnalisisAgenteSchema
from service.reporteAnalisisAgente_service import Analizar_llamada_por_Agente,Mostrar_AnalisisAgente,ObtenerReporteAnalisisAgenteporID

router=APIRouter()
@router.post("/reporteAnalisisAgente", response_model=AnalisisAgenteSchema)
def agregar_reporte_agente(Agente:str, fecha_inicio:str, fecha_fin:str)-> List[AnalisisAgenteSchema]:
    """
    Endpoint para obtener todos los reportes de análisis de agentes.
    """
    try:
        FechaInicio_dt = datetime.strptime(fecha_inicio, "%d-%m-%Y").replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
        )
        FechaFin_dt = datetime.strptime(fecha_fin, "%d-%m-%Y").replace(
            hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc
        )
        return Analizar_llamada_por_Agente(
        Agente=Agente,
        fecha_inicio=FechaInicio_dt,
        fecha_fin=FechaFin_dt
    )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de fecha inválido. Usa formato DD-MM-YYYY"
        )
    
@router.get("/reporteAnalisisAgente", response_model=List[AnalisisAgenteSchema])
def mostrar_analisis_agente(
    Agente: str,
    fecha_inicio: str,
    fecha_fin: str
) -> List[AnalisisAgenteSchema]:
    """
    Endpoint para mostrar análisis de un agente en un rango de fechas.
    """
    try:
        FechaInicio_dt = datetime.strptime(fecha_inicio, "%d-%m-%Y").replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
        )
        FechaFin_dt = datetime.strptime(fecha_fin, "%d-%m-%Y").replace(
            hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc
        )
        return Mostrar_AnalisisAgente(
            Agente=Agente,
            fecha_inicio=FechaInicio_dt,
            fecha_fin=FechaFin_dt
        )
    
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de fecha inválido. Usa formato DD-MM-YYYY"
        )
    

@router.get("/reporteAnalisisAgente/{id}",response_model=AnalisisAgenteSchema)
def mostrar_reporteAnalisisAgentebyId(id:str)-> AnalisisAgenteSchema :
      """
    Endpoint para mostrar análisis de un agente por Id.
        """
      try:
        return ObtenerReporteAnalisisAgenteporID(
             id
        )
    
      except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de fecha inválido. Usa formato DD-MM-YYYY"
        )
    