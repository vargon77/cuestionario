from __future__ import annotations

from app.models.contracts import PhaseDefinition, PhaseId, PhaseKind


PHASE_SEQUENCE: tuple[PhaseId, ...] = (
    PhaseId.FASE_0,
    PhaseId.FASE_1,
    PhaseId.FASE_2,
    PhaseId.FASE_3,
    PhaseId.FASE_3B,
    PhaseId.FASE_4,
    PhaseId.FASE_5,
    PhaseId.FASE_6,
    PhaseId.FASE_7,
    PhaseId.FASE_7B,
    PhaseId.FASE_7C,
    PhaseId.FASE_8,
    PhaseId.FASE_8B,
    PhaseId.FASE_9,
    PhaseId.FASE_10,
    PhaseId.FASE_11,
    PhaseId.FASE_12,
    PhaseId.FASE_13,
    PhaseId.FASE_14,
    PhaseId.FASE_15,
    PhaseId.FASE_16,
    PhaseId.FASE_17,
    PhaseId.FASE_18,
)


def _next_phase(phase_id: PhaseId) -> PhaseId | None:
    index = PHASE_SEQUENCE.index(phase_id)
    if index == len(PHASE_SEQUENCE) - 1:
        return None
    return PHASE_SEQUENCE[index + 1]


def _definition(
    phase_id: PhaseId,
    title: str,
    kind: PhaseKind,
    input_schema: str,
    output_schema: str,
    *,
    requires_human_confirmation: bool = False,
    gate_config: dict[str, object] | None = None,
) -> PhaseDefinition:
    return PhaseDefinition(
        id=phase_id,
        title=title,
        kind=kind,
        input_schema=input_schema,
        output_schema=output_schema,
        requires_human_confirmation=requires_human_confirmation,
        next_phase=_next_phase(phase_id),
        gate_config=gate_config or {},
    )


