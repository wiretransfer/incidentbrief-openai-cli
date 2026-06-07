import json
import os
import urllib.error
import urllib.request


API_URL = "https://api.openai.com/v1/responses"


def get_openai_key(env=None):
    env = os.environ if env is None else env
    return env.get("OPENAI_API_KEY") or env.get("openai_api_key") or ""


def extract_output_text(payload: dict) -> str:
    if isinstance(payload.get("output_text"), str):
        return payload["output_text"]

    chunks: list[str] = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            text = content.get("text") or content.get("output_text")
            if isinstance(text, str):
                chunks.append(text)
    return "\n".join(chunks).strip()


def request_json(payload: dict, api_key: str | None = None, urlopen=urllib.request.urlopen) -> dict:
    api_key = api_key or get_openai_key()
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY or openai_api_key before running IncidentBrief.")

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=60) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        try:
            message = json.loads(raw).get("error", {}).get("message", raw)
        except json.JSONDecodeError:
            message = raw or error.reason
        raise RuntimeError(message) from error

    output_text = extract_output_text(body)
    if not output_text:
        raise RuntimeError("OpenAI response did not include output text.")
    return json.loads(output_text)
