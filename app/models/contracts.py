from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, computed_field


CONSTRAINTS_HASH_FORMULA = "sha256(CONSTRAINTS_SECTION + ESTIMATIONS_SECTION)"
ORPHAN_CHECK_RULE = (
    "toda operacion debe conectar a actor+objeto+estado+regla+recurso+objetivo"
)
DEFAULT_HARD_RULES = [
    "no colloquial questions",
    "no open questions without structure",
    "no advance without explicit human confirmation where required",
    "no SEC under 70",
    "no percentages in acceptance rules",
    "no numbers without units",
    "no orphan graph nodes",
    "NO_SE -> use pattern default from defaults_repository; INCIERTO -> use maximum safe value; APROXIMADO -> use provided value; always document in ESTIMATIONS",
    "show full dimension table before asking for answers (MAPA VISIBLE)",
    "no implicit module approval; every module requires explicit ACEPTADO/FUTURO/EXCLUSION",
    "every number must have unit; every operation must have actor; every state must have transition",
    "every entity must trace to objective + operation + rule + actor",
    "every operation must have actor + state change + rules + resources + space + time",
    "every state transition must have trigger + origin + destination + validation + rollback",
    "every communication must have protocol + timeout + failure strategy + security",
    "every objective must be observable + verifiable and must affect operations/resources/decisions",
    "every limited resource must have max + degradation + fallback + monitoring",
    "every event must have origin + action + priority + error behavior",
    "every relation must have cardinality + ownership + consistency + propagation",
]


T = TypeVar("T", bound=BaseModel)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class PhaseId(str, Enum):
    FASE_0 = "FASE_0"
    FASE_1 = "FASE_1"
    FASE_2 = "FASE_2"
    FASE_3 = "FASE_3"
    FASE_3B = "FASE_3B"
    FASE_4 = "FASE_4"
    FASE_5 = "FASE_5"
    FASE_6 = "FASE_6"
    FASE_7 = "FASE_7"
    FASE_7B = "FASE_7B"
    FASE_7C = "FASE_7C"
    FASE_8 = "FASE_8"
    FASE_8B = "FASE_8B"
    FASE_9 = "FASE_9"
    FASE_10 = "FASE_10"
    FASE_11 = "FASE_11"
    FASE_12 = "FASE_12"
    FASE_13 = "FASE_13"
    FASE_14 = "FASE_14"
    FASE_15 = "FASE_15"
    FASE_16 = "FASE_16"
    FASE_17 = "FASE_17"
    FASE_18 = "FASE_18"


class PhaseKind(str, Enum):
    CAPTURE = "CAPTURE"
    INFERENCE = "INFERENCE"
    VALIDATION = "VALIDATION"
    GENERATION = "GENERATION"
    GRAPH = "GRAPH"
    CHECKPOINT = "CHECKPOINT"


class GateStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    FAIL_HARD = "FAIL_HARD"
    NEEDS_REPAIR = "NEEDS_REPAIR"
    NEEDS_HUMAN = "NEEDS_HUMAN"


class CheckpointVerdict(str, Enum):
    APPROVED = "SI"
    CHANGE_REQUESTED = "NO_CAMBIAR"
    INCOMPLETE = "INCOMPLETO"
    REVALIDATE = "REVALIDAR"


class PhaseDefinition(StrictModel):
    id: PhaseId
    title: str
    kind: PhaseKind
    input_schema: str
    output_schema: str
    requires_human_confirmation: bool = False
    next_phase: PhaseId | None = None
    gate_config: dict[str, Any] = Field(default_factory=dict)


class RuleResult(StrictModel):
    rule_id: str
    label: str
    max_points: int = Field(ge=0)
    points: int = Field(ge=0)
    passed: bool
    failures: list[str] = Field(default_factory=list)
    repair_phase: PhaseId | None = None
    evidence_paths: list[str] = Field(default_factory=list)


class ScoreReport(StrictModel):
    score_id: str
    phase_id: PhaseId
    total_points: int = Field(ge=0)
    max_points: int = Field(default=100, gt=0)
    status: str
    risk: str | None = None
    rules: list[RuleResult] = Field(default_factory=list)
    repair_targets: list[PhaseId] = Field(default_factory=list)

    @computed_field
    @property
    def percent(self) -> int:
        return round((self.total_points / self.max_points) * 100)


class EstimationType(str, Enum):
    CONFIRMADO = "CONFIRMADO"
    RANGO_ESTIMADO = "RANGO_ESTIMADO"
    DESCONOCIDO = "DESCONOCIDO"
    POR_DEFECTO = "POR_DEFECTO"


class EstimationSource(str, Enum):
    HUMANO_EXACTO = "humano_exacto"
    HUMANO_ESTIMADO = "humano_estimado"
    HUMANO_DESCONOCIDO = "humano_desconocido"
    ESTANDAR_PROYECTOS = "estandar_proyectos"


