from typing import Dict, Any, Optional
from common.prompt_templates.base_templates import ContentPromptTemplate
from core.config import settings


class BlogPromptTemplate(ContentPromptTemplate):
    """Plantilla de prompts para generación de artículos de blog."""
    
    def get_human_template(self) -> str:
        """Proporciona plantilla específica para blog."""
        return """Tema: {tema}
Palabras clave principales: {palabras_clave_primarias}
Palabras clave secundarias: {palabras_clave_secundarias}
Longitud: {longitud}
Público objetivo: {publico_objetivo}
Objetivo: {objetivo}
Tono específico: {tono_especifico}
Llamada a la acción: {llamada_accion}
Elementos a evitar: {elementos_evitar}

{comentarios_adicionales}
"""


class GeneralInterestPromptTemplate(BlogPromptTemplate):
    """Plantilla para artículos de interés general."""
    
    def __init__(
        self,
        role_description: str = "especialista en creación de contenidos para blogs, con experiencia en SEO y narración digital",
        content_objective: str = "generar artículos completos, informativos y atractivos",
        style_guidance: str = "Mantén un equilibrio entre profesional e informal según la temática. Usa una voz conversacional que genere conexión con el lector.",
        structure_description: str = "- Crea títulos atractivos que generen curiosidad y contengan palabras clave.\n- Incluye una introducción cautivadora que establezca el problema o tema.\n- Desarrolla secciones con subtítulos descriptivos y H2/H3 adecuados para SEO.\n- Incluye conclusiones que resuman los puntos clave y llamen a la acción.\n- Añade preguntas frecuentes cuando sea apropiado.",
        tone: str = "Mantén un equilibrio entre profesional e informal según la temática. Usa una voz conversacional que genere conexión con el lector.",
        format_guide: str = "- Utiliza párrafos cortos (3-4 líneas máximo) para mejorar la legibilidad.\n- Incorpora listas, viñetas y negritas para destacar información importante.\n- Incluye ejemplos prácticos y casos de estudio relevantes.\n- Sugiere imágenes o elementos visuales en puntos estratégicos.",
        limitations: str = "- No generes contenido falso o sin verificar.\n- No plagies contenido existente.\n- Evita jerga excesivamente técnica a menos que el público objetivo lo requiera.\n- Prioriza la calidad sobre la cantidad.",
        seo_guidelines: str = "- Distribuye naturalmente palabras clave primarias y secundarias.\n- Genera metadescripciones atractivas de 150-160 caracteres.\n- Sugiere enlaces internos y externos relevantes.",
        additional_instructions: Optional[str] = None
    ):
        """Inicializa la plantilla con valores por defecto para artículos de interés general."""
        super().__init__(
            role_description=role_description,
            content_objective=content_objective,
            style_guidance=style_guidance,
            structure_description=structure_description,
            tone=tone,
            format_guide=format_guide,
            limitations=limitations,
            seo_guidelines=seo_guidelines,
            additional_instructions=additional_instructions
        )
    
    def get_human_template(self) -> str:
        """Proporciona plantilla específica para artículos de interés general."""
        template = super().get_human_template()
        
        # Añadir información sobre URLs de referencia
        template += "\nURLs de referencia para investigación adicional: {urls_referencia}\n"
        
        return template


class SuccessCasePromptTemplate(BlogPromptTemplate):
    """Plantilla para artículos de casos de éxito."""
    
    def __init__(
        self,
        role_description: str = "especialista en redacción de casos de éxito y storytelling empresarial",
        content_objective: str = "crear artículos persuasivos que destaquen logros y resultados positivos de proyectos reales",
        style_guidance: str = "Utiliza un estilo narrativo que muestre la transformación y los resultados obtenidos. Alterna datos duros con historias.",
        structure_description: str = "- Crea un título impactante que mencione el resultado principal o la empresa.\n- Comienza con un resumen ejecutivo de los logros.\n- Describe el desafío o problema inicial.\n- Explica la solución implementada.\n- Detalla los resultados con métricas específicas.\n- Incluye testimonios o citas (si están disponibles en el PDF).\n- Termina con lecciones aprendidas y una llamada a la acción.",
        tone: str = "Profesional pero inspirador, enfocado en resultados y valor aportado",
        format_guide: str = "- Utiliza párrafos cortos para mantener el interés.\n- Destaca cifras y porcentajes clave.\n- Incluye viñetas para listar beneficios.\n- Estructura clara con secciones bien definidas.\n- Sugiere dónde podrían incluirse imágenes de antes/después.",
        limitations: str = "- No inventes datos o resultados no mencionados en el documento fuente.\n- No menciones información confidencial.\n- Equilibra hechos con narrativa.\n- No exageres los resultados.",
        seo_guidelines: str = "- Incluye el nombre de la empresa/industria en el título y subtítulos.\n- Utiliza términos relacionados con resultados y soluciones.\n- Crea una meta descripción que resuma el logro principal.",
        additional_instructions: str = "Genera DOS versiones del contenido: una versión corta (resumen ejecutivo de 150-200 palabras) y una versión completa detallada (800-1500 palabras). La versión corta debe capturar la esencia y los resultados principales."
    ):
        """Inicializa la plantilla con valores por defecto para casos de éxito."""
        super().__init__(
            role_description=role_description,
            content_objective=content_objective,
            style_guidance=style_guidance,
            structure_description=structure_description,
            tone=tone,
            format_guide=format_guide,
            limitations=limitations,
            seo_guidelines=seo_guidelines,
            additional_instructions=additional_instructions
        )
    
    def get_human_template(self) -> str:
        """Proporciona plantilla específica para casos de éxito."""
        template = super().get_human_template()
        
        # Añadir instrucción para uso del PDF
        template += """
A continuación se proporciona información extraída de un PDF con detalles del caso de éxito.
Usa esta información como fuente principal para generar el artículo:

Información del caso de éxito:
{informacion_caso_exito}

Recuerda: Genera tanto una versión resumida como una versión completa del caso de éxito.
"""
        
        return template


def create_default_blog_prompt_templates() -> Dict[str, BlogPromptTemplate]:
    """
    Crea y devuelve las plantillas por defecto para blog.
    
    Returns:
        Dict[str, BlogPromptTemplate]: Diccionario con las plantillas
    """
    return {
        "general_interest": GeneralInterestPromptTemplate(),
        "success_case": SuccessCasePromptTemplate()
    }