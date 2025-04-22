from typing import Dict, Any, List, Optional, Union
import json
import re
import inspect

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
    
    def _create_template_instance(self, template_class, original_template, additional_instructions):
        """
        Crea una nueva instancia de plantilla basada en la clase proporcionada.
        Solo incluye los parámetros que acepta específicamente cada clase.
        
        Args:
            template_class: Clase de la plantilla a crear
            original_template: Plantilla original de la que copiar valores
            additional_instructions: Instrucciones adicionales
            
        Returns:
            LinkedInPromptTemplate: Nueva instancia de la plantilla
        """
        # Inspeccionar la firma del constructor de la clase
        signature = inspect.signature(template_class.__init__)
        valid_params = list(signature.parameters.keys())
        
        # Quitar 'self' que siempre está en la firma pero no se pasa al constructor
        if 'self' in valid_params:
            valid_params.remove('self')
        
        # Crear un diccionario con los parámetros válidos para esta clase
        template_kwargs = {}
        
        # Añadir solo los parámetros que la clase acepta
        param_mapping = {
            'role_description': 'role_description',
            'content_objective': 'content_objective',
            'style_guidance': 'style_guidance',
            'structure_description': 'structure_description',
            'tone': 'tone',
            'format_guide': 'format_guide',
            'additional_instructions': 'additional_instructions',
            'engagement_tips': 'engagement_tips',
            'limitations': 'limitations'
        }
        
        for param_name, attr_name in param_mapping.items():
            if param_name in valid_params and hasattr(original_template, attr_name):
                # Valor especial para instrucciones adicionales
                if param_name == 'additional_instructions':
                    template_kwargs[param_name] = additional_instructions
                else:
                    template_kwargs[param_name] = getattr(original_template, attr_name)
        
        # Crear y devolver la nueva instancia
        return template_class(**template_kwargs)
    
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
            
            # Verificar si se proporcionaron parámetros de system prompt en la solicitud
            # y crear una plantilla personalizada si es necesario
            if any([
                request.role_description is not None,
                request.content_objective is not None,
                request.style_guidance is not None,
                request.structure_description is not None,
                request.tone is not None,
                request.format_guide is not None,
                request.engagement_tips is not None,
                request.limitations is not None,
                request.additional_instructions is not None
            ]):
                # Crear un diccionario con los valores base de la plantilla original
                template_kwargs = {}
                
                # Lista de atributos a verificar y posiblemente sobrescribir
                template_attrs = [
                    'role_description', 'content_objective', 'style_guidance',
                    'structure_description', 'tone', 'format_guide', 
                    'engagement_tips', 'limitations', 'additional_instructions'
                ]
                
                # Para cada atributo, usar el valor de la solicitud si se proporciona,
                # de lo contrario, usar el valor de la plantilla original si existe
                for attr in template_attrs:
                    request_value = getattr(request, attr, None)
                    if request_value is not None:
                        # Si el valor se proporciona en la solicitud, usarlo
                        template_kwargs[attr] = request_value
                    elif hasattr(style_template, attr):
                        # Si no se proporciona pero existe en la plantilla original, usarlo
                        template_kwargs[attr] = getattr(style_template, attr)
                
                # Crear una nueva instancia de la plantilla con los valores combinados
                # Utilizamos la misma clase que la plantilla original
                template_class = type(style_template)
                custom_template = self._create_template_instance(
                    template_class, style_template, template_kwargs.get('additional_instructions', '')
                )
                
                # Para los demás atributos (que no son additional_instructions, ya manejado por _create_template_instance)
                for attr in template_attrs:
                    if attr != 'additional_instructions' and attr in template_kwargs:
                        # Solo establecer atributos que la clase acepta
                        if hasattr(custom_template, attr):
                            setattr(custom_template, attr, template_kwargs[attr])
                
                # Usar esta plantilla personalizada en lugar de la original
                self.update_prompt_template(custom_template)
            else:
                # Si no hay parámetros personalizados, usar la plantilla estándar del estilo
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
                    
                    # Usar nuestro método auxiliar para crear la plantilla correctamente
                    template_class = type(self.prompt_template)
                    new_template = self._create_template_instance(
                        template_class=template_class,
                        original_template=self.prompt_template,
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
                # response_text = format_content_for_readability(response_text)
                
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