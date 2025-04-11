from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings(BaseSettings):
    """Configuraciones de la aplicación."""
    
    # Información del proyecto
    PROJECT_NAME: str = "Content Generator API"
    PROJECT_DESCRIPTION: str = "API para generar contenido estratégico para LinkedIn y Blog usando agentes especializados"
    PROJECT_VERSION: str = "0.1.0"
    
    # API
    API_V1_STR: str = "/api/v1"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8001"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    
    # Configuraciones de Base de Datos
    # PostgreSQL para datos relacionales
    POSTGRES_USER: Optional[str] = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: Optional[str] = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: Optional[str] = os.getenv("POSTGRES_DB")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    # MongoDB para datos no relacionales
    MONGODB_URI: Optional[str] = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "content_generator")
    
    # Qdrant para base de datos vectorial
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "documents")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Configuraciones por defecto para los agentes
    DEFAULT_BLOG_AGENT_CONFIG: Dict[str, Any] = {
        "role_description": "especialista en creación de contenidos para blogs",
        "content_objective": "generar artículos completos, informativos y atractivos",
        "style_guidance": "Mantén un equilibrio entre profesional e informal según la temática",
        "structure_description": "Incluye título, introducción, desarrollo con subtítulos y conclusión"
    }
    
    DEFAULT_LINKEDIN_AGENT_CONFIG: Dict[str, Any] = {
        "role_description": "especialista en creación de contenido para LinkedIn",
        "content_objective": "generar publicaciones virales y de alto impacto",
        "style_guidance": "Profesional pero conversacional, incluye emojis estratégicamente",
        "structure_description": "Utiliza párrafos cortos, llamada a la acción al final"
    }
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env"
    }

# Instancia de configuración
settings = Settings()