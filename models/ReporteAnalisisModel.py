from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ReporteAnalisisSchema(BaseModel):
    id: str = Field(..., alias="_id")
    cliente: Optional[str] = None
    numero_llamadas: Optional[int] = None
    performance_score_promedio: Optional[float] = None
    satisfaccion_cliente_promedio: Optional[float] = None
    dispersion_performance_score: Optional[float] = None
    dispersion_satisfaccion_cliente: Optional[float] = None
    sentimiento_global: Optional[str] = None
    porcentaje_resueltos: Optional[float] = None
    porcentaje_escalados: Optional[float] = None
    porcentaje_followup: Optional[float] = None
    porcentaje_alertas_calidad: Optional[float] = None
    
    temas_principales: List[str] = Field(default_factory=list)
    palabras_clave_frecuentes: List[str] = Field(default_factory=list)
    fortalezas_recurrentes: List[str] = Field(default_factory=list)
    oportunidades_mejora_recurrentes: List[str] = Field(default_factory=list)
    alertas_calidad_recurrentes: List[str] = Field(default_factory=list)
    
    agentes_destacados: List[str] = Field(default_factory=list)
    agentes_con_bajo_performance: List[str] = Field(default_factory=list)
    
    tendencias: Optional[str] = None
    recomendaciones: List[str] = Field(default_factory=list)
    resumen_ejecutivo: Optional[str] = None
    
    fecha_inicio_busqueda: Optional[datetime] = None
    fecha_fin_busqueda: Optional[datetime] = None
    DateTime_realizado: Optional[datetime] = None