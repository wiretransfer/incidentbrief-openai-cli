from .client import request_json
from .schemas import DEFAULT_MODEL, INCIDENT_SCHEMA, INSTRUCTIONS


def normalize_log(value: str) -> str:
    log = " ".join(str(value).split())
    if len(log) < 20:
        raise ValueError("Provide at least 20 characters of incident log.")
    if len(log) > 16000:
        raise ValueError("Keep incident logs under 16000 characters.")
    return log


def build_payload(log: str, model: str = DEFAULT_MODEL) -> dict:
    normalized = normalize_log(log)
    return {
        "model": model,
        "store": False,
        "max_output_tokens": 1600,
        "instructions": INSTRUCTIONS,
        "input": f"Incident log:\n{normalized}",
        "text": {
            "format": {
                "type": "json_schema",
                "name": "incidentbrief_summary",
                "strict": True,
                "schema": INCIDENT_SCHEMA,
            }
        },
    }


def run_incidentbrief(log: str, model: str | None = None, api_key: str | None = None, urlopen=None) -> dict:
    payload = build_payload(log, model or DEFAULT_MODEL)
    if urlopen is None:
        return request_json(payload, api_key=api_key)
    return request_json(payload, api_key=api_key, urlopen=urlopen)


def render_markdown(result: dict) -> str:
    lines = [
        f"# {result.get('title', 'Incident Brief')}",
        "",
        f"Severity: {result.get('severity', 'unknown')}",
        f"Status: {result.get('current_status', 'unknown')}",
        "",
        "## Impact",
    ]
    for item in result.get("impact", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Timeline"])
    for item in result.get("timeline", []):
        lines.append(f"- {item['time']}: {item['event']} ({item['evidence']})")
    lines.extend(["", "## Likely Causes"])
    for item in result.get("likely_causes", []):
        lines.append(f"- {item}")
    updates = result.get("next_updates", {})
    lines.extend(["", "## Updates", f"- Internal: {updates.get('internal', '')}", f"- Customer: {updates.get('customer', '')}"])
    lines.extend(["", "## Follow Ups"])
    for item in result.get("follow_ups", []):
        lines.append(f"- {item['owner']}: {item['item']} by {item['due']}")
    return "\n".join(lines).strip()
