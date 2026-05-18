from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.orchestrator import PhaseExecution
from app.models.contracts import (
    EstimationEntry,
    EstimationSource,
    EstimationStatus,
    EstimationType,
    PhaseContext,
    PhaseId,
    PhaseOutput,
)


@dataclass(frozen=True)
class CaptureSpec:
    artifact_key: str
    prompt: str
    min_items: int = 1
    requires_number_or_unknown: bool = False
    requires_unit_or_unknown: bool = False


CAPTURE_SPECS: dict[PhaseId, CaptureSpec] = {
    PhaseId.FASE_0: CaptureSpec(
        artifact_key="actors",
        min_items=2,
        prompt=(
            "PREGUNTA 1 - ACTORES\n"
            "Actor | Tipo | Cantidad | Frecuencia | Permisos | Criticidad"
        ),
    ),
    PhaseId.FASE_1: CaptureSpec(
        artifact_key="objects",
        min_items=3,
        requires_number_or_unknown=True,
        requires_unit_or_unknown=True,
        prompt=(
            "PREGUNTA 2 - OBJETOS:\n"
            "El sistema maneja \"cosas\" persistentes.\n"
            "\n"
            "Para los valores que no sepas, usa estos formatos:\n"
            "- Valor exacto    : \"1000/dia\"\n"
            "- Rango estimado  : \"500-2000/dia\"\n"
            "- No se           : \"DESCONOCIDO\" (usare estandar)\n"
            "\n"
            "Responde esta tabla:\n"
            "| Objeto | Volumen/dia | Retencion | Atributos (3-5) |\n"
            "|--------|-------------|-----------|-----------------|\n"
            "| 1.     |             |           |                 |\n"
            "Requisitos:\n"
            "  - Minimo 3 objetos principales\n"
            "  - Maximo 10 objetos (fusiona si son similares)\n"
            "  - Volumen: numero con unidad o rango o DESCONOCIDO\n"
            "  - Retencion: numero + unidad o rango o DESCONOCIDO\n"
            "\n"
            "[EXTENSION V6 — TABLA EXTENDIDA DE OBJETOS]\n"
            "| Objeto | Volumen | Retencion | Atributos | Owner | Criticidad |\n"
            "|--------|---------|-----------|-----------|-------|------------|\n"
            "\n"
            
        ),
    ),
    PhaseId.FASE_2: CaptureSpec(
        artifact_key="operations",
        min_items=1,
        prompt=(
            "PREGUNTA 3 - OPERACIONES:\n"
            "Por cada objeto: que operaciones se pueden hacer.\n"
            "Formato: Para [OBJETO_N]: Crear, Leer, Actualizar, Eliminar, [especificas]\n"
            "Luego: operaciones que involucran MULTIPLES objetos.\n"
            "\n"
            "[EXTENSION V6 — TABLA DE OPERACIONES]\n"
            "| Operacion | Actor | Objetos | Trigger | Resultado | Criticidad |\n"
            "|-----------|-------|---------|---------|-----------|------------|"
        ),
    ),
    PhaseId.FASE_3: CaptureSpec(
        artifact_key="states",
        min_items=3,
        prompt=(
            "PREGUNTA 4 - ESTADOS:\n"
            "Para cada objeto con ciclo de vida, define estados.\n"
            "Requisito: minimo 3 estados, maximo 8.\n"
            "Formato: [OBJETO]: [ESTADO_INICIAL] → [ESTADO_2] → [ESTADO_FINAL]\n"
            "                                      ↘ [ESTADO_ALTERNO]\n"
            "Si responden \"solo activo/inactivo\" → re-preguntar obligatoriamente.\n"
            "\n"
            "[EXTENSION V6 — TABLA DE ESTADOS]\n"
            "| Objeto | Estado_Origen | Evento | Estado_Destino | Rollback | Terminal |\n"
            "|--------|---------------|--------|----------------|----------|----------|"
        ),
    ),
    PhaseId.FASE_3B: CaptureSpec(
        artifact_key="relations",
        prompt=(
            "PREGUNTAS FUNDAMENTALES:\n"
            "- Quien pertenece a quien?\n"
            "- Que depende de que?\n"
            "- Que cardinalidad existe entre los objetos?\n"
            "- Que herencia existe?\n"
            "- Que composicion existe?\n"
            "- Que propagacion existe cuando un objeto cambia?\n"
            "\n"
            "Responde esta tabla:\n"
            "| Origen | Relacion | Destino | Cardinalidad | Propagacion | Obligatoria |\n"
            "|--------|----------|---------|--------------|-------------|-------------|\n"
            "\n"
            "TIPOS DE RELACION:\n"
            "- 1:1\n"
            "- 1:N\n"
            "- N:N\n"
            "- dependencia\n"
            "- ownership\n"
            "- composicion"
        ),
    ),
    PhaseId.FASE_4: CaptureSpec(
        artifact_key="rules",
        min_items=5,
        prompt=(
            "PREGUNTA 5 - REGLAS NO NEGOCIABLES:\n"
            "Dime 5 cosas que el sistema NO DEBE HACER bajo NINGUNA circunstancia.\n"
            "No aceptar obviedades. Quiero reglas especificas del dominio.\n"
            "Escribe 5 reglas ahora.\n"
            "\n"
            "[EXTENSION V6 — TABLA DE REGLAS]\n"
            "| Regla | Tipo | Condicion | Rechazo | Severidad |\n"
            "|-------|------|-----------|---------|-----------|\n"
            "\n"
            "TIPOS DE REGLA V6:\n"
            "- negocio\n"
            "- seguridad\n"
            "- consistencia\n"
            "- cumplimiento\n"
            "- integridad\n"
            "\n"
            "PREGUNTAS ADICIONALES V6:\n"
            "- Que nunca debe ocurrir?\n"
            "- Que validaciones existen?\n"
            "- Que restricciones legales existen?\n"
            "- Que politicas existen?\n"
            "- Que condiciones invalidan operaciones?"
        ),
    ),
    PhaseId.FASE_5: CaptureSpec(
        artifact_key="events",
        prompt=(
            "PREGUNTA 6 - EVENTOS:\n"
            "Por cada evento especifica:\n"
            "  - Nombre del evento\n"
            "  - Origen (usuario, temporizador, sistema externo, sensor)\n"
            "  - Accion que debe tomar el sistema\n"
            "No avances si hay eventos sin accion definida.\n"
            "\n"
            "[EXTENSION V6 — TABLA DE EVENTOS]\n"
            "| Evento | Origen | Prioridad | Accion | Timeout | Error_Strategy |\n"
            "|--------|--------|-----------|--------|---------|----------------|\n"
            "\n"
            "TIPOS DE EVENTO V6:\n"
            "- usuario\n"
            "- tiempo\n"
            "- sistema externo\n"
            "- sensor\n"
            "- webhook\n"
            "- error\n"
            "\n"
            "PREGUNTAS ADICIONALES V6:\n"
            "- Que dispara acciones?\n"
            "- Que sucede fuera del sistema?\n"
            "- Que eventos temporales existen?\n"
            "- Que eventos fallidos existen?\n"
            "- Que eventos requieren reaccion inmediata?"
        ),
    ),
    PhaseId.FASE_6: CaptureSpec(
        artifact_key="time",
        requires_number_or_unknown=True,
        requires_unit_or_unknown=True,
        prompt=(
            "PREGUNTA 7 - TIEMPO:\n"
            "Responde CADA una con numeros concretos, estimaciones, o \"DESCONOCIDO\":\n"
            "1. Tiempo max respuesta operacion normal: _____ (ms/s) [default segun tipo]\n"
            "2. Tiempo max respuesta operacion compleja: _____ (ms/s) [default segun tipo]\n"
            "3. Tiempo max sin respuesta antes de timeout: _____ (ms/s) [default: 3x normal]\n"
            "4. Hay operaciones que expiran? Cuales y en cuanto tiempo?\n"
            "5. Hay horarios donde el sistema NO debe operar?\n"
            "6. Hay picos predecibles de carga?\n"
            "7. Que pasa si una operacion toma mas tiempo del esperado?\n"
            "Si respondes \"DESCONOCIDO\", usare los valores estandar para tu tipo de sistema.\n"
            "\n"
            "[EXTENSION V6 — TABLA DE TIEMPO]\n"
            "| Elemento | SLA | Timeout | Expiracion | Scheduler |\n"
            "|----------|-----|---------|------------|-----------|\n"
            "\n"
            "TIPOS TEMPORALES V6:\n"
            "- timeout\n"
            "- SLA\n"
            "- expiracion\n"
            "- scheduler\n"
            "- ventana de mantenimiento\n"
            "\n"
            "PREGUNTAS ADICIONALES V6:\n"
            "- Cuando ocurre algo?\n"
            "- Cuanto tarda?\n"
            "- Que expira?\n"
            "- Que depende del orden temporal?\n"
            "- Que ventanas de operacion o mantenimiento existen?"
        ),
    ),
    PhaseId.FASE_7: CaptureSpec(
        artifact_key="resources",
        requires_number_or_unknown=True,
        requires_unit_or_unknown=True,
        prompt=(
            "PREGUNTA 8 - RECURSOS:\n"
            "1. Usuarios concurrentes maximos estimados: _____\n"
            "2. Operaciones por segundo en pico: _____ (rps)\n"
            "3. Almacenamiento total estimado primer anio: _____ (MB/GB/TB)\n"
            "4. Ancho de banda estimado por mes: _____ (MB/GB)\n"
            "5. Hay recursos humanos limitados?\n"
            "6. Hay recursos fisicos limitados?\n"
            "7. Hay limites de APIs externas?\n"
            "Para CADA recurso limitado: especifica QUE PASA si se excede.\n"
            "\n"
            "[EXTENSION V6 — TABLA DE RECURSOS]\n"
            "| Recurso | Maximo | Unidad | Degradacion | Monitoreo |\n"
            "|---------|--------|--------|-------------|-----------|\n"
            "\n"
            "TIPOS DE RECURSO V6:\n"
            "- CPU\n"
            "- memoria\n"
            "- almacenamiento\n"
            "- ancho de banda\n"
            "- APIs externas\n"
            "- operadores humanos\n"
            "\n"
            "PREGUNTAS ADICIONALES V6:\n"
            "- Que consume el sistema?\n"
            "- Que limites existen?\n"
            "- Que costos existen?\n"
            "- Que se agota?\n"
            "- Que escalabilidad requiere?"
        ),
    ),
    PhaseId.FASE_7B: CaptureSpec(
        artifact_key="space",
        prompt=(
            "PREGUNTAS FUNDAMENTALES:\n"
            "- Donde ocurre algo?\n"
            "- Que esta distribuido?\n"
            "- Que regiones existen?\n"
            "- Que componentes estan cerca o lejos entre si?\n"
            "- Que latencias geograficas existen?\n"
            "\n"
            "Responde esta tabla:\n"
            "| Componente | Ubicacion | Region | Replicacion | Latencia_Max |\n"
            "|------------|-----------|--------|-------------|--------------|\n"
            "\n"
            "TIPOS DE ESPACIO:\n"
            "- local\n"
            "- edge\n"
            "- cloud\n"
            "- multi-region\n"
            "- on-premise\n"
            "- hibrido\n"
            "\n"
            "COMPLEMENTA DIMENSIONES:\n"
            "- TIEMPO (FASE_6)\n"
            "- RECURSOS (FASE_7)\n"
            "- EVENTOS (FASE_5)\n"
            "\n"
            "No avanzar si hay operaciones distribuidas sin ubicacion definida."
        ),
    ),
    PhaseId.FASE_7C: CaptureSpec(
        artifact_key="communication",
        prompt=(
            "PREGUNTAS FUNDAMENTALES:\n"
            "- Como se comunican los componentes entre si?\n"
            "- Que protocolos usan?\n"
            "- Que orden se garantiza en los mensajes?\n"
            "- Que tolerancia a fallos existe?\n"
            "- Que sincronizacion existe?\n"
            "\n"
            "Responde esta tabla:\n"
            "| Emisor | Receptor | Protocolo | Sync_Async | Retry | Orden_Garantizado |\n"
            "|--------|----------|-----------|------------|-------|-------------------|\n"
            "\n"
            "TIPOS DE COMUNICACION:\n"
            "- sync\n"
            "- async\n"
            "- pub/sub\n"
            "- queue\n"
            "- websocket\n"
            "- RPC\n"
            "- REST\n"
            "- GraphQL\n"
            "\n"
            "COMPLEMENTA DIMENSIONES:\n"
            "- EVENTOS (FASE_5)\n"
            "- OPERACIONES (FASE_2)\n"
            "- REGLAS (FASE_4)\n"
            "\n"
            "REGLAS V6 PARA COMUNICACION:\n"
            "- toda comunicacion debe tener protocolo\n"
            "- toda comunicacion debe tener timeout\n"
            "- toda comunicacion debe tener estrategia de fallo\n"
            "- toda comunicacion debe tener reglas de seguridad\n"
            "\n"
            "No avanzar si hay canales de comunicacion sin protocolo definido."
        ),
    ),
    PhaseId.FASE_8B: CaptureSpec(
        artifact_key="objectives",
        prompt=(
            "PREGUNTAS FUNDAMENTALES:\n"
            "- Que busca optimizar el sistema?\n"
            "- Que problema concreto resuelve?\n"
            "- Como se mide el exito?\n"
            "- Que prioridades existen entre objetivos?\n"
            "- Que tradeoffs acepta el sistema?\n"
            "\n"
            "Responde esta tabla:\n"
            "| Objetivo | KPI | Prioridad | Tradeoff | Horizonte |\n"
            "|----------|-----|-----------|----------|-----------|\n"
            "\n"
            "TIPOS DE OBJETIVO:\n"
            "- reducir tiempo\n"
            "- reducir costo\n"
            "- aumentar throughput\n"
            "- aumentar precision\n"
            "- automatizar\n"
            "- supervisar\n"
            "\n"
            "REGLAS V6 PARA OBJETIVOS:\n"
            "- todo objetivo debe tener KPI\n"
            "- todo objetivo debe afectar operaciones\n"
            "- todo objetivo debe ser observable\n"
            "- todo objetivo debe ser verificable\n"
            "- todo objetivo debe afectar recursos\n"
            "- todo objetivo debe afectar decisiones\n"
            "\n"
            "COMPLEMENTA DIMENSIONES:\n"
            "- acceptance_rules (FASE_9)\n"
            "- scopes (FASE_10)\n"
            "- risks (FASE_10)\n"
            "\n"
            "No avanzar si hay objetivos sin KPI definido o verificable."
        ),
    ),
}


