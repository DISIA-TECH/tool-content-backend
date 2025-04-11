from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field


class PromptComponent(BaseModel):
    """Componente de un prompt."""
    key: str
    value: str
    description: str


class AgentConfig(BaseModel):
    """Configuración base para un agente."""
    model: str = Field(default="gpt-4")
    temperature: float = Field(default=0.7, ge=0, le=1)
    prompt_components: Dict[str, PromptComponent] = Field(default_factory=dict)


class ContentRequest(BaseModel):
    """Solicitud base para generación de contenido."""
    temperature: Optional[float] = Field(default=0.7, ge=0, le=1)
    model: Optional[str] = None
    system_components: Optional[Dict[str, str]] = None
    

class ContentResponse(BaseModel):
    """Respuesta base de generación de contenido."""
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SystemPromptConfig(BaseModel):
    """Configuración del system prompt."""
    role_description: str
    content_objective: str
    style_guidance: str
    structure_description: str
    tone: Optional[str] = None
    format_guide: Optional[str] = None
    seo_guidelines: Optional[str] = None
    limitations: Optional[str] = None
    additional_instructions: Optional[str] = None
    

class HumanPromptConfig(BaseModel):
    """Configuración del human prompt."""
    template: str