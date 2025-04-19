from typing import Dict, Any, List, Optional, Union
import json
import re

from common.base_agent import BaseAgent
from common.utils.helpers import extract_hashtags, format_content_for_readability
from linkedin.prompts.linkedin_prompts import (
    LinkedInPromptTemplate,
    get_prompt_template_for_style,
    get_author_system_prompt
)
from linkedin.models.linkedin_models import (
    LinkedInPostRequest,
    LinkedInPostResponse,
    LinkedInPostStyle,
    LinkedInAuthor
)
from core.logger import get_logger
from core.config import settings

logger = get_logger("linkedin_agent")


class LinkedInAgent(BaseAgent):
    """Agente para generación de posts de LinkedIn."""
    
    def __init__(
        self,
        prompt_template: LinkedInPromptTemplate,
        model: str = settings.OPENAI_MODEL,
        temperature: float = settings.DEFAULT_TEMPERATURE
    ):
        """
        Inicializa el agente para LinkedIn.
        
        Args:
            prompt_template: Plantilla de prompts específica para LinkedIn
            model: Modelo de lenguaje a utilizar
            temperature: Temperatura para la generación
        """
        super().__init__(prompt_template, model, temperature)
        logger.info(f"Agente de LinkedIn inicializado con modelo {model}")
    
    @staticmethod
    def _parse_linkedin_post(response_text: str) -> Dict[str, Any]:
        """
        Parsea la respuesta del LLM para obtener estructura.
        
        Args:
            response_text: Texto de respuesta del LLM
            
        Returns:
            Dict[str, Any]: Datos estructurados del post
        """
        try:
            # Extraer hashtags
            hashtags = extract_hashtags(response_text)
            
            # Considerar todo el texto como contenido del post
            post_text = response_text
            
            return {
                "texto": post_text,
                "hashtags": hashtags
            }
        except Exception as e:
            logger.error(f"Error al parsear respuesta de LinkedIn: {str(e)}")
            return {
                "texto": response_text,
                "hashtags": []
            }
    
    def _get_model_for_author(self, author: LinkedInAuthor) -> str:
        """
        Determina qué modelo usar según el autor seleccionado.
        
        Args:
            author: Autor seleccionado
            
        Returns:
            str: ID del modelo a utilizar
        """
        # Mapeo de autores a modelos fine-tuned
        author_models = {
            LinkedInAuthor.PABLO: "ft:gpt-4o-pablo-linkedin-20250320",  # Ejemplo, a reemplazar con el ID real
            LinkedInAuthor.AITOR: "ft:gpt-4o-aitor-linkedin-20250325",  # Ejemplo, a reemplazar con el ID real
        }
        
        # Si hay un modelo específico para el autor, usarlo
        if author in author_models:
            return author_models[author]
        
        # Si no, usar el modelo predeterminado
        return self.model
    
    async def generate_content(self, **kwargs) -> Any:
        """
        Implementación del método abstracto de BaseAgent.
        Este método simplemente llama a generate_post con los kwargs.
        
        Args:
            **kwargs: Parámetros para la generación
            
        Returns:
            Any: Contenido generado
        """
        if isinstance(kwargs.get("request"), LinkedInPostRequest):
            return await self.generate_post(kwargs["request"])
        else:
            logger.error("Se requiere un objeto LinkedInPostRequest para generar contenido")
            raise ValueError("Se requiere un objeto LinkedInPostRequest para generar contenido")
    
    async def generate_post(self, request: LinkedInPostRequest) -> LinkedInPostResponse:
        """
        Genera un post de LinkedIn según la solicitud.
        
        Args:
            request: Solicitud de generación de post
            
        Returns:
            LinkedInPostResponse: Post de LinkedIn generado
        """
        try:
            # Seleccionar plantilla según el estilo
            style_template = get_prompt_template_for_style(request.estilo)
            original_template = self.prompt_template
            self.update_prompt_template(style_template)
            
            # Determinar si usar un modelo fine-tuned o el modelo estándar
            use_fine_tuned = request.autor != LinkedInAuthor.DEFAULT
            original_model = self.model
            
            if use_fine_tuned:
                # Actualizar el modelo al específico del autor
                fine_tuned_model = self._get_model_for_author(request.autor)
                self.update_model_settings(model=fine_tuned_model)
                
                # Añadir instrucciones específicas para emular al autor
                author_instructions = get_author_system_prompt(request.autor)
                if author_instructions:
                    additional_instructions = self.prompt_template.additional_instructions or ""
                    combined_instructions = f"{additional_instructions}\n\n{author_instructions}" if additional_instructions else author_instructions
                    
                    # Crear nueva plantilla con las instrucciones del autor
                    new_template = type(style_template)(
                        role_description=style_template.role_description,
                        content_objective=style_template.content_objective,
                        style_guidance=style_template.style_guidance,
                        structure_description=style_template.structure_description,
                        tone=style_template.tone,
                        format_guide=style_template.format_guide,
                        engagement_tips=style_template.engagement_tips if hasattr(style_template, 'engagement_tips') else "",
                        limitations=style_template.limitations,
                        additional_instructions=combined_instructions
                    )
                    self.update_prompt_template(new_template)
            
            # Preparar kwargs para el prompt
            kwargs = {
                "tema": request.tema,
                "informacion_adicional": request.informacion_adicional or "No se proporcionó información adicional."
            }
            
            # Generar el post
            try:
                response_text = await self._call_llm(**kwargs)
                
                # Formatear para legibilidad
                response_text = format_content_for_readability(response_text)
                
                # Procesar la respuesta
                parsed_response = self._parse_linkedin_post(response_text)
                
                # Crear respuesta estructurada
                return LinkedInPostResponse(
                    texto=parsed_response["texto"],
                    hashtags=parsed_response["hashtags"],
                    content=parsed_response["texto"],  # Para compatibilidad con ContentResponse
                    autor=request.autor.value,
                    estilo=request.estilo.value,
                    metadata={
                        "post_type": "linkedin",
                        "author": request.autor.value,
                        "style": request.estilo.value,
                        "model_used": self.model,
                        "temperature": self.temperature
                    }
                )
            finally:
                # Restaurar plantilla y modelo originales
                self.update_prompt_template(original_template)
                if use_fine_tuned:
                    self.update_model_settings(model=original_model)
                
        except Exception as e:
            logger.error(f"Error al generar post de LinkedIn: {str(e)}")
            raise