from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.orchestrator import PhaseExecution
from app.models.contracts import PhaseContext, PhaseId, PhaseOutput


@dataclass(frozen=True)
class InferenceRule:
    rule_id: str
    module: str
    question: str
    required_artifacts: tuple[str, ...]


FASE_8_RULES: tuple[InferenceRule, ...] = (
    InferenceRule("REGLA_1", "autenticacion", "Hay ACTORES. Hay autenticacion definida? Como se identifican?", ("actors", "actor_seed")),
    InferenceRule("REGLA_2", "base_de_datos", "Hay OBJETOS. Que base de datos? Volumen especifico?", ("objects", "objects_raw")),
    InferenceRule("REGLA_3", "auditoria", "Hay OPERACIONES. Necesitamos auditoria de quien hizo que?", ("operations",)),
    InferenceRule("REGLA_4", "health_checks", "Hay EVENTOS externos. Como monitoreamos health checks?", ("events",)),
    InferenceRule("REGLA_5", "pre_flight_checks", "Hay REGLAS NO-GO. Necesitamos pre-flight checks?", ("rules",)),
    InferenceRule("REGLA_6", "circuit_breaker", "Hay TIEMPOS definidos. Necesitamos circuit breaker?", ("time",)),
    InferenceRule("REGLA_7", "queue_excedentes", "Hay RECURSOS limitados. Necesitamos queue para excedentes?", ("resources",)),
    InferenceRule("REGLA_8", "rbac", "Hay MULTIPLES ACTORES. Necesitamos RBAC explicito?", ("actors",)),
    InferenceRule("REGLA_9", "transacciones_atomicas", "Hay OPERACIONES CRUZADAS. Necesitamos transacciones atomicas?", ("operations", "relations")),
    InferenceRule("REGLA_10", "scheduler_jobs", "Hay EVENTOS TEMPORALES. Necesitamos scheduler de jobs?", ("events", "time")),
    InferenceRule("REGLA_11", "backup_automatico", "Hay OBJETOS con volumen diario. Necesitamos backup automatico?", ("objects", "objects_raw")),
    InferenceRule("REGLA_12", "rate_limiting", "Hay respuesta_tiempo definida. Necesitamos rate limiting?", ("time", "resources")),
)


def execute_fase8_inference(ctx: PhaseContext) -> PhaseExecution:
    artifacts = ctx.artifacts.dimensions_12d
    proposals = _existing_or_new_proposals(artifacts)
    decisions = parse_module_decisions(ctx.user_input or "", proposals)
    resolved = _apply_decisions(proposals, decisions)
    missing = [
        proposal["module"]
        for proposal in resolved
        if proposal["status"] == "PENDING_HUMAN_DECISION"
    ]

    prompt = format_module_prompt(resolved, missing)
    output = PhaseOutput(
        phase_id=PhaseId.FASE_8,
        artifact_updates={
            "dimensions_12d": {
                "module_inference": {
                    "rules_source": "FASE_8_RULES",
                    "proposals": resolved,
                }
            }
        },
        questions_asked=[prompt],
        explicit_approvals=[
            f"{proposal['module']}:{proposal['decision']}"
            for proposal in resolved
            if proposal.get("decision") == "ACEPTADO_V1"
        ],
        next_phase_hint=PhaseId.FASE_8 if missing else PhaseId.FASE_8B,
    )
    return PhaseExecution(output=output, prompt=prompt)


