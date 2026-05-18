from __future__ import annotations

from app.core.phase_registry import (
    DETERMINISTIC_PHASE_KINDS,
    get_phase_definition,
    is_deterministic_phase,
)
from app.models.contracts import (
    CheckpointVerdict,
    GateResult,
    GateStatus,
    PhaseId,
    PhaseKind,
    PhaseOutput,
    ScoreReport,
)


LLM_ALLOWED_KINDS = frozenset({PhaseKind.CAPTURE, PhaseKind.INFERENCE})
MAX_FASE9_REPAIR_ATTEMPTS = 3


class PhaseKindViolationError(RuntimeError):
    """A deterministic phase attempted to access LLMService."""


def assert_llm_allowed(phase_id: PhaseId) -> None:
    definition = get_phase_definition(phase_id)
    if definition.kind not in LLM_ALLOWED_KINDS:
        deterministic = ", ".join(kind.value for kind in DETERMINISTIC_PHASE_KINDS)
        raise PhaseKindViolationError(
            f"{phase_id.value} is {definition.kind.value} and is deterministic. "
            "Use only persisted artifacts, templates, validators, scoring, hashes "
            "or graph builders for this phase. LLMService must not be injected. "
            f"Deterministic kinds: {deterministic}."
        )


def evaluate_gate(
    *,
    phase_id: PhaseId,
    output: PhaseOutput,
    score: ScoreReport | None = None,
    repair_attempts_made: int = 0,
) -> GateResult:
    if phase_id == PhaseId.FASE_9:
        if score is None:
            raise ValueError("FASE_9 gate requires ScoreReport")
        return evaluate_fase9_gate(
            score,
            repair_attempts_made=repair_attempts_made,
        )

    if phase_id == PhaseId.FASE_17:
        if score is None:
            raise ValueError("FASE_17 gate requires ScoreReport")
        return evaluate_fase17_gate(score)

    definition = get_phase_definition(phase_id)
    if definition.requires_human_confirmation:
        return GateResult(status=GateStatus.NEEDS_HUMAN, next_phase=phase_id)

    return GateResult(
        status=GateStatus.PASS,
        next_phase=output.next_phase_hint or definition.next_phase,
    )


def evaluate_fase9_gate(
    score: ScoreReport,
    *,
    repair_attempts_made: int,
) -> GateResult:
    if score.phase_id != PhaseId.FASE_9:
        raise ValueError("FASE_9 gate received score for a different phase")

    if score.percent >= 85:
        return GateResult(
            status=GateStatus.PASS,
            score=score,
            next_phase=PhaseId.FASE_10,
        )

    if score.percent >= 70:
        repair_phase = _first_repair_target(score) or PhaseId.FASE_1
        if repair_attempts_made >= MAX_FASE9_REPAIR_ATTEMPTS:
            return GateResult(
                status=GateStatus.FAIL_HARD,
                score=score,
                repair_phase=PhaseId.FASE_1,
                max_retries_remaining=0,
                blocking_rules=_failed_rule_ids(score),
                next_phase=PhaseId.FASE_1,
            )
        remaining = MAX_FASE9_REPAIR_ATTEMPTS - repair_attempts_made
        return GateResult(
            status=GateStatus.NEEDS_REPAIR,
            score=score,
            repair_phase=repair_phase,
            max_retries_remaining=remaining,
            blocking_rules=_failed_rule_ids(score),
            next_phase=repair_phase,
        )

    return GateResult(
        status=GateStatus.FAIL,
        score=score,
        repair_phase=PhaseId.FASE_1,
        blocking_rules=_failed_rule_ids(score),
        next_phase=PhaseId.FASE_1,
    )


def evaluate_fase17_gate(score: ScoreReport) -> GateResult:
    if score.phase_id != PhaseId.FASE_17:
        raise ValueError("FASE_17 gate received score for a different phase")

    # FASE_17 never blocks before the final human checkpoint. Low scores and
    # failed rules travel as risk evidence so FASE_18 can present them.
    return GateResult(
        status=GateStatus.PASS,
        score=score,
        repair_phase=_first_repair_target(score),
        blocking_rules=_failed_rule_ids(score),
        next_phase=PhaseId.FASE_18,
    )


def evaluate_checkpoint_gate(
    *,
    phase_id: PhaseId,
    verdict: CheckpointVerdict,
) -> GateResult:
    definition = get_phase_definition(phase_id)
    allowed = set(definition.gate_config.get("allowed_verdicts", []))
    if verdict.value not in allowed:
        return GateResult(
            status=GateStatus.FAIL,
            errors=[f"{verdict.value} is not allowed for {phase_id.value}"],
            next_phase=phase_id,
        )

    if verdict == CheckpointVerdict.APPROVED:
        return GateResult(status=GateStatus.PASS, next_phase=definition.next_phase)

    if verdict == CheckpointVerdict.REVALIDATE:
        return GateResult(status=GateStatus.NEEDS_REPAIR, next_phase=PhaseId.FASE_17)

    return GateResult(status=GateStatus.NEEDS_REPAIR, next_phase=phase_id)


def _first_repair_target(score: ScoreReport) -> PhaseId | None:
    if score.repair_targets:
        return score.repair_targets[0]
    for rule in score.rules:
        if not rule.passed and rule.repair_phase is not None:
            return rule.repair_phase
    return None


def _failed_rule_ids(score: ScoreReport) -> list[str]:
    return [rule.rule_id for rule in score.rules if not rule.passed]
