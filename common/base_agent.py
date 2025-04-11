from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import json

from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from common.prompt_templates.base_templates import BasePromptTemplate
from core.logger import get_logger
from core.config import settings

logger = get_logger("base_agent")


class BaseAgent(ABC):
    """Clase base para todos los agentes de generación de contenido."""
    
    def __init__(
        self,
        prompt_template: BasePromptTemplate,
        model: str = settings.OPENAI_MODEL,
        temperature: float = settings.DEFAULT_TEMPERATURE
    ):
        """
        Inicializa el agente con una plantilla de prompts y configuración del modelo.
        
        Args:
            prompt_template: Plantilla de prompts a utilizar
            model: Modelo de lenguaje a utilizar
            temperature: Temperatura para la generación (creatividad)
        """
        self.prompt_template = prompt_template
        self.model = model
        self.temperature = temperature
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self) -> ChatOpenAI:
        """
        Inicializa el modelo de lenguaje.
        
        Returns:
            ChatOpenAI: Instancia del modelo configurado
        """
        logger.info(f"Inicializando LLM con modelo: {self.model}, temperatura: {self.temperature}")
        return ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            api_key=settings.OPENAI_API_KEY
        )
    
    def update_prompt_template(self, new_template: BasePromptTemplate) -> None:
        """
        Actualiza la plantilla de prompts del agente.
        
        Args:
            new_template: Nueva plantilla a utilizar
        """
        self.prompt_template = new_template
        logger.info("Plantilla de prompts actualizada")
    
    def update_model_settings(self, model: Optional[str] = None, temperature: Optional[float] = None) -> None:
        """
        Actualiza la configuración del modelo.
        
        Args:
            model: Nuevo modelo a utilizar (opcional)
            temperature: Nueva temperatura a utilizar (opcional)
        """
        if model:
            self.model = model
        
        if temperature is not None:
            self.temperature = temperature
            
        self.llm = self._initialize_llm()
        logger.info(f"Configuración del modelo actualizada - Modelo: {self.model}, Temperatura: {self.temperature}")
    
    def _get_messages(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Construye los mensajes para la llamada al modelo.
        
        Args:
            **kwargs: Variables para rellenar las plantillas
            
        Returns:
            List[Dict[str, Any]]: Lista de mensajes formateados
        """
        prompt_data = self.prompt_template.get_prompt_data()
        
        # Crear mensaje de sistema
        system_message = SystemMessage(content=prompt_data["system_message"])
        
        # Formatear plantilla de usuario con los kwargs
        human_content = prompt_data["human_template"].format(**kwargs)
        human_message = HumanMessage(content=human_content)
        
        return [system_message, human_message]
    
    @abstractmethod
    async def generate_content(self, **kwargs) -> Any:
        """
        Genera contenido basado en los parámetros proporcionados.
        
        Args:
            **kwargs: Parámetros para la generación
            
        Returns:
            Any: Contenido generado
        """
        pass
    
    async def _call_llm(self, **kwargs) -> str:
        """
        Realiza la llamada al modelo de lenguaje.
        
        Args:
            **kwargs: Variables para rellenar las plantillas
            
        Returns:
            str: Respuesta del modelo
        """
        try:
            messages = self._get_messages(**kwargs)
            logger.debug(f"Enviando mensajes al LLM: {json.dumps([m.dict() for m in messages], indent=2)}")
            
            response = await self.llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Error al llamar al LLM: {str(e)}")
            raise