from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.core.scoring import rule_result
from app.models.contracts import PhaseId, RuleResult


def r1_actors(artifacts: Mapping[str, Any]) -> RuleResult:
    return _presence("R1", "Actores", 4, artifacts, "actors", PhaseId.FASE_0, aliases=("actor_seed",), min_items=1)


def r2_objects(artifacts: Mapping[str, Any]) -> RuleResult:
    return _presence("R2", "Objetos", 6, artifacts, "objects", PhaseId.FASE_1, aliases=("objects_raw",), min_items=1)


def r3_operations(artifacts: Mapping[str, Any]) -> RuleResult:
    return _presence("R3", "Operaciones", 5, artifacts, "operations", PhaseId.FASE_2)


def r4_states(artifacts: Mapping[str, Any]) -> RuleResult:
    return _presence("R4", "Estados", 5, artifacts, "states", PhaseId.FASE_3)


def r5_rules(artifacts: Mapping[str, Any]) -> RuleResult:
    return _presence("R5", "Reglas", 5, artifacts, "rules", PhaseId.FASE_4)


def r6_events(artifacts: Mapping[str, Any]) -> RuleResult:
    return _presence("R6", "Eventos", 5, artifacts, "events", PhaseId.FASE_5)


def r7_time(artifacts: Mapping[str, Any]) -> RuleResult:
    return _presence("R7", "Tiempo", 5, artifacts, "time", PhaseId.FASE_6)


def r8_resources(artifacts: Mapping[str, Any]) -> RuleResult:
    return _presence("R8", "Recursos", 5, artifacts, "resources", PhaseId.FASE_7)


def r9_no_lexical_ambiguity(artifacts: Mapping[str, Any]) -> RuleResult:
    offenders = [
        key
        for key, value in artifacts.items()
        if any(token in _raw(value).lower() for token in ("tal vez", "quizas", "etc", "depende"))
    ]
    return rule_result(
        rule_id="R9",
        label="Ausencia de ambiguedad lexica",
        max_points=10,
        points=10 if not offenders else 0,
        failures=[f"ambiguedad no documentada en {key}" for key in offenders],
        repair_phase=PhaseId.FASE_1 if offenders else None,
        evidence_paths=[f"artifacts.dimensions_12d.{key}" for key in offenders],
    )


def r10_internal_consistency(artifacts: Mapping[str, Any]) -> RuleResult:
    missing = []
    if _has(artifacts, "operations") and not (_has(artifacts, "actors") or _has(artifacts, "actor_seed")):
        missing.append("operations require actors")
    if _has(artifacts, "operations") and not (_has(artifacts, "objects") or _has(artifacts, "objects_raw")):
        missing.append("operations require objects")
    return rule_result(
        rule_id="R10",
        label="Consistencia interna",
        max_points=10,
        points=10 if not missing else 0,
        failures=missing,
        repair_phase=PhaseId.FASE_2 if missing else None,
        evidence_paths=["artifacts.dimensions_12d.operations"],
    )


def r11_inference_coverage(artifacts: Mapping[str, Any]) -> RuleResult:
    return _presence("R11", "Cobertura de inferencia", 10, artifacts, "module_inference", PhaseId.FASE_8)


def r12_complete_quantification(artifacts: Mapping[str, Any]) -> RuleResult:
    offenders = []
    for key in ("objects", "objects_raw", "time", "resources"):
        if key in artifacts and not _has_number_or_unknown(_raw(artifacts[key])):
            offenders.append(key)
    return rule_result(
        rule_id="R12",
        label="Cuantificacion completa",
        max_points=10,
        points=10 if not offenders else 0,
        failures=[f"{key} lacks number/range/DESCONOCIDO" for key in offenders],
        repair_phase=PhaseId.FASE_1 if offenders else None,
        evidence_paths=[f"artifacts.dimensions_12d.{key}" for key in offenders],
    )