class EstimationStatus(str, Enum):
    ACTIVA = "ACTIVA"
    REFINADA = "REFINADA"
    DESCARTADA = "DESCARTADA"
    OBSOLETA = "OBSOLETA"


class EstimationRange(StrictModel):
    min: Any
    max: Any


class EstimationEntry(StrictModel):
    id: str
    campo: str
    tipo: EstimationType
    valor_usado: Any
    rango: EstimationRange | None = None
    confianza: float = Field(ge=0.0, le=1.0)
    fuente: EstimationSource
    mitigation: str
    requiere_revision: bool
    revision_deadline: datetime | None = None
    estado: EstimationStatus


class EstimationsSection(StrictModel):
    entries: list[EstimationEntry] = Field(default_factory=list)


class DecisionRecord(StrictModel):
    id: str
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    agent: Literal["ENTREVISTADOR"] = "ENTREVISTADOR"
    decision: str
    rationale: str
    overrides: list[str] = Field(default_factory=list)
    status: Literal["LOCKED"] = "LOCKED"


class SECState(StrictModel):
    global_state: Literal["UNKNOWN"] = "UNKNOWN"
    per_scope_states: dict[str, Literal["UNKNOWN"]] = Field(default_factory=dict)


SEC_SECTION_NAMES = (
    "METADATA",
    "PROBLEM",
    "OUTCOME",
    "CONSTRAINTS",
    "ESTIMATIONS",
    "SYSTEM_LOGIC",
    "SYSTEM_GRAPH",
    "TRACEABILITY_GRAPH",
    "SCOPES",
    "RISKS",
    "EXCLUSIONS",
    "ACCEPTANCE_RULES",
    "DECISION_RECORD",
    "STATE",
    "OBSERVABILITY",
    "FAILURE_STRATEGIES",
    "DEPLOYMENT_TOPOLOGY",
    "SECURITY_MODEL",
    "PERFORMANCE_MODEL",
    "GOVERNANCE_MODEL",
)


class SECMetadata(StrictModel):
    sec_id: str
    version: int = Field(ge=1)
    timestamp: datetime
    entrevistador: Literal["V6 - ARQUITECTURA UNIVERSAL INTEGRADA"] = (
        "V6 - ARQUITECTURA UNIVERSAL INTEGRADA"
    )
    tipo_sistema: str
    validation_score: int = Field(ge=0, le=100)
    estado: str
    constraints_hash: str
    sec_hash: str | None = None


class SECDocument(StrictModel):
    metadata: SECMetadata
    sections: dict[str, Any]
    required_sections: tuple[str, ...] = SEC_SECTION_NAMES

    @computed_field
    @property
    def complete(self) -> bool:
        return all(section in self.sections for section in self.required_sections)


class Criticality(str, Enum):
    CRITICA = "CRITICA"
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"


class Consistency(str, Enum):
    FUERTE = "FUERTE"
    EVENTUAL = "EVENTUAL"


class NodeType(str, Enum):
    ACTOR = "ACTOR"
    OBJETO = "OBJETO"
    OPERACION = "OPERACION"
    EVENTO = "EVENTO"
    ESTADO = "ESTADO"
    REGLA = "REGLA"
    RECURSO = "RECURSO"
    OBJETIVO = "OBJETIVO"
    ESPACIO = "ESPACIO"
    CANAL = "CANAL"


class EdgeType(str, Enum):
    EJECUTA = "ejecuta"
    MODIFICA = "modifica"
    DISPARA = "dispara"
    RESTRINGE = "restringe"
    CONSUME = "consume"
    COMUNICA = "comunica"
    DEPENDE = "depende"
    OPTIMIZA = "optimiza"
    REPLICA = "replica"
    MONITOREA = "monitorea"


class GraphNode(StrictModel):
    id: str
    tipo: NodeType
    criticidad: Criticality
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(StrictModel):
    source: str
    target: str
    tipo: EdgeType
    criticidad: Criticality
    consistencia: Consistency


