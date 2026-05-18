from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any

from app.core.defaults_repository import detect_system_type, get_defaults
from app.core.orchestrator import PhaseExecution
from app.models.contracts import (
    CONSTRAINTS_HASH_FORMULA,
    DecisionRecord,
    PhaseContext,
    PhaseId,
    PhaseOutput,
    SECMetadata,
    SEC_SECTION_NAMES,
    SECDocument,
    ScoreReport,
)


MIN_SEC_SCORE = 70


def execute_initial_sec_generation(ctx: PhaseContext) -> PhaseExecution:
    score = _required_score(ctx, "v5_completeness", PhaseId.FASE_9)
    _ensure_score_allows_generation(score)
    sec = build_sec_document(ctx, score=score, version=1, extended=False)
    return PhaseExecution(
        output=PhaseOutput(
            phase_id=PhaseId.FASE_10,
            artifact_updates={"sec_initial": sec.model_dump(mode="json")},
        ),
        prompt="SEC inicial generado de forma deterministica.",
    )


def execute_extended_sec_generation(ctx: PhaseContext) -> PhaseExecution:
    score = _score_for_extended_generation(ctx)
    _ensure_score_allows_generation(score)
    sec = build_sec_document(ctx, score=score, version=2, extended=True)
    return PhaseExecution(
        output=PhaseOutput(
            phase_id=PhaseId.FASE_16,
            artifact_updates={"sec_extended": sec.model_dump(mode="json")},
        ),
        prompt="SEC extendido de 20 secciones generado de forma deterministica.",
    )


def build_sec_document(
    ctx: PhaseContext,
    *,
    score: ScoreReport,
    version: int,
    extended: bool,
) -> SECDocument:
    artifacts = ctx.artifacts
    dimensions = artifacts.dimensions_12d
    system_type = detect_system_type(_raw_dimension(dimensions, "actor_seed"))
    defaults = get_defaults(system_type)
    timestamp = datetime.now(timezone.utc)
    sec_id = _sec_id(timestamp, dimensions, version)
    sections = _build_sections(
        ctx,
        sec_id=sec_id,
        score=score,
        defaults=defaults,
        extended=extended,
    )
    constraints_hash = _hash_payload(
        {
            "constraints": sections["CONSTRAINTS"],
            "estimations": sections["ESTIMATIONS"],
        }
    )
    metadata = SECMetadata(
        sec_id=sec_id,
        version=version,
        timestamp=timestamp,
        tipo_sistema=system_type.value,
        validation_score=score.percent,
        estado=score.status,
        constraints_hash=f"sha256:{constraints_hash}",
    )
    document = SECDocument(metadata=metadata, sections=sections)
    sec_hash = _hash_payload(document.model_dump(mode="json"))
    metadata.sec_hash = f"sha256:{sec_hash}"
    return SECDocument(metadata=metadata, sections=sections)


def _build_sections(
    ctx: PhaseContext,
    *,
    sec_id: str,
    score: ScoreReport,
    defaults: Any,
    extended: bool,
) -> dict[str, Any]:
    dimensions = ctx.artifacts.dimensions_12d
    estimations = ctx.artifacts.estimations.model_dump(mode="json")
    decisions = ctx.artifacts.decision_records or [
        DecisionRecord(
            id="DEC-001",
            decision="SEC generado deterministicamente desde artefactos persistidos.",
            rationale="FASE_10/FASE_16 generation",
            overrides=[],
        )
    ]
    module_inference = dimensions.get("module_inference", {})
    proposals = module_inference.get("proposals", []) if isinstance(module_inference, dict) else []

    constraints = {
        "max_scopes": 5,
        "max_complexity": "MEDIA",
        "max_tokens": 8000,
        "riesgo_permitido": "MEDIO",
        "tiempo_max_respuesta": defaults.normal_response_time,
        "concurrentes_max": defaults.concurrency,
        "formula": CONSTRAINTS_HASH_FORMULA,
    }
    sections = {
        "METADATA": {
            "sec_id": sec_id,
            "version": 2 if extended else 1,
            "validation_score": score.percent,
            "estado": score.status,
        },
        "PROBLEM": _problem_statement(dimensions),
        "OUTCOME": _outcome_statement(dimensions),
        "CONSTRAINTS": constraints,
        "ESTIMATIONS": estimations,
        "SYSTEM_LOGIC": {
            "user_flow": _rows_or_raw(dimensions, "operations"),
            "system_actions": _rows_or_raw(dimensions, "events"),
        },
        "SYSTEM_GRAPH": _graph_payload(ctx.artifacts.system_graph),
        "TRACEABILITY_GRAPH": _graph_payload(ctx.artifacts.traceability_graph),
        "SCOPES": _scopes(dimensions),
        "RISKS": _risks(dimensions, proposals),
        "EXCLUSIONS": _exclusions(dimensions, proposals),
        "ACCEPTANCE_RULES": _acceptance_rules(dimensions, defaults),
        "DECISION_RECORD": [record.model_dump(mode="json") for record in decisions],
        "STATE": ctx.artifacts.sec_state.model_dump(mode="json"),
        "OBSERVABILITY": _observability(dimensions),
        "FAILURE_STRATEGIES": _failure_strategies(dimensions),
        "DEPLOYMENT_TOPOLOGY": _deployment_topology(dimensions),
        "SECURITY_MODEL": _security_model(proposals),
        "PERFORMANCE_MODEL": _performance_model(defaults),
        "GOVERNANCE_MODEL": _governance_model(dimensions),
    }
    return {section: sections[section] for section in SEC_SECTION_NAMES}


