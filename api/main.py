
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.config import settings
from core.logger import app_logger
from api.router import api_router

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas API
app.include_router(api_router, prefix=settings.API_V1_STR)

# Manejo de eventos
@app.on_event("startup")
async def startup_event():
    app_logger.info("Iniciando aplicación...")
    # Verificar configuraciones críticas
    if not settings.OPENAI_API_KEY:
        app_logger.warning("API Key de OpenAI no configurada. Algunas funcionalidades pueden no estar disponibles.")
    
    app_logger.info(f"Aplicación configurada en: {settings.HOST}:{settings.PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    app_logger.info("Cerrando aplicación...")


@app.get("/")
async def root():
    """Endpoint raíz para verificar que la API está funcionando."""
    return {
        "status": "online",
        "name": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION
    }


@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API."""
    return {"status": "healthy"}


if __name__ == "__main__":
    """Punto de entrada para ejecutar la aplicación con uvicorn."""
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )