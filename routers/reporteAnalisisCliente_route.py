from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from datetime import datetime, timezone  # Añade timezone al import
from service.reporteAnalisisCliente_service import buscar_Todos_ReporteAnalisis_service,Analizar_llamada_por_Area
from models.reporteAnalisisClienteModel import ReporteAnalisisSchema
router = APIRouter()



@router.get("/ReporteAnalisisArea", response_model=List[ReporteAnalisisSchema])
def obtener_todos_reportes():
    return buscar_Todos_ReporteAnalisis_service()

@router.post("/ReporteAnalisisArea", response_model=ReporteAnalisisSchema)
def Agregar_ReporteAnalis_Cliente(
    Cliente: str,
    FechaInicio: str ,
    FechaFin: str
) -> ReporteAnalisisSchema:
    """
    Endpoint para agregar un reporte de análisis de cliente.
    """
    # Convertir las fechas de string a datetime
    try:
        FechaInicio_dt = datetime.strptime(FechaInicio, "%d-%m-%Y").replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
        )
        FechaFin_dt = datetime.strptime(FechaFin, "%d-%m-%Y").replace(
            hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc
        )
        return Analizar_llamada_por_Area(
        Area=Cliente,
        fecha_inicio=FechaInicio_dt,
        fecha_fin=FechaFin_dt
    )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de fecha inválido. Usa formato DD-MM-YYYY"
        )
    
