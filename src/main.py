# backend/DESDECERO/src/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Solo usamos router_frames, porque las sesiones ya no existen
from src.api.router_frames import router as frames_router

app = FastAPI(
    title="Attention Monitor API",
    version="2.0.0",
    description="Microservicio para procesar frames y calcular métricas de atención en tiempo real."
)

# CORS para permitir conexión desde React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O usa ["http://localhost:5173"] si deseas restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Attention Monitor API running",
        "version": "2.0.0",
        "endpoints": ["/process"]
    }


# ÚNICO router del microservicio
app.include_router(
    frames_router,
    prefix="",                   # ✔ Sin slash final
    tags=["frames-processing"]
)
