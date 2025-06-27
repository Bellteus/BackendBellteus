from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from datetime import datetime, timezone  # Añade timezone al import
from service.reporteAnalisis_service import buscar_Todos_ReporteAnalisis_service
from models.ReporteAnalisisModel import ReporteAnalisisSchema

router = APIRouter()



@router.get("/ReporteAnalisisArea", response_model=List[ReporteAnalisisSchema])
def obtener_todos_reportes():
    return buscar_Todos_ReporteAnalisis_service()