from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

privacy_processing_activities_total = Gauge(
    "privacy_processing_activities_total",
    "Total number of registered processing activities",
    ["tenant_id", "status"],
)

privacy_activities_without_basis_total = Gauge(
    "privacy_activities_without_basis_total",
    "Active activities without a legal basis",
    ["tenant_id"],
)

privacy_localization_failures_total = Gauge(
    "privacy_localization_failures_total",
    "Activities with non-compliant localization",
    ["tenant_id"],
)

privacy_dsr_open_total = Gauge(
    "privacy_dsr_open_total",
    "Currently open data subject requests",
    ["tenant_id"],
)

privacy_dsr_overdue_total = Gauge(
    "privacy_dsr_overdue_total",
    "Overdue data subject requests",
    ["tenant_id"],
)

privacy_dsr_completion_duration_seconds = Histogram(
    "privacy_dsr_completion_duration_seconds",
    "Time to complete a DSR",
    ["tenant_id", "request_type"],
    buckets=[3600, 86400, 259200, 604800, 1209600, 2592000],
)

privacy_processor_reviews_total = Counter(
    "privacy_processor_reviews_total",
    "Total processor reviews completed",
    ["tenant_id"],
)

privacy_processor_rejections_total = Counter(
    "privacy_processor_rejections_total",
    "Processor reviews that resulted in rejection",
    ["tenant_id"],
)

privacy_processor_review_duration_seconds = Histogram(
    "privacy_processor_review_duration_seconds",
    "Time to complete a processor review",
    ["tenant_id"],
)

privacy_incidents_total = Counter(
    "privacy_incidents_total",
    "Total privacy incidents reported",
    ["tenant_id", "severity"],
)

privacy_incidents_open_total = Gauge(
    "privacy_incidents_open_total",
    "Currently open privacy incidents",
    ["tenant_id"],
)

privacy_rule_engine_duration_seconds = Histogram(
    "privacy_rule_engine_duration_seconds",
    "Rule engine evaluation duration",
    ["rule_set"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0],
)