def execute_capture_phase(ctx: PhaseContext) -> PhaseExecution:
    spec = CAPTURE_SPECS[ctx.phase_id]
    raw_answer = (ctx.user_input or "").strip()
    rows = parse_rows(raw_answer)
    payload = {
        "raw": raw_answer,
        "rows": rows,
        "item_count": len(rows),
        "quality_flags": quality_flags(raw_answer, spec, ctx.phase_id),
        "source": "human",
    }
    updates: dict[str, Any] = {spec.artifact_key: payload}

    if ctx.phase_id == PhaseId.FASE_0:
        updates["actor_seed"] = {"raw_goal": raw_answer, "source": "human"}
    if ctx.phase_id == PhaseId.FASE_1:
        updates["objects_raw"] = raw_answer

    output = PhaseOutput(
        phase_id=ctx.phase_id,
        artifact_updates={"dimensions_12d": updates},
        questions_asked=[next_prompt(ctx.phase_id)],
        estimations=estimation_entries(spec.artifact_key, raw_answer),
    )
    return PhaseExecution(output=output, prompt=output.questions_asked[0])


def next_prompt(phase_id: PhaseId) -> str:
    sequence = list(CAPTURE_SPECS)
    index = sequence.index(phase_id)
    if index == len(sequence) - 1:
        return "Continuare con validacion de completitud."
    return CAPTURE_SPECS[sequence[index + 1]].prompt


