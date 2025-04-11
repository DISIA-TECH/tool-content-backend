from typing import Dict, Any, List, Optional, Union
import json

from common.base_agent import BaseAgent
from blog.prompts.blog_prompts import BlogPromptTemplate, GeneralInterestPromptTemplate, SuccessCasePromptTemplate
from blog.models.blog_models import (
    GeneralInterestRequest, 
    SuccessCaseRequest, 
    BlogArticleResponse,
    SuccessCaseResponse,
    BlogPromptCustomizationRequest
)
from common.utils.helpers import extract_text_from_pdf, extract_content_from_url, format_content_for_readability
from core.logger import get_logger
from core.config import settings

logger = get_logger("blog_agent")


class BlogAgent(BaseAgent):
    """Agente base para generación de artículos de blog."""
    
    def __init__(
        self,
        prompt_template: BlogPromptTemplate,
        model: str = settings.OPENAI_MODEL,
        temperature: float = settings.DEFAULT_TEMPERATURE
    ):
        """
        Inicializa el agente para blog.
        
        Args:
            prompt_template: Plantilla de prompts específica para blog
            model: Modelo de lenguaje a utilizar
            temperature: Temperatura para la generación
        """
        super().__init__(prompt_template, model, temperature)
    
    async def update_customization(self, request: BlogPromptCustomizationRequest) -> None:
        """
        Actualiza la personalización del agente con la configuración proporcionada.
        
        Args:
            request: Solicitud de personalización
        """
        # Obtener configuración actual
        current_prompt_template = self.prompt_template
        
        # Actualizar solo campos no nulos
        role_description = request.role_description or current_prompt_template.role_description
        content_objective = request.content_objective or current_prompt_template.content_objective
        style_guidance = request.style_guidance or current_prompt_template.style_guidance
        structure_description = request.structure_description or current_prompt_template.structure_description
        tone = request.tone or current_prompt_template.tone
        format_guide = request.format_guide or current_prompt_template.format_guide
        seo_guidelines = request.seo_guidelines or current_prompt_template.seo_guidelines
        limitations = request.limitations or current_prompt_template.limitations
        additional_instructions = request.additional_instructions or current_prompt_template.additional_instructions
        
        # Crear nueva instancia del mismo tipo
        new_template = type(current_prompt_template)(
            role_description=role_description,
            content_objective=content_objective,
            style_guidance=style_guidance,
            structure_description=structure_description,
            tone=tone,
            format_guide=format_guide,
            seo_guidelines=seo_guidelines,
            limitations=limitations,
            additional_instructions=additional_instructions
        )
        
        # Actualizar plantilla
        self.update_prompt_template(new_template)
        
        # Actualizar configuración del modelo si se proporcionó
        if request.model or request.temperature is not None:
            self.update_model_settings(model=request.model, temperature=request.temperature)
        
        logger.info("Configuración del agente de blog actualizada")
    
    @staticmethod
    def _parse_blog_response(response_text: str) -> Dict[str, Any]:
        """
        Parsea la respuesta del LLM para obtener estructura.
        
        Args:
            response_text: Texto de respuesta del LLM
            
        Returns:
            Dict[str, Any]: Datos estructurados del artículo
        """
        try:
            # Extraer título
            title_match = response_text.split("\n")[0]
            if "# " in title_match:
                title = title_match.replace("# ", "")
            else:
                title = title_match
            
            # Extraer meta descripción si existe
            meta_description = None
            meta_match = response_text.lower().find("meta descripción")
            if meta_match != -1:
                end_line = response_text.find("\n", meta_match)
                if end_line != -1:
                    meta_text = response_text[meta_match:end_line]
                    parts = meta_text.split(":", 1)
                    if len(parts) > 1:
                        meta_description = parts[1].strip()
            
            # Extraer palabras clave si existen
            keywords = []
            keywords_match = response_text.lower().find("palabras clave")
            if keywords_match != -1:
                end_line = response_text.find("\n", keywords_match)
                if end_line != -1:
                    keywords_text = response_text[keywords_match:end_line]
                    parts = keywords_text.split(":", 1)
                    if len(parts) > 1:
                        keywords_raw = parts[1].strip()
                        keywords = [k.strip() for k in keywords_raw.split(",")]
            
            # El contenido es todo el texto
            content = response_text
            
            return {
                "titulo": title,
                "meta_descripcion": meta_description,
                "palabras_clave": keywords,
                "content": content
            }
        except Exception as e:
            logger.error(f"Error al parsear respuesta del blog: {str(e)}")
            # En caso de error, devolver el contenido completo con un título genérico
            return {
                "titulo": "Artículo de blog",
                "content": response_text
            }
    
    @staticmethod
    def _parse_success_case_response(response_text: str) -> Dict[str, Any]:
        """
        Parsea la respuesta del LLM para casos de éxito.
        
        Args:
            response_text: Texto de respuesta del LLM
            
        Returns:
            Dict[str, Any]: Datos estructurados del caso de éxito
        """
        try:
            # Buscar secciones de resumen y contenido completo
            resumen_idx = response_text.lower().find("versión corta")
            if resumen_idx == -1:
                resumen_idx = response_text.lower().find("resumen ejecutivo")
            
            completo_idx = response_text.lower().find("versión completa")
            if completo_idx == -1:
                completo_idx = response_text.lower().find("versión detallada")
            
            # Si no se encuentran marcadores, dividir en título y contenido
            if resumen_idx == -1 or completo_idx == -1:
                # Extraer título
                title_match = response_text.split("\n")[0]
                if "# " in title_match:
                    title = title_match.replace("# ", "")
                else:
                    title = title_match
                
                # Generar un resumen de las primeras 200 palabras
                words = response_text.split()
                resumen = " ".join(words[:200])
                
                return {
                    "titulo": title,
                    "resumen_corto": resumen,
                    "contenido_completo": response_text,
                    "meta_descripcion": None,
                    "palabras_clave": []
                }
            
            # Extraer título (tomar la primera línea antes de cualquier marcador)
            first_part = response_text[:min(resumen_idx, completo_idx)]
            title_lines = [line for line in first_part.split("\n") if line.strip()]
            title = title_lines[0].replace("# ", "") if title_lines else "Caso de Éxito"
            
            # Determinar qué sección viene primero
            if resumen_idx < completo_idx:
                resumen = response_text[resumen_idx:completo_idx].strip()
                completo = response_text[completo_idx:].strip()
            else:
                completo = response_text[completo_idx:resumen_idx].strip()
                resumen = response_text[resumen_idx:].strip()
            
            # Limpiar etiquetas de sección
            for marker in ["versión corta:", "resumen ejecutivo:", "versión completa:", "versión detallada:"]:
                resumen = resumen.lower().replace(marker, "").strip()
                completo = completo.lower().replace(marker, "").strip()
            
            # Extraer meta descripción si existe
            meta_description = None
            meta_match = response_text.lower().find("meta descripción")
            if meta_match != -1:
                end_line = response_text.find("\n", meta_match)
                if end_line != -1:
                    meta_text = response_text[meta_match:end_line]
                    parts = meta_text.split(":", 1)
                    if len(parts) > 1:
                        meta_description = parts[1].strip()
            
            # Extraer palabras clave si existen
            keywords = []
            keywords_match = response_text.lower().find("palabras clave")
            if keywords_match != -1:
                end_line = response_text.find("\n", keywords_match)
                if end_line != -1:
                    keywords_text = response_text[keywords_match:end_line]
                    parts = keywords_text.split(":", 1)
                    if len(parts) > 1:
                        keywords_raw = parts[1].strip()
                        keywords = [k.strip() for k in keywords_raw.split(",")]
            
            return {
                "titulo": title,
                "resumen_corto": resumen,
                "contenido_completo": completo,
                "meta_descripcion": meta_description,
                "palabras_clave": keywords
            }
        except Exception as e:
            logger.error(f"Error al parsear respuesta del caso de éxito: {str(e)}")
            return {
                "titulo": "Caso de Éxito",
                "resumen_corto": response_text[:200],
                "contenido_completo": response_text,
                "meta_descripcion": None,
                "palabras_clave": []
            }
    
    async def generate_content(self, **kwargs) -> Union[BlogArticleResponse, SuccessCaseResponse]:
        """
        Método abstracto que debe ser implementado por las subclases.
        """
        raise NotImplementedError("Debe implementarse en las subclases")


