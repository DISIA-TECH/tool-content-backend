from typing import Dict, Any, List, Optional, Union
import json

from blog.agents.blog_agent import GeneralInterestBlogAgent, SuccessCaseBlogAgent
from blog.models.blog_models import (
    GeneralInterestRequest, 
    SuccessCaseRequest, 
    BlogArticleResponse,
    SuccessCaseResponse,
    BlogPromptCustomizationRequest,
    BlogArticleType
)
from blog.prompts.blog_prompts import GeneralInterestPromptTemplate, SuccessCasePromptTemplate
from core.logger import get_logger
from core.config import settings

logger = get_logger("blog_service")


class BlogService:
    """Servicio para gestionar la generación de artículos de blog."""
    
    def __init__(self):
        """Inicializa el servicio de blog con los agentes necesarios."""
        # Inicializar agentes
        self.general_interest_agent = GeneralInterestBlogAgent()
        self.success_case_agent = SuccessCaseBlogAgent()
        
        logger.info("Servicio de blog inicializado")
    
    async def customize_general_interest_prompt(self, request: BlogPromptCustomizationRequest) -> Dict[str, Any]:
        """
        Personaliza el prompt para artículos de interés general.
        
        Args:
            request: Solicitud de personalización
            
        Returns:
            Dict[str, Any]: Resultado de la operación
        """
        try:
            await self.general_interest_agent.update_customization(request)
            
            # Obtener configuración actual
            template = self.general_interest_agent.prompt_template
            logger.info("hola mundo", template)
            model = self.general_interest_agent.model
            temperature = self.general_interest_agent.temperature
            
            return {
                "success": True,
                "message": "Prompt para artículos de interés general personalizado correctamente",
                "config": {
                    "role_description": template.role_description,
                    "content_objective": template.content_objective,
                    "style_guidance": template.style_guidance,
                    "structure_description": template.structure_description,
                    "tone": template.tone,
                    "format_guide": template.format_guide,
                    "seo_guidelines": template.seo_guidelines,
                    "limitations": template.limitations,
                    "additional_instructions": template.additional_instructions,
                    "model": model,
                    "temperature": temperature
                }
            }
        except Exception as e:
            logger.error(f"Error al personalizar prompt de interés general: {str(e)}")
            return {
                "success": False,
                "message": f"Error al personalizar prompt: {str(e)}",
                "error": str(e)
            }
    
    async def customize_success_case_prompt(self, request: BlogPromptCustomizationRequest) -> Dict[str, Any]:
        """
        Personaliza el prompt para casos de éxito.
        
        Args:
            request: Solicitud de personalización
            
        Returns:
            Dict[str, Any]: Resultado de la operación
        """
        try:
            await self.success_case_agent.update_customization(request)
            
            # Obtener configuración actual
            template = self.success_case_agent.prompt_template
            model = self.success_case_agent.model
            temperature = self.success_case_agent.temperature
            
            return {
                "success": True,
                "message": "Prompt para casos de éxito personalizado correctamente",
                "config": {
                    "role_description": template.role_description,
                    "content_objective": template.content_objective,
                    "style_guidance": template.style_guidance,
                    "structure_description": template.structure_description,
                    "tone": template.tone,
                    "format_guide": template.format_guide,
                    "seo_guidelines": template.seo_guidelines,
                    "limitations": template.limitations,
                    "additional_instructions": template.additional_instructions,
                    "model": model,
                    "temperature": temperature
                }
            }
        except Exception as e:
            logger.error(f"Error al personalizar prompt de casos de éxito: {str(e)}")
            return {
                "success": False,
                "message": f"Error al personalizar prompt: {str(e)}",
                "error": str(e)
            }
    
    async def get_prompt_configurations(self) -> Dict[str, Any]:
        """
        Obtiene las configuraciones actuales de los prompts.
        
        Returns:
            Dict[str, Any]: Configuraciones de los prompts
        """
        return {
            "general_interest": {
                "role_description": self.general_interest_agent.prompt_template.role_description,
                "content_objective": self.general_interest_agent.prompt_template.content_objective,
                "style_guidance": self.general_interest_agent.prompt_template.style_guidance,
                "structure_description": self.general_interest_agent.prompt_template.structure_description,
                "tone": self.general_interest_agent.prompt_template.tone,
                "format_guide": self.general_interest_agent.prompt_template.format_guide,
                "seo_guidelines": self.general_interest_agent.prompt_template.seo_guidelines,
                "limitations": self.general_interest_agent.prompt_template.limitations,
                "additional_instructions": self.general_interest_agent.prompt_template.additional_instructions,
                "model": self.general_interest_agent.model,
                "temperature": self.general_interest_agent.temperature
            },
            "success_case": {
                "role_description": self.success_case_agent.prompt_template.role_description,
                "content_objective": self.success_case_agent.prompt_template.content_objective,
                "style_guidance": self.success_case_agent.prompt_template.style_guidance,
                "structure_description": self.success_case_agent.prompt_template.structure_description,
                "tone": self.success_case_agent.prompt_template.tone,
                "format_guide": self.success_case_agent.prompt_template.format_guide,
                "seo_guidelines": self.success_case_agent.prompt_template.seo_guidelines,
                "limitations": self.success_case_agent.prompt_template.limitations,
                "additional_instructions": self.success_case_agent.prompt_template.additional_instructions,
                "model": self.success_case_agent.model,
                "temperature": self.success_case_agent.temperature
            }
        }
    
    async def generate_general_interest_article(self, request: GeneralInterestRequest) -> BlogArticleResponse:
        """
        Genera un artículo de interés general.
        
        Args:
            request: Solicitud de generación
            
        Returns:
            BlogArticleResponse: Artículo generado
        """
        try:
            logger.info(f"Generando artículo de interés general sobre: {request.tema}")
            return await self.general_interest_agent.generate_content(request)
        except Exception as e:
            logger.error(f"Error al generar artículo de interés general: {str(e)}")
            raise
    
    async def generate_success_case_article(
        self, 
        request: SuccessCaseRequest, 
        pdf_content: Optional[bytes] = None
    ) -> SuccessCaseResponse:
        """
        Genera un artículo de caso de éxito.
        
        Args:
            request: Solicitud de generación
            pdf_content: Contenido del PDF con detalles del caso (opcional)
            
        Returns:
            SuccessCaseResponse: Artículo de caso de éxito generado
        """
        try:
            logger.info(f"Generando artículo de caso de éxito sobre: {request.tema}")
            return await self.success_case_agent.generate_content(request, pdf_content)
        except Exception as e:
            logger.error(f"Error al generar artículo de caso de éxito: {str(e)}")
            raise
    
    async def generate_blog_article(
        self, 
        article_type: str,
        request: Union[GeneralInterestRequest, SuccessCaseRequest],
        pdf_content: Optional[bytes] = None
    ) -> Union[BlogArticleResponse, SuccessCaseResponse]:
        """
        Genera un artículo de blog según el tipo especificado.
        
        Args:
            article_type: Tipo de artículo ("general_interest" o "success_case")
            request: Solicitud de generación
            pdf_content: Contenido del PDF para casos de éxito (opcional)
            
        Returns:
            Union[BlogArticleResponse, SuccessCaseResponse]: Artículo generado
        """
        if article_type == "general_interest":
            return await self.generate_general_interest_article(request)
        elif article_type == "success_case":
            return await self.generate_success_case_article(request, pdf_content)
        else:
            raise ValueError(f"Tipo de artículo no válido: {article_type}")