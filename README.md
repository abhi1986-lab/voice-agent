# Voice Agent (100% Open Source Stack)

This project provides a local-first voice agent that can:

1. Join a call over **Microsoft Teams (web meeting URL)** or **phone via SIP dial-out**.
2. Run guided discovery with the user in **maximum 10 cross conversations**.
3. Produce a **structured prompt package** (system prompt + user prompt + output schema) that can be sent to any AI model.

## Open-source components used

- **Playwright**: browser automation to join Teams web meetings.
- **baresip (external binary)**: SIP/phone dial-out.
- **faster-whisper**: offline speech-to-text.
- **webrtcvad**: open-source voice activity detection.
- **llama-cpp-python**: local LLM inference with GGUF models.
- **FastAPI/Uvicorn**: API serving layer + minimal UI.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
playwright install chromium
```

Install SIP dialer (Linux example):

```bash
sudo apt-get install baresip
```

## Run

### 1) Run web API + UI

```bash
voice-agent serve --host 0.0.0.0 --port 8000 --reload
```

Equivalent direct command:

```bash
uvicorn voice_agent.api:app --host 0.0.0.0 --port 8000 --reload
```

- Open API docs: `http://localhost:8000/docs`
- Open UI page: `http://localhost:8000/`

### 2) Use the UI

- Paste a Teams meeting URL into **Paste Teams URL…**
- Click **Set Agent**
- The UI immediately shows a `job_id` and starts polling every 2 seconds.
- Status transitions: `STARTED` → `RUNNING` → `SUCCESS` or `FAILED`.

### 3) Use API directly

Start a Teams join job:

```bash
curl -X POST http://localhost:8000/agents/teams \
  -H "Content-Type: application/json" \
  -d '{"meeting_url":"https://teams.microsoft.com/l/meetup-join/..."}'
```

Check job status:

```bash
curl http://localhost:8000/agents/<job_id>
```

Health check:

```bash
curl http://localhost:8000/health
```

### 4) Existing CLI call mode

Teams:

```bash
voice-agent call --channel teams --destination "https://teams.microsoft.com/l/meetup-join/..."
```

Phone via SIP:

```bash
voice-agent call --channel phone --destination "sip:+15551234567@sip.example.com"
```

With local GGUF model for better prompt synthesis:

```bash
voice-agent call --channel teams --destination "<teams-url>" --model-path ./models/your-model.gguf
```

## Notes

- Teams joining in Codespaces runs Playwright in **headless mode** by default.
- Teams sign-in, tenant policy checks, or lobby acceptance may still block auto-join.
- PSTN calls usually need a SIP provider/PBX, but the software stack remains open source.
- If no local LLM model is passed, a deterministic fallback prompt builder is used.
