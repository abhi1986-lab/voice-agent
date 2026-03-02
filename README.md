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

## Install (local machine)

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

## Run from CLI

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

## Step-by-step: run this in GitHub Codespaces and test in UI

1. Push this repository to GitHub.
2. Open the repo page → click **Code** → **Codespaces** → **Create codespace on work branch**.
3. In the Codespaces terminal, run:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

4. Start the API server:

   ```bash
   uvicorn voice_agent.api:app --host 0.0.0.0 --port 8000 --reload
   ```

5. In Codespaces, open the **Ports** tab and make port **8000** public or visible in browser.
6. Click **Open in Browser** for port 8000.
7. Open Swagger UI at:

   ```text
   https://<your-codespace-url>-8000.app.github.dev/docs
   ```

8. In the UI, open `POST /prompt` → click **Try it out**.
9. Paste this example body:

   ```json
   {
     "turns": [
       {"speaker": "agent", "text": "What do you want to achieve?"},
       {"speaker": "user", "text": "Create a launch plan for my mobile app."},
       {"speaker": "agent", "text": "What constraints should I follow?"},
       {"speaker": "user", "text": "Budget under $5k and delivery in 2 weeks."}
     ],
     "model_path": null
   }
   ```

10. Click **Execute** and verify the response has:
    - `title`
    - `system_prompt`
    - `user_prompt`
    - `output_schema`

### Optional: test the CLI in Codespaces terminal

```bash
voice-agent --channel teams --destination "https://teams.microsoft.com/l/meetup-join/..."
```

> Note: Teams browser automation and SIP dial-out may need additional account/login, media permissions, and telephony setup that are often restricted in cloud dev containers.

## Notes

- Teams sign-in or lobby acceptance may still require account/session setup.
- PSTN calls usually need a SIP provider/PBX, but the software stack remains open source.
- If no local LLM model is passed, a deterministic fallback prompt builder is used.
