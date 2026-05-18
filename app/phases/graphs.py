from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.core.orchestrator import PhaseExecution
from app.models.contracts import (
    Consistency,
    Criticality,
    EdgeType,
    GraphEdge,
    GraphNode,
    NodeType,
    PhaseContext,
    PhaseId,
    PhaseOutput,
    SystemGraph,
    TraceabilityGraph,
    TraceabilityLevel,
    TraceabilityMatrix,
    TraceabilityMatrixRow,
    TraceabilityNode,
    TraceabilityType,
)


REQUIRED_SYSTEM_GRAPH_DIMENSIONS = (
    "actors",
    "objects",
    "operations",
    "states",
    "rules",
    "resources",
    "objectives",
)


@dataclass(frozen=True)
class OperationLinks:
    operation_id: str
    actor_id: str
    object_id: str
    state_id: str
    rule_id: str
    resource_id: str
    objective_id: str


def execute_system_graph_generation(ctx: PhaseContext) -> PhaseExecution:
    graph, links = build_system_graph(ctx.artifacts.dimensions_12d)
    _validate_no_orphan_operations(links)
    return PhaseExecution(
        output=PhaseOutput(
            phase_id=PhaseId.FASE_14,
            artifact_updates={"system_graph": graph.model_dump(mode="json")},
        ),
        prompt="SYSTEM_GRAPH generado de forma deterministica.",
    )


def execute_traceability_graph_generation(ctx: PhaseContext) -> PhaseExecution:
    if ctx.artifacts.sec_initial is None:
        raise ValueError("FASE_15 requires initial SEC before traceability generation")
    if ctx.artifacts.system_graph is None:
        raise ValueError("FASE_15 requires SYSTEM_GRAPH before traceability generation")

    traceability = build_traceability_graph(
        sec=ctx.artifacts.sec_initial,
        system_graph=ctx.artifacts.system_graph,
    )
    return PhaseExecution(
        output=PhaseOutput(
            phase_id=PhaseId.FASE_15,
            artifact_updates={"traceability_graph": traceability.model_dump(mode="json")},
        ),
        prompt="TRACEABILITY_GRAPH generado de forma deterministica.",
    )


def build_system_graph(dimensions: dict[str, Any]) -> tuple[SystemGraph, list[OperationLinks]]:
    missing = [
        key
        for key in REQUIRED_SYSTEM_GRAPH_DIMENSIONS
        if not _dimension_items(dimensions, key)
    ]
    if missing:
        raise ValueError(
            "SYSTEM_GRAPH requires complete 12D dimensions: " + ", ".join(missing)
        )

    nodes: dict[str, GraphNode] = {}
    edges: list[GraphEdge] = []
    links: list[OperationLinks] = []

    actors = _add_dimension_nodes(nodes, dimensions, "actors", NodeType.ACTOR)
    objects = _add_dimension_nodes(nodes, dimensions, "objects", NodeType.OBJETO)
    operations = _add_dimension_nodes(nodes, dimensions, "operations", NodeType.OPERACION)
    states = _add_dimension_nodes(nodes, dimensions, "states", NodeType.ESTADO)
    rules = _add_dimension_nodes(nodes, dimensions, "rules", NodeType.REGLA)
    resources = _add_dimension_nodes(nodes, dimensions, "resources", NodeType.RECURSO)
    objectives = _add_dimension_nodes(nodes, dimensions, "objectives", NodeType.OBJETIVO)
    events = _add_dimension_nodes(nodes, dimensions, "events", NodeType.EVENTO)
    spaces = _add_dimension_nodes(nodes, dimensions, "space", NodeType.ESPACIO)
    channels = _add_dimension_nodes(nodes, dimensions, "communication", NodeType.CANAL)

    for index, operation in enumerate(operations):
        actor = _linked_node(actors, dimensions, "operations", index, 2)
        obj = _linked_node(objects, dimensions, "operations", index, 3)
        state = _linked_node(states, dimensions, "operations", index, 6)
        rule = _linked_node(rules, dimensions, "operations", index, 4)
        resource = _linked_node(resources, dimensions, "operations", index, 5)
        objective = objectives[min(index, len(objectives) - 1)]
        links.append(
            OperationLinks(
                operation_id=operation,
                actor_id=actor,
                object_id=obj,
                state_id=state,
                rule_id=rule,
                resource_id=resource,
                objective_id=objective,
            )
        )
        edges.extend(
            [
                _edge(actor, operation, EdgeType.EJECUTA),
                _edge(operation, obj, EdgeType.MODIFICA),
                _edge(operation, state, EdgeType.MODIFICA),
                _edge(rule, operation, EdgeType.RESTRINGE),
                _edge(operation, resource, EdgeType.CONSUME),
                _edge(operation, objective, EdgeType.OPTIMIZA),
            ]
        )

        if events:
            edges.append(_edge(events[min(index, len(events) - 1)], operation, EdgeType.DISPARA))
        if spaces:
            edges.append(_edge(operation, spaces[min(index, len(spaces) - 1)], EdgeType.DEPENDE))
        if channels:
            edges.append(_edge(operation, channels[min(index, len(channels) - 1)], EdgeType.COMUNICA))

    _validate_no_orphan_nodes(nodes, edges)
    return SystemGraph(nodes=list(nodes.values()), edges=_dedupe_edges(edges)), links