def r13_risk_plan(artifacts: Mapping[str, Any]) -> RuleResult:
    passed = _has(artifacts, "rules") and _has(artifacts, "module_inference")
    return rule_result(
        rule_id="R13",
        label="Plan de riesgos",
        max_points=10,
        points=10 if passed else 0,
        failures=[] if passed else ["missing rules or module inference"],
        repair_phase=PhaseId.FASE_4 if not _has(artifacts, "rules") else PhaseId.FASE_8,
        evidence_paths=["artifacts.dimensions_12d.rules", "artifacts.dimensions_12d.module_inference"],
    )


def r14_verifiable_metrics(artifacts: Mapping[str, Any]) -> RuleResult:
    raw = _raw(artifacts.get("objectives"))
    passed = "kpi" in raw.lower() or _has_number_or_unknown(raw)
    return rule_result(
        rule_id="R14",
        label="Verificabilidad de metricas",
        max_points=10,
        points=10 if passed else 0,
        failures=[] if passed else ["objectives lack KPI or measurable evidence"],
        repair_phase=PhaseId.FASE_8B,
        evidence_paths=["artifacts.dimensions_12d.objectives"],
    )


def r15_excess_strategy(artifacts: Mapping[str, Any]) -> RuleResult:
    raw = f"{_raw(artifacts.get('resources'))} {_raw(artifacts.get('time'))}".lower()
    passed = any(token in raw for token in ("degrad", "fallback", "queue", "cola", "timeout", "excede"))
    return rule_result(
        rule_id="R15",
        label="Estrategia de exceso",
        max_points=10,
        points=10 if passed else 0,
        failures=[] if passed else ["missing overload strategy"],
        repair_phase=PhaseId.FASE_7,
        evidence_paths=["artifacts.dimensions_12d.resources", "artifacts.dimensions_12d.time"],
    )


FASE9_RULES = (
    r1_actors,
    r2_objects,
    r3_operations,
    r4_states,
    r5_rules,
    r6_events,
    r7_time,
    r8_resources,
    r9_no_lexical_ambiguity,
    r10_internal_consistency,
    r11_inference_coverage,
    r12_complete_quantification,
    r13_risk_plan,
    r14_verifiable_metrics,
    r15_excess_strategy,
)


def _presence(
    rule_id: str,
    label: str,
    points: int,
    artifacts: Mapping[str, Any],
    key: str,
    repair_phase: PhaseId,
    *,
    aliases: tuple[str, ...] = (),
    min_items: int = 1,
) -> RuleResult:
    keys = (key, *aliases)
    matched = next((candidate for candidate in keys if _has(artifacts, candidate)), None)
    item_count = _item_count(artifacts[matched]) if matched else 0
    passed = item_count >= min_items
    return rule_result(
        rule_id=rule_id,
        label=label,
        max_points=points,
        points=points if passed else 0,
        failures=[] if passed else [f"missing or incomplete {key}"],
        repair_phase=repair_phase,
        evidence_paths=[f"artifacts.dimensions_12d.{matched or key}"],
    )


def _has(artifacts: Mapping[str, Any], key: str) -> bool:
    return key in artifacts and _item_count(artifacts[key]) > 0


def _item_count(value: Any) -> int:
    if isinstance(value, dict):
        if "item_count" in value:
            return int(value["item_count"])
        if "rows" in value and isinstance(value["rows"], list):
            return len(value["rows"])
        if "proposals" in value and isinstance(value["proposals"], list):
            return len(value["proposals"])
        return 1 if value else 0
    if isinstance(value, str):
        return 1 if value.strip() else 0
    if isinstance(value, list):
        return len(value)
    return 1 if value is not None else 0


def _raw(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return str(value.get("raw", value))
    return str(value)


def _has_number_or_unknown(raw: str) -> bool:
    normalized = raw.lower()
    return any(char.isdigit() for char in raw) or "desconocido" in normalized or "no se" in normalized
