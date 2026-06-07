import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from incidentbrief_openai_cli.client import extract_output_text, get_openai_key
from incidentbrief_openai_cli.workflow import build_payload, render_markdown, run_incidentbrief


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class IncidentBriefTests(unittest.TestCase):
    def test_reads_upper_or_lower_key_name(self):
        self.assertEqual(get_openai_key({"OPENAI_API_KEY": "upper"}), "upper")
        self.assertEqual(get_openai_key({"openai_api_key": "lower"}), "lower")

    def test_build_payload_uses_structured_outputs(self):
        payload = build_payload("09:02 errors rose and 09:19 errors returned to baseline.", "gpt-5.5")

        self.assertEqual(payload["model"], "gpt-5.5")
        self.assertFalse(payload["store"])
        self.assertEqual(payload["text"]["format"]["type"], "json_schema")
        self.assertTrue(payload["text"]["format"]["strict"])

    def test_extract_output_text_from_responses_shape(self):
        payload = {"output": [{"content": [{"text": "{\"ok\": true}"}]}]}

        self.assertEqual(extract_output_text(payload), "{\"ok\": true}")

    def test_run_incidentbrief_uses_supplied_urlopen(self):
        expected = {
            "title": "Checkout errors after payment deploy",
            "severity": "SEV2",
            "current_status": "Recovered",
            "timeline": [{"time": "09:02", "event": "Errors rose", "evidence": "8 percent checkout errors"}],
            "impact": ["US checkout failures"],
            "likely_causes": ["Payment-service deploy regression"],
            "next_updates": {"internal": "Post rollback monitoring", "customer": "Checkout has recovered"},
            "follow_ups": [{"owner": "SRE", "item": "Write postmortem", "due": "Next business day"}],
        }
        captured = {}

        def fake_urlopen(request, timeout):
            captured["body"] = json.loads(request.data.decode("utf-8"))
            captured["authorization"] = request.get_header("Authorization")
            captured["timeout"] = timeout
            return FakeResponse({"output_text": json.dumps(expected)})

        result = run_incidentbrief(
            "09:02 errors rose to 8 percent and 09:19 errors returned to baseline.",
            api_key="test-key",
            model="gpt-5.5",
            urlopen=fake_urlopen,
        )

        self.assertEqual(result, expected)
        self.assertEqual(captured["authorization"], "Bearer test-key")
        self.assertEqual(captured["timeout"], 60)

    def test_render_markdown_includes_sections(self):
        markdown = render_markdown(
            {
                "title": "Checkout incident",
                "severity": "SEV2",
                "current_status": "Recovered",
                "timeline": [{"time": "09:02", "event": "Errors rose", "evidence": "monitor"}],
                "impact": ["Checkout failures"],
                "likely_causes": ["Deploy"],
                "next_updates": {"internal": "Watch metrics", "customer": "Recovered"},
                "follow_ups": [{"owner": "SRE", "item": "Postmortem", "due": "Tomorrow"}],
            }
        )

        self.assertIn("# Checkout incident", markdown)
        self.assertIn("## Timeline", markdown)


if __name__ == "__main__":
    unittest.main()
