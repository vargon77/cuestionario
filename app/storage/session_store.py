from __future__ import annotations

from typing import Protocol

from app.models.contracts import (
    AuditEvent,
    InterviewSession,
    PhaseId,
    ScoreReport,
)


class SessionNotFoundError(KeyError):
    """Session id was not found in the state store."""


class SessionStore(Protocol):
    def create_session(self, session_id: str) -> InterviewSession: ...

    def get_session(self, session_id: str) -> InterviewSession: ...

    def save_session(self, session: InterviewSession) -> InterviewSession: ...

    def append_audit_event(
        self,
        session_id: str,
        event: AuditEvent,
    ) -> InterviewSession: ...

    def save_score(
        self,
        session_id: str,
        score_key: str,
        score: ScoreReport,
    ) -> InterviewSession: ...

    def increment_repair_attempt(
        self,
        session_id: str,
        phase_id: PhaseId,
    ) -> InterviewSession: ...


class InMemorySessionStore:
    """Development store with copy-on-read/write semantics.

    This mimics a durable store boundary: callers must explicitly save changes
    instead of relying on shared object references.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, InterviewSession] = {}

    def create_session(self, session_id: str) -> InterviewSession:
        if session_id in self._sessions:
            raise ValueError(f"session already exists: {session_id}")
        session = InterviewSession(session_id=session_id)
        self._sessions[session_id] = _copy_session(session)
        return _copy_session(session)

    def get_session(self, session_id: str) -> InterviewSession:
        session = self._sessions.get(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)
        return _copy_session(session)

    def save_session(self, session: InterviewSession) -> InterviewSession:
        self._sessions[session.session_id] = _copy_session(session)
        return self.get_session(session.session_id)

    def append_audit_event(
        self,
        session_id: str,
        event: AuditEvent,
    ) -> InterviewSession:
        session = self.get_session(session_id)
        session.audit_log.append(event)
        return self.save_session(session)

    def save_score(
        self,
        session_id: str,
        score_key: str,
        score: ScoreReport,
    ) -> InterviewSession:
        session = self.get_session(session_id)
        session.scores[score_key] = score
        return self.save_session(session)

    def increment_repair_attempt(
        self,
        session_id: str,
        phase_id: PhaseId,
    ) -> InterviewSession:
        session = self.get_session(session_id)
        session.repair_attempts.increment(phase_id)
        return self.save_session(session)


def _copy_session(session: InterviewSession) -> InterviewSession:
    return session.model_copy(deep=True)

