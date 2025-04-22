from typing import Dict, Any, List, Optional, Union, Literal
from enum import Enum
from pydantic import BaseModel, Field
from common.models.base_models import ContentRequest, ContentResponse, SystemPromptConfig
from enum import Enum


class LinkedInSystemPromptConfig(SystemPromptConfig):
    """Configuración específica del system prompt para LinkedIn."""
    # Añadir campos específicos para LinkedIn si es necesario
    pass


class LinkedInPostStyle(str, Enum):
    """Estilos disponibles para posts de LinkedIn."""
    LEADERSHIP = "Leadership"
    BEHIND_THE_SCENES = "Behind the Scenes"
    WINS = "Wins"
    CEO_JOURNEY = "CEO Journey"
    HOT_TAKES = "Hot Takes"


class LinkedInAuthor(str, Enum):
    """Autores disponibles para posts de LinkedIn."""
    PABLO = "Pablo"
    AITOR = "Aitor"
    DEFAULT = "Default"  # Autor por defecto sin fine-tuning


class LinkedInPostRequest(ContentRequest):
    """Solicitud para generar un post de LinkedIn."""
    tema: str = Field(description="Tema del post")
    autor: LinkedInAuthor = Field(
        default=LinkedInAuthor.DEFAULT,
        description="Autor cuyo estilo se emulará (requiere modelo fine-tuned)"
    )
    estilo: LinkedInPostStyle = Field(
        default=LinkedInPostStyle.LEADERSHIP,
        description="Estilo del post a generar"
    )
    informacion_adicional: Optional[str] = Field(
        default=None,
        description="Información adicional para contextualizar el post"
    )
    
    # Nuevos parámetros opcionales para el system prompt
    role_description: Optional[str] = Field(
        default=None,
        description="Descripción del rol del autor del contenido"
    )
    content_objective: Optional[str] = Field(
        default=None,
        description="Objetivo principal del contenido"
    )
    style_guidance: Optional[str] = Field(
        default=None,
        description="Guía de estilo para el contenido"
    )
    structure_description: Optional[str] = Field(
        default=None,
        description="Descripción de la estructura del contenido"
    )
    tone: Optional[str] = Field(
        default=None,
        description="Tono del contenido"
    )
    format_guide: Optional[str] = Field(
        default=None,
        description="Guía de formato para el contenido"
    )
    engagement_tips: Optional[str] = Field(
        default=None,
        description="Consejos para aumentar el engagement del contenido"
    )
    limitations: Optional[str] = Field(
        default=None,
        description="Limitaciones a considerar al generar el contenido"
    )
    additional_instructions: Optional[str] = Field(
        default=None,
        description="Instrucciones adicionales para la generación del contenido"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "tema": "Transformación digital en empresas tradicionales",
                "autor": "Default",
                "estilo": "Leadership",
                "informacion_adicional": "Basado en nuestra experiencia reciente con clientes del sector industrial",
                "role_description": "líder visionario con experiencia en transformación digital",
                "content_objective": "inspirar a otros líderes compartiendo perspectivas estratégicas",
                "style_guidance": "Inspirador y estratégico, orientado a resultados",
                "structure_description": "Comienza con un hecho impactante, desarrolla una visión estratégica",
                "tone": "Autoritativo pero accesible, con enfoque en el valor estratégico",
                "format_guide": "Párrafos concisos, una frase destacada, emojis relevantes",
                "engagement_tips": "Compartir una lección personal, mencionar un desafío superado",
                "limitations": "Evitar jerga excesivamente técnica, mantener el enfoque estratégico",
                "additional_instructions": "Balancear visión tecnológica con impacto humano y organizacional"
            }
        }

class LinkedInPostResponse(ContentResponse):
    """Respuesta con el post de LinkedIn generado."""
    texto: str = Field(description="Texto del post")
    hashtags: List[str] = Field(
        default_factory=list,
        description="Hashtags sugeridos"
    )
    autor: str = Field(description="Autor emulado en el post")
    estilo: str = Field(description="Estilo utilizado en el post")
    
    class Config:
        json_schema_extra = {
            "example": {
                "texto": "La transformación digital no es solo sobre tecnología...",
                "hashtags": ["#TransformaciónDigital", "#Liderazgo", "#Innovación"],
                "autor": "Pablo",
                "estilo": "Leadership",
                "metadata": {
                    "generated_at": "2025-04-16T10:30:00Z",
                    "model_used": "ft:gpt-4o-pablo-linkedin-20250320"
                }
            }
        }


class LinkedInStyleConfigRequest(BaseModel):
    """Solicitud para configurar un estilo de LinkedIn."""
    estilo: LinkedInPostStyle
    role_description: Optional[str] = None
    content_objective: Optional[str] = None
    tone: Optional[str] = None
    format_guide: Optional[str] = None
    engagement_tips: Optional[str] = None
    additional_instructions: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "estilo": "Leadership",
                "role_description": "líder visionario con experiencia en transformación digital",
                "content_objective": "inspirar a otros líderes compartiendo perspectivas estratégicas",
                "tone": "Autoritativo pero accesible, con enfoque en el valor estratégico"
            }
        }


class AuthorModelInfo(BaseModel):
    """Información sobre el modelo fine-tuned de un autor."""
    author_id: str
    model_id: str
    description: str
    training_samples: int
    created_at: str
    is_active: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "author_id": "pablo",
                "model_id": "ft:gpt-4o-pablo-linkedin-20250320",
                "description": "Modelo entrenado con 200 posts de Pablo enfocados en liderazgo",
                "training_samples": 200,
                "created_at": "2025-03-20T15:30:00Z",
                "is_active": True
            }
        }