def build_traceability_graph(
    *,
    sec: dict[str, Any],
    system_graph: SystemGraph,
) -> TraceabilityGraph:
    operations = [node for node in system_graph.nodes if node.tipo == NodeType.OPERACION]
    if not operations:
        raise ValueError("TRACEABILITY_GRAPH requires at least one operation node")

    hierarchy: list[TraceabilityNode] = []
    rows: list[TraceabilityMatrixRow] = []
    scopes = _sec_scopes(sec)
    objective_nodes = [node for node in system_graph.nodes if node.tipo == NodeType.OBJETIVO]

    for index, operation in enumerate(operations):
        objective = objective_nodes[min(index, len(objective_nodes) - 1)]
        scope = scopes[min(index, len(scopes) - 1)]
        state = _first_target(system_graph, operation.id, EdgeType.MODIFICA, NodeType.ESTADO)
        rule = _first_source(system_graph, operation.id, EdgeType.RESTRINGE, NodeType.REGLA)
        resource = _first_target(system_graph, operation.id, EdgeType.CONSUME, NodeType.RECURSO)

        chain = [
            TraceabilityNode(
                id=f"trace-{objective.id}",
                nivel=TraceabilityLevel.OBJETIVO,
                tipo=TraceabilityType.NEGOCIO,
                refs=[objective.id],
            ),
            TraceabilityNode(
                id=f"trace-{scope}",
                nivel=TraceabilityLevel.SCOPE,
                tipo=TraceabilityType.FUNCIONAL,
                refs=[scope, objective.id],
            ),
            TraceabilityNode(
                id=f"trace-{operation.id}",
                nivel=TraceabilityLevel.OPERACION,
                tipo=TraceabilityType.OPERACIONAL,
                refs=[operation.id, scope],
            ),
            TraceabilityNode(
                id=f"trace-{state.id}",
                nivel=TraceabilityLevel.ESTADO,
                tipo=TraceabilityType.OPERACIONAL,
                refs=[state.id, operation.id],
            ),
            TraceabilityNode(
                id=f"trace-{rule.id}",
                nivel=TraceabilityLevel.REGLA,
                tipo=TraceabilityType.SEGURIDAD,
                refs=[rule.id, operation.id],
            ),
            TraceabilityNode(
                id=f"trace-{resource.id}",
                nivel=TraceabilityLevel.RECURSO,
                tipo=TraceabilityType.INFRAESTRUCTURA,
                refs=[resource.id, operation.id],
            ),
        ]
        hierarchy.extend(chain)
        rows.append(
            TraceabilityMatrixRow(
                objetivo=objective.id,
                scope=scope,
                operacion=operation.id,
                recurso=resource.id,
                kpi=_kpi_for_objective(objective),
            )
        )

    return TraceabilityGraph(
        hierarchy=_dedupe_trace_nodes(hierarchy),
        matrix=TraceabilityMatrix(rows=rows),
        traceability_type=TraceabilityType.FUNCIONAL,
    )


def _add_dimension_nodes(
    nodes: dict[str, GraphNode],
    dimensions: dict[str, Any],
    key: str,
    node_type: NodeType,
) -> list[str]:
    ids = []
    for index, label in enumerate(_dimension_items(dimensions, key), start=1):
        node_id = _node_id(node_type, label, index)
        nodes[node_id] = GraphNode(
            id=node_id,
            tipo=node_type,
            criticidad=Criticality.MEDIA,
            metadata={"label": label, "dimension": key},
        )
        ids.append(node_id)
    return ids


def _dimension_items(dimensions: dict[str, Any], key: str) -> list[str]:
    value = dimensions.get(key)
    if isinstance(value, dict):
        rows = value.get("rows")
        if isinstance(rows, list) and rows:
            return [
                str(row.get("c1")).strip()
                for row in rows
                if isinstance(row, dict) and str(row.get("c1", "")).strip()
            ]
        raw = str(value.get("raw") or value.get("raw_goal") or "").strip()
        if raw:
            return [item.strip() for item in raw.split(";") if item.strip()] or [raw]
    if isinstance(value, str) and value.strip():
        return [item.strip() for item in value.split(";") if item.strip()] or [value.strip()]
    return []


