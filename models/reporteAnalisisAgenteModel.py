from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class ProtocoloCumplidoSchema(BaseModel):
    sí: Optional[int]
    parcial: Optional[int]
    no: Optional[int]

class AnalisisAgenteSchema(BaseModel):
    _id:str
    id_empleado: str
    nombre_empleado: Optional[str]
    numero_llamadas: Optional[int]
    performance_score_promedio: Optional[float]
    satisfaccion_cliente_promedio: Optional[float]
    dispersión_performance_score: Optional[float]
    dispersión_satisfaccion_cliente: Optional[float]
    sentimiento_predominante: Optional[str]
    porcentaje_resueltos: Optional[float]
    porcentaje_escalados: Optional[float]
    porcentaje_followup: Optional[float]
    porcentaje_alertas_calidad: Optional[float]
    protocolo_cumplido: Optional[ProtocoloCumplidoSchema]
    fortalezas_recurrentes: Optional[List[str]]
    oportunidades_mejora_recurrentes: Optional[List[str]]
    temas_principales: Optional[List[str]]
    palabras_clave_frecuentes: Optional[List[str]]
    alertas_calidad_recurrentes: Optional[List[str]]
    recomendaciones: Optional[List[str]]
    resumen_ejecutivo: Optional[str]
    fecha_inicio_busqueda: Optional[str]
    fecha_fin_busqueda: Optional[str]
    DateTime_realizado: Optional[str]

AnalisisAgenteSchema.model_rebuild()
