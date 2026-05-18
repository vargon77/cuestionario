from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.core.scoring import rule_result
from app.models.contracts import PhaseId, RuleResult


def validador_1_actor_operation(artifacts: Mapping[str, Any]) -> RuleResult:
    return _requires("VALIDADOR_1", "Actor/operation lens", artifacts, ("actors", "operations"), PhaseId.FASE_2)


def validador_2_object_operation(artifacts: Mapping[str, Any]) -> RuleResult:
    return _requires("VALIDADOR_2", "Object/operation lens", artifacts, ("objects", "operations"), PhaseId.FASE_2)


def validador_3_state_event(artifacts: Mapping[str, Any]) -> RuleResult:
    return _requires("VALIDADOR_3", "State/event lens", artifacts, ("states", "events"), PhaseId.FASE_5)


def validador_4_rule_operation(artifacts: Mapping[str, Any]) -> RuleResult:
    return _requires("VALIDADOR_4", "Rule/operation lens", artifacts, ("rules", "operations"), PhaseId.FASE_4)


def validador_5_objective_kpi(artifacts: Mapping[str, Any]) -> RuleResult:
    raw = _raw(artifacts.get("objectives")).lower()
    passed = _has(artifacts, "objectives") and ("kpi" in raw or "|" in raw or any(char.isdigit() for char in raw))
    return rule_result(
        rule_id="VALIDADOR_5",
        label="Objective/KPI lens",
        max_points=1,
        points=1 if passed else 0,
        failures=[] if passed else ["objectives must include KPI or measurable evidence"],
        repair_phase=PhaseId.FASE_8B,
        evidence_paths=["artifacts.dimensions_12d.objectives"],
    )


def validador_6_resource_time(artifacts: Mapping[str, Any]) -> RuleResult:
    return _requires("VALIDADOR_6", "Resource/time lens", artifacts, ("resources", "time"), PhaseId.FASE_7)


def validador_7_space_resource(artifacts: Mapping[str, Any]) -> RuleResult:
    return _requires("VALIDADOR_7", "Space/resource lens", artifacts, ("space", "resources"), PhaseId.FASE_7B)


def validador_8_communication_security(artifacts: Mapping[str, Any]) -> RuleResult:
    return _requires("VALIDADOR_8", "Communication/security lens", artifacts, ("communication", "rules"), PhaseId.FASE_7C)


def validador_9_inference_decisions(artifacts: Mapping[str, Any]) -> RuleResult:
    inference = artifacts.get("module_inference")
    proposals = inference.get("proposals", []) if isinstance(inference, dict) else []
    passed = bool(proposals)
    return rule_result(
        rule_id="VALIDADOR_9",
        label="Inference decision lens",
        max_points=1,
        points=1 if passed else 0,
        failures=[] if passed else ["missing module inference proposals"],
        repair_phase=PhaseId.FASE_8,
        evidence_paths=["artifacts.dimensions_12d.module_inference"],
    )


def validador_10_no_implicit_modules(artifacts: Mapping[str, Any]) -> RuleResult:
    inference = artifacts.get("module_inference")
    proposals = inference.get("proposals", []) if isinstance(inference, dict) else []
    implicit = [
        str(proposal.get("module"))
        for proposal in proposals
        if isinstance(proposal, dict) and proposal.get("decision") in {None, "IMPLICIT"}
    ]
    return rule_result(
        rule_id="VALIDADOR_10",
        label="No implicit module approval",
        max_points=1,
        points=1 if not implicit else 0,
        failures=[f"module lacks explicit decision: {module}" for module in implicit],
        repair_phase=PhaseId.FASE_8 if implicit else None,
        evidence_paths=["artifacts.dimensions_12d.module_inference"],
    )


