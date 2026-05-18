from __future__ import annotations

import os
from functools import lru_cache

from app.core.orchestrator import InterviewOrchestrator
from app.phases.default_runner import DefaultPhaseRunner
from app.storage.postgres_session_store import PostgresSessionStore
from app.storage.session_store import InMemorySessionStore, SessionStore


@lru_cache(maxsize=1)
def get_session_store() -> SessionStore:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return PostgresSessionStore(database_url)
    return InMemorySessionStore()


@lru_cache(maxsize=1)
def get_orchestrator() -> InterviewOrchestrator:
    return InterviewOrchestrator(
        store=get_session_store(),
        phase_runner=DefaultPhaseRunner(),
    )
