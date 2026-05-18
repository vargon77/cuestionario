# Entrevistador V6

Entrevistador V6 es una implementacion Python/FastAPI del protocolo definido en `plan.md`: transforma una peticion vaga en artefactos gobernados de entrevista, SEC inicial, SYSTEM_GRAPH, TRACEABILITY_GRAPH y validacion final deterministica.

## Alcance Implementado

- Orquestador de fases con estado persistido por sesion.
- Contratos Pydantic para fases, SEC, scores, checkpoints, grafos y trazabilidad.
- Fases de captura 0-7C y 8B con artefactos estructurados.
- Inferencia deterministica de modulos en FASE_8 y FASE_12.
- Scoring de completitud FASE_9 con reglas R1-R15.
- Generacion SEC inicial FASE_10 sin LLM y con hashes.
- Checkpoint humano FASE_11.
- Generacion deterministica de SYSTEM_GRAPH en FASE_14.
- Generacion deterministica de TRACEABILITY_GRAPH en FASE_15.
- Generacion SEC extendido FASE_16.
- Validadores cruzados FASE_13 y score final FASE_17.
- Checkpoint humano final FASE_18.
- Dashboard React/Vite para operar sesiones, artefactos, scores y grafos.

## Reglas Clave

- FASE_9, FASE_10, FASE_14, FASE_15, FASE_16 y FASE_17 no usan LLM para scores, hashes, grafos, riesgo ni transiciones.
- No se genera SEC si el score FASE_9 es menor a 70.
- FASE_17 siempre avanza a FASE_18 con evidencia de riesgo.
- FASE_11 acepta `SI`, `NO_CAMBIAR`, `INCOMPLETO`.
- FASE_18 acepta `SI`, `NO_CAMBIAR`, `INCOMPLETO`, `REVALIDAR`.
- SYSTEM_GRAPH no permite nodos huerfanos; cada operacion conecta actor, objeto, estado, regla, recurso y objetivo.
- TRACEABILITY_GRAPH sigue la jerarquia fija: objetivo -> scope -> operacion -> estado -> regla -> recurso.

## Estructura

- `app/main.py`: app FastAPI.
- `app/api/routes/interview.py`: endpoints de sesiones.
- `app/core/orchestrator.py`: avance de fases, gates y persistencia de artefactos.
- `app/core/phase_registry.py`: mapa de fases 0-18.
- `app/phases/`: ejecucion por tipo de fase.
- `app/validators/`: reglas deterministicas FASE_9, FASE_13 y FASE_17.
- `app/models/contracts.py`: contratos Pydantic.
- `frontend/`: dashboard Bun + React + Vite.
- `tests/`: cobertura del flujo backend.

## Ejecucion Local

Backend:

```powershell
python -m pip install -e ".[dev]"
python -m uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
bun install
bun run dev
```

Stack con Docker:

```powershell
docker compose up --build
```

URLs por defecto:

- API: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Verificacion

```powershell
python -m pytest
```

Estado de cierre verificado: `60 passed`.

Nota: el build frontend requiere Bun instalado:

```powershell
cd frontend
bun run build
```

## Limites Actuales

- No hay proveedor LLM real configurado; el diseno mantiene `LLMService` como puerto desacoplado.
- No hay autenticacion de producto.
- La persistencia productiva esta esbozada con PostgreSQL JSONB; el store en memoria sigue disponible para pruebas.
- El frontend es consola operativa, no UI final de producto.
