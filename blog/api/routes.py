from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body, status, Form
from typing import Dict, Any, Optional
from pydantic import ValidationError
import json

from blog.models.blog_models import (
    GeneralInterestRequest, 
    SuccessCaseRequest, 
    BlogArticleResponse,
    SuccessCaseResponse,
    BlogPromptCustomizationRequest,
    BlogArticleType
)
from blog.services.blog_service import BlogService
from core.logger import get_logger

logger = get_logger("blog_api")

router = APIRouter(prefix="/blog", tags=["Blog"])


async def get_blog_service() -> BlogService:
    """
    Dependencia para obtener el servicio de blog.
    
    Returns:
        BlogService: Instancia del servicio
    """
    return BlogService()


@router.get("/config", response_model=Dict[str, Any])
async def get_prompt_configurations(
    service: BlogService = Depends(get_blog_service)
):
    """
    Obtiene las configuraciones actuales de los prompts para blog.
    """
    try:
        return await service.get_prompt_configurations()
    except Exception as e:
        logger.error(f"Error al obtener configuraciones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener configuraciones: {str(e)}"
        )


@router.post("/config/general-interest", response_model=Dict[str, Any])
async def customize_general_interest_prompt(
    request: BlogPromptCustomizationRequest,
    service: BlogService = Depends(get_blog_service)
):
    """
    Personaliza el prompt para artículos de interés general.
    """
    try:
        result = await service.customize_general_interest_prompt(request)
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al personalizar prompt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al personalizar prompt: {str(e)}"
        )


@router.post("/config/success-case", response_model=Dict[str, Any])
async def customize_success_case_prompt(
    request: BlogPromptCustomizationRequest,
    service: BlogService = Depends(get_blog_service)
):
    """
    Personaliza el prompt para artículos de casos de éxito.
    """
    try:
        result = await service.customize_success_case_prompt(request)
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al personalizar prompt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al personalizar prompt: {str(e)}"
        )


@router.post("/generate/general-interest", response_model=BlogArticleResponse)
async def generate_general_interest_article(
    request: GeneralInterestRequest,
    service: BlogService = Depends(get_blog_service)
):
    """
    Genera un artículo de blog de interés general.
    """
    try:
        return await service.generate_general_interest_article(request)
    except Exception as e:
        logger.error(f"Error al generar artículo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar artículo: {str(e)}"
        )


@router.post("/generate/success-case", response_model=SuccessCaseResponse)
async def generate_success_case_article(
    request: str = Form(...),
    pdf_file: Optional[UploadFile] = File(None),
    service: BlogService = Depends(get_blog_service)
):
    """
    Genera un artículo de blog de caso de éxito.
    """
    try:

        # Convertir string JSON a diccionario
        request_data = json.loads(request)
        # Crear objeto SuccessCaseRequest a partir del diccionario
        validated_request = SuccessCaseRequest(**request_data)


        pdf_content = None
        if pdf_file:
            pdf_content = await pdf_file.read()
            
        # Generar el artículo utilizando el servicio
        return await service.generate_success_case_article(validated_request, pdf_content)
    except json.JSONDecodeError as e:
        logger.error(f"Error al decodificar JSON: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"JSON inválido en el campo 'request': {str(e)}"
        )
    except ValidationError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Datos inválidos: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error al generar artículo de caso de éxito: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar artículo: {str(e)}"
        )


@router.post("/generate", response_model=Dict[str, Any])
async def generate_blog_article(
    article_type: BlogArticleType,
    request: Dict[str, Any] = Body(...),
    pdf_file: Optional[UploadFile] = File(None),
    service: BlogService = Depends(get_blog_service)
):
    """
    Genera un artículo de blog según el tipo especificado.
    """
    try:
        # Determinar tipo de artículo y validar solicitud
        if article_type.type == "general_interest":
            validated_request = GeneralInterestRequest(**request)
            response = await service.generate_general_interest_article(validated_request)
        elif article_type.type == "success_case":
            validated_request = SuccessCaseRequest(**request)
            pdf_content = None
            if pdf_file:
                pdf_content = await pdf_file.read()
            response = await service.generate_success_case_article(validated_request, pdf_content)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de artículo no válido: {article_type.type}"
            )
        
        # Convertir respuesta a diccionario para respuesta genérica
        return {
            "article_type": article_type.type,
            "content": response.model_dump()
        }
    except Exception as e:
        logger.error(f"Error al generar artículo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar artículo: {str(e)}"
        )