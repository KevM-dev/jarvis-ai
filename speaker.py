"""
speaker.py — Text-to-speech using ElevenLabs (primary) with pyttsx3 fallback.
"""

import io
import os
import threading


class Speaker:
    def __init__(self, elevenlabs_api_key: str = None, voice_id: str = None):
        self.elevenlabs_api_key = elevenlabs_api_key
        self.voice_id = voice_id or "nPczCjzI2devNBz1zQrb"  # ElevenLabs "Brian" voice
        self.use_elevenlabs = bool(elevenlabs_api_key)
        self._lock = threading.Lock()

        if self.use_elevenlabs:
            self._init_elevenlabs()
        else:
            self._init_pyttsx3()

    def _init_elevenlabs(self):
        try:
            from elevenlabs.client import ElevenLabs
            self.el_client = ElevenLabs(api_key=self.elevenlabs_api_key)
            print("TTS: ElevenLabs ready.")
        except ImportError:
            print("ElevenLabs package not installed — falling back to pyttsx3.")
            self.use_elevenlabs = False
            self._init_pyttsx3()

    def _init_pyttsx3(self):
        import pyttsx3
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty("voices")
        # Pick a male voice if available
        for voice in voices:
            if "male" in voice.name.lower() or "david" in voice.name.lower():
                self.engine.setProperty("voice", voice.id)
                break
        self.engine.setProperty("rate", 165)
        self.engine.setProperty("volume", 1.0)
        print("TTS: pyttsx3 ready.")

    def speak(self, text: str):
        """Speak the given text aloud."""
        print(f"\nJARVIS: {text}\n")
        with self._lock:
            if self.use_elevenlabs:
                self._speak_elevenlabs(text)
            else:
                self._speak_pyttsx3(text)

    def _speak_elevenlabs(self, text: str):
        try:
            import pygame
            audio = self.el_client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=text,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )
            audio_bytes = b"".join(audio)

            pygame.mixer.init()
            pygame.mixer.music.load(io.BytesIO(audio_bytes))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(50)
        except Exception as e:
            print(f"[ElevenLabs error] {e} — falling back to pyttsx3.")
            self.use_elevenlabs = False
            self._init_pyttsx3()
            self._speak_pyttsx3(text)

    def _speak_pyttsx3(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()
