from typing import Dict, Any, List, Optional, Union, Literal
from pydantic import BaseModel, Field, HttpUrl
from common.models.base_models import ContentRequest, ContentResponse, SystemPromptConfig


class BlogSystemPromptConfig(SystemPromptConfig):
    """Configuración específica del system prompt para blog."""
    # Añadir campos específicos para blogs si es necesario
    pass


class BlogArticleType(BaseModel):
    """Tipo de artículo de blog."""
    type: Literal["general_interest", "success_case"] = Field(
        description="Tipo de artículo: interés general o caso de éxito"
    )


class GeneralInterestRequest(ContentRequest):
    """Solicitud para generar artículo de interés general."""
    tema: str = Field(description="Tema del artículo")
    palabras_clave_primarias: List[str] = Field(
        description="Lista de palabras clave primarias",
        default_factory=list
    )
    palabras_clave_secundarias: List[str] = Field(
        description="Lista de palabras clave secundarias", 
        default_factory=list
    )
    longitud: str = Field(
        description="Rango de palabras (ej: 800-1200 palabras)",
        default="800-1200 palabras"
    )
    publico_objetivo: str = Field(
        description="Descripción del público objetivo",
        default="Profesionales del sector"
    )
    objetivo: str = Field(
        description="Objetivo del artículo (informar, persuadir, etc.)",
        default="Informar"
    )
    tono_especifico: str = Field(
        description="Tono específico (formal, casual, técnico, etc.)",
        default="Profesional con toque conversacional"
    )
    llamada_accion: str = Field(
        description="Llamada a la acción para el lector",
        default="Contactar para más información"
    )
    elementos_evitar: List[str] = Field(
        description="Temas o enfoques a evitar",
        default_factory=list
    )
    urls_referencia: List[HttpUrl] = Field(
        description="URLs para extraer información adicional",
        default_factory=list
    )
    comentarios_adicionales: Optional[str] = Field(
        default=None,
        description="Comentarios adicionales para la generación"
    )
    # Modificación: cambiar system_components a un diccionario con campos específicos
    system_components: Optional[Dict[str, str]] = Field(
        default=None,
        description="Componentes del sistema para personalizar el prompt"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "tema": "Inteligencia Artificial en el marketing digital",
                "palabras_clave_primarias": ["IA", "marketing digital"],
                "palabras_clave_secundarias": ["ROI", "automatización"],
                "longitud": "1000-1500 palabras",
                "publico_objetivo": "Profesionales de marketing",
                "objetivo": "Informar",
                "tono_especifico": "Profesional con toque conversacional",
                "llamada_accion": "Contactar para asesoría",
                "elementos_evitar": ["Jerga técnica excesiva"],
                "urls_referencia": ["https://example.com/articulo"],
                "comentarios_adicionales": "Incluir ejemplos prácticos",
                "system_components": {
                    "role_description": "especialista en marketing digital",
                    "content_objective": "informar sobre aplicaciones de IA",
                    "tone": "Profesional pero accesible",
                    "style_guidance": "Usar un tono conversacional",
                    "structure_description": "Introducción, desarrollo, conclusión",
                    "format_guide": "Usar párrafos cortos y listas",
                    "seo_guidelines": "Incluir palabras clave de forma natural",
                    "limitations": "No generar contenido engañoso",
                    "additional_instructions": "Incluir estadísticas recientes"
                }
            }
        }


class SuccessCaseRequest(ContentRequest):
    """Solicitud para generar artículo de caso de éxito."""
    tema: str = Field(description="Título o tema del caso de éxito")
    publico_objetivo: str = Field(
        description="Descripción del público objetivo",
        default="Clientes potenciales y actuales"
    )
    objetivo: str = Field(
        description="Objetivo del artículo (mostrar resultados, etc.)",
        default="Mostrar resultados y beneficios"
    )
    tono_especifico: str = Field(
        description="Tono específico (formal, casual, técnico, etc.)",
        default="Profesional con enfoque en logros"
    )
    llamada_accion: str = Field(
        description="Llamada a la acción para el lector",
        default="Solicitar una consulta gratuita"
    )
    pdf_caso_exito: Optional[bool] = Field(
        default=True,
        description="Indicador de si se adjunta PDF con información"
    )
    elementos_evitar: List[str] = Field(
        description="Temas o enfoques a evitar",
        default_factory=list
    )
    comentarios_adicionales: Optional[str] = Field(
        default=None,
        description="Comentarios adicionales para la generación"
    )
    # Modificación: cambiar system_components a un diccionario con campos específicos
    system_components: Optional[Dict[str, str]] = Field(
        default=None,
        description="Componentes del sistema para personalizar el prompt"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "tema": "Aumento de ventas en empresa ABC con nuestra plataforma",
                "publico_objetivo": "Directores comerciales",
                "objetivo": "Demostrar resultados tangibles",
                "tono_especifico": "Profesional con datos concretos",
                "llamada_accion": "Solicitar una demostración",
                "elementos_evitar": ["Información confidencial"],
                "comentarios_adicionales": "Destacar el ROI",
                "system_components": {
                    "role_description": "narrador de casos de éxito",
                    "content_objective": "mostrar resultados medibles",
                    "tone": "Basado en datos y persuasivo"
                }
            }
        }


class BlogArticleResponse(ContentResponse):
    """Respuesta con el artículo de blog generado."""
    titulo: str = Field(description="Título del artículo")
    meta_descripcion: Optional[str] = Field(
        default=None,
        description="Meta descripción para SEO"
    )
    palabras_clave: List[str] = Field(
        default_factory=list,
        description="Palabras clave utilizadas"
    )


class SuccessCaseResponse(BlogArticleResponse):
    """Respuesta con el artículo de caso de éxito generado."""
    resumen_corto: str = Field(description="Resumen corto del caso de éxito")
    contenido_completo: str = Field(description="Contenido completo del caso de éxito")


class BlogPromptCustomizationRequest(BaseModel):
    """Solicitud para personalizar los prompts del generador de blog."""
    role_description: Optional[str] = None
    content_objective: Optional[str] = None
    style_guidance: Optional[str] = None
    structure_description: Optional[str] = None
    tone: Optional[str] = None
    format_guide: Optional[str] = None
    seo_guidelines: Optional[str] = None
    limitations: Optional[str] = None
    additional_instructions: Optional[str] = None
    human_template: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0, le=1)

    class Config:
        json_schema_extra = {
            "example": {
                "role_description": "especialista en contenido de blog tecnológico",
                "tone": "Educativo pero accesible",
                "temperature": 0.8,
                "structure_description": "Introducción, problema, solución, ejemplos, conclusión"
            }
        }