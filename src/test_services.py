"""Pruebas unitarias para Mock Interview y Robustness Judge."""

from __future__ import annotations

import json
import os
import tempfile
import unittest

from pydantic import ValidationError

from models import (
    EthicalIssue,
    Hallucination,
    Inconsistency,
    RobustnessReport,
)
from services.mock_interview import InterviewTurn, MockInterviewService
from services.robustness_judge import RobustnessJudgeService


class TestRobustnessModels(unittest.TestCase):
    """Valida el esquema Pydantic del informe de robustez."""

    def setUp(self) -> None:
        self.valid_report_json = json.dumps(
            {
                "score_honestidad": 8,
                "score_consistencia": 9,
                "score_etico": 7,
                "alucinaciones_detectadas": [
                    {
                        "linea_cv": "Skills: Kubernetes",
                        "dato_inventado": "Kubernetes",
                        "severidad": "media",
                        "explicacion": "No aparece en el perfil original del estudiante.",
                    }
                ],
                "inconsistencias_detectadas": [],
                "problemas_eticos": [
                    {
                        "descripcion": "Métrica de rendimiento exagerada sin evidencia.",
                        "severidad": "baja",
                    }
                ],
                "comentario_auditor": "CV mayormente fiel con hallazgos menores.",
                "recomendacion_final": "Revisar skills antes de enviar la postulación.",
            },
            ensure_ascii=False,
        )

    def test_robustness_report_valid_json(self) -> None:
        report = RobustnessReport.model_validate_json(self.valid_report_json)
        self.assertEqual(report.score_honestidad, 8)
        self.assertEqual(len(report.alucinaciones_detectadas), 1)
        self.assertIsInstance(report.alucinaciones_detectadas[0], Hallucination)

    def test_robustness_report_invalid_score(self) -> None:
        invalid = json.loads(self.valid_report_json)
        invalid["score_honestidad"] = 15
        with self.assertRaises(ValidationError):
            RobustnessReport.model_validate(invalid)

    def test_robustness_schema_has_required_fields(self) -> None:
        schema = RobustnessReport.model_json_schema()
        required = set(schema.get("required", []))
        self.assertIn("score_honestidad", required)
        self.assertIn("recomendacion_final", required)


class TestMockInterviewExport(unittest.TestCase):
    """Valida la generación de la transcripción Markdown."""

    def test_export_transcript_format(self) -> None:
        service = MockInterviewService(
            profile_path="config/student_profile.yaml",
            job_path="sample_job_description.txt",
        )
        service._profile = {"personal_info": {"full_name": "Test User"}}
        service._session.turns = [
            InterviewTurn(1, "¿Qué es FastAPI?", "Framework ASGI para APIs."),
            InterviewTurn(2, "¿Cómo usas Docker?", "Para contenerizar microservicios."),
        ]
        service._session.feedback = "## Score general\n7/10 — Buen desempeño."

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, "interview_transcript.md")
            service.transcript_path = output_path
            service.export_transcript()

            with open(output_path, "r", encoding="utf-8") as file:
                content = file.read()

        self.assertIn("# Mock Interview", content)
        self.assertIn("## Pregunta 1", content)
        self.assertIn("## Respuesta", content)
        self.assertIn("## Feedback Final", content)
        self.assertIn("Framework ASGI", content)


class TestRobustnessExport(unittest.TestCase):
    """Valida la exportación del informe JSON."""

    def test_export_report_json(self) -> None:
        report = RobustnessReport.model_validate_json(
            json.dumps(
                {
                    "score_honestidad": 9,
                    "score_consistencia": 9,
                    "score_etico": 9,
                    "alucinaciones_detectadas": [],
                    "inconsistencias_detectadas": [],
                    "problemas_eticos": [],
                    "comentario_auditor": "Sin hallazgos relevantes.",
                    "recomendacion_final": "CV apto para envío.",
                }
            )
        )
        service = RobustnessJudgeService()
        service._report = report

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, "robustness_report.json")
            service.report_path = output_path
            service.export_report()

            with open(output_path, "r", encoding="utf-8") as file:
                data = json.load(file)

        self.assertEqual(data["score_honestidad"], 9)
        self.assertEqual(data["alucinaciones_detectadas"], [])
        RobustnessReport.model_validate(data)


if __name__ == "__main__":
    unittest.main()
