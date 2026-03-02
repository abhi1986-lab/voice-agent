from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock, Thread
from urllib.parse import urlparse
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from voice_agent.call_joiners import TeamsJoiner
from voice_agent.models import InteractionTurn
from voice_agent.prompt_builder import StructuredPromptBuilder

app = FastAPI(title="Voice Agent API")


class PromptRequest(BaseModel):
    turns: list[InteractionTurn]
    model_path: str | None = None


class TeamsAgentRequest(BaseModel):
    meeting_url: str


jobs: dict[str, dict[str, str]] = {}
_jobs_lock = Lock()


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _set_job_status(job_id: str, status: str, error: str | None = None) -> None:
    with _jobs_lock:
        job = jobs[job_id]
        job["status"] = status
        job["updated_at"] = _now_iso()
        if error:
            job["error"] = error


def _run_teams_job(job_id: str, meeting_url: str) -> None:
    try:
        _set_job_status(job_id, "RUNNING")
        TeamsJoiner().join(meeting_url)
        _set_job_status(job_id, "SUCCESS")
    except Exception as exc:  # pragma: no cover - runtime safety for background thread
        _set_job_status(job_id, "FAILED", str(exc))


def _is_valid_teams_url(raw_url: str) -> bool:
    parsed = urlparse(raw_url)
    return parsed.scheme in {"http", "https"} and "teams" in parsed.netloc.lower()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/prompt")
def create_prompt(req: PromptRequest):
    builder = StructuredPromptBuilder(model_path=req.model_path)
    return builder.build(req.turns)


@app.post("/agents/teams")
def create_teams_agent(req: TeamsAgentRequest) -> dict[str, str]:
    if not _is_valid_teams_url(req.meeting_url):
        raise HTTPException(status_code=400, detail="meeting_url must be a valid Microsoft Teams URL")

    now = _now_iso()
    job_id = str(uuid4())
    with _jobs_lock:
        jobs[job_id] = {
            "job_id": job_id,
            "status": "STARTED",
            "created_at": now,
            "updated_at": now,
            "meeting_url": req.meeting_url,
        }

    Thread(target=_run_teams_job, args=(job_id, req.meeting_url), daemon=True).start()
    return {"job_id": job_id, "status": "STARTED"}


@app.get("/agents/{job_id}")
def get_agent_job(job_id: str) -> dict[str, str]:
    with _jobs_lock:
        job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return job


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Voice Agent</title>
    <style>
      body { font-family: sans-serif; margin: 2rem; max-width: 680px; }
      input { width: 100%; padding: 0.6rem; margin-bottom: 0.7rem; }
      button { padding: 0.6rem 1rem; cursor: pointer; }
      #status { margin-top: 1rem; padding: 0.8rem; background: #f4f4f4; border-radius: 6px; white-space: pre-wrap; }
    </style>
  </head>
  <body>
    <h1>Set Teams Agent</h1>
    <input id=\"meetingUrl\" placeholder=\"Paste Teams URL…\" />
    <button id=\"setAgent\">Set Agent</button>
    <div id=\"status\">Idle</div>

    <script>
      const statusEl = document.getElementById('status');
      const btn = document.getElementById('setAgent');

      const render = (text) => { statusEl.textContent = text; };

      const pollJob = async (jobId) => {
        const timer = setInterval(async () => {
          const res = await fetch(`/agents/${jobId}`);
          const data = await res.json();
          render(`Job: ${jobId}\nStatus: ${data.status}${data.error ? `\nError: ${data.error}` : ''}`);
          if (data.status === 'SUCCESS' || data.status === 'FAILED') {
            clearInterval(timer);
            btn.disabled = false;
          }
        }, 2000);
      };

      btn.addEventListener('click', async () => {
        btn.disabled = true;
        const meeting_url = document.getElementById('meetingUrl').value.trim();
        render('Submitting...');

        const res = await fetch('/agents/teams', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ meeting_url })
        });

        const data = await res.json();
        if (!res.ok) {
          render(`Failed to start job: ${data.detail || 'Unknown error'}`);
          btn.disabled = false;
          return;
        }

        render(`Job: ${data.job_id}\nStatus: ${data.status}`);
        pollJob(data.job_id);
      });
    </script>
  </body>
</html>
"""
