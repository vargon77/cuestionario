from __future__ import annotations

import hashlib
import json
from typing import Protocol

from app.core.context_anchor import ContextAnchorService
from app.core.gates import evaluate_checkpoint_gate, evaluate_gate
from app.core.phase_registry import get_phase_definition
from app.models.contracts import (
    AuditEvent,
    CheckpointVerdict,
    GateResult,
    GateStatus,
    InterviewSession,
    PhaseContext,
    PhaseId,
    PhaseOutput,
    ScoreReport,
    StrictModel,
    SystemGraph,
    TraceabilityGraph,
    TurnResult,
)
from app.phases.checkpoints import checkpoint_state_value
from app.storage.session_store import InMemorySessionStore, SessionStore


class PhaseExecution(StrictModel):
    output: PhaseOutput
    score: ScoreReport | None = None
    prompt: str | None = None


class PhaseRunner(Protocol):
    def execute(self, ctx: PhaseContext) -> PhaseExecution: ...


class StubPhaseRunner:
    """Safe placeholder until concrete phase modules exist."""

    def execute(self, ctx: PhaseContext) -> PhaseExecution:
        return PhaseExecution(
            output=PhaseOutput(
                phase_id=ctx.phase_id,
                questions_asked=[
                    f"{ctx.phase_id.value} is not implemented yet."
                ],
            ),
            prompt=f"{ctx.phase_id.value} is not implemented yet.",
        )


class InterviewOrchestrator:
    def __init__(
        self,
        *,
        store: SessionStore | None = None,
        phase_runner: PhaseRunner | None = None,
        anchor_service: ContextAnchorService | None = None,
    ) -> None:
        self.store = store or InMemorySessionStore()
        self.phase_runner = phase_runner or StubPhaseRunner()
        self.anchor_service = anchor_service or ContextAnchorService()

    def start_session(self, session_id: str) -> TurnResult:
        session = self.store.create_session(session_id)
        anchor = self.anchor_service.build_anchor(session)
        return TurnResult(
            session_id=session.session_id,
            current_phase=session.current_phase,
            prompt=anchor.render(),
            artifacts_summary=_artifact_summary(session),
        )

    def advance(
        self,
        session_id: str,
        user_input: str | None = None,
    ) -> TurnResult:
        session = self.store.get_session(session_id)
        phase_id = session.current_phase
        definition = get_phase_definition(phase_id)

        preflight_gate = _preflight_gate(session, phase_id)
        if preflight_gate is not None:
            if preflight_gate.next_phase is not None:
                session.current_phase = preflight_gate.next_phase
            session.audit_log.append(
                AuditEvent(
                    phase_id=phase_id,
                    input_hash=_hash_payload(user_input or ""),
                    output_hash=_hash_payload(preflight_gate),
                    gate_result=preflight_gate.status,
                )
            )
            saved = self.store.save_session(session)
            return TurnResult(
                session_id=saved.session_id,
                current_phase=phase_id,
                next_phase=preflight_gate.next_phase,
                prompt="SEC generation blocked by validation gate.",
                artifacts_summary=_artifact_summary(saved),
                gate=preflight_gate,
                blocked=True,
            )

        if definition.requires_human_confirmation:
            anchor = self.anchor_service.build_anchor(session, phase_id)
            return TurnResult(
                session_id=session.session_id,
                current_phase=phase_id,
                prompt=anchor.render(),
                artifacts_summary=_artifact_summary(session),
                gate=GateResult(status=GateStatus.NEEDS_HUMAN, next_phase=phase_id),
                blocked=True,
            )

        ctx = PhaseContext(
            session_id=session.session_id,
            phase_id=phase_id,
            anchor=session.global_anchor,
            artifacts=session.artifacts,
            scores=session.scores,
            user_input=user_input,
        )
        execution = self.phase_runner.execute(ctx)
        _ensure_phase_output_matches(phase_id, execution.output)

        attempts_made = session.repair_attempts.attempts_for(phase_id)
        gate = evaluate_gate(
            phase_id=phase_id,
            output=execution.output,
            score=execution.score,
            repair_attempts_made=attempts_made,
        )

        self._apply_execution(session, execution, gate, user_input=user_input)
        saved = self.store.save_session(session)

        return TurnResult(
            session_id=saved.session_id,
            current_phase=phase_id,
            next_phase=gate.next_phase,
            prompt=execution.prompt,
            artifacts_summary=_artifact_summary(saved),
            gate=gate,
            blocked=gate.status in {GateStatus.FAIL, GateStatus.FAIL_HARD},
        )

    def submit_checkpoint(
        self,
        session_id: str,
        verdict: CheckpointVerdict,
    ) -> TurnResult:
        session = self.store.get_session(session_id)
        phase_id = session.current_phase
        gate = evaluate_checkpoint_gate(phase_id=phase_id, verdict=verdict)
        _apply_checkpoint_state(session, phase_id, verdict)

        if gate.next_phase is not None:
            session.current_phase = gate.next_phase
        session.audit_log.append(
            AuditEvent(
                phase_id=phase_id,
                input_hash=_hash_payload(verdict.value),
                output_hash=_hash_payload(gate),
                gate_result=gate.status,
            )
        )
        saved = self.store.save_session(session)

        return TurnResult(
            session_id=saved.session_id,
            current_phase=phase_id,
            next_phase=gate.next_phase,
            artifacts_summary=_artifact_summary(saved),
            gate=gate,
            blocked=gate.status in {GateStatus.FAIL, GateStatus.NEEDS_REPAIR},
        )

    def _apply_execution(
        self,
        session: InterviewSession,
        execution: PhaseExecution,
        gate: GateResult,
        *,
        user_input: str | None,
    ) -> None:
        phase_id = session.current_phase
        _apply_artifact_updates(session, execution.output)

        if execution.score is not None:
            session.scores[_score_key(execution.score.phase_id)] = execution.score

        if phase_id == PhaseId.FASE_9 and gate.status == GateStatus.NEEDS_REPAIR:
            session.repair_attempts.increment(PhaseId.FASE_9)

        if gate.next_phase is not None:
            session.current_phase = gate.next_phase

        session.audit_log.append(
            AuditEvent(
                phase_id=phase_id,
                input_hash=_hash_payload(user_input or ""),
                output_hash=_hash_payload(execution.output),
                gate_result=gate.status,
            )
        )


