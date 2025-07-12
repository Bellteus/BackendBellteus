from fastapi import FastAPI
from routers.audios_route import router as audio_router
from routers.auth_route import router as auth_router
from routers.reporteAnalisisCliente_route import router as reporteAnalisisArea_router
from routers.reporteAnalisisAgente_route import router as reporteAnalisisAgente_router
import uvicorn
from fastapi.middleware.cors import CORSMiddleware  # 👈 importa esto
from routers.log_route import router as log_router
app = FastAPI()
origins = [
    "http://localhost:5173",         # frontend local
    "http://127.0.0.1:5173",         # otra posible IP local
    "https://bellteus.netlify.app/",  # frontend en producción
    "*"  # 👈 solo para pruebas, permite todo. Evítalo en producción.
]

# 👇 Activa el middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # puede ser ["*"] para pruebas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Registra tus routers
#app.include_router(call_data_records_router)
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(audio_router, tags=["Audios"])
app.include_router(reporteAnalisisArea_router, tags=["Reporte Analisis Cliente"])
app.include_router(reporteAnalisisAgente_router, tags=["Reporte Analisis Agente"])
app.include_router(log_router, tags=["Logs"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001)
