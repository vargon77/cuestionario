from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.core.scoring import rule_result
from app.models.contracts import PhaseId, RuleResult


def vf_1_completitud(package: Mapping[str, Any]) -> RuleResult:
    required = ("dimensions_12d", "sec_initial", "system_graph", "traceability_graph")
    missing = [key for key in required if not package.get(key)]
    return _area("VF_1", "COMPLETITUD", not missing, missing, PhaseId.FASE_14)


def vf_2_consistencia(package: Mapping[str, Any]) -> RuleResult:
    graph = package.get("system_graph") or {}
    nodes = graph.get("nodes", []) if isinstance(graph, dict) else []
    edges = graph.get("edges", []) if isinstance(graph, dict) else []
    has_operation = any(node.get("tipo") == "OPERACION" for node in nodes if isinstance(node, dict))
    passed = has_operation and bool(edges)
    return _area("VF_2", "CONSISTENCIA", passed, ["system graph lacks operation/edge consistency"], PhaseId.FASE_14)


def vf_3_trazabilidad(package: Mapping[str, Any]) -> RuleResult:
    trace = package.get("traceability_graph") or {}
    hierarchy = trace.get("hierarchy", []) if isinstance(trace, dict) else []
    matrix = trace.get("matrix", {}) if isinstance(trace, dict) else {}
    passed = bool(hierarchy) and bool(matrix.get("rows") if isinstance(matrix, dict) else [])
    return _area("VF_3", "TRAZABILIDAD", passed, ["traceability hierarchy or matrix missing"], PhaseId.FASE_15)


def vf_4_operabilidad(package: Mapping[str, Any]) -> RuleResult:
    sec = _sections(package).get("FAILURE_STRATEGIES")
    passed = bool(sec)
    return _area("VF_4", "OPERABILIDAD", passed, ["failure strategies missing"], PhaseId.FASE_16)


def vf_5_observabilidad(package: Mapping[str, Any]) -> RuleResult:
    observability = _sections(package).get("OBSERVABILITY", {})
    passed = isinstance(observability, dict) and all(
        key in observability for key in ("logs", "metrics", "tracing", "audit_trails")
    )
    return _area("VF_5", "OBSERVABILIDAD", passed, ["observability incomplete"], PhaseId.FASE_16)


def vf_6_escalabilidad(package: Mapping[str, Any]) -> RuleResult:
    performance = _sections(package).get("PERFORMANCE_MODEL", {})
    passed = isinstance(performance, dict) and all(
        key in performance for key in ("throughput_max", "concurrentes_max", "degradacion_bajo_carga")
    )
    return _area("VF_6", "ESCALABILIDAD", passed, ["performance model incomplete"], PhaseId.FASE_16)


def vf_7_resiliencia(package: Mapping[str, Any]) -> RuleResult:
    raw = str(_sections(package).get("FAILURE_STRATEGIES", "")).lower()
    passed = any(token in raw for token in ("fallback", "recovery", "timeout", "degrad"))
    return _area("VF_7", "RESILIENCIA", passed, ["resilience strategy missing fallback/recovery"], PhaseId.FASE_16)


def vf_8_seguridad(package: Mapping[str, Any]) -> RuleResult:
    security = _sections(package).get("SECURITY_MODEL", {})
    rules = _sections(package).get("ACCEPTANCE_RULES", [])
    passed = bool(security) and bool(rules)
    return _area("VF_8", "SEGURIDAD", passed, ["security model or acceptance rules missing"], PhaseId.FASE_16)


def vf_9_gobernanza(package: Mapping[str, Any]) -> RuleResult:
    sections = _sections(package)
    passed = bool(sections.get("DECISION_RECORD")) and bool(sections.get("GOVERNANCE_MODEL"))
    return _area("VF_9", "GOBERNANZA", passed, ["decision record or governance model missing"], PhaseId.FASE_16)


def vf_10_verificabilidad(package: Mapping[str, Any]) -> RuleResult:
    acceptance = _sections(package).get("ACCEPTANCE_RULES", [])
    raw = " ".join(str(rule) for rule in acceptance).lower() if isinstance(acceptance, list) else str(acceptance).lower()
    passed = bool(acceptance) and "->" in raw and "rejects" in raw
    return _area("VF_10", "VERIFICABILIDAD", passed, ["acceptance rules are not binary/verifiable"], PhaseId.FASE_16)


FASE17_RULES = (
    vf_1_completitud,
    vf_2_consistencia,
    vf_3_trazabilidad,
    vf_4_operabilidad,
    vf_5_observabilidad,
    vf_6_escalabilidad,
    vf_7_resiliencia,
    vf_8_seguridad,
    vf_9_gobernanza,
    vf_10_verificabilidad,
)


def _area(
    rule_id: str,
    label: str,
    passed: bool,
    failures: list[str],
    repair_phase: PhaseId,
) -> RuleResult:
    return rule_result(
        rule_id=rule_id,
        label=label,
        max_points=10,
        points=10 if passed else 0,
        failures=[] if passed else failures,
        repair_phase=None if passed else repair_phase,
        evidence_paths=["artifacts"],
    )


def _sections(package: Mapping[str, Any]) -> Mapping[str, Any]:
    sec = package.get("sec_extended") or package.get("sec_initial") or {}
    if isinstance(sec, dict):
        sections = sec.get("sections", {})
        if isinstance(sections, dict):
            return sections
    return {}
