from typing import List, Optional
from pydantic import BaseModel, Field

class ContactInfo(BaseModel):
    """
    Representa la información de contacto estructurada del ingeniero junior.
    """
    email: Optional[str] = Field(None, description="Email address of the junior engineer")
    phone: Optional[str] = Field(None, description="Phone number of the junior engineer")
    location: Optional[str] = Field(None, description="Physical location or city and country")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")

class OptimizedExperience(BaseModel):
    """
    Representa una experiencia profesional optimizada para la oferta laboral.
    """
    company: str = Field(description="Name of the company or organization")
    role: str = Field(description="Optimized role title aligned with the job description")
    period: str = Field(description="Employment or project period")
    tailored_achievements: List[str] = Field(
        description="Action-oriented, high-impact achievements tailored to the target job description. Focus on metrics, technologies, and results without inventing any facts."
    )

class OptimizedEducation(BaseModel):
    """
    Representa la formación académica u proyectos de estudio optimizados.
    """
    institution: str = Field(description="Name of the educational institution")
    degree: str = Field(description="Degree name or certification")
    period: str = Field(description="Period of study or completion date")
    achievements: List[str] = Field(
        description="Key academic achievements, coursework, or project descriptions aligned with the job requirements."
    )

class OptimizedCV(BaseModel):
    """
    Estructura completa del currículum optimizado y adaptado.
    """
    full_name: str = Field(description="Full name of the junior engineer")
    contact_info: ContactInfo = Field(description="Structured contact info of the junior engineer")
    professional_summary: str = Field(
        description="A powerful 3-4 sentence professional summary tailored to the target job using the Pygmalion Effect, highlighting technical capability and potential."
    )
    optimized_skills: List[str] = Field(
        description="List of core technical and professional skills filtered and sorted by relevance to the job description."
    )
    experiences: List[OptimizedExperience] = Field(
        description="List of professional experiences with achievements tailored using action verbs and technical keywords."
    )
    education: List[OptimizedEducation] = Field(
        description="List of education details and tailored academic projects."
    )


class Hallucination(BaseModel):
    """
    Representa una alucinación detectada en el CV generado respecto al perfil original.
    """
    linea_cv: str = Field(description="Fragmento o línea del CV donde aparece el dato cuestionable")
    dato_inventado: str = Field(description="Dato que no consta en el perfil original del estudiante")
    severidad: str = Field(description="Nivel de severidad: baja, media o alta")
    explicacion: str = Field(description="Justificación técnica del hallazgo para evitar falsos positivos")


class Inconsistency(BaseModel):
    """
    Representa una inconsistencia interna detectada en el CV generado.
    """
    descripcion: str = Field(description="Descripción clara de la inconsistencia encontrada")
    severidad: str = Field(description="Nivel de severidad: baja, media o alta")


class EthicalIssue(BaseModel):
    """
    Representa un problema ético o de compliance detectado en el CV.
    """
    descripcion: str = Field(description="Descripción del problema ético o de exageración")
    severidad: str = Field(description="Nivel de severidad: baja, media o alta")


class RobustnessReport(BaseModel):
    """
    Informe estructurado de auditoría de robustez, honestidad y ética del CV generado.
    """
    score_honestidad: int = Field(
        ge=1, le=10,
        description="Puntuación de honestidad del CV (1-10) respecto al perfil original"
    )
    score_consistencia: int = Field(
        ge=1, le=10,
        description="Puntuación de consistencia interna del CV (1-10)"
    )
    score_etico: int = Field(
        ge=1, le=10,
        description="Puntuación ética y de compliance del CV (1-10)"
    )
    alucinaciones_detectadas: List[Hallucination] = Field(
        default_factory=list,
        description="Lista de alucinaciones o datos inventados detectados"
    )
    inconsistencias_detectadas: List[Inconsistency] = Field(
        default_factory=list,
        description="Lista de inconsistencias internas detectadas"
    )
    problemas_eticos: List[EthicalIssue] = Field(
        default_factory=list,
        description="Lista de problemas éticos o de exageración detectados"
    )
    comentario_auditor: str = Field(
        description="Comentario general del auditor independiente sobre el CV analizado"
    )
    recomendacion_final: str = Field(
        description="Recomendación final accionable para el candidato o revisor humano"
    )
