from __future__ import annotations

from typing import Any

from app.models.contracts import AuditEvent, InterviewSession, PhaseId, ScoreReport
from app.storage.session_store import SessionNotFoundError


class PostgresSessionStore:
    """PostgreSQL JSONB implementation of the SessionStore protocol.

    The import of SQLAlchemy is intentionally delayed so the rest of the
    project remains testable before database dependencies are installed.
    """

    def __init__(self, database_url: str) -> None:
        try:
            from sqlalchemy import create_engine
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "PostgresSessionStore requires sqlalchemy and psycopg. "
                "Install project dependencies before using PostgreSQL storage."
            ) from exc

        self._engine = create_engine(database_url, future=True)
        self.create_schema()

    def create_schema(self) -> None:
        from sqlalchemy import text

        ddl = """
        CREATE TABLE IF NOT EXISTS interview_sessions (
            session_id TEXT PRIMARY KEY,
            payload JSONB NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
        with self._engine.begin() as conn:
            conn.execute(text(ddl))

    def create_session(self, session_id: str) -> InterviewSession:
        from sqlalchemy import text

        session = InterviewSession(session_id=session_id)
        payload = _dump_session(session)
        with self._engine.begin() as conn:
            existing = conn.execute(
                text("SELECT 1 FROM interview_sessions WHERE session_id = :id"),
                {"id": session_id},
            ).first()
            if existing:
                raise ValueError(f"session already exists: {session_id}")
            conn.execute(
                text(
                    """
                    INSERT INTO interview_sessions (session_id, payload)
                    VALUES (:id, CAST(:payload AS jsonb))
                    """
                ),
                {"id": session_id, "payload": payload},
            )
        return self.get_session(session_id)

    def get_session(self, session_id: str) -> InterviewSession:
        from sqlalchemy import text

        with self._engine.begin() as conn:
            row = conn.execute(
                text("SELECT payload FROM interview_sessions WHERE session_id = :id"),
                {"id": session_id},
            ).mappings().first()
        if row is None:
            raise SessionNotFoundError(session_id)
        return InterviewSession.model_validate(row["payload"])

    def save_session(self, session: InterviewSession) -> InterviewSession:
        from sqlalchemy import text

        payload = _dump_session(session)
        with self._engine.begin() as conn:
            result = conn.execute(
                text(
                    """
                    UPDATE interview_sessions
                    SET payload = CAST(:payload AS jsonb), updated_at = now()
                    WHERE session_id = :id
                    """
                ),
                {"id": session.session_id, "payload": payload},
            )
        if result.rowcount == 0:
            raise SessionNotFoundError(session.session_id)
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


def _dump_session(session: InterviewSession) -> str:
    return session.model_dump_json()

