import requests
from typing import List, Dict, Any, Optional
import json
from io import BytesIO
import re
from pathlib import Path
import tempfile
import os

from PyPDF2 import PdfReader
from core.logger import get_logger
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = get_logger("helpers")


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extrae texto de un archivo PDF.
    
    Args:
        pdf_bytes: Bytes del archivo PDF
        
    Returns:
        str: Texto extraído del PDF
    """
    try:
        pdf_file = BytesIO(pdf_bytes)
        pdf_reader = PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        logger.info(f"Texto extraído de PDF con {len(pdf_reader.pages)} páginas")
        return text
    except Exception as e:
        logger.error(f"Error al guardar archivo temporal: {str(e)}")
        raise


def clean_temp_file(file_path: str) -> None:
    """
    Elimina un archivo temporal.
    
    Args:
        file_path: Ruta al archivo a eliminar
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Archivo temporal eliminado: {file_path}")
    except Exception as e:
        logger.error(f"Error al eliminar archivo temporal: {str(e)}")


def format_content_for_readability(content: str) -> str:
    """
    Formatea el contenido para mejorar su legibilidad.
    
    Args:
        content: Contenido a formatear
        
    Returns:
        str: Contenido formateado
    """
    # Asegurar espacios después de puntos y comas
    content = re.sub(r'\.(?=[A-Z])', '. ', content)
    content = re.sub(r'\,(?=[A-Z])', ', ', content)
    
    # Eliminar espacios múltiples
    content = re.sub(r'\s+', ' ', content)
    
    # Asegurar que los párrafos estén bien separados
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content.strip()


def save_temp_file(content: bytes, extension: str = ".pdf") -> str:
    """
    Guarda contenido en un archivo temporal.
    
    Args:
        content: Contenido a guardar
        extension: Extensión del archivo
        
    Returns:
        str: Ruta al archivo temporal
    """
    try:
        temp_dir = tempfile.gettempdir()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=extension, dir=temp_dir)
        
        with open(temp_file.name, "wb") as f:
            f.write(content)
        
        logger.info(f"Archivo temporal guardado en: {temp_file.name}")
        return temp_file.name
    except Exception as e:
        logger.error(f"Error al extraer texto del PDF: {str(e)}")
        raise


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Divide un texto largo en chunks más pequeños.
    
    Args:
        text: Texto a dividir
        chunk_size: Tamaño máximo de cada chunk
        chunk_overlap: Superposición entre chunks
        
    Returns:
        List[str]: Lista de chunks de texto
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    
    chunks = text_splitter.create_documents([text])
    return [chunk.page_content for chunk in chunks]


def extract_content_from_url(url: str) -> str:
    """
    Extrae el contenido de una URL.
    
    Args:
        url: URL de la que extraer el contenido
        
    Returns:
        str: Contenido extraído
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Aquí se podría implementar un parser HTML más sofisticado
        # Por ahora simplificamos a texto plano
        content = response.text
        
        # Eliminar tags HTML básicos
        content = re.sub(r'<[^>]+>', ' ', content)
        # Eliminar espacios múltiples
        content = re.sub(r'\s+', ' ', content).strip()
        
        logger.info(f"Contenido extraído de URL: {url}")
        return content
    except Exception as e:
        logger.error(f"Error al extraer contenido de URL: {str(e)}")
        raise


def extract_hashtags(text: str) -> List[str]:
    """
    Extrae hashtags de un texto.
    
    Args:
        text: Texto del que extraer hashtags
        
    Returns:
        List[str]: Lista de hashtags extraídos
    """
    hashtags = re.findall(r'#(\w+)', text)
    return hashtags