def execute_fase12_systemic_inference(ctx: PhaseContext) -> PhaseExecution:
    artifacts = ctx.artifacts.dimensions_12d
    covered = {
        str(proposal.get("module"))
        for proposal in artifacts.get("module_inference", {}).get("proposals", [])
        if proposal.get("module")
    }
    candidates = [
        {
            "module": "observabilidad_trazas",
            "reason": "Eventos, operaciones y reglas requieren evidencia operativa.",
            "required_artifacts": ("events", "operations", "rules"),
        },
        {
            "module": "gestion_configuracion",
            "reason": "Recursos, comunicacion y espacio requieren parametros versionables.",
            "required_artifacts": ("resources", "communication", "space"),
        },
        {
            "module": "gobernanza_decisiones",
            "reason": "El SEC requiere decisiones bloqueadas, exclusiones y racionales auditables.",
            "required_artifacts": ("module_inference", "objectives"),
        },
        {
            "module": "validacion_grafos",
            "reason": "SYSTEM_GRAPH y TRACEABILITY_GRAPH no deben tener nodos huerfanos.",
            "required_artifacts": ("relations", "objectives", "operations"),
        },
    ]
    proposals = [
        {
            "module": candidate["module"],
            "reason": candidate["reason"],
            "status": "PROPOSED",
        }
        for candidate in candidates
        if candidate["module"] not in covered
        and any(key in artifacts for key in candidate["required_artifacts"])
    ]
    prompt = "FASE_12 - INFERENCIA SISTEMICA\n" + "\n".join(
        f"- {proposal['module']}: {proposal['reason']}" for proposal in proposals
    )
    output = PhaseOutput(
        phase_id=PhaseId.FASE_12,
        artifact_updates={
            "dimensions_12d": {
                "systemic_inference": {
                    "extends": "FASE_8",
                    "duplicates_excluded": sorted(covered),
                    "proposals": proposals,
                }
            }
        },
        questions_asked=[prompt],
    )
    return PhaseExecution(output=output, prompt=prompt)


def _existing_or_new_proposals(artifacts: dict[str, Any]) -> list[dict[str, Any]]:
    existing = artifacts.get("module_inference")
    if isinstance(existing, dict) and existing.get("proposals"):
        return [dict(proposal) for proposal in existing["proposals"]]

    proposals = []
    for rule in FASE_8_RULES:
        if not any(key in artifacts for key in rule.required_artifacts):
            continue
        proposals.append(
            {
                "rule_id": rule.rule_id,
                "module": rule.module,
                "question": rule.question,
                "required_decision": "ACEPTADO_V1 | FUTURO | EXCLUSION",
                "status": "PENDING_HUMAN_DECISION",
            }
        )
    return proposals


def parse_module_decisions(
    raw_answer: str,
    proposals: list[dict[str, Any]],
) -> dict[str, str]:
    normalized = raw_answer.upper()
    if not normalized.strip():
        return {}

    allowed = {"ACEPTADO_V1", "FUTURO", "EXCLUSION"}
    decisions: dict[str, str] = {}
    for proposal in proposals:
        module = str(proposal["module"])
        module_upper = module.upper()
        for decision in allowed:
            if f"{module_upper}:{decision}" in normalized:
                decisions[module] = decision
            if f"{module_upper} {decision}" in normalized:
                decisions[module] = decision
    if len(proposals) == 1 and normalized.strip() in allowed:
        decisions[str(proposals[0]["module"])] = normalized.strip()
    return decisions


def _apply_decisions(
    proposals: list[dict[str, Any]],
    decisions: dict[str, str],
) -> list[dict[str, Any]]:
    resolved = []
    for proposal in proposals:
        next_proposal = dict(proposal)
        module = str(next_proposal["module"])
        decision = decisions.get(module) or next_proposal.get("decision")
        if decision:
            next_proposal["decision"] = decision
            next_proposal["status"] = "DECIDED"
        resolved.append(next_proposal)
    return resolved


def format_module_prompt(
    proposals: list[dict[str, Any]],
    missing: list[str],
) -> str:
    lines = [
        "FASE_8 - INFERENCIA ACTIVA",
        "Responde cada modulo con ACEPTADO_V1, FUTURO o EXCLUSION.",
    ]
    lines.extend(
        f"- {proposal['rule_id']} {proposal['module']}: {proposal['question']}"
        for proposal in proposals
        if proposal["status"] == "PENDING_HUMAN_DECISION"
    )
    if missing:
        lines.append("Pendientes: " + ", ".join(missing))
    else:
        lines.append("Todas las decisiones de FASE_8 quedaron registradas.")
    return "\n".join(lines)