class GeneralInterestBlogAgent(BlogAgent):
    """Agente para generar artículos de blog de interés general."""
    
    def __init__(
        self,
        prompt_template: Optional[GeneralInterestPromptTemplate] = None,
        model: str = settings.OPENAI_MODEL,
        temperature: float = settings.DEFAULT_TEMPERATURE
    ):
        """
        Inicializa el agente para artículos de interés general.
        
        Args:
            prompt_template: Plantilla de prompts para artículos de interés general
            model: Modelo de lenguaje a utilizar
            temperature: Temperatura para la generación
        """
        template = prompt_template or GeneralInterestPromptTemplate()
        super().__init__(template, model, temperature)
        logger.info(f"Agente de blog para artículos de interés general inicializado con modelo {model}")
    
    async def _get_url_contents(self, urls: List[str]) -> str:
        """
        Obtiene contenido de las URLs proporcionadas.
        
        Args:
            urls: Lista de URLs
            
        Returns:
            str: Contenido extraído
        """
        contents = []
        for url in urls:
            try:
                content = extract_content_from_url(url)
                # Limitar tamaño para evitar tokens excesivos
                if content:
                    summary = content[:2000]
                    contents.append(f"Contenido de {url}:\n{summary}\n")
            except Exception as e:
                logger.error(f"Error al extraer contenido de URL {url}: {str(e)}")
                contents.append(f"No se pudo extraer contenido de {url}\n")
        
        if not contents:
            return ""
        
        return "\n".join(contents)
    
    async def generate_content(self, request: GeneralInterestRequest) -> BlogArticleResponse:
        """
        Genera un artículo de blog de interés general.
        
        Args:
            request: Solicitud de generación
            
        Returns:
            BlogArticleResponse: Artículo generado
        """
        try:
            # Actualizar configuración del modelo si se especifica
            if request.model or request.temperature is not None:
                self.update_model_settings(
                    model=request.model or self.model,
                    temperature=request.temperature if request.temperature is not None else self.temperature
                )
            
            # Extraer contenido de URLs si se proporcionaron
            urls_content = ""
            if request.urls_referencia:
                urls_content = await self._get_url_contents(request.urls_referencia)
                
            # Preparar kwargs para el prompt
            kwargs = {
                "tema": request.tema,
                "palabras_clave_primarias": ", ".join(request.palabras_clave_primarias),
                "palabras_clave_secundarias": ", ".join(request.palabras_clave_secundarias),
                "longitud": request.longitud,
                "publico_objetivo": request.publico_objetivo,
                "objetivo": request.objetivo,
                "tono_especifico": request.tono_especifico,
                "llamada_accion": request.llamada_accion,
                "elementos_evitar": ", ".join(request.elementos_evitar),
                "urls_referencia": ", ".join([str(url) for url in request.urls_referencia]),
                "comentarios_adicionales": request.comentarios_adicionales or ""
            }
            
            # Añadir información de URLs al prompt si está disponible
            if urls_content:
                kwargs["comentarios_adicionales"] += f"\n\nInformación adicional de las URLs:\n{urls_content}"
            
            # Manejar system_components si se proporcionaron
            if request.system_components:
                original_template = self.prompt_template
                try:
                    # Verificar qué campos de system_components son válidos para el constructor
                    valid_fields = {
                        'role_description', 'content_objective', 'style_guidance', 
                        'structure_description', 'tone', 'format_guide', 
                        'seo_guidelines', 'limitations', 'additional_instructions'
                    }
                    
                    # Filtrar solo los campos válidos
                    filtered_components = {
                        k: v for k, v in request.system_components.items() 
                        if k in valid_fields and v is not None
                    }
                    
                    # Si hay campos válidos, crear una nueva plantilla
                    if filtered_components:
                        # Crear una nueva plantilla con los campos proporcionados
                        # y mantener los valores originales para los campos no proporcionados
                        template_args = {
                            'role_description': original_template.role_description,
                            'content_objective': original_template.content_objective,
                            'style_guidance': original_template.style_guidance,
                            'structure_description': original_template.structure_description,
                            'tone': original_template.tone if hasattr(original_template, 'tone') else "",
                            'format_guide': original_template.format_guide if hasattr(original_template, 'format_guide') else "",
                            'seo_guidelines': original_template.seo_guidelines if hasattr(original_template, 'seo_guidelines') else "",
                            'limitations': original_template.limitations if hasattr(original_template, 'limitations') else "",
                            'additional_instructions': original_template.additional_instructions
                        }
                        
                        # Actualizar con los campos proporcionados
                        template_args.update(filtered_components)
                        
                        # Crear la plantilla temporal
                        temp_template = type(original_template)(**template_args)
                        self.update_prompt_template(temp_template)
                        
                        # Log para debugging
                        logger.debug(f"Usando plantilla temporal con campos: {filtered_components.keys()}")
                    
                    # Generar contenido
                    response_text = await self._call_llm(**kwargs)
                    
                    # Restaurar plantilla original
                    self.update_prompt_template(original_template)
                except Exception as e:
                    # Asegurar que se restaure la plantilla original incluso si hay error
                    self.update_prompt_template(original_template)
                    logger.error(f"Error al usar system_components: {str(e)}")
                    raise e
            else:
                # Generar contenido con la plantilla actual
                response_text = await self._call_llm(**kwargs)
            
            # Formatear para legibilidad
            response_text = format_content_for_readability(response_text)
            
            # Procesar la respuesta
            parsed_response = self._parse_blog_response(response_text)
            
            # Crear respuesta estructurada
            return BlogArticleResponse(
                content=parsed_response["content"],
                titulo=parsed_response["titulo"],
                meta_descripcion=parsed_response.get("meta_descripcion"),
                palabras_clave=parsed_response.get("palabras_clave", []),
                metadata={
                    "article_type": "general_interest",
                    "topic": request.tema,
                    "target_audience": request.publico_objetivo,
                    "primary_keywords": request.palabras_clave_primarias,
                    "secondary_keywords": request.palabras_clave_secundarias
                }
            )
        
        except Exception as e:
            logger.error(f"Error al generar artículo de interés general: {str(e)}")
            raise


