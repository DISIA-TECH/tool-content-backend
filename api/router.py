from fastapi import APIRouter

from blog.api.routes import router as blog_router
# Importar otros routers a medida que se vayan implementando
# from linkedin.api.routes import router as linkedin_router

# Router principal de la API
api_router = APIRouter()

# Incluir routers de diferentes módulos
api_router.include_router(blog_router)
# api_router.include_router(linkedin_router)  # Se añadirá cuando esté implementado