def _required_score(
    ctx: PhaseContext,
    score_key: str,
    phase_id: PhaseId,
) -> ScoreReport:
    score = ctx.scores.get(score_key)
    if score is None:
        raise ValueError(f"{phase_id.value} score is required before SEC generation")
    if score.phase_id != phase_id:
        raise ValueError(f"{score_key} must come from {phase_id.value}")
    return score


def _score_for_extended_generation(ctx: PhaseContext) -> ScoreReport:
    if "v6_final" in ctx.scores:
        return ctx.scores["v6_final"]
    return _required_score(ctx, "v5_completeness", PhaseId.FASE_9)


def _ensure_score_allows_generation(score: ScoreReport) -> None:
    if score.percent < MIN_SEC_SCORE:
        raise ValueError("SEC generation requires validation score >= 70")


def _sec_id(timestamp: datetime, dimensions: dict[str, Any], version: int) -> str:
    raw_name = _raw_dimension(dimensions, "actor_seed") or "SEC"
    short_name = re.sub(r"[^A-Za-z0-9]+", "_", raw_name).strip("_")[:24] or "SEC"
    return f"{timestamp:%Y%m%d}_{short_name.upper()}_V{version}"


def _problem_statement(dimensions: dict[str, Any]) -> str:
    actors = _raw_dimension(dimensions, "actors") or _raw_dimension(dimensions, "actor_seed") or "ACTORES"
    operations = _raw_dimension(dimensions, "operations") or "OPERACION"
    return f"Los {actors} no pueden {operations} causando IMPACTO_MEDIBLE"


def _outcome_statement(dimensions: dict[str, Any]) -> str:
    actors = _raw_dimension(dimensions, "actors") or "ACTORES_PRINCIPALES"
    operations = _raw_dimension(dimensions, "operations") or "OPERACIONES_CLAVE"
    objects = _raw_dimension(dimensions, "objects") or _raw_dimension(dimensions, "objects_raw") or "OBJETOS_PRINCIPALES"
    return f"Los {actors} pueden {operations} con {objects}"


def _scopes(dimensions: dict[str, Any]) -> list[dict[str, Any]]:
    operations = _rows_or_raw(dimensions, "operations")
    return [
        {
            "id": "SCOPE_1",
            "input": "artefactos capturados",
            "output": operations or "resultado observable",
            "done_when": "resultado ocurre y queda registrado",
            "dependencies": "NINGUNA",
            "depth": 1,
            "leaf": True,
            "max_subscopes": 0,
        }
    ]


def _risks(dimensions: dict[str, Any], proposals: list[dict[str, Any]]) -> list[str]:
    risks = ["Riesgo 1: ambiguedad remanente -> Mitigation: revalidar dimensiones incompletas"]
    if any(proposal.get("status") == "PENDING_HUMAN_DECISION" for proposal in proposals):
        risks.append("Riesgo 2: modulos pendientes -> Mitigation: bloquear aprobacion implicita")
    if _raw_dimension(dimensions, "resources"):
        risks.append("Riesgo 3: exceso de recursos -> Mitigation: aplicar degradacion/fallback")
    return risks


def _exclusions(dimensions: dict[str, Any], proposals: list[dict[str, Any]]) -> list[str]:
    exclusions = _rows_or_raw(dimensions, "rules")
    if not isinstance(exclusions, list):
        exclusions = [exclusions] if exclusions else []
    for proposal in proposals:
        decision = proposal.get("decision")
        if decision == "FUTURO":
            exclusions.append(f"FUTURO_EXCLUSION: {proposal['module']}")
        if decision == "EXCLUSION":
            exclusions.append(f"NO-GO: {proposal['module']}")
    return exclusions


