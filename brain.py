"""
brain.py — AI brain using Groq (free tier) with conversation memory.
Groq free tier: 6,000 requests/day, no credit card needed.
Sign up at: https://console.groq.com
"""

from groq import Groq

SYSTEM_PROMPT = """You are JARVIS, an advanced AI assistant similar to the one from Iron Man.
Your responses must be:
- Concise and natural for spoken conversation (2-3 sentences max unless more detail is needed)
- Free of markdown, bullet points, asterisks, or any formatting symbols
- Confident, helpful, and slightly formal in tone
- Direct — get to the point immediately

When asked for lists, speak them naturally: "First... Second... Third..."
Never use symbols like dashes, asterisks, or hashes in your response."""


class Brain:
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.history: list[dict] = []
        self.max_history = 20  # keep last 20 turns to avoid token bloat

    def think(self, user_input: str) -> str:
        self.history.append({"role": "user", "content": user_input})

        # Trim history if it gets too long
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=400,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + self.history,
        )

        reply = response.choices[0].message.content.strip()
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def clear_memory(self):
        self.history = []
        return "Memory cleared. Starting fresh."