def parse_rows(raw_answer: str) -> list[dict[str, str]]:
    rows = []
    for line in raw_answer.splitlines():
        clean = line.strip().strip("|")
        if not clean or set(clean) <= {"-", "|", " "}:
            continue
        cells = [cell.strip() for cell in clean.split("|") if cell.strip()]
        if cells:
            rows.append({f"c{i + 1}": cell for i, cell in enumerate(cells)})
    if rows:
        return rows
    return [{"c1": item.strip()} for item in raw_answer.split(";") if item.strip()]


def quality_flags(raw_answer: str, spec: CaptureSpec, phase_id: PhaseId) -> list[str]:
    flags = []
    item_count = len(parse_rows(raw_answer))
    if item_count < spec.min_items:
        flags.append(f"min_items:{item_count}/{spec.min_items}")
    if spec.requires_number_or_unknown and not has_number_or_unknown(raw_answer):
        flags.append("missing_number_or_unknown")
    if spec.requires_unit_or_unknown and not has_unit_or_unknown(raw_answer):
        flags.append("missing_unit_or_unknown")
    
    # FASE_2 specific validation: check that each operation has a clear owner object
    if phase_id == PhaseId.FASE_2:
        # Parse preserving empty fields to check for missing Objetos column
        lines = [line.strip() for line in raw_answer.splitlines() if line.strip() and not set(line.strip()) <= {"-", "|", " "}]
        for i, line in enumerate(lines):
            # Count pipes to determine number of fields
            # Expected format: Operacion | Actor | Objetos | Trigger | Resultado | Criticidad (6 fields)
            # We need at least 3 fields to check Objetos (field 3)
            if line.count('|') < 2:  # Need at least 2 pipes for 3 fields
                flags.append(f"fila_{i+1}:_campos_insuficientes")
                continue
                
            # Split preserving empty fields
            parts = [part.strip() for part in line.split('|')]
            
            # Check if Objetos field (index 2) is empty
            if len(parts) >= 3:
                objetos = parts[2]  # Objetos is the 3rd field (0-indexed)
                if not objetos:
                    flags.append(f"fila_{i+1}:_operacion_sin_objetos")
            else:
                flags.append(f"fila_{i+1}:_campos_insuficientes")
                
    # FASE_1 specific validation: check object fields
    elif phase_id == PhaseId.FASE_1:
        # Parse preserving empty fields
        lines = [line.strip() for line in raw_answer.splitlines() if line.strip() and not set(line.strip()) <= {"-", "|", " "}]
        for i, line in enumerate(lines):
            # Expected format: Objeto | Volumen/dia | Retencion | Atributos (3-5) | Owner | Criticidad
            # We need at least 5 fields to check all required columns
            if line.count('|') < 4:  # Need at least 4 pipes for 5 fields
                flags.append(f"fila_{i+1}:_campos_insuficientes")
                continue
                
            # Split preserving empty fields
            parts = [part.strip() for part in line.split('|')]
            
            # Check if we have at least 5 fields (Objeto, Volumen/dia, Retencion, Atributos, Owner, Criticidad)
            if len(parts) >= 5:
                objeto = parts[0]
                volumen_dia = parts[1] if len(parts) > 1 else ""
                retencion = parts[2] if len(parts) > 2 else ""
                atributos = parts[3] if len(parts) > 3 else ""
                owner = parts[4] if len(parts) > 4 else ""
                criticidad = parts[5] if len(parts) > 5 else ""
                
                # Validate objeto is not empty
                if not objeto:
                    flags.append(f"fila_{i+1}:_objeto_vacío")
                
                # Validate volumen_dia: numero con unidad o rango o DESCONOCIDO
                if not volumen_dia:
                    flags.append(f"fila_{i+1}:_volumen_día_vacío")
                elif not (any(char.isdigit() for char in volumen_dia) or 
                          "/" in volumen_dia or  # for ranges like 500-2000/dia
                          volumen_dia.upper() == "DESCONOCIDO"):
                    flags.append(f"fila_{i+1}:_volumen_día_formato_inválido")
                
                # Validate retencion: numero + unidad o rango o DESCONOCIDO
                if not retencion:
                    flags.append(f"fila_{i+1}:_retención_vacía")
                elif not (any(char.isdigit() for char in retencion) or 
                          "/" in retencion or  # for ranges
                          retencion.upper() == "DESCONOCIDO"):
                    flags.append(f"fila_{i+1}:_retención_formato_inválido")
                
                # Validate atributos: at least 3 attributes (separated by commas)
                if not atributos:
                    flags.append(f"fila_{i+1}:_atributos_vacíos")
                else:
                    # Count attributes separated by commas
                    attr_list = [attr.strip() for attr in atributos.split(",") if attr.strip()]
                    if len(attr_list) < 3:
                        flags.append(f"fila_{i+1}:_atributos_insuficientes:{len(attr_list)}/3")
                
                # Validate owner is not empty
                if not owner:
                    flags.append(f"fila_{i+1}:_objeto_sin_owner")
                
                # Validate criticidad is not empty
                if not criticidad:
                    flags.append(f"fila_{i+1}:_objeto_sin_criticidad")
            else:
                flags.append(f"fila_{i+1}:_campos_insuficientes")
                
    # FASE_3 specific validation: check minimum 3 states
    elif phase_id == PhaseId.FASE_3:
        if item_count < 3:
            flags.append(f"estados_insuficientes:{item_count}/3")
            
    # FASE_4 specific validation: check minimum 5 rules
    elif phase_id == PhaseId.FASE_4:
        if item_count < 5:
            flags.append(f"reglas_insuficientes:{item_count}/5")
            
    # FASE_5 specific validation: check that events have actions defined
    elif phase_id == PhaseId.FASE_5:
        # Parse preserving empty fields to check for missing Accion column
        lines = [line.strip() for line in raw_answer.splitlines() if line.strip() and not set(line.strip()) <= {"-", "|", " "}]
        for i, line in enumerate(lines):
            # Expected format: Evento | Origen | Prioridad | Accion | Timeout | Error_Strategy (6 fields)
            # We need at least 4 fields to check Accion (field 4)
            if line.count('|') < 3:  # Need at least 3 pipes for 4 fields
                flags.append(f"fila_{i+1}:_campos_insuficientes")
                continue
                
            # Split preserving empty fields
            parts = [part.strip() for part in line.split('|')]
            
            # Check if Accion field (index 3) is empty
            if len(parts) >= 4:
                accion = parts[3]  # Accion is the 4th field (0-indexed)
                if not accion:
                    flags.append(f"fila_{i+1}:_evento_sin_accion")
            else:
                flags.append(f"fila_{i+1}:_campos_insuficientes")
                
    # FASE_6 specific validation: check that time fields have numbers or UNKNOWN
    elif phase_id == PhaseId.FASE_6:
        # Parse preserving empty fields
        lines = [line.strip() for line in raw_answer.splitlines() if line.strip() and not set(line.strip()) <= {"-", "|", " "}]
        for i, line in enumerate(lines):
            # Split preserving empty fields
            parts = [part.strip() for part in line.split('|')]
            
            # Check each field for numbers or UNKNOWN
            for j, part in enumerate(parts):
                if not part:  # Empty field
                    flags.append(f"fila_{i+1}:campo_{j+1}_vacío")
                elif not (any(char.isdigit() for char in part) or part.upper() == "DESCONOCIDO"):
                    flags.append(f"fila_{i+1}:campo_{j+1}_sin_numero_o_desconocido")
                    
    # FASE_7 specific validation: check that resources have numbers or UNKNOWN
    elif phase_id == PhaseId.FASE_7:
        # Parse preserving empty fields
        lines = [line.strip() for line in raw_answer.splitlines() if line.strip() and not set(line.strip()) <= {"-", "|", " "}]
        for i, line in enumerate(lines):
            # Split preserving empty fields
            parts = [part.strip() for part in line.split('|')]
            
            # Check each field for numbers or UNKNOWN
            for j, part in enumerate(parts):
                if not part:  # Empty field
                    flags.append(f"fila_{i+1}:campo_{j+1}_vacío")
                elif not (any(char.isdigit() for char in part) or part.upper() == "DESCONOCIDO"):
                    flags.append(f"fila_{i+1}:campo_{j+1}_sin_numero_o_desconocido")
                    
    # FASE_7B specific validation: check that space components have location defined
    elif phase_id == PhaseId.FASE_7B:
        # Parse preserving empty fields to check for missing Ubicacion column
        lines = [line.strip() for line in raw_answer.splitlines() if line.strip() and not set(line.strip()) <= {"-", "|", " "}]
        for i, line in enumerate(lines):
            # Expected format: Componente | Ubicacion | Region | Replicacion | Latencia_Max (5 fields)
            # We need at least 2 fields to check Ubicacion (field 2)
            if line.count('|') < 1:  # Need at least 1 pipe for 2 fields
                flags.append(f"fila_{i+1}:_campos_insuficientes")
                continue
                
            # Split preserving empty fields
            parts = [part.strip() for part in line.split('|')]
            
            # Check if Ubicacion field (index 1) is empty
            if len(parts) >= 2:
                ubicacion = parts[1]  # Ubicacion is the 2nd field (0-indexed)
                if not ubicacion:
                    flags.append(f"fila_{i+1}:_componente_sin_ubicacion")
            else:
                flags.append(f"fila_{i+1}:_campos_insuficientes")
                
    # FASE_7C specific validation: check that communication has protocol defined
    elif phase_id == PhaseId.FASE_7C:
        # Parse preserving empty fields to check for missing Protocolo column
        lines = [line.strip() for line in raw_answer.splitlines() if line.strip() and not set(line.strip()) <= {"-", "|", " "}]
        for i, line in enumerate(lines):
            # Expected format: Emisor | Receptor | Protocolo | Sync_Async | Retry | Orden_Garantizado (6 fields)
            # We need at least 3 fields to check Protocolo (field 3)
            if line.count('|') < 2:  # Need at least 2 pipes for 3 fields
                flags.append(f"fila_{i+1}:_campos_insuficientes")
                continue
                
            # Split preserving empty fields
            parts = [part.strip() for part in line.split('|')]
            
            # Check if Protocolo field (index 2) is empty
            if len(parts) >= 3:
                protocolo = parts[2]  # Protocolo is the 3rd field (0-indexed)
                if not protocolo:
                    flags.append(f"fila_{i+1}:_comunicacion_sin_protocolo")
            else:
                flags.append(f"fila_{i+1}:_campos_insuficientes")
                
    # FASE_8B specific validation: check that objectives have KPI defined
    elif phase_id == PhaseId.FASE_8B:
        # Parse preserving empty fields to check for missing KPI column
        lines = [line.strip() for line in raw_answer.splitlines() if line.strip() and not set(line.strip()) <= {"-", "|", " "}]
        for i, line in enumerate(lines):
            # Expected format: Objetivo | KPI | Prioridad | Tradeoff | Horizonte (5 fields)
            # We need at least 2 fields to check KPI (field 2)
            if line.count('|') < 1:  # Need at least 1 pipe for 2 fields
                flags.append(f"fila_{i+1}:_campos_insuficientes")
                continue
                
            # Split preserving empty fields
            parts = [part.strip() for part in line.split('|')]
            
            # Check if KPI field (index 1) is empty
            if len(parts) >= 2:
                kpi = parts[1]  # KPI is the 2nd field (0-indexed)
                if not kpi:
                    flags.append(f"fila_{i+1}:_objetivo_sin_kpi")
            else:
                flags.append(f"fila_{i+1}:_campos_insuficientes")
                
    return flags


def estimation_entries(field: str, raw_answer: str) -> list[EstimationEntry]:
    if not contains_unknown(raw_answer):
        return []
    return [
        EstimationEntry(
            id=f"EST_{field}_unknown",
            campo=field,
            tipo=EstimationType.DESCONOCIDO,
            valor_usado="DESCONOCIDO",
            confianza=0.5,
            fuente=EstimationSource.HUMANO_DESCONOCIDO,
            mitigation="Documentar y resolver con defaults_repository.",
            requiere_revision=True,
            estado=EstimationStatus.ACTIVA,
        )
    ]


def contains_unknown(raw_answer: str) -> bool:
    normalized = raw_answer.lower()
    return any(token in normalized for token in ("desconocido", "no se", "nose"))


def has_number_or_unknown(raw_answer: str) -> bool:
    return any(char.isdigit() for char in raw_answer) or contains_unknown(raw_answer)


def has_unit_or_unknown(raw_answer: str) -> bool:
    normalized = raw_answer.lower()
    units = ("ms", "s", "seg", "min", "hora", "dia", "rps", "mb", "gb", "tb")
    return any(unit in normalized for unit in units) or contains_unknown(raw_answer)
