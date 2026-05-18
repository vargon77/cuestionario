from __future__ import annotations

from app.models.contracts import CheckpointVerdict, PhaseId


CHECKPOINT_1_TEMPLATE = """=== CONTRATO SEC GENERADO ===
Puntuacion de calidad: {score}%
Umbral requerido: 85% (ideal) / 70% (minimo)
Estado: {status}
{sec_document}
Este contrato representa lo que discutimos?
RESPONDE CON UNA DE ESTAS OPCIONES:

'SI'                            -> El SEC esta listo.
'NO_CAMBIAR: [especificacion]'  -> Modifico el SEC.
'INCOMPLETO: [dimension]'       -> Regreso a FASE.
"""


CHECKPOINT_2_TEMPLATE = """=== CONTRATO SEC GENERADO ===

Validation Score : {score}
Estado           : {status}
Riesgo           : {risk}

SECCIONES:
- Problem
- Outcome
- Constraints
- System Graph
- Traceability Graph
- Risks
- Exclusions
- Acceptance Rules

=== VALIDACION HUMANA OBLIGATORIA ===

RESPONDE:

1. SI
2. NO_CAMBIAR: [detalle]
3. INCOMPLETO: [fase]
4. REVALIDAR: [elemento]
"""


def parse_checkpoint_verdict(raw: str | CheckpointVerdict) -> CheckpointVerdict:
    if isinstance(raw, CheckpointVerdict):
        return raw

    command = raw.strip().split(":", 1)[0].strip().upper()
    if command in {"SI"}:
        return CheckpointVerdict.APPROVED
    if command in {"NO", "NO CAMBIAR", "NO_CAMBIAR"}:
        return CheckpointVerdict.CHANGE_REQUESTED
    if command in {"INCOMPLETO", "INCOMPLETE"}:
        return CheckpointVerdict.INCOMPLETE
    if command == "REVALIDAR":
        return CheckpointVerdict.REVALIDATE
    valid = ", ".join(verdict.value for verdict in CheckpointVerdict)
    raise ValueError(f"invalid checkpoint verdict: {raw!r}. Valid: {valid}")


def checkpoint_state_value(verdict: CheckpointVerdict) -> str:
    if verdict == CheckpointVerdict.APPROVED:
        return "approved"
    if verdict == CheckpointVerdict.CHANGE_REQUESTED:
        return "change_requested"
    if verdict == CheckpointVerdict.INCOMPLETE:
        return "incomplete"
    if verdict == CheckpointVerdict.REVALIDATE:
        return "revalidate"
    raise ValueError(f"unsupported checkpoint verdict: {verdict.value}")


def template_for_phase(phase_id: PhaseId) -> str:
    if phase_id == PhaseId.FASE_11:
        return CHECKPOINT_1_TEMPLATE
    if phase_id == PhaseId.FASE_18:
        return CHECKPOINT_2_TEMPLATE
    raise ValueError(f"{phase_id.value} is not a checkpoint phase")