class SystemGraph(StrictModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class TraceabilityType(str, Enum):
    FUNCIONAL = "funcional"
    TEMPORAL = "temporal"
    OPERACIONAL = "operacional"
    SEGURIDAD = "seguridad"
    INFRAESTRUCTURA = "infraestructura"
    NEGOCIO = "negocio"


class TraceabilityLevel(str, Enum):
    OBJETIVO = "objetivo"
    SCOPE = "scope"
    OPERACION = "operacion"
    ESTADO = "estado"
    REGLA = "regla"
    RECURSO = "recurso"


class TraceabilityNode(StrictModel):
    id: str
    nivel: TraceabilityLevel
    tipo: TraceabilityType
    refs: list[str] = Field(default_factory=list)


class TraceabilityMatrixRow(StrictModel):
    objetivo: str
    scope: str
    operacion: str
    recurso: str
    kpi: str


class TraceabilityMatrix(StrictModel):
    rows: list[TraceabilityMatrixRow] = Field(default_factory=list)


class TraceabilityGraph(StrictModel):
    hierarchy: list[TraceabilityNode] = Field(default_factory=list)
    matrix: TraceabilityMatrix = Field(default_factory=TraceabilityMatrix)
    traceability_type: TraceabilityType


class ArtifactBundle(StrictModel):
    dimensions_12d: dict[str, Any] = Field(default_factory=dict)
    sec_initial: dict[str, Any] | None = None
    system_graph: SystemGraph | None = None
    traceability_graph: TraceabilityGraph | None = None
    sec_extended: dict[str, Any] | None = None
    validation_reports: dict[str, Any] = Field(default_factory=dict)
    estimations: EstimationsSection = Field(default_factory=EstimationsSection)
    decision_records: list[DecisionRecord] = Field(default_factory=list)
    sec_state: SECState = Field(default_factory=SECState)


class LLMCallAudit(StrictModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    phase_id: PhaseId
    prompt_hash: str
    response_hash: str
    response_model: str
    status: str


class LLMState(StrictModel):
    provider: str = "fake"
    calls: list[LLMCallAudit] = Field(default_factory=list)


class CheckpointState(StrictModel):
    phase_11: Literal["pending", "approved", "change_requested", "incomplete"] = (
        "pending"
    )
    phase_18: Literal[
        "pending",
        "approved",
        "change_requested",
        "incomplete",
        "revalidate",
    ] = "pending"


class RepairAttemptState(StrictModel):
    attempts_by_phase: dict[PhaseId, int] = Field(default_factory=dict)

    def attempts_for(self, phase_id: PhaseId) -> int:
        return self.attempts_by_phase.get(phase_id, 0)

    def increment(self, phase_id: PhaseId) -> int:
        next_value = self.attempts_for(phase_id) + 1
        self.attempts_by_phase[phase_id] = next_value
        return next_value


class AuditEvent(StrictModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    phase_id: PhaseId
    input_hash: str
    output_hash: str
    gate_result: GateStatus


class GlobalAnchor(StrictModel):
    goal: str = "Convert vague request into SEC + graphs"
    hard_rules: list[str] = Field(default_factory=lambda: list(DEFAULT_HARD_RULES))


class InterviewSession(StrictModel):
    session_id: str
    current_phase: PhaseId = PhaseId.FASE_0
    global_anchor: GlobalAnchor = Field(default_factory=GlobalAnchor)
    artifacts: ArtifactBundle = Field(default_factory=ArtifactBundle)
    scores: dict[str, ScoreReport] = Field(default_factory=dict)
    llm: LLMState = Field(default_factory=LLMState)
    checkpoints: CheckpointState = Field(default_factory=CheckpointState)
    repair_attempts: RepairAttemptState = Field(default_factory=RepairAttemptState)
    audit_log: list[AuditEvent] = Field(default_factory=list)


class PromptEnvelope(StrictModel):
    system_anchor: str
    phase_contract: str
    user_input: str
    artifacts_summary: dict[str, Any] = Field(default_factory=dict)
    response_schema_name: str


class LLMPolicy(StrictModel):
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    timeout_seconds: int = Field(default=30, gt=0)
    max_malformed_retries: int = Field(default=2, ge=0)
    allow_free_text: bool = False
    refusal_behavior: Literal["ASK_REPAIR", "BLOCK", "FALLBACK_DEFAULT"] = (
        "ASK_REPAIR"
    )


class LLMResult(StrictModel, Generic[T]):
    value: T | None = None
    refusal: str | None = None
    error: str | None = None

    @computed_field
    @property
    def ok(self) -> bool:
        return self.value is not None and self.refusal is None and self.error is None


class PhaseContext(StrictModel):
    session_id: str
    phase_id: PhaseId
    anchor: GlobalAnchor
    artifacts: ArtifactBundle
    scores: dict[str, ScoreReport] = Field(default_factory=dict)
    user_input: str | None = None


class PhaseOutput(StrictModel):
    phase_id: PhaseId
    artifact_updates: dict[str, Any] = Field(default_factory=dict)
    questions_asked: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    estimations: list[EstimationEntry] = Field(default_factory=list)
    explicit_approvals: list[str] = Field(default_factory=list)
    validation_findings: list[str] = Field(default_factory=list)
    next_phase_hint: PhaseId | None = None


class GateResult(StrictModel):
    status: GateStatus
    score: ScoreReport | None = None
    errors: list[str] = Field(default_factory=list)
    repair_phase: PhaseId | None = None
    max_retries_remaining: int | None = Field(default=None, ge=0)
    blocking_rules: list[str] = Field(default_factory=list)
    next_phase: PhaseId | None = None


class TurnResult(StrictModel):
    session_id: str
    current_phase: PhaseId
    next_phase: PhaseId | None = None
    prompt: str | None = None
    artifacts_summary: dict[str, Any] = Field(default_factory=dict)
    gate: GateResult | None = None
    blocked: bool = False
