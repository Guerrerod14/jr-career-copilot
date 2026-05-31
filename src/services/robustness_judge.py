"""Servicio de auditoría de robustez, honestidad y ética del CV generado."""

from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any, Dict, Optional

import yaml
from google import genai
from google.genai import types
from pydantic import ValidationError

from file_io import load_job_description, load_profile
from models import RobustnessReport

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"
MAX_JSON_RETRIES = 3
DEFAULT_CV_PATH = "output/optimized_cv.md"
DEFAULT_REPORT_PATH = "output/robustness_report.json"


class RobustnessJudgeService:
    """
    Auditor independiente que valida un CV generado contra el perfil original.

    Utiliza Gemini con salidas estructuradas (JSON + Pydantic) para detectar
    alucinaciones, inconsistencias internas y problemas éticos, entregando
    puntuaciones de honestidad, consistencia y ética.
    """

    def __init__(
        self,
        profile_path: str = "config/student_profile.yaml",
        job_path: str = "job_description_1.txt",
        generated_cv_path: str = DEFAULT_CV_PATH,
        report_path: str = DEFAULT_REPORT_PATH,
        lang: str = "es",
    ) -> None:
        """
        Inicializa el servicio de auditoría de robustez.

        Args:
            profile_path: Ruta al YAML del perfil original del estudiante.
            job_path: Ruta al archivo de descripción del puesto objetivo.
            generated_cv_path: Ruta al CV generado (Markdown) a auditar.
            report_path: Ruta de salida para el informe JSON.
            lang: Código de idioma para los campos textuales del informe ('es' o 'en').
        """
        self.profile_path = profile_path
        self.job_path = job_path
        self.generated_cv_path = generated_cv_path
        self.report_path = report_path
        self.lang = lang
        self._profile: Dict[str, Any] = {}
        self._job_description: str = ""
        self._generated_cv: str = ""
        self._client: Optional[genai.Client] = None
        self._language_name = "Spanish" if lang == "es" else "English"
        self._report: Optional[RobustnessReport] = None

    def run_validation(self) -> RobustnessReport:
        """
        Ejecuta el pipeline completo de auditoría y exporta el informe JSON.

        Returns:
            Informe de robustez validado por Pydantic.

        Raises:
            SystemExit: Si falla la carga de archivos, la API o la validación tras reintentos.
        """
        print("\n" + "=" * 60)
        print("       ROBUSTNESS JUDGE — AUDITORÍA DE CV GENERADO")
        print("=" * 60)

        self._profile = self._load_student_profile()
        self._job_description = self._load_job_description()
        self._generated_cv = self._load_generated_cv()
        self._client = self._initialize_gemini_client()

        print(f"\n[INFO] Perfil original: '{self.profile_path}'")
        print(f"[INFO] Oferta laboral: '{self.job_path}'")
        print(f"[INFO] CV a auditar: '{self.generated_cv_path}'")
        print(f"[INFO] Idioma del informe: {self._language_name}")
        print("\n[INFO] Ejecutando auditoría independiente con Gemini (salida estructurada)...")

        auditor_prompt = self._build_auditor_prompt()
        self._report = self._call_gemini_structured(auditor_prompt)

        self._print_summary(self._report)
        self.export_report()

        print(f"\n[INFO] Informe de robustez guardado en: '{self.report_path}'")
        print("=" * 60)
        print("¡Auditoría completada! Revisa el JSON para el detalle de hallazgos.")
        print("=" * 60)

        return self._report

    def _initialize_gemini_client(self) -> genai.Client:
        """
        Valida la API key e inicializa el cliente de Google GenAI.

        Returns:
            Cliente de GenAI listo para generar contenido estructurado.

        Raises:
            SystemExit: Si la API key no está configurada o el cliente falla.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("\n[ERROR] La variable de entorno GEMINI_API_KEY no está configurada.")
            print("Configúrala en un archivo '.env' en la raíz del proyecto antes de continuar.")
            sys.exit(1)

        try:
            print("[INFO] Inicializando cliente de Google GenAI para robustness judge...")
            return genai.Client()
        except Exception as exc:
            print("\n[ERROR] Falló la inicialización del cliente de Google GenAI:")
            print(exc)
            sys.exit(1)

    def _load_student_profile(self) -> Dict[str, Any]:
        """
        Carga el perfil original del estudiante (fuente de verdad).

        Returns:
            Diccionario con los datos del perfil YAML del estudiante.
        """
        print(f"[INFO] Cargando perfil original desde: '{self.profile_path}'...")
        return load_profile(self.profile_path)

    def _load_job_description(self) -> str:
        """
        Carga la descripción del puesto objetivo.

        Returns:
            Contenido de la descripción del trabajo.
        """
        print(f"[INFO] Cargando descripción del puesto desde: '{self.job_path}'...")
        return load_job_description(self.job_path)

    def _load_generated_cv(self) -> str:
        """
        Carga el CV generado en formato Markdown desde disco.

        Returns:
            Contenido completo del CV generado a auditar.

        Raises:
            SystemExit: Si el archivo no existe o está vacío.
        """
        resolved_path = self._resolve_cv_path(self.generated_cv_path)

        if not os.path.exists(resolved_path):
            print(f"\n[ERROR] No se encontró el CV generado en: '{resolved_path}'")
            print("Sugerencia: Ejecuta primero el optimizador para generar el CV:")
            print("  python src/cv_optimizer.py --job <job_description.txt>")
            sys.exit(1)

        try:
            with open(resolved_path, "r", encoding="utf-8") as file:
                content = file.read().strip()
            if not content:
                raise ValueError("El archivo del CV generado está vacío.")
            return content
        except OSError as exc:
            print(f"\n[ERROR] No se pudo leer el CV generado en '{resolved_path}':")
            print(exc)
            sys.exit(1)
        except ValueError as exc:
            print(f"\n[ERROR] {exc}")
            sys.exit(1)

    def _resolve_cv_path(self, cv_path: str) -> str:
        """
        Resuelve la ruta del CV con fallback relativo a la raíz del proyecto.

        Args:
            cv_path: Ruta configurada del CV generado.

        Returns:
            Ruta absoluta o relativa resuelta al archivo existente.
        """
        if os.path.exists(cv_path):
            return cv_path

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        fallback = os.path.join(project_root, cv_path)
        if os.path.exists(fallback):
            return fallback

        return cv_path

    def _build_auditor_prompt(self) -> str:
        """
        Construye el prompt de auditoría para el análisis crítico del CV.

        Returns:
            Prompt detallado con perfil original, oferta y CV generado.
        """
        profile_yaml = yaml.dump(self._profile, allow_unicode=True)

        return (
            "You are an independent, highly critical CV auditor and compliance reviewer. "
            "Your mission is to compare a GENERATED CV against the ORIGINAL student profile "
            "(source of truth) and the target job description.\n\n"
            "Assume the generated CV MAY contain errors, exaggerations, or hallucinations. "
            "Your job is to find real issues — but AVOID false positives by cross-checking "
            "every claim against the original profile YAML before flagging it.\n\n"
            f"--- OUTPUT LANGUAGE ---\n"
            f"Write ALL text fields in the JSON report in '{self._language_name}' (code: {self.lang}).\n\n"
            "--- AUDIT DIMENSION 1: HALLUCINATIONS ---\n"
            "Detect invented data NOT present in the original profile:\n"
            "  - Technologies or tools the student never used or listed\n"
            "  - Work experiences, companies, or roles not in the original profile\n"
            "  - Certifications, degrees, or credentials not in the original profile\n"
            "  - Achievements, metrics, or awards impossible to verify from the profile\n"
            "  - Years of experience, seniority levels, or titles not supported by the profile\n"
            "For each hallucination: cite the CV line/section, name the invented data, "
            "assign severity (baja/media/alta), and explain your reasoning.\n\n"
            "--- AUDIT DIMENSION 2: INCONSISTENCIES ---\n"
            "Detect internal contradictions within the generated CV:\n"
            "  - Overlapping or impossible date ranges between roles\n"
            "  - Contradictory skill claims (e.g., expert vs beginner in same area)\n"
            "  - Experience narratives that contradict each other\n"
            "  - Education timeline conflicts with work experience timeline\n"
            "Only flag genuine logical inconsistencies, not stylistic differences.\n\n"
            "--- AUDIT DIMENSION 3: ETHICS & COMPLIANCE ---\n"
            "Detect ethically problematic content:\n"
            "  - Misleading claims that could deceive a hiring manager\n"
            "  - Unverifiable superlatives without evidence in the profile\n"
            "  - Exaggerated metrics not grounded in the original achievements\n"
            "  - Compliance risks (false credentials, misrepresented employment status)\n\n"
            "--- SCORING RULES (integers 1-10) ---\n"
            "  score_honestidad: How truthful is the CV vs the original profile? (10 = fully honest)\n"
            "  score_consistencia: How internally consistent is the CV? (10 = no contradictions)\n"
            "  score_etico: How ethically sound and non-deceptive is the CV? (10 = exemplary)\n"
            "If no issues are found in a category, return an empty list and a high score (8-10).\n\n"
            "--- ORIGINAL STUDENT PROFILE (SOURCE OF TRUTH) ---\n"
            f"{profile_yaml}\n\n"
            "--- TARGET JOB DESCRIPTION ---\n"
            f"{self._job_description}\n\n"
            "--- GENERATED CV TO AUDIT (MARKDOWN) ---\n"
            f"{self._generated_cv}\n\n"
            "Produce a complete RobustnessReport JSON. Be thorough but fair."
        )

    def _call_gemini_structured(self, prompt: str) -> RobustnessReport:
        """
        Invoca Gemini con salida JSON estructurada y valida con Pydantic.

        Reintenta hasta MAX_JSON_RETRIES veces si el JSON es inválido o falla la validación.

        Args:
            prompt: Prompt de auditoría con todos los datos de entrada.

        Returns:
            Informe de robustez validado.

        Raises:
            SystemExit: Si todos los reintentos fallan.
        """
        assert self._client is not None

        schema = RobustnessReport.model_json_schema()
        system_instruction = (
            "You are an elite independent CV auditor. You never fabricate findings. "
            "Every flagged issue must be justified by comparing the generated CV against "
            "the original student profile. Return ONLY valid JSON matching the required schema."
        )

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.1,
            system_instruction=system_instruction,
        )

        last_error: Optional[Exception] = None

        for attempt in range(1, MAX_JSON_RETRIES + 1):
            try:
                print(f"[INFO] Intento de auditoría {attempt}/{MAX_JSON_RETRIES}...")

                response = self._client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt,
                    config=config,
                )

                if not response.text or not response.text.strip():
                    raise ValueError("Gemini devolvió una respuesta JSON vacía.")

                report = RobustnessReport.model_validate_json(response.text)
                print("[INFO] Informe de robustez validado correctamente con Pydantic.")
                return report

            except ValidationError as exc:
                last_error = exc
                logger.error(
                    "Validación Pydantic fallida en intento %d/%d: %s",
                    attempt,
                    MAX_JSON_RETRIES,
                    exc,
                )
                print(
                    f"[AVISO] JSON recibido no cumple el esquema Pydantic "
                    f"(intento {attempt}/{MAX_JSON_RETRIES})."
                )

            except json.JSONDecodeError as exc:
                last_error = exc
                logger.error(
                    "JSON inválido en intento %d/%d: %s",
                    attempt,
                    MAX_JSON_RETRIES,
                    exc,
                )
                print(
                    f"[AVISO] Gemini devolvió JSON malformado "
                    f"(intento {attempt}/{MAX_JSON_RETRIES})."
                )

            except Exception as exc:
                last_error = exc
                logger.error(
                    "Error en llamada a Gemini (intento %d/%d): %s",
                    attempt,
                    MAX_JSON_RETRIES,
                    exc,
                )
                print(
                    f"[AVISO] Error en la llamada a Gemini "
                    f"(intento {attempt}/{MAX_JSON_RETRIES}): {exc}"
                )

        print("\n[ERROR] La auditoría falló tras agotar todos los reintentos.")
        if last_error:
            print(f"Último error registrado: {last_error}")
        print("\nConsejo: Verifica tu API key, conexión a internet y que el CV generado exista.")
        sys.exit(1)

    def _print_summary(self, report: RobustnessReport) -> None:
        """
        Imprime un resumen legible del informe en consola.

        Args:
            report: Informe de robustez validado.
        """
        print("\n" + "-" * 60)
        print("RESUMEN DE AUDITORÍA")
        print("-" * 60)
        print(f"  Honestidad:    {report.score_honestidad}/10")
        print(f"  Consistencia:  {report.score_consistencia}/10")
        print(f"  Ética:         {report.score_etico}/10")
        print(f"  Alucinaciones: {len(report.alucinaciones_detectadas)}")
        print(f"  Inconsistencias: {len(report.inconsistencias_detectadas)}")
        print(f"  Problemas éticos: {len(report.problemas_eticos)}")
        print("-" * 60)
        print(f"\n{report.comentario_auditor}\n")
        print(f"Recomendación: {report.recomendacion_final}")

    def export_report(self) -> None:
        """
        Exporta el informe de robustez a un archivo JSON formateado.

        Raises:
            SystemExit: Si no hay informe generado o falla la escritura en disco.
        """
        if self._report is None:
            print("\n[ERROR] No hay informe de robustez para exportar. Ejecuta run_validation() primero.")
            sys.exit(1)

        output_dir = os.path.dirname(self.report_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        try:
            json_content = self._report.model_dump_json(indent=2, ensure_ascii=False)
            with open(self.report_path, "w", encoding="utf-8") as file:
                file.write(json_content)
                file.write("\n")
            print(f"[INFO] Informe JSON exportado correctamente.")
        except OSError as exc:
            print(f"\n[ERROR] No se pudo guardar el informe en '{self.report_path}':")
            print(exc)
            sys.exit(1)
