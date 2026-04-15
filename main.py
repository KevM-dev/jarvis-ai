"""
main.py — JARVIS voice assistant entry point.

Flow:
  1. Idle: listen for wake word ("Hey Jarvis")
  2. Activated: listen for full voice command
  3. Process command with Claude AI
  4. Speak response aloud
  5. Repeat
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# ── Validate required config ──────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")  # Optional

if not ANTHROPIC_API_KEY:
    print("ERROR: ANTHROPIC_API_KEY is not set. Add it to your .env file.")
    sys.exit(1)

# ── Import modules ────────────────────────────────────────────────────────────
from brain import Brain
from listener import Listener
from speaker import Speaker

# ── Commands that exit the loop ───────────────────────────────────────────────
EXIT_PHRASES = {"goodbye", "shut down", "power off", "exit", "quit", "that's all"}

# ── Commands handled locally ──────────────────────────────────────────────────
def handle_local_command(text: str, brain: Brain, speaker: Speaker) -> bool:
    """
    Handle built-in commands without hitting the API.
    Returns True if the command was handled locally.
    """
    if any(phrase in text for phrase in EXIT_PHRASES):
        speaker.speak("Goodbye. JARVIS going offline.")
        return True  # signal to exit

    if "clear memory" in text or "forget everything" in text:
        msg = brain.clear_memory()
        speaker.speak(msg)
        return False  # handled but keep running

    return False  # not handled locally


def main():
    print("=" * 50)
    print("  JARVIS — AI Voice Assistant")
    print("  Powered by Claude & ElevenLabs")
    print("=" * 50)

    listener = Listener(wake_words=["jarvis", "hey jarvis", "hi jarvis"])
    speaker = Speaker(elevenlabs_api_key=ELEVENLABS_API_KEY)
    brain = Brain(api_key=ANTHROPIC_API_KEY)

    speaker.speak("JARVIS online. Say 'Hey Jarvis' to activate me.")

    print("\nWaiting for wake word... (say 'Hey Jarvis')\n")

    while True:
        try:
            # ── Phase 1: Wait for wake word ───────────────────────────────────
            if not listener.listen_for_wake_word():
                continue

            # ── Phase 2: Wake word detected — listen for command ──────────────
            speaker.speak("Yes?")

            command = listener.listen_for_command()

            if not command:
                speaker.speak("I didn't catch that. Say Hey Jarvis to try again.")
                continue

            print(f"You: {command}")

            # ── Phase 3: Check for local commands ─────────────────────────────
            should_exit = handle_local_command(command, brain, speaker)
            if should_exit:
                break

            # ── Phase 4: Send to Claude and speak response ────────────────────
            response = brain.think(command)
            speaker.speak(response)

        except KeyboardInterrupt:
            speaker.speak("Interrupted. JARVIS going offline.")
            print("\nShutting down.")
            break
        except Exception as e:
            print(f"[Unexpected error] {e}")
            speaker.speak("I encountered an error. Please try again.")


if __name__ == "__main__":
    main()
