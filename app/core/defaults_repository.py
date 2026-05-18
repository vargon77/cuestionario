from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SystemType(str, Enum):
    DASHBOARD_INTERNO = "DASHBOARD_INTERNO"
    API_PUBLICA = "API_PUBLICA"
    TIEMPO_REAL_IOT = "TIEMPO_REAL_IOT"
    BATCH_ETL = "BATCH_ETL"
    WEB_B2C = "WEB_B2C"


@dataclass(frozen=True)
class RecommendedModule:
    name: str
    priority: str
    rationale: str


@dataclass(frozen=True)
class SystemDefaults:
    system_type: SystemType
    daily_volume: str
    retention: str
    concurrency: str
    normal_response_time: str
    complex_response_time: str
    timeout: str
    recommended_modules: tuple[RecommendedModule, ...]


DEFAULTS: dict[SystemType, SystemDefaults] = {
    SystemType.DASHBOARD_INTERNO: SystemDefaults(
        system_type=SystemType.DASHBOARD_INTERNO,
        daily_volume="10-200 operaciones",
        retention="90 dias",
        concurrency="5-50 usuarios",
        normal_response_time="500ms",
        complex_response_time="1500ms",
        timeout="1500ms",
        recommended_modules=(
            RecommendedModule("autenticacion_sso", "CRITICA", "92% de proyectos lo requieren"),
            RecommendedModule("autorizacion_por_rol", "ALTA", "78% incluye RBAC"),
            RecommendedModule("auditoria", "MEDIA", "65% requiere trazabilidad"),
            RecommendedModule("exportacion_datos", "MEDIA", "70% necesita exportar reportes"),
        ),
    ),
    SystemType.API_PUBLICA: SystemDefaults(
        system_type=SystemType.API_PUBLICA,
        daily_volume="10000-100000 requests",
        retention="indefinido",
        concurrency="100-1000",
        normal_response_time="100ms",
        complex_response_time="500ms",
        timeout="300ms",
        recommended_modules=(
            RecommendedModule("api_keys", "CRITICA", "95% requiere autenticacion"),
            RecommendedModule("rate_limiting", "CRITICA", "45% de fallos por falta de rate limiting"),
            RecommendedModule("versionado_api", "ALTA", "88% necesita versionado"),
            RecommendedModule("documentacion_openapi", "ALTA", "92% requiere documentacion"),
        ),
    ),
    SystemType.TIEMPO_REAL_IOT: SystemDefaults(
        system_type=SystemType.TIEMPO_REAL_IOT,
        daily_volume="100000-1000000 eventos",
        retention="7-30 dias",
        concurrency="10000-100000",
        normal_response_time="50ms",
        complex_response_time="200ms",
        timeout="150ms",
        recommended_modules=(
            RecommendedModule("ingestion_masiva", "CRITICA", "100% necesita ingestion"),
            RecommendedModule("procesamiento_stream", "CRITICA", "100% requiere streaming"),
            RecommendedModule("alertas_tiempo_real", "ALTA", "85% necesita alertas"),
            RecommendedModule("redundancia_geografica", "ALTA", "78% requiere alta disponibilidad"),
        ),
    ),
    SystemType.BATCH_ETL: SystemDefaults(
        system_type=SystemType.BATCH_ETL,
        daily_volume="1000000 registros",
        retention="90 dias",
        concurrency="1 proceso",
        normal_response_time="1 hora (por job)",
        complex_response_time="4 horas",
        timeout="8 horas",
        recommended_modules=(
            RecommendedModule("orquestador", "CRITICA", "100% necesita orquestacion"),
            RecommendedModule("checkpoint_reanudacion", "CRITICA", "90% requiere recuperacion"),
            RecommendedModule("monitoreo_procesos", "ALTA", "85% necesita monitoreo"),
            RecommendedModule("data_quality", "MEDIA", "70% requiere validacion"),
        ),
    ),
    SystemType.WEB_B2C: SystemDefaults(
        system_type=SystemType.WEB_B2C,
        daily_volume="5000-50000 operaciones",
        retention="180 dias",
        concurrency="500-5000",
        normal_response_time="200ms",
        complex_response_time="1000ms",
        timeout="600ms",
        recommended_modules=(
            RecommendedModule("autenticacion", "CRITICA", "100% requiere login"),
            RecommendedModule("autorizacion_rbac", "ALTA", "80% necesita roles"),
            RecommendedModule("rate_limiting", "ALTA", "35% de fallos por falta de rate limiting"),
            RecommendedModule("cache", "MEDIA", "75% necesita cache"),
            RecommendedModule("monitoreo_health", "ALTA", "90% requiere health checks"),
        ),
    ),
}


def detect_system_type(description: str) -> SystemType:
    normalized = description.lower()
    keyword_map = {
        SystemType.DASHBOARD_INTERNO: ("dashboard", "reporte", "analytics", "interno"),
        SystemType.API_PUBLICA: ("api", "endpoint", "servicio"),
        SystemType.TIEMPO_REAL_IOT: ("iot", "sensor", "dispositivo", "telemetria"),
        SystemType.BATCH_ETL: ("batch", "etl", "procesamiento", "pipeline"),
        SystemType.WEB_B2C: ("web", "app", "usuario", "cliente"),
    }
    for system_type, keywords in keyword_map.items():
        if any(keyword in normalized for keyword in keywords):
            return system_type
    return SystemType.WEB_B2C


def get_defaults(system_type: SystemType | str) -> SystemDefaults:
    return DEFAULTS[SystemType(system_type)]
