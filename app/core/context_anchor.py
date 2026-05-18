from __future__ import annotations

import hashlib

from app.core.phase_registry import get_phase_definition
from app.models.contracts import GlobalAnchor, InterviewSession, PhaseId, StrictModel


class ContextAnchor(StrictModel):
    session_id: str
    phase_id: PhaseId
    goal: str
    hard_rules: list[str]
    phase_title: str
    phase_kind: str
    acceptance_criteria: dict[str, object]
    source_snapshot_hash: str

    def render(self) -> str:
        rules = "\n".join(f"- {rule}" for rule in self.hard_rules)
        return (
            f"Goal: {self.goal}\n"
            f"Phase: {self.phase_id.value} - {self.phase_title}\n"
            f"Kind: {self.phase_kind}\n"
            f"Rules:\n{rules}\n"
            f"Acceptance: {self.acceptance_criteria}"
        )


class ContextAnchorService:
    def build_anchor(
        self,
        session: InterviewSession,
        phase_id: PhaseId | None = None,
    ) -> ContextAnchor:
        resolved_phase_id = phase_id or session.current_phase
        definition = get_phase_definition(resolved_phase_id)
        anchor = session.global_anchor

        return ContextAnchor(
            session_id=session.session_id,
            phase_id=resolved_phase_id,
            goal=anchor.goal,
            hard_rules=list(anchor.hard_rules),
            phase_title=definition.title,
            phase_kind=definition.kind.value,
            acceptance_criteria=dict(definition.gate_config),
            source_snapshot_hash=_anchor_hash(anchor, resolved_phase_id),
        )


def _anchor_hash(anchor: GlobalAnchor, phase_id: PhaseId) -> str:
    payload = (
        anchor.goal
        + "\n"
        + phase_id.value
        + "\n"
        + "\n".join(anchor.hard_rules)
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

