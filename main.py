"""
main.py — JARVIS voice assistant entry point.

Flow:
  - GUI runs on the main thread (required by Tkinter)
  - Voice loop runs on a background daemon thread
  - GUI state is updated thread-safely via a queue
"""

import os
import sys
import threading
from dotenv import load_dotenv

load_dotenv()

# ── Validate required config ──────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("ERROR: GROQ_API_KEY is not set. Add it to your .env file.")
    print("Get a free key at: https://console.groq.com")
    sys.exit(1)

# ── Imports ───────────────────────────────────────────────────────────────────
from brain import Brain
from listener import Listener
from speaker import Speaker
from gui import JarvisGUI

EXIT_PHRASES = {"goodbye", "shut down", "power off", "exit", "quit", "that's all"}


# ── Voice loop (runs in background thread) ────────────────────────────────────

def voice_loop(gui: JarvisGUI, brain: Brain, listener: Listener, speaker: Speaker):
    speaker.speak("JARVIS online. Say Hey Jarvis to activate me.")

    while True:
        try:
            # ── Idle: wait for wake word ──────────────────────────────────────
            gui.set_status("STANDBY")

            if not listener.listen_for_wake_word():
                continue

            # ── Activated: listen for command ─────────────────────────────────
            gui.set_status("LISTENING")
            speaker.speak("Yes?")

            command = listener.listen_for_command()

            if not command:
                speaker.speak("I didn't catch that. Say Hey Jarvis to try again.")
                continue

            gui.set_texts(command=command, response="")
            print(f"You: {command}")

            # ── Built-in commands ─────────────────────────────────────────────
            if any(phrase in command for phrase in EXIT_PHRASES):
                gui.set_status("STANDBY")
                gui.set_texts(response="Goodbye. Going offline.")
                speaker.speak("Goodbye. JARVIS going offline.")
                break

            if "clear memory" in command or "forget everything" in command:
                brain.clear_memory()
                reply = "Memory cleared. Starting fresh."
                gui.set_texts(response=reply)
                speaker.speak(reply)
                continue

            # ── Ask Claude / Groq ─────────────────────────────────────────────
            gui.set_status("THINKING")
            response = brain.think(command)

            gui.set_texts(response=response)
            gui.set_status("SPEAKING")
            speaker.speak(response)

        except Exception as e:
            print(f"[Error] {e}")
            gui.set_status("STANDBY")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    gui      = JarvisGUI()
    brain    = Brain(api_key=GROQ_API_KEY)
    listener = Listener(wake_words=["jarvis", "hey jarvis", "hi jarvis"])
    speaker  = Speaker()

    t = threading.Thread(
        target=voice_loop,
        args=(gui, brain, listener, speaker),
        daemon=True,
    )
    t.start()

    gui.run()   # blocks on main thread until window is closed


if __name__ == "__main__":
    main()
