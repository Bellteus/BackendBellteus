from typing import Optional,List
from pydantic import BaseModel, Field
from datetime import date, datetime

class AnalisisLLMSchema(BaseModel):
    performance_score: float
    sentimiento_cliente: Optional[str]
    satisfaccion_cliente: Optional[float]
    sentimiento_inicio: Optional[str]
    sentimiento_fin: Optional[str]
    caso_resuelto: Optional[str]
    escalado: Optional[str]
    complejidad_caso: Optional[str]
    acciones_acordadas: Optional[List[str]] = None
    necesita_followup: Optional[str]
    alerta_calidad: Optional[List[str]] = None
    fortalezas: Optional[List[str]] = None
    oportunidades_mejora: Optional[List[str]] = None
    protocolo_cumplido: Optional[str]
    evidencia_frases: Optional[List[str]] = None
    personas_mencionadas: Optional[List[str]] = None
    palabras_clave: Optional[List[str]] = None
    topicos_principales: Optional[List[str]] = None
    resumen: Optional[str]
    observaciones_llm: Optional[str]

class AudioMongoSchema(BaseModel):
    id: str = Field(None, description="ID MongoDB",alias='_id')
    audio_file: Optional[str]= None
    CallId: Optional[int]= None
    FechaHoraInicio: Optional[datetime] = None  # Cambiar date por datetime
    FechaHoraFin: Optional[datetime] = None
    ANI: Optional[float] = None
    CallDirection: Optional[str] = None
    Cliente: Optional[str] = None
    NombreArea: Optional[str] = None
    IdEmpleado: Optional[str] = None
    NombreEmpleado: Optional[str] = None
    TRANSCRIPCION: Optional[str] = None
    ANALISIS_LLM: Optional[AnalisisLLMSchema] = None  # Cambia Any por un modelo si tienes la estructura detallada

    class Config:
        from_attributes = True
        populate_by_name = True


class MetadataAudioReporteriaMongoSchema(BaseModel):
    id: str = Field(None, description="ID MongoDB",alias='_id')
    audio_file: Optional[str]= None
    CallId: Optional[int]= None
    FechaHoraInicio: Optional[datetime] = None  # Cambiar date por datetime
    FechaHoraFin: Optional[datetime] = None
    ANI: Optional[float] = None
    CallDirection: Optional[str] = None
    Cliente: Optional[str] = None
    NombreArea: Optional[str] = None
    IdEmpleado: Optional[str] = None
    NombreEmpleado: Optional[str] = None