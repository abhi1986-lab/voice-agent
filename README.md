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
- **FastAPI/Uvicorn**: optional API serving layer.

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

Teams:

```bash
voice-agent --channel teams --destination "https://teams.microsoft.com/l/meetup-join/..."
```

Phone via SIP:

```bash
voice-agent --channel phone --destination "sip:+15551234567@sip.example.com"
```

With local GGUF model for better prompt synthesis:

```bash
voice-agent --channel teams --destination "<teams-url>" --model-path ./models/your-model.gguf
```

## Notes

- Teams sign-in or lobby acceptance may still require account/session setup.
- PSTN calls usually need a SIP provider/PBX, but the software stack remains open source.
- If no local LLM model is passed, a deterministic fallback prompt builder is used.
