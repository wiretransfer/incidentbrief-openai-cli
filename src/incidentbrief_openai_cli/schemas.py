DEFAULT_MODEL = "gpt-5.5"
TOOL_NAME = "IncidentBrief"

INSTRUCTIONS = (
    "Create an operational incident brief from raw logs. "
    "Separate observed evidence from likely causes. "
    "Use concise language suitable for responders and customer-facing updates."
)

EXAMPLE_TEXT = (
    "09:02 checkout errors rose to 8 percent after payment-service deploy 2026.06.07.3. "
    "09:07 support reported customer checkout failures in the US region. "
    "09:11 rollback started. 09:19 errors returned to baseline."
)

INCIDENT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "title",
        "severity",
        "current_status",
        "timeline",
        "impact",
        "likely_causes",
        "next_updates",
        "follow_ups",
    ],
    "properties": {
        "title": {"type": "string"},
        "severity": {"type": "string", "enum": ["SEV1", "SEV2", "SEV3", "SEV4"]},
        "current_status": {"type": "string"},
        "timeline": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["time", "event", "evidence"],
                "properties": {
                    "time": {"type": "string"},
                    "event": {"type": "string"},
                    "evidence": {"type": "string"},
                },
            },
        },
        "impact": {"type": "array", "items": {"type": "string"}},
        "likely_causes": {"type": "array", "items": {"type": "string"}},
        "next_updates": {
            "type": "object",
            "additionalProperties": False,
            "required": ["internal", "customer"],
            "properties": {
                "internal": {"type": "string"},
                "customer": {"type": "string"},
            },
        },
        "follow_ups": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["owner", "item", "due"],
                "properties": {
                    "owner": {"type": "string"},
                    "item": {"type": "string"},
                    "due": {"type": "string"},
                },
            },
        },
    },
}
