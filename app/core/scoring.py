from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from app.models.contracts import PhaseId, RuleResult, ScoreReport


RuleFn = Callable[[Mapping[str, Any]], RuleResult]


def classify_fase9(total_points: int) -> str:
    if total_points >= 85:
        return "APROBADO"
    if total_points >= 70:
        return "APROBADO_CON_RESERVAS"
    return "RECHAZADO"


def classify_fase17(total_points: int) -> tuple[str, str]:
    if total_points >= 90:
        return "APROBADO_ENTERPRISE", "LOW"
    if total_points >= 80:
        return "APROBADO_PRODUCCION", "LOW"
    if total_points >= 70:
        return "APROBADO_CON_RESERVAS", "MEDIUM"
    return "RECHAZADO", "HIGH"


def run_rules(
    *,
    score_id: str,
    phase_id: PhaseId,
    artifacts: Mapping[str, Any],
    rules: Iterable[RuleFn],
    status: str | None = None,
    risk: str | None = None,
    max_points: int = 100,
) -> ScoreReport:
    results = [rule(artifacts) for rule in rules]
    _validate_rule_results(results)

    total_points = sum(result.points for result in results)
    percent = round((total_points / max_points) * 100)
    repair_targets = _unique_repair_targets(results)

    if status is None:
        status, risk = classify_score(phase_id, percent, risk=risk)

    return ScoreReport(
        score_id=score_id,
        phase_id=phase_id,
        total_points=total_points,
        max_points=max_points,
        status=status,
        risk=risk,
        rules=results,
        repair_targets=repair_targets,
    )


def classify_score(
    phase_id: PhaseId,
    total_points: int,
    *,
    risk: str | None = None,
) -> tuple[str, str | None]:
    if phase_id == PhaseId.FASE_9:
        return classify_fase9(total_points), risk
    if phase_id == PhaseId.FASE_17:
        return classify_fase17(total_points)
    return ("APROBADO" if total_points >= 70 else "RECHAZADO"), risk


def rule_result(
    *,
    rule_id: str,
    label: str,
    max_points: int,
    points: int,
    failures: list[str] | None = None,
    repair_phase: PhaseId | None = None,
    evidence_paths: list[str] | None = None,
) -> RuleResult:
    return RuleResult(
        rule_id=rule_id,
        label=label,
        max_points=max_points,
        points=points,
        passed=points == max_points and not failures,
        failures=failures or [],
        repair_phase=repair_phase,
        evidence_paths=evidence_paths or [],
    )


def _validate_rule_results(results: list[RuleResult]) -> None:
    for result in results:
        if result.points > result.max_points:
            raise ValueError(
                f"{result.rule_id} returned {result.points} points "
                f"but max_points is {result.max_points}"
            )
        if result.points < 0:
            raise ValueError(f"{result.rule_id} returned negative points")


def _unique_repair_targets(results: list[RuleResult]) -> list[PhaseId]:
    seen: set[PhaseId] = set()
    targets: list[PhaseId] = []
    for result in results:
        if result.passed or result.repair_phase is None:
            continue
        if result.repair_phase in seen:
            continue
        seen.add(result.repair_phase)
        targets.append(result.repair_phase)
    return targets
