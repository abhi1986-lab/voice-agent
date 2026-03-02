from __future__ import annotations

import tempfile
import wave

import numpy as np
import sounddevice as sd
import webrtcvad
from faster_whisper import WhisperModel


class OfflineSpeechPipeline:
    def __init__(self, whisper_model: str = "base") -> None:
        self.model = WhisperModel(whisper_model, device="cpu", compute_type="int8")
        self.vad = webrtcvad.Vad(2)

    def record_until_silence(self, sample_rate: int = 16000, max_seconds: int = 12) -> str:
        audio = sd.rec(int(max_seconds * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
        sd.wait()
        frames = audio.flatten().tobytes()
        # basic VAD probe for activity
        frame_ms = 30
        frame_bytes = int(sample_rate * 2 * (frame_ms / 1000))
        active = any(
            self.vad.is_speech(frames[i : i + frame_bytes], sample_rate)
            for i in range(0, len(frames) - frame_bytes, frame_bytes)
        )
        if not active:
            return ""

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fp:
            with wave.open(fp.name, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(np.asarray(audio).tobytes())
            segments, _ = self.model.transcribe(fp.name)
            return " ".join(seg.text.strip() for seg in segments if seg.text.strip())
