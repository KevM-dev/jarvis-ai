"""
listener.py — Microphone input, wake word detection, and speech-to-text.
"""

import speech_recognition as sr


class Listener:
    def __init__(self, wake_words: list[str] = None):
        self.recogniser = sr.Recognizer()
        self.wake_words = wake_words or ["jarvis", "hey jarvis", "hi jarvis"]
        self.mic = sr.Microphone()

        # Calibrate on init
        print("Calibrating microphone for ambient noise...")
        with self.mic as source:
            self.recogniser.adjust_for_ambient_noise(source, duration=1)
        print("Calibration complete.")

    def _transcribe(self, audio) -> str | None:
        """Convert audio to text using Google STT."""
        try:
            return self.recogniser.recognize_google(audio).lower().strip()
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"[STT Error] Google Speech Recognition unavailable: {e}")
            return None

    def listen_for_wake_word(self) -> bool:
        """
        Listen in a short burst and return True if a wake word is detected.
        Non-blocking style — call this in a loop.
        """
        try:
            with self.mic as source:
                audio = self.recogniser.listen(source, timeout=3, phrase_time_limit=4)
            text = self._transcribe(audio)
            if text:
                for word in self.wake_words:
                    if word in text:
                        return True
        except sr.WaitTimeoutError:
            pass
        return False

    def listen_for_command(self, timeout: int = 8) -> str | None:
        """
        Listen for a full voice command after wake word is detected.
        Returns transcribed text or None if nothing was captured.
        """
        print("Listening for command...")
        try:
            with self.mic as source:
                audio = self.recogniser.listen(source, timeout=5, phrase_time_limit=timeout)
            text = self._transcribe(audio)
            return text
        except sr.WaitTimeoutError:
            return None
