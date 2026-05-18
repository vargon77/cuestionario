from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies import get_orchestrator
from app.core.orchestrator import InterviewOrchestrator
from app.phases.checkpoints import parse_checkpoint_verdict
from app.storage.session_store import SessionNotFoundError


router = APIRouter(prefix="/sessions", tags=["sessions"])


class CreateSessionRequest(BaseModel):
    session_id: str


class AdvanceRequest(BaseModel):
    user_input: str | None = None


class CheckpointRequest(BaseModel):
    verdict: str


@router.post("", status_code=status.HTTP_201_CREATED)
def create_session(
    request: CreateSessionRequest,
    orchestrator: InterviewOrchestrator = Depends(get_orchestrator),
) -> dict[str, Any]:
    try:
        return orchestrator.start_session(request.session_id).model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{session_id}")
def get_session(
    session_id: str,
    orchestrator: InterviewOrchestrator = Depends(get_orchestrator),
) -> dict[str, Any]:
    try:
        session = orchestrator.store.get_session(session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="session not found") from exc
    return session.model_dump(mode="json")


@router.post("/{session_id}/advance")
def advance_session(
    session_id: str,
    request: AdvanceRequest,
    orchestrator: InterviewOrchestrator = Depends(get_orchestrator),
) -> dict[str, Any]:
    try:
        return orchestrator.advance(
            session_id,
            user_input=request.user_input,
        ).model_dump(mode="json")
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="session not found") from exc


@router.post("/{session_id}/checkpoint")
def submit_checkpoint(
    session_id: str,
    request: CheckpointRequest,
    orchestrator: InterviewOrchestrator = Depends(get_orchestrator),
) -> dict[str, Any]:
    try:
        verdict = parse_checkpoint_verdict(request.verdict)
        return orchestrator.submit_checkpoint(
            session_id,
            verdict,
        ).model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="session not found") from exc
