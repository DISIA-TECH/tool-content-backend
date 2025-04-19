from typing import Dict, Any, List, Optional, Union
import json

from linkedin.models.linkedin_models import (
    LinkedInPostRequest,
    LinkedInPostResponse,
    LinkedInPostStyle,
    LinkedInAuthor,
    LinkedInStyleConfigRequest,
    AuthorModelInfo
)
from linkedin.agents.linkedin_agent import LinkedInAgent
from linkedin.prompts.linkedin_prompts import (
    LinkedInPromptTemplate,
    get_prompt_template_for_style
)
from core.logger import get_logger
from core.config import settings

logger = get_logger("linkedin_service")


class LinkedInService:
    """Servicio para gestionar la generación de posts de LinkedIn."""
    
    def __init__(self):
        """Inicializa el servicio de LinkedIn con el agente necesario."""
        # Inicializar agente base
        self.agent = LinkedInAgent(LinkedInPromptTemplate())
        
        # Configuraciones de estilo por defecto (se podrían cargar de BD o archivo)
        self._style_configs = {}
        
        # Información de los modelos fine-tuned de autores
        self._author_models = {
            LinkedInAuthor.PABLO.value: AuthorModelInfo(
                author_id="pablo",
                model_id="ft:gpt-4o-pablo-linkedin-20250320",  # ID de ejemplo
                description="Modelo entrenado con posts de Pablo enfocados en liderazgo empresarial",
                training_samples=200,
                created_at="2025-03-20T15:30:00Z",
                is_active=True
            ),
            LinkedInAuthor.AITOR.value: AuthorModelInfo(
                author_id="aitor",
                model_id="ft:gpt-4o-aitor-linkedin-20250325",  # ID de ejemplo
                description="Modelo entrenado con posts de Aitor sobre innovación tecnológica",
                training_samples=180,
                created_at="2025-03-25T14:45:00Z",
                is_active=True
            )
        }
        
        logger.info("Servicio de LinkedIn inicializado")
    
    async def generate_post(self, request: LinkedInPostRequest) -> LinkedInPostResponse:
        """
        Genera un post de LinkedIn según la solicitud.
        
        Args:
            request: Solicitud con parámetros para la generación
            
        Returns:
            LinkedInPostResponse: Post generado
        """
        try:
            logger.info(f"Generando post de LinkedIn sobre: {request.tema}, estilo: {request.estilo}, autor: {request.autor}")
            
            # Actualizar temperatura o modelo si se proporcionaron
            if request.temperature is not None or request.model is not None:
                self.agent.update_model_settings(
                    model=request.model or self.agent.model,
                    temperature=request.temperature if request.temperature is not None else self.agent.temperature
                )
            
            # Generar post
            post = await self.agent.generate_post(request)
            return post
            
        except Exception as e:
            logger.error(f"Error al generar post de LinkedIn: {str(e)}")
            raise
    
    async def customize_style(self, request: LinkedInStyleConfigRequest) -> Dict[str, Any]:
        """
        Personaliza la configuración de un estilo de post.
        
        Args:
            request: Solicitud con la configuración del estilo
            
        Returns:
            Dict[str, Any]: Resultado de la operación
        """
        try:
            # Obtener la plantilla base para el estilo
            base_template = get_prompt_template_for_style(request.estilo)
            
            # Crear un diccionario con los valores actuales
            current_config = {
                "role_description": base_template.role_description,
                "content_objective": base_template.content_objective,
                "tone": base_template.tone if hasattr(base_template, "tone") else "",
                "format_guide": base_template.format_guide if hasattr(base_template, "format_guide") else "",
                "engagement_tips": base_template.engagement_tips if hasattr(base_template, "engagement_tips") else "",
                "additional_instructions": base_template.additional_instructions
            }
            
            # Actualizar con los valores proporcionados
            if request.role_description:
                current_config["role_description"] = request.role_description
            if request.content_objective:
                current_config["content_objective"] = request.content_objective
            if request.tone:
                current_config["tone"] = request.tone
            if request.format_guide:
                current_config["format_guide"] = request.format_guide
            if request.engagement_tips:
                current_config["engagement_tips"] = request.engagement_tips
            if request.additional_instructions:
                current_config["additional_instructions"] = request.additional_instructions
            
            # Guardar la configuración personalizada
            self._style_configs[request.estilo.value] = current_config
            
            logger.info(f"Estilo {request.estilo.value} personalizado correctamente")
            
            return {
                "success": True,
                "message": f"Estilo {request.estilo.value} personalizado correctamente",
                "config": current_config
            }
            
        except Exception as e:
            logger.error(f"Error al personalizar estilo: {str(e)}")
            return {
                "success": False,
                "message": f"Error al personalizar estilo: {str(e)}",
                "error": str(e)
            }
    
    async def get_available_styles(self) -> List[Dict[str, Any]]:
        """
        Obtiene los estilos disponibles para posts de LinkedIn.
        
        Returns:
            List[Dict[str, Any]]: Lista de estilos disponibles con sus descripciones
        """
        styles = []
        
        for style in LinkedInPostStyle:
            # Obtener template para este estilo
            template = get_prompt_template_for_style(style)
            
            # Crear descripción del estilo
            style_info = {
                "id": style.value,
                "name": style.value,
                "description": template.content_objective,
                "is_customized": style.value in self._style_configs
            }
            
            styles.append(style_info)
        
        return styles
    
    async def get_available_authors(self) -> List[Dict[str, Any]]:
        """
        Obtiene los autores disponibles para posts de LinkedIn.
        
        Returns:
            List[Dict[str, Any]]: Lista de autores disponibles con información de sus modelos
        """
        authors = []
        
        for author in LinkedInAuthor:
            author_info = {
                "id": author.value,
                "name": author.value
            }
            
            # Añadir información del modelo si está disponible
            if author.value in self._author_models:
                model_info = self._author_models[author.value]
                author_info["model_info"] = {
                    "model_id": model_info.model_id,
                    "description": model_info.description,
                    "training_samples": model_info.training_samples,
                    "created_at": model_info.created_at,
                    "is_active": model_info.is_active
                }
            
            authors.append(author_info)
        
        return authors
    
    async def get_author_details(self, author_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene detalles específicos de un autor.
        
        Args:
            author_id: ID del autor
            
        Returns:
            Optional[Dict[str, Any]]: Detalles del autor o None si no existe
        """
        if author_id in self._author_models:
            model_info = self._author_models[author_id]
            return {
                "id": author_id,
                "name": author_id,  # Podría ser diferente del ID en una implementación real
                "model_info": {
                    "model_id": model_info.model_id,
                    "description": model_info.description,
                    "training_samples": model_info.training_samples,
                    "created_at": model_info.created_at,
                    "is_active": model_info.is_active
                }
            }
        
        return None