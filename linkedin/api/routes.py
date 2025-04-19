from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional

from linkedin.models.linkedin_models import (
    LinkedInPostRequest,
    LinkedInPostResponse,
    LinkedInStyleConfigRequest
)
from linkedin.services.linkedin_service import LinkedInService
from core.logger import get_logger

logger = get_logger("linkedin_api")

router = APIRouter(prefix="/linkedin", tags=["LinkedIn"])

# Variable global para mantener una única instancia del servicio
_linkedin_service_instance = None

async def get_linkedin_service() -> LinkedInService:
    """
    Dependencia para obtener el servicio de LinkedIn.
    Usa un patrón singleton para mantener una única instancia.
    
    Returns:
        LinkedInService: Instancia del servicio
    """
    global _linkedin_service_instance
    if _linkedin_service_instance is None:
        _linkedin_service_instance = LinkedInService()
        logger.info("Se creó una nueva instancia del servicio de LinkedIn")
    return _linkedin_service_instance


@router.post("/generate", response_model=LinkedInPostResponse)
async def generate_linkedin_post(
    request: LinkedInPostRequest,
    service: LinkedInService = Depends(get_linkedin_service)
):
    """
    Genera un post de LinkedIn según los parámetros proporcionados.
    
    Args:
        request: Parámetros para la generación
        service: Servicio de LinkedIn
    
    Returns:
        LinkedInPostResponse: Post generado
    """
    try:
        return await service.generate_post(request)
    except Exception as e:
        logger.error(f"Error al generar post de LinkedIn: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar post: {str(e)}"
        )


@router.post("/styles/customize", response_model=Dict[str, Any])
async def customize_linkedin_style(
    request: LinkedInStyleConfigRequest,
    service: LinkedInService = Depends(get_linkedin_service)
):
    """
    Personaliza la configuración de un estilo de post de LinkedIn.
    
    Args:
        request: Configuración del estilo
        service: Servicio de LinkedIn
    
    Returns:
        Dict[str, Any]: Resultado de la operación
    """
    try:
        result = await service.customize_style(request)
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al personalizar estilo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al personalizar estilo: {str(e)}"
        )


@router.get("/styles", response_model=List[Dict[str, Any]])
async def get_linkedin_styles(
    service: LinkedInService = Depends(get_linkedin_service)
):
    """
    Obtiene los estilos disponibles para posts de LinkedIn.
    
    Args:
        service: Servicio de LinkedIn
    
    Returns:
        List[Dict[str, Any]]: Lista de estilos disponibles
    """
    try:
        return await service.get_available_styles()
    except Exception as e:
        logger.error(f"Error al obtener estilos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estilos: {str(e)}"
        )


@router.get("/authors", response_model=List[Dict[str, Any]])
async def get_linkedin_authors(
    service: LinkedInService = Depends(get_linkedin_service)
):
    """
    Obtiene los autores disponibles para posts de LinkedIn.
    
    Args:
        service: Servicio de LinkedIn
    
    Returns:
        List[Dict[str, Any]]: Lista de autores disponibles
    """
    try:
        return await service.get_available_authors()
    except Exception as e:
        logger.error(f"Error al obtener autores: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener autores: {str(e)}"
        )


@router.get("/authors/{author_id}", response_model=Dict[str, Any])
async def get_author_details(
    author_id: str,
    service: LinkedInService = Depends(get_linkedin_service)
):
    """
    Obtiene detalles de un autor específico.
    
    Args:
        author_id: ID del autor
        service: Servicio de LinkedIn
    
    Returns:
        Dict[str, Any]: Detalles del autor
    """
    try:
        author_details = await service.get_author_details(author_id)
        if not author_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Autor no encontrado: {author_id}"
            )
        return author_details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener detalles del autor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener detalles del autor: {str(e)}"
        )