def _linked_node(
    candidates: list[str],
    dimensions: dict[str, Any],
    source_key: str,
    index: int,
    cell: int,
) -> str:
    if not candidates:
        raise ValueError(f"SYSTEM_GRAPH cannot link {source_key}: missing candidates")
    rows = dimensions.get(source_key, {}).get("rows") if isinstance(dimensions.get(source_key), dict) else None
    if isinstance(rows, list) and index < len(rows) and isinstance(rows[index], dict):
        raw = str(rows[index].get(f"c{cell}", "")).strip()
        matched = _match_node(candidates, raw)
        if matched:
            return matched
    return candidates[min(index, len(candidates) - 1)]


def _match_node(candidates: list[str], raw: str) -> str | None:
    normalized_raw = _normalize(raw)
    if not normalized_raw:
        return None
    for candidate in candidates:
        if normalized_raw in candidate or candidate in normalized_raw:
            return candidate
    return None


def _edge(source: str, target: str, edge_type: EdgeType) -> GraphEdge:
    return GraphEdge(
        source=source,
        target=target,
        tipo=edge_type,
        criticidad=Criticality.MEDIA,
        consistencia=Consistency.FUERTE,
    )


def _validate_no_orphan_operations(links: list[OperationLinks]) -> None:
    for link in links:
        if not all(
            [
                link.actor_id,
                link.object_id,
                link.state_id,
                link.rule_id,
                link.resource_id,
                link.objective_id,
            ]
        ):
            raise ValueError(
                "orphan operation: every operation must connect to "
                "actor+object+state+rule+resource+objective"
            )


def _validate_no_orphan_nodes(nodes: dict[str, GraphNode], edges: list[GraphEdge]) -> None:
    connected = {edge.source for edge in edges} | {edge.target for edge in edges}
    orphan_ids = sorted(node_id for node_id in nodes if node_id not in connected)
    if orphan_ids:
        raise ValueError("SYSTEM_GRAPH contains orphan nodes: " + ", ".join(orphan_ids))


def _first_target(
    graph: SystemGraph,
    source: str,
    edge_type: EdgeType,
    target_type: NodeType,
) -> GraphNode:
    nodes = {node.id: node for node in graph.nodes}
    for edge in graph.edges:
        if edge.source == source and edge.tipo == edge_type:
            target = nodes.get(edge.target)
            if target and target.tipo == target_type:
                return target
    raise ValueError(f"missing traceability target {target_type.value} for {source}")


def _first_source(
    graph: SystemGraph,
    target: str,
    edge_type: EdgeType,
    source_type: NodeType,
) -> GraphNode:
    nodes = {node.id: node for node in graph.nodes}
    for edge in graph.edges:
        if edge.target == target and edge.tipo == edge_type:
            source = nodes.get(edge.source)
            if source and source.tipo == source_type:
                return source
    raise ValueError(f"missing traceability source {source_type.value} for {target}")


def _sec_scopes(sec: dict[str, Any]) -> list[str]:
    scopes = sec.get("sections", {}).get("SCOPES", [])
    if isinstance(scopes, list) and scopes:
        ids = [str(scope.get("id")) for scope in scopes if isinstance(scope, dict) and scope.get("id")]
        if ids:
            return ids
    return ["SCOPE_1"]


def _kpi_for_objective(objective: GraphNode) -> str:
    label = str(objective.metadata.get("label", "KPI_VERIFICABLE"))
    parts = [part.strip() for part in label.split("|") if part.strip()]
    return parts[1] if len(parts) > 1 else "KPI_VERIFICABLE"


def _dedupe_edges(edges: list[GraphEdge]) -> list[GraphEdge]:
    seen = set()
    unique = []
    for edge in edges:
        key = (edge.source, edge.target, edge.tipo)
        if key in seen:
            continue
        seen.add(key)
        unique.append(edge)
    return unique


def _dedupe_trace_nodes(nodes: list[TraceabilityNode]) -> list[TraceabilityNode]:
    seen = set()
    unique = []
    for node in nodes:
        if node.id in seen:
            continue
        seen.add(node.id)
        unique.append(node)
    return unique


def _node_id(node_type: NodeType, label: str, index: int) -> str:
    normalized = _normalize(label)[:36] or str(index)
    return f"{node_type.value}_{index}_{normalized}"


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
