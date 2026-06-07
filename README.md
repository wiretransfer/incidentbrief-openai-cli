# Incidentbrief Openai Cli

A dependency-free Python CLI that turns incident logs into severity, impact, timeline, update, and follow-up briefs with the OpenAI Responses API.

IncidentBrief is a command-line Python package for turning raw incident logs into operational briefs. It calls the OpenAI Responses API at runtime and returns strict JSON or clean Markdown for responders and stakeholders.

## Setup

```powershell
python -m pip install -e .
$env:OPENAI_API_KEY = "your_api_key_here"
# or
$env:openai_api_key = "your_api_key_here"
```

## Usage

```powershell
incidentbrief --file incident-log.txt
incidentbrief --format json "09:02 checkout errors rose to 8 percent. 09:11 rollback started."
Get-Content incident-log.txt | incidentbrief
```

## Import

```python
from incidentbrief_openai_cli.workflow import build_payload, render_markdown, run_incidentbrief
```

Run tests:

```powershell
python -m unittest discover -s tests
```