def _acceptance_rules(dimensions: dict[str, Any], defaults: Any) -> list[str]:
    actor = _first_cell(dimensions, "actors") or "ACTOR"
    operation = _first_cell(dimensions, "operations") or "OPERACION"
    resource = _first_cell(dimensions, "resources") or "RECURSO"
    return [
        f"AR-1: {actor} ejecuta {operation} -> resultado ocurre en < {defaults.normal_response_time}",
        "AR-2: condicion prohibida -> sistema REJECTS con mensaje \"OPERACION_NO_PERMITIDA\"",
        f"AR-3: Recurso {resource} alcanza limite -> sistema aplica COMPORTAMIENTO_DEGRADADO",
    ]


def _observability(dimensions: dict[str, Any]) -> dict[str, Any]:
    return {
        "logs": "eventos criticos y errores",
        "metrics": "latencia, throughput, errores, recursos",
        "tracing": "operaciones criticas",
        "alerts": _rows_or_raw(dimensions, "events") or "errores y timeouts",
        "dashboards": "salud operativa",
        "audit_trails": "operaciones con actor y timestamp",
    }


def _failure_strategies(dimensions: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "componente": "sistema",
            "fallo_tipo": "timeout",
            "estrategia": "fallback",
            "fallback": _raw_dimension(dimensions, "resources") or "degradacion controlada",
            "recovery": "segun SLA capturado",
        }
    ]


def _deployment_topology(dimensions: dict[str, Any]) -> dict[str, Any]:
    return {
        "componentes": ["api", "storage", "worker"],
        "ubicacion": _raw_dimension(dimensions, "space") or "cloud",
        "regiones": "region primaria",
        "replicacion": "pendiente de FASE_14/15" ,
        "latencia_max": _raw_dimension(dimensions, "time") or "DESCONOCIDO",
    }


def _security_model(proposals: list[dict[str, Any]]) -> dict[str, Any]:
    modules = {str(proposal.get("module")) for proposal in proposals}
    return {
        "autenticacion": "requerida" if any("auth" in module or "autentic" in module for module in modules) else "pendiente",
        "autorizacion": "RBAC" if any("rbac" in module.lower() for module in modules) else "pendiente",
        "cifrado": "en transito y en reposo",
        "auditoria": "operaciones criticas",
        "politicas": "segun reglas NO-GO",
    }


def _performance_model(defaults: Any) -> dict[str, str]:
    return {
        "throughput_max": defaults.daily_volume,
        "latencia_p99": defaults.complex_response_time,
        "concurrentes_max": defaults.concurrency,
        "degradacion_bajo_carga": "fallback documentado",
        "sla_disponibilidad": "99%",
    }


def _governance_model(dimensions: dict[str, Any]) -> dict[str, str]:
    return {
        "propietario_sistema": _first_cell(dimensions, "actors") or "OWNER_PENDIENTE",
        "revision_periodica": "mensual",
        "proceso_cambios": "decision_record LOCKED por cambio",
        "compliance": _raw_dimension(dimensions, "rules") or "pendiente",
        "responsables_sec": "ENTREVISTADOR",
    }


def _graph_payload(graph: Any) -> Any:
    if graph is None:
        return {"status": "PENDING_GRAPH_GENERATION"}
    if hasattr(graph, "model_dump"):
        return graph.model_dump(mode="json")
    return graph


def _rows_or_raw(dimensions: dict[str, Any], key: str) -> Any:
    value = dimensions.get(key)
    if isinstance(value, dict):
        return value.get("rows") or value.get("raw") or value
    return value


def _first_cell(dimensions: dict[str, Any], key: str) -> str | None:
    value = dimensions.get(key)
    if isinstance(value, dict):
        rows = value.get("rows")
        if rows and isinstance(rows, list):
            first = rows[0]
            if isinstance(first, dict):
                return str(first.get("c1"))
        raw = value.get("raw")
        return str(raw) if raw else None
    return str(value) if value else None


def _raw_dimension(dimensions: dict[str, Any], key: str) -> str:
    value = dimensions.get(key)
    if isinstance(value, dict):
        if "raw_goal" in value:
            return str(value["raw_goal"])
        if "raw" in value:
            return str(value["raw"])
    return str(value) if value else ""


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
