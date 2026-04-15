# JARVIS — AI Voice Assistant

A Jarvis-style voice assistant powered by **Claude AI**, **ElevenLabs TTS**, and **Google Speech Recognition**.

## How It Works

```
Microphone → Wake Word Detection → Google STT → Claude AI → ElevenLabs TTS → Speaker
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

> On Windows, if PyAudio fails:
> ```bash
> pip install pipwin && pipwin install pyaudio
> ```

### 2. Configure API keys

```bash
cp .env.example .env
```

Open `.env` and add your keys:
- **ANTHROPIC_API_KEY** — Required. Get it at [console.anthropic.com](https://console.anthropic.com)
- **ELEVENLABS_API_KEY** — Optional but recommended for a premium Jarvis voice. Get it at [elevenlabs.io](https://elevenlabs.io)

### 3. Run

```bash
python main.py
```

Then say **"Hey Jarvis"** to activate.

## Voice Options

| Mode | Setup | Quality |
|---|---|---|
| pyttsx3 (default) | No API key needed | Basic |
| ElevenLabs | `ELEVENLABS_API_KEY` in `.env` | Jarvis-quality |

To change the ElevenLabs voice, update `voice_id` in `speaker.py`. Browse voices at [elevenlabs.io/voice-library](https://elevenlabs.io/voice-library).

## Built-in Commands

| Say | Action |
|---|---|
| "Hey Jarvis" | Activate |
| "Clear memory" | Reset conversation history |
| "Goodbye" / "Shut down" | Exit |

## Project Structure

```
jarvis-ai/
├── main.py          # Entry point and main loop
├── brain.py         # Claude AI integration
├── listener.py      # Wake word + speech-to-text
├── speaker.py       # Text-to-speech (ElevenLabs / pyttsx3)
├── requirements.txt
└── .env.example
```
