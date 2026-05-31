"""Servicio de entrevista técnica simulada con Gemini para ingenieros junior."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import yaml
from google import genai
from google.genai import types

from file_io import load_job_description, load_profile

MAX_INTERVIEW_QUESTIONS = 7
GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_TRANSCRIPT_PATH = "output/interview_transcript.md"


@dataclass
class InterviewTurn:
    """Representa un turno de la entrevista (pregunta y respuesta del candidato)."""

    question_number: int
    question: str
    answer: str = ""


@dataclass
class InterviewSession:
    """Estado mutable de una sesión de entrevista simulada."""

    turns: List[InterviewTurn] = field(default_factory=list)
    feedback: str = ""
    messages: List[types.Content] = field(default_factory=list)


class MockInterviewService:
    """
    Orquesta una entrevista técnica interactiva simulada con memoria conversacional.

    El reclutador virtual (Gemini) formula hasta siete preguntas progresivas
    basadas exclusivamente en el stack del CV del estudiante y la oferta laboral,
    y al finalizar entrega feedback estructurado con puntuación general.
    """

    def __init__(
        self,
        profile_path: str = "config/student_profile.yaml",
        job_path: str = "job_description_1.txt",
        lang: str = "es",
        transcript_path: str = DEFAULT_TRANSCRIPT_PATH,
    ) -> None:
        """
        Inicializa el servicio de mock interview.

        Args:
            profile_path: Ruta al archivo YAML del perfil del estudiante.
            job_path: Ruta al archivo de texto con la descripción del puesto.
            lang: Código de idioma de la entrevista ('es' o 'en').
            transcript_path: Ruta de salida para la transcripción en Markdown.
        """
        self.profile_path = profile_path
        self.job_path = job_path
        self.lang = lang
        self.transcript_path = transcript_path
        self._profile: Dict[str, Any] = {}
        self._job_description: str = ""
        self._client: Optional[genai.Client] = None
        self._session = InterviewSession()
        self._language_name = "Spanish" if lang == "es" else "English"

    def run_interactive(self) -> None:
        """
        Ejecuta el flujo completo de entrevista simulada en consola.

        Genera preguntas progresivas, recoge respuestas del usuario,
        produce feedback final y exporta la transcripción a Markdown.
        """
        print("\n" + "=" * 60)
        print("       MOCK INTERVIEW — ENTREVISTA TÉCNICA SIMULADA")
        print("=" * 60)

        self._profile = self._load_student_profile()
        self._job_description = self._load_job_description()
        self._client = self._initialize_gemini_client()

        candidate_name = self._profile.get("personal_info", {}).get("full_name", "Candidato")
        print(f"\n[INFO] Candidato: {candidate_name}")
        print(f"[INFO] Oferta laboral cargada desde: '{self.job_path}'")
        print(f"[INFO] Idioma de la entrevista: {self._language_name}")
        print(
            "\n[INFO] Un reclutador técnico senior te hará hasta "
            f"{MAX_INTERVIEW_QUESTIONS} preguntas. Responde con honestidad y detalle técnico."
        )
        print("[INFO] Escribe 'salir' en cualquier momento para abortar la entrevista.\n")

        self._session.messages = []
        system_prompt = self._build_system_prompt()

        for question_index in range(1, MAX_INTERVIEW_QUESTIONS + 1):
            question_text = self._generate_question(
                question_index=question_index,
                system_prompt=system_prompt,
            )
            turn = InterviewTurn(question_number=question_index, question=question_text)
            self._session.turns.append(turn)

            print("-" * 60)
            print(f"\n[PREGUNTA {question_index}/{MAX_INTERVIEW_QUESTIONS}]")
            print(question_text)
            print()

            user_answer = self._read_user_answer()
            if user_answer is None:
                print("\n[INFO] Entrevista cancelada por el usuario.")
                sys.exit(0)

            turn.answer = user_answer
            self._append_turn_to_history(question_text, user_answer)

            if question_index < MAX_INTERVIEW_QUESTIONS:
                print(f"\n[INFO] Respuesta registrada. Preparando pregunta {question_index + 1}...\n")

        print("\n" + "=" * 60)
        print("[INFO] Entrevista finalizada. Generando feedback del reclutador...")
        print("=" * 60 + "\n")

        self._session.feedback = self._generate_feedback(system_prompt=system_prompt)
        print(self._session.feedback)

        self.export_transcript()
        print(f"\n[INFO] Transcripción guardada en: '{self.transcript_path}'")
        print("=" * 60)
        print("¡Mock interview completada! Revisa el feedback y la transcripción.")
        print("=" * 60)

    def _initialize_gemini_client(self) -> genai.Client:
        """
        Valida la API key e inicializa el cliente de Google GenAI.

        Returns:
            Cliente de GenAI listo para generar contenido.

        Raises:
            SystemExit: Si la API key no está configurada o el cliente falla.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("\n[ERROR] La variable de entorno GEMINI_API_KEY no está configurada.")
            print("Configúrala en un archivo '.env' en la raíz del proyecto antes de continuar.")
            sys.exit(1)

        try:
            print("[INFO] Inicializando cliente de Google GenAI para mock interview...")
            return genai.Client()
        except Exception as exc:
            print("\n[ERROR] Falló la inicialización del cliente de Google GenAI:")
            print(exc)
            sys.exit(1)

    def _load_student_profile(self) -> Dict[str, Any]:
        """
        Carga el perfil del estudiante desde el archivo YAML configurado.

        Returns:
            Diccionario con los datos del perfil del estudiante.
        """
        print(f"[INFO] Cargando perfil del estudiante desde: '{self.profile_path}'...")
        return load_profile(self.profile_path)

    def _load_job_description(self) -> str:
        """
        Carga la descripción del puesto desde el archivo de texto configurado.

        Returns:
            Contenido de la descripción del trabajo como cadena de texto.
        """
        print(f"[INFO] Cargando descripción del puesto desde: '{self.job_path}'...")
        return load_job_description(self.job_path)

    def _build_system_prompt(self) -> str:
        """
        Construye el system prompt que define el comportamiento del reclutador virtual.

        Returns:
            Instrucciones de sistema para Gemini como reclutador técnico senior.
        """
        skills_block = yaml.dump(
            self._profile.get("skills", []),
            allow_unicode=True,
            default_flow_style=False,
        )
        experiences_block = yaml.dump(
            self._profile.get("experiences", []),
            allow_unicode=True,
            default_flow_style=False,
        )

        return (
            "You are a senior technical recruiter conducting a rigorous but fair "
            "mock technical interview for a junior software engineer candidate.\n\n"
            "--- INTERVIEW LANGUAGE ---\n"
            f"Conduct the entire interview EXCLUSIVELY in '{self._language_name}' (code: {self.lang}).\n\n"
            "--- STRICT TECHNOLOGY SCOPE RULE ---\n"
            "You may ONLY ask questions about technologies, tools, frameworks, databases, "
            "methodologies, and concepts that appear EXPLICITLY in EITHER:\n"
            "  (a) The candidate's CV/profile (skills, experiences, education achievements), OR\n"
            "  (b) The target job description provided.\n"
            "NEVER ask about technologies, cloud providers, languages, or domains absent from both sources.\n"
            "If a technology is only in the job description but not in the CV, you may ask about "
            "the candidate's theoretical understanding or willingness to learn — but frame it as junior-level.\n\n"
            "--- INTERVIEW PROGRESSION RULES ---\n"
            "1. Ask exactly ONE question per turn. No multi-part compound questions.\n"
            "2. Progress from foundational concepts to deeper, scenario-based technical questions.\n"
            "3. Evaluate technical depth: syntax knowledge, architecture reasoning, debugging, trade-offs.\n"
            "4. Adapt follow-up difficulty based on the quality of previous answers in the conversation history.\n"
            "5. Maximum total questions in the session: "
            f"{MAX_INTERVIEW_QUESTIONS}. This is question {{question_num}} of {MAX_INTERVIEW_QUESTIONS}.\n"
            "6. Be professional, encouraging, and concise. Do not reveal interview answers.\n\n"
            "--- CANDIDATE CV (SOURCE OF TRUTH FOR THEIR STACK) ---\n"
            f"Skills:\n{skills_block}\n"
            f"Experiences:\n{experiences_block}\n"
            f"Full profile YAML:\n{yaml.dump(self._profile, allow_unicode=True)}\n\n"
            "--- TARGET JOB DESCRIPTION ---\n"
            f"{self._job_description}\n"
        )

    def _generate_question(self, question_index: int, system_prompt: str) -> str:
        """
        Genera la siguiente pregunta de entrevista usando el historial conversacional.

        Args:
            question_index: Número de pregunta actual (1-7).
            system_prompt: Instrucciones de sistema del reclutador.

        Returns:
            Texto de la pregunta formulada por Gemini.

        Raises:
            SystemExit: Si la llamada a Gemini falla o devuelve respuesta vacía.
        """
        formatted_system = system_prompt.replace("{question_num}", str(question_index))

        if question_index == 1:
            user_instruction = (
                "Start the mock interview now. Greet the candidate briefly (one sentence) "
                f"and ask your FIRST technical question (question 1 of {MAX_INTERVIEW_QUESTIONS}). "
                "Output ONLY the greeting and the question — no feedback yet."
            )
            contents: List[types.Content] = [
                types.Content(
                    role="user",
                    parts=[types.Part(text=user_instruction)],
                )
            ]
        else:
            user_instruction = (
                f"Based on the candidate's previous answers in this conversation, "
                f"ask your NEXT technical interview question (question {question_index} "
                f"of {MAX_INTERVIEW_QUESTIONS}). "
                "Increase depth appropriately. Output ONLY the question — no preamble, no feedback."
            )
            contents = list(self._session.messages)
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text=user_instruction)],
                )
            )

        return self._call_gemini(
            contents=contents,
            system_prompt=formatted_system,
            temperature=0.4,
            error_context=f"generar la pregunta {question_index}",
        )

    def _generate_feedback(self, system_prompt: str) -> str:
        """
        Genera el feedback final estructurado tras completar las siete preguntas.

        Args:
            system_prompt: Instrucciones de sistema del reclutador.

        Returns:
            Texto del feedback final con fortalezas, debilidades, tecnologías y score.
        """
        feedback_instruction = (
            "The mock interview is now COMPLETE. All questions have been answered.\n"
            "Provide your FINAL structured feedback in the following Markdown format:\n\n"
            "## Fortalezas\n"
            "- (bullet points)\n\n"
            "## Debilidades\n"
            "- (bullet points)\n\n"
            "## Tecnologías a reforzar\n"
            "- (bullet points — only technologies from the allowed stack)\n\n"
            "## Score general\n"
            "X/10 — (one paragraph justification)\n\n"
            "Be honest, constructive, and specific. Reference actual answers from the conversation. "
            f"Write everything in '{self._language_name}'."
        )

        contents = list(self._session.messages)
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part(text=feedback_instruction)],
            )
        )

        return self._call_gemini(
            contents=contents,
            system_prompt=system_prompt,
            temperature=0.3,
            error_context="generar el feedback final",
        )

    def _call_gemini(
        self,
        contents: List[types.Content],
        system_prompt: str,
        temperature: float,
        error_context: str,
    ) -> str:
        """
        Ejecuta una llamada a Gemini con la configuración indicada.

        Args:
            contents: Historial de mensajes para la conversación.
            system_prompt: Instrucción de sistema del reclutador.
            temperature: Temperatura de generación.
            error_context: Descripción del contexto para mensajes de error.

        Returns:
            Texto generado por el modelo.

        Raises:
            SystemExit: Si la API falla o devuelve respuesta vacía.
        """
        assert self._client is not None

        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_prompt,
        )

        try:
            response = self._client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config=config,
            )
            if not response.text or not response.text.strip():
                raise ValueError("Gemini devolvió una respuesta vacía.")
            return response.text.strip()
        except Exception as exc:
            print(f"\n[ERROR] Falló la llamada a Gemini al {error_context}:")
            print(exc)
            sys.exit(1)

    def _append_turn_to_history(self, question: str, answer: str) -> None:
        """
        Agrega el turno pregunta-respuesta al historial conversacional de Gemini.

        Args:
            question: Texto de la pregunta del reclutador.
            answer: Texto de la respuesta del candidato.
        """
        self._session.messages.append(
            types.Content(
                role="user",
                parts=[types.Part(text=f"[RECRUITER QUESTION]\n{question}")],
            )
        )
        self._session.messages.append(
            types.Content(
                role="model",
                parts=[types.Part(text=f"[CANDIDATE ANSWER]\n{answer}")],
            )
        )

    def _read_user_answer(self) -> Optional[str]:
        """
        Lee la respuesta del candidato desde la entrada estándar.

        Returns:
            Respuesta del usuario, o None si eligió salir.
        """
        while True:
            try:
                raw_input = input("Tu respuesta: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n[INFO] Entrada interrumpida.")
                return None

            if raw_input.lower() in {"salir", "exit", "quit"}:
                return None

            if not raw_input:
                print("[AVISO] La respuesta no puede estar vacía. Intenta de nuevo.")
                continue

            return raw_input

    def export_transcript(self) -> None:
        """
        Exporta la transcripción completa de la entrevista a un archivo Markdown.

        El archivo incluye todas las preguntas, respuestas y el feedback final.
        """
        lines: List[str] = ["# Mock Interview", ""]

        candidate_name = self._profile.get("personal_info", {}).get("full_name", "Candidato")
        lines.append(f"**Candidato:** {candidate_name}")
        lines.append(f"**Oferta:** {os.path.basename(self.job_path)}")
        lines.append(f"**Idioma:** {self.lang}")
        lines.append("")

        for turn in self._session.turns:
            lines.append(f"## Pregunta {turn.question_number}")
            lines.append("")
            lines.append(turn.question)
            lines.append("")
            lines.append("## Respuesta")
            lines.append("")
            lines.append(turn.answer if turn.answer else "_(sin respuesta)_")
            lines.append("")

        lines.append("## Feedback Final")
        lines.append("")
        lines.append(self._session.feedback if self._session.feedback else "_(no generado)_")
        lines.append("")

        content = "\n".join(lines)
        output_dir = os.path.dirname(self.transcript_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        try:
            with open(self.transcript_path, "w", encoding="utf-8") as file:
                file.write(content)
        except OSError as exc:
            print(f"\n[ERROR] No se pudo guardar la transcripción en '{self.transcript_path}':")
            print(exc)
            sys.exit(1)
