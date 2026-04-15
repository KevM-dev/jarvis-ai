"""
listener.py — Microphone input, wake word detection, and speech-to-text.
Uses sounddevice for recording (Python 3.14 compatible, no PyAudio needed).
"""

import io
import wave
import tempfile
import os
import numpy as np
import sounddevice as sd
import speech_recognition as sr


SAMPLE_RATE = 16000
CHANNELS = 1


class Listener:
    def __init__(self, wake_words: list[str] = None):
        self.recogniser = sr.Recognizer()
        self.wake_words = wake_words or ["jarvis", "hey jarvis", "hi jarvis"]
        print("Listener ready.")

    def _record_audio(self, duration: int = 5) -> bytes:
        """Record audio for `duration` seconds and return as WAV bytes."""
        recording = sd.rec(
            int(duration * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
        )
        sd.wait()

        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # int16 = 2 bytes
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(recording.tobytes())
        buf.seek(0)
        return buf.read()

    def _record_until_silence(self, max_duration: int = 8, silence_threshold: int = 300) -> bytes:
        """
        Record until silence is detected or max_duration is reached.
        Returns WAV bytes.
        """
        chunk_duration = 0.5  # seconds per chunk
        chunks = []
        silence_chunks = 0
        max_silence_chunks = 3  # ~1.5 seconds of silence to stop

        for _ in range(int(max_duration / chunk_duration)):
            chunk = sd.rec(
                int(chunk_duration * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype="int16",
            )
            sd.wait()
            chunks.append(chunk)

            amplitude = np.abs(chunk).mean()
            if amplitude < silence_threshold:
                silence_chunks += 1
                if silence_chunks >= max_silence_chunks and len(chunks) > max_silence_chunks:
                    break
            else:
                silence_chunks = 0

        all_audio = np.concatenate(chunks, axis=0)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(all_audio.tobytes())
        buf.seek(0)
        return buf.read()

    def _transcribe(self, wav_bytes: bytes) -> str | None:
        """Convert WAV bytes to text using Google STT."""
        audio_file = sr.AudioFile(io.BytesIO(wav_bytes))
        with audio_file as source:
            audio = self.recogniser.record(source)
        try:
            return self.recogniser.recognize_google(audio).lower().strip()
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"[STT Error] Google Speech Recognition unavailable: {e}")
            return None

    def listen_for_wake_word(self) -> bool:
        """
        Record a short burst and return True if a wake word is detected.
        Call this in a loop.
        """
        try:
            wav = self._record_audio(duration=3)
            text = self._transcribe(wav)
            if text:
                for word in self.wake_words:
                    if word in text:
                        return True
        except Exception as e:
            print(f"[Listener error] {e}")
        return False

    def listen_for_command(self) -> str | None:
        """
        Record until silence or 8 seconds, then transcribe and return the text.
        """
        print("Listening for command...")
        try:
            wav = self._record_until_silence(max_duration=8)
            return self._transcribe(wav)
        except Exception as e:
            print(f"[Listener error] {e}")
            return None