def validador_11_quantified_constraints(artifacts: Mapping[str, Any]) -> RuleResult:
    offenders = [key for key in ("time", "resources") if _has(artifacts, key) and not _has_number(_raw(artifacts[key]))]
    return rule_result(
        rule_id="VALIDADOR_11",
        label="Quantified constraints lens",
        max_points=1,
        points=1 if not offenders else 0,
        failures=[f"{key} lacks numeric value or DESCONOCIDO" for key in offenders],
        repair_phase=PhaseId.FASE_6 if offenders else None,
        evidence_paths=[f"artifacts.dimensions_12d.{key}" for key in offenders],
    )


def validador_12_state_rollback(artifacts: Mapping[str, Any]) -> RuleResult:
    raw = _raw(artifacts.get("states")).lower()
    passed = _has(artifacts, "states") and any(token in raw for token in ("rollback", "reversa", "terminal", "->", " a "))
    return rule_result(
        rule_id="VALIDADOR_12",
        label="State rollback/transition lens",
        max_points=1,
        points=1 if passed else 0,
        failures=[] if passed else ["states need transition and rollback/terminal evidence"],
        repair_phase=PhaseId.FASE_3,
        evidence_paths=["artifacts.dimensions_12d.states"],
    )


def validador_13_event_error_behavior(artifacts: Mapping[str, Any]) -> RuleResult:
    raw = _raw(artifacts.get("events")).lower()
    passed = _has(artifacts, "events") and any(token in raw for token in ("error", "timeout", "fallo", "retry", "prioridad"))
    return rule_result(
        rule_id="VALIDADOR_13",
        label="Event error behavior lens",
        max_points=1,
        points=1 if passed else 0,
        failures=[] if passed else ["events need priority or error behavior"],
        repair_phase=PhaseId.FASE_5,
        evidence_paths=["artifacts.dimensions_12d.events"],
    )


def validador_14_acceptance_readiness(artifacts: Mapping[str, Any]) -> RuleResult:
    return _requires("VALIDADOR_14", "Acceptance readiness lens", artifacts, ("objectives", "rules"), PhaseId.FASE_8B)


def validador_15_governance_readiness(artifacts: Mapping[str, Any]) -> RuleResult:
    return _requires("VALIDADOR_15", "Governance readiness lens", artifacts, ("actors", "rules", "module_inference"), PhaseId.FASE_4)


CROSS_VALIDATORS = (
    validador_1_actor_operation,
    validador_2_object_operation,
    validador_3_state_event,
    validador_4_rule_operation,
    validador_5_objective_kpi,
    validador_6_resource_time,
    validador_7_space_resource,
    validador_8_communication_security,
    validador_9_inference_decisions,
    validador_10_no_implicit_modules,
    validador_11_quantified_constraints,
    validador_12_state_rollback,
    validador_13_event_error_behavior,
    validador_14_acceptance_readiness,
    validador_15_governance_readiness,
)


def _requires(
    rule_id: str,
    label: str,
    artifacts: Mapping[str, Any],
    keys: tuple[str, ...],
    repair_phase: PhaseId,
) -> RuleResult:
    missing = [key for key in keys if not _has(artifacts, key)]
    return rule_result(
        rule_id=rule_id,
        label=label,
        max_points=1,
        points=1 if not missing else 0,
        failures=[f"missing {key}" for key in missing],
        repair_phase=repair_phase if missing else None,
        evidence_paths=[f"artifacts.dimensions_12d.{key}" for key in keys],
    )


def _has(artifacts: Mapping[str, Any], key: str) -> bool:
    value = artifacts.get(key)
    if value is None:
        return False
    if isinstance(value, dict):
        if isinstance(value.get("rows"), list):
            return len(value["rows"]) > 0
        if isinstance(value.get("proposals"), list):
            return len(value["proposals"]) > 0
        return bool(value)
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value)
    return True


def _raw(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(str(item) for item in value.values())
    return str(value)


def _has_number(raw: str) -> bool:
    normalized = raw.lower()
    return any(char.isdigit() for char in raw) or "desconocido" in normalized or "no se" in normalized