PHASE_DEFINITIONS: dict[PhaseId, PhaseDefinition] = {
    PhaseId.FASE_0: _definition(
        PhaseId.FASE_0,
        "Actor seed and opening prompt",
        PhaseKind.CAPTURE,
        "EmptySessionGoal",
        "ActorSeedOutput",
    ),
    PhaseId.FASE_1: _definition(
        PhaseId.FASE_1,
        "Objects table",
        PhaseKind.CAPTURE,
        "ActorSeedOutput",
        "ObjectsTableOutput",
        gate_config={"min_objects": 3, "max_objects": 10},
    ),
    PhaseId.FASE_2: _definition(
        PhaseId.FASE_2,
        "Operations table",
        PhaseKind.CAPTURE,
        "ObjectsTableOutput",
        "OperationsTableOutput",
    ),
    PhaseId.FASE_3: _definition(
        PhaseId.FASE_3,
        "State transitions",
        PhaseKind.CAPTURE,
        "OperationsTableOutput",
        "StateTransitionOutput",
        gate_config={"min_states": 3},
    ),
    PhaseId.FASE_3B: _definition(
        PhaseId.FASE_3B,
        "Relations table",
        PhaseKind.CAPTURE,
        "ObjectsActorsOutput",
        "RelationsTableOutput",
    ),
    PhaseId.FASE_4: _definition(
        PhaseId.FASE_4,
        "Domain no-go rules",
        PhaseKind.CAPTURE,
        "PartialModelOutput",
        "NoGoRulesOutput",
        gate_config={"min_rules": 5},
    ),
    PhaseId.FASE_5: _definition(
        PhaseId.FASE_5,
        "External events",
        PhaseKind.CAPTURE,
        "RulesOperationsOutput",
        "ExternalEventsOutput",
    ),
    PhaseId.FASE_6: _definition(
        PhaseId.FASE_6,
        "Time model",
        PhaseKind.CAPTURE,
        "OperationsEventsOutput",
        "TimeModelOutput",
    ),
    PhaseId.FASE_7: _definition(
        PhaseId.FASE_7,
        "Resource model",
        PhaseKind.CAPTURE,
        "OperationsTimeOutput",
        "ResourceModelOutput",
    ),
    PhaseId.FASE_7B: _definition(
        PhaseId.FASE_7B,
        "Space model",
        PhaseKind.CAPTURE,
        "ResourceModelOutput",
        "SpaceModelOutput",
    ),
    PhaseId.FASE_7C: _definition(
        PhaseId.FASE_7C,
        "Communication model",
        PhaseKind.CAPTURE,
        "ComponentsOutput",
        "CommunicationModelOutput",
    ),
    PhaseId.FASE_8: _definition(
        PhaseId.FASE_8,
        "Initial module inference",
        PhaseKind.INFERENCE,
        "Partial12DModelDims1To11",
        "ExplicitModuleQuestionsOutput",
    ),
    PhaseId.FASE_8B: _definition(
        PhaseId.FASE_8B,
        "Objective model",
        PhaseKind.CAPTURE,
        "FullModelOutput",
        "ObjectiveModelOutput",
    ),
    PhaseId.FASE_9: _definition(
        PhaseId.FASE_9,
        "V5 completeness scoring",
        PhaseKind.VALIDATION,
        "ExtractedModelOutput",
        "ScoreReport",
        gate_config={
            "pass_score": 85,
            "reserve_min_score": 70,
            "reserve_max_retries": 3,
            "fail_repair_phase": PhaseId.FASE_1.value,
        },
    ),
    PhaseId.FASE_10: _definition(
        PhaseId.FASE_10,
        "Initial SEC generation",
        PhaseKind.GENERATION,
        "V5ScoreAndModel",
        "InitialSEC",
    ),
    PhaseId.FASE_11: _definition(
        PhaseId.FASE_11,
        "Human checkpoint 1",
        PhaseKind.CHECKPOINT,
        "InitialSEC",
        "CheckpointState",
        requires_human_confirmation=True,
        gate_config={"allowed_verdicts": ["SI", "NO_CAMBIAR", "INCOMPLETO"]},
    ),
    PhaseId.FASE_12: _definition(
        PhaseId.FASE_12,
        "Systemic inference",
        PhaseKind.INFERENCE,
        "ApprovedSEC",
        "V6InfrastructureModuleProposals",
        gate_config={"no_duplicate_phase": PhaseId.FASE_8.value},
    ),
    PhaseId.FASE_13: _definition(
        PhaseId.FASE_13,
        "Cross-validation panel",
        PhaseKind.VALIDATION,
        "Model12DAndModules",
        "CrossValidationReport",
        gate_config={"validators": 15},
    ),
    PhaseId.FASE_14: _definition(
        PhaseId.FASE_14,
        "SYSTEM_GRAPH generation",
        PhaseKind.GRAPH,
        "Model12DAndReport",
        "SystemGraph",
        gate_config={"no_orphan_nodes": True},
    ),
    PhaseId.FASE_15: _definition(
        PhaseId.FASE_15,
        "TRACEABILITY_GRAPH generation",
        PhaseKind.GRAPH,
        "SECAndSystemGraph",
        "TraceabilityGraph",
    ),
    PhaseId.FASE_16: _definition(
        PhaseId.FASE_16,
        "Extended SEC generation",
        PhaseKind.GENERATION,
        "AllArtifacts",
        "ExtendedSEC20Sections",
    ),
    PhaseId.FASE_17: _definition(
        PhaseId.FASE_17,
        "Final validation panel",
        PhaseKind.VALIDATION,
        "FullPackage",
        "FinalScoreReport",
        gate_config={"minimum_score": 70},
    ),
    PhaseId.FASE_18: _definition(
        PhaseId.FASE_18,
        "Human checkpoint 2",
        PhaseKind.CHECKPOINT,
        "FullPackage",
        "FinalHumanApproval",
        requires_human_confirmation=True,
        gate_config={
            "allowed_verdicts": [
                "SI",
                "NO_CAMBIAR",
                "INCOMPLETO",
                "REVALIDAR",
            ]
        },
    ),
}


DETERMINISTIC_PHASE_KINDS = frozenset(
    {
        PhaseKind.VALIDATION,
        PhaseKind.GENERATION,
        PhaseKind.GRAPH,
        PhaseKind.CHECKPOINT,
    }
)


def get_phase_definition(phase_id: PhaseId) -> PhaseDefinition:
    return PHASE_DEFINITIONS[phase_id]


def is_deterministic_phase(phase_id: PhaseId) -> bool:
    return PHASE_DEFINITIONS[phase_id].kind in DETERMINISTIC_PHASE_KINDS