def _ensure_phase_output_matches(phase_id: PhaseId, output: PhaseOutput) -> None:
    if output.phase_id != phase_id:
        raise ValueError(
            f"phase runner returned {output.phase_id.value} while current phase is "
            f"{phase_id.value}"
        )


def _apply_artifact_updates(
    session: InterviewSession,
    output: PhaseOutput,
) -> None:
    if not output.artifact_updates:
        return

    if "dimensions_12d" in output.artifact_updates:
        session.artifacts.dimensions_12d.update(output.artifact_updates["dimensions_12d"])
    if "sec_initial" in output.artifact_updates:
        session.artifacts.sec_initial = output.artifact_updates["sec_initial"]
    if "system_graph" in output.artifact_updates:
        session.artifacts.system_graph = SystemGraph.model_validate(
            output.artifact_updates["system_graph"]
        )
    if "traceability_graph" in output.artifact_updates:
        session.artifacts.traceability_graph = TraceabilityGraph.model_validate(
            output.artifact_updates["traceability_graph"]
        )
    if "sec_extended" in output.artifact_updates:
        session.artifacts.sec_extended = output.artifact_updates["sec_extended"]
    if "validation_reports" in output.artifact_updates:
        session.artifacts.validation_reports.update(
            output.artifact_updates["validation_reports"]
        )
    if output.estimations:
        session.artifacts.estimations.entries.extend(output.estimations)


def _apply_checkpoint_state(
    session: InterviewSession,
    phase_id: PhaseId,
    verdict: CheckpointVerdict,
) -> None:
    state_value = checkpoint_state_value(verdict)
    if phase_id == PhaseId.FASE_11:
        if state_value == "revalidate":
            return
        session.checkpoints.phase_11 = state_value
    if phase_id == PhaseId.FASE_18:
        session.checkpoints.phase_18 = state_value


def _score_key(phase_id: PhaseId) -> str:
    if phase_id == PhaseId.FASE_9:
        return "v5_completeness"
    if phase_id == PhaseId.FASE_17:
        return "v6_final"
    return phase_id.value.lower()


def _preflight_gate(
    session: InterviewSession,
    phase_id: PhaseId,
) -> GateResult | None:
    if phase_id != PhaseId.FASE_10:
        return None

    score = session.scores.get("v5_completeness")
    if score is None:
        return GateResult(
            status=GateStatus.FAIL,
            errors=["FASE_9 score is required before SEC generation"],
            repair_phase=PhaseId.FASE_9,
            blocking_rules=["NO_SEC_WITHOUT_FASE_9_SCORE"],
            next_phase=PhaseId.FASE_9,
        )

    if score.percent >= 70:
        return None

    repair_phase = (
        score.repair_targets[0]
        if score.repair_targets
        else _first_failed_repair_phase(score) or PhaseId.FASE_1
    )
    return GateResult(
        status=GateStatus.FAIL,
        score=score,
        errors=["SEC generation requires validation score >= 70"],
        repair_phase=repair_phase,
        blocking_rules=[rule.rule_id for rule in score.rules if not rule.passed]
        or ["NO_SEC_UNDER_70"],
        next_phase=repair_phase,
    )


def _first_failed_repair_phase(score: ScoreReport) -> PhaseId | None:
    for rule in score.rules:
        if not rule.passed and rule.repair_phase is not None:
            return rule.repair_phase
    return None


def _artifact_summary(session: InterviewSession) -> dict[str, object]:
    return {
        "dimensions_12d_keys": sorted(session.artifacts.dimensions_12d.keys()),
        "has_sec_initial": session.artifacts.sec_initial is not None,
        "has_system_graph": session.artifacts.system_graph is not None,
        "has_traceability_graph": session.artifacts.traceability_graph is not None,
        "has_sec_extended": session.artifacts.sec_extended is not None,
        "scores": sorted(session.scores.keys()),
        "audit_events": len(session.audit_log),
    }


def _hash_payload(payload: object) -> str:
    if isinstance(payload, StrictModel):
        data = payload.model_dump(mode="json")
    else:
        data = payload
    encoded = json.dumps(data, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
