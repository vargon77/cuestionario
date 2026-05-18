from __future__ import annotations

from app.core.orchestrator import PhaseExecution
from app.core.scoring import rule_result, run_rules
from app.models.contracts import PhaseContext, PhaseId, PhaseOutput
from app.validators.cross_validators import CROSS_VALIDATORS
from app.validators.fase17_rules import FASE17_RULES
from app.validators.fase9_rules import FASE9_RULES


def execute_fase9_validation(ctx: PhaseContext) -> PhaseExecution:
    artifacts = ctx.artifacts.dimensions_12d
    if set(artifacts) <= {"actor_seed", "objects_raw"}:
        return _execute_legacy_minimal_validation(ctx)

    score = run_rules(
        score_id="v5-completeness",
        phase_id=PhaseId.FASE_9,
        artifacts=artifacts,
        rules=FASE9_RULES,
        max_points=100,
    )
    output = PhaseOutput(
        phase_id=PhaseId.FASE_9,
        validation_findings=[
            failure for rule in score.rules for failure in rule.failures
        ],
    )
    return PhaseExecution(
        output=output,
        score=score,
        prompt=f"FASE_9 score: {score.percent}% ({score.status})",
    )


def execute_fase13_cross_validation(ctx: PhaseContext) -> PhaseExecution:
    results = [validator(ctx.artifacts.dimensions_12d) for validator in CROSS_VALIDATORS]
    findings = [failure for result in results for failure in result.failures]
    report = {
        "phase_id": PhaseId.FASE_13.value,
        "validators": [result.model_dump(mode="json") for result in results],
        "passed": all(result.passed for result in results),
        "findings": findings,
        "repair_targets": [
            result.repair_phase.value
            for result in results
            if not result.passed and result.repair_phase is not None
        ],
    }
    return PhaseExecution(
        output=PhaseOutput(
            phase_id=PhaseId.FASE_13,
            artifact_updates={
                "validation_reports": {"fase13_cross_validation": report}
            },
            validation_findings=findings,
        ),
        prompt=(
            "FASE_13 cross-validation: "
            f"{'PASS' if report['passed'] else 'NEEDS_REPAIR'}"
        ),
    )


def execute_fase17_final_validation(ctx: PhaseContext) -> PhaseExecution:
    package = ctx.artifacts.model_dump(mode="json")
    score = run_rules(
        score_id="v6-final",
        phase_id=PhaseId.FASE_17,
        artifacts=package,
        rules=FASE17_RULES,
        max_points=100,
    )
    findings = [failure for rule in score.rules for failure in rule.failures]
    report = {
        "phase_id": PhaseId.FASE_17.value,
        "score": score.model_dump(mode="json"),
        "findings": findings,
        "risk": score.risk,
        "repair_targets": [phase.value for phase in score.repair_targets],
    }
    return PhaseExecution(
        output=PhaseOutput(
            phase_id=PhaseId.FASE_17,
            artifact_updates={
                "validation_reports": {"fase17_final_validation": report}
            },
            validation_findings=findings,
        ),
        score=score,
        prompt=f"FASE_17 final score: {score.percent}% ({score.status}, risk={score.risk})",
    )


def _execute_legacy_minimal_validation(ctx: PhaseContext) -> PhaseExecution:
    artifacts = ctx.artifacts.dimensions_12d
    rules = [
        lambda _: rule_result(
            rule_id="R1",
            label="Actores",
            max_points=4,
            points=4 if "actor_seed" in artifacts else 0,
            failures=[] if "actor_seed" in artifacts else ["missing actor seed"],
            repair_phase=PhaseId.FASE_0,
            evidence_paths=["artifacts.dimensions_12d.actor_seed"],
        ),
        lambda _: rule_result(
            rule_id="R2",
            label="Objetos",
            max_points=6,
            points=6 if "objects_raw" in artifacts else 0,
            failures=[] if "objects_raw" in artifacts else ["missing objects"],
            repair_phase=PhaseId.FASE_1,
            evidence_paths=["artifacts.dimensions_12d.objects_raw"],
        ),
    ]
    score = run_rules(
        score_id="v5-completeness-minimal",
        phase_id=PhaseId.FASE_9,
        artifacts=artifacts,
        rules=rules,
        max_points=10,
    )
    return PhaseExecution(
        output=PhaseOutput(phase_id=PhaseId.FASE_9),
        score=score,
        prompt=f"FASE_9 score: {score.percent}% ({score.status})",
    )