class SuccessCaseBlogAgent(BlogAgent):
    """Agente para generar artículos de casos de éxito."""
    
    def __init__(
        self,
        prompt_template: Optional[SuccessCasePromptTemplate] = None,
        model: str = settings.OPENAI_MODEL,
        temperature: float = settings.DEFAULT_TEMPERATURE
    ):
        """
        Inicializa el agente para casos de éxito.
        
        Args:
            prompt_template: Plantilla de prompts para casos de éxito
            model: Modelo de lenguaje a utilizar
            temperature: Temperatura para la generación
        """
        template = prompt_template or SuccessCasePromptTemplate()
        super().__init__(template, model, temperature)
        logger.info(f"Agente de blog para casos de éxito inicializado con modelo {model}")
    
    async def generate_content(self, request: SuccessCaseRequest, pdf_content: Optional[bytes] = None) -> SuccessCaseResponse:
        """
        Genera un artículo de caso de éxito.
        
        Args:
            request: Solicitud de generación
            pdf_content: Contenido del PDF con detalles del caso (opcional)
            
        Returns:
            SuccessCaseResponse: Artículo de caso de éxito generado
        """
        try:
            # Actualizar configuración del modelo si se especifica
            if request.model or request.temperature is not None:
                self.update_model_settings(
                    model=request.model or self.model,
                    temperature=request.temperature if request.temperature is not None else self.temperature
                )
            
            # Extraer información del PDF si se proporcionó
            caso_exito_info = ""
            if pdf_content:
                try:
                    pdf_text = extract_text_from_pdf(pdf_content)
                    caso_exito_info = pdf_text
                except Exception as e:
                    logger.error(f"Error al procesar PDF: {str(e)}")
                    caso_exito_info = "No se pudo extraer información del PDF proporcionado."
            
            # Preparar kwargs para el prompt
            kwargs = {
                "tema": request.tema,
                "publico_objetivo": request.publico_objetivo,
                "objetivo": request.objetivo,
                "tono_especifico": request.tono_especifico,
                "llamada_accion": request.llamada_accion,
                "elementos_evitar": ", ".join(request.elementos_evitar),
                "comentarios_adicionales": request.comentarios_adicionales or "",
                "informacion_caso_exito": caso_exito_info
            }
            
            # Manejar system_components si se proporcionaron
            if request.system_components:
                original_template = self.prompt_template
                try:
                    # Verificar qué campos de system_components son válidos para el constructor
                    valid_fields = {
                        'role_description', 'content_objective', 'style_guidance', 
                        'structure_description', 'tone', 'format_guide', 
                        'seo_guidelines', 'limitations', 'additional_instructions'
                    }
                    
                    # Filtrar solo los campos válidos
                    filtered_components = {
                        k: v for k, v in request.system_components.items() 
                        if k in valid_fields and v is not None
                    }
                    
                    # Si hay campos válidos, crear una nueva plantilla
                    if filtered_components:
                        # Crear una nueva plantilla con los campos proporcionados
                        # y mantener los valores originales para los campos no proporcionados
                        template_args = {
                            'role_description': original_template.role_description,
                            'content_objective': original_template.content_objective,
                            'style_guidance': original_template.style_guidance,
                            'structure_description': original_template.structure_description,
                            'tone': original_template.tone if hasattr(original_template, 'tone') else "",
                            'format_guide': original_template.format_guide if hasattr(original_template, 'format_guide') else "",
                            'seo_guidelines': original_template.seo_guidelines if hasattr(original_template, 'seo_guidelines') else "",
                            'limitations': original_template.limitations if hasattr(original_template, 'limitations') else "",
                            'additional_instructions': original_template.additional_instructions
                        }
                        
                        # Actualizar con los campos proporcionados
                        template_args.update(filtered_components)
                        
                        # Crear la plantilla temporal
                        temp_template = type(original_template)(**template_args)
                        self.update_prompt_template(temp_template)
                        
                        # Log para debugging
                        logger.debug(f"Usando plantilla temporal con campos: {filtered_components.keys()}")
                    
                    # Generar contenido
                    response_text = await self._call_llm(**kwargs)
                    
                    # Restaurar plantilla original
                    self.update_prompt_template(original_template)
                except Exception as e:
                    # Asegurar que se restaure la plantilla original incluso si hay error
                    self.update_prompt_template(original_template)
                    logger.error(f"Error al usar system_components: {str(e)}")
                    raise e
            else:
                # Generar contenido con la plantilla actual
                response_text = await self._call_llm(**kwargs)
            
            # Formatear para legibilidad
            response_text = format_content_for_readability(response_text)
            
            # Procesar la respuesta
            parsed_response = self._parse_success_case_response(response_text)
            
            # Crear respuesta estructurada
            return SuccessCaseResponse(
                content=parsed_response["contenido_completo"],
                titulo=parsed_response["titulo"],
                resumen_corto=parsed_response["resumen_corto"],
                contenido_completo=parsed_response["contenido_completo"],
                meta_descripcion=parsed_response.get("meta_descripcion"),
                palabras_clave=parsed_response.get("palabras_clave", []),
                metadata={
                    "article_type": "success_case",
                    "topic": request.tema,
                    "target_audience": request.publico_objetivo,
                    "with_pdf": pdf_content is not None
                }
            )
        
        except Exception as e:
            logger.error(f"Error al generar artículo de caso de éxito: {str(e)}")
            raise