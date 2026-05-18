from __future__ import annotations

from app.core.orchestrator import PhaseExecution
from app.phases.capture import CAPTURE_SPECS, execute_capture_phase
from app.phases.generation import (
    execute_extended_sec_generation,
    execute_initial_sec_generation,
)
from app.phases.graphs import (
    execute_system_graph_generation,
    execute_traceability_graph_generation,
)
from app.phases.inference import execute_fase8_inference, execute_fase12_systemic_inference
from app.phases.validation_panel import (
    execute_fase13_cross_validation,
    execute_fase17_final_validation,
    execute_fase9_validation,
)
from app.models.contracts import PhaseContext, PhaseId, PhaseOutput


class DefaultPhaseRunner:
    """Minimal deterministic runner for the first executable vertical slice.

    It deliberately avoids LLM calls. Capture phases persist raw structured
    placeholders; validation and generation phases remain deterministic.
    """

    def execute(self, ctx: PhaseContext) -> PhaseExecution:
        if ctx.phase_id in CAPTURE_SPECS:
            return execute_capture_phase(ctx)
        if ctx.phase_id == PhaseId.FASE_8:
            return execute_fase8_inference(ctx)
        if ctx.phase_id == PhaseId.FASE_12:
            return execute_fase12_systemic_inference(ctx)
        if ctx.phase_id == PhaseId.FASE_13:
            return execute_fase13_cross_validation(ctx)
        if ctx.phase_id == PhaseId.FASE_9:
            return execute_fase9_validation(ctx)
        if ctx.phase_id == PhaseId.FASE_10:
            return execute_initial_sec_generation(ctx)
        if ctx.phase_id == PhaseId.FASE_14:
            return execute_system_graph_generation(ctx)
        if ctx.phase_id == PhaseId.FASE_15:
            return execute_traceability_graph_generation(ctx)
        if ctx.phase_id == PhaseId.FASE_16:
            return execute_extended_sec_generation(ctx)
        if ctx.phase_id == PhaseId.FASE_17:
            return execute_fase17_final_validation(ctx)
        return _not_implemented(ctx)


def _not_implemented(ctx: PhaseContext) -> PhaseExecution:
    return PhaseExecution(
        output=PhaseOutput(
            phase_id=ctx.phase_id,
            questions_asked=[f"{ctx.phase_id.value} pendiente de implementacion."],
        ),
        prompt=f"{ctx.phase_id.value} pendiente de implementacion.",
    )
