from fastapi import Header, HTTPException, status
from typing import Optional

from core.config import settings
from core.logger import get_logger

logger = get_logger("api_dependencies")


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """
    Verifica la API key en las solicitudes (si está configurada).
    
    Args:
        x_api_key: API key proporcionada en el header X-API-Key
        
    Raises:
        HTTPException: Si la API key no es válida
    """
    # Esta es una implementación simple. En un entorno de producción,
    # se debería implementar una validación más robusta.
    
    # Si no hay API key configurada, omitir la verificación
    if not hasattr(settings, 'API_KEY') or not settings.API_KEY:
        return
    
    if not x_api_key:
        logger.warning("Solicitud sin API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key no proporcionada"
        )
    
    if x_api_key != settings.API_KEY:
        logger.warning(f"Solicitud con API key inválida: {x_api_key[:5]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida"
        )


async def get_current_user():
    """
    Placeholder para autenticación de usuario.
    En un entorno de producción, se implementaría la autenticación adecuada.
    """
    # En una implementación completa, esta función verificaría tokens JWT
    # o algún otro mecanismo de autenticación.
    return {"id": "demo_user", "role": "admin"}