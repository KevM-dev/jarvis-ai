"""
gui.py — Jarvis-style animated GUI using Tkinter.

Visual elements:
  - Rotating segmented rings (outer, middle, inner)
  - Pulsing core with glow
  - Status indicator that changes colour per state
  - Audio level bars (active when LISTENING or SPEAKING)
  - Conversation text panel
  - Corner brackets & grid overlay
"""

import tkinter as tk
import math
import random
import queue

# ── Palette ───────────────────────────────────────────────────────────────────
BG       = "#050510"
C_BRIGHT = "#00d4ff"   # cyan
C_MID    = "#005577"
C_DIM    = "#001a26"
C_ACCENT = "#0044ff"   # blue accent

STATUS_COLOURS = {
    "STANDBY":   "#00d4ff",
    "LISTENING": "#00ff88",
    "THINKING":  "#ffaa00",
    "SPEAKING":  "#ff6622",
}

W, H  = 900, 660
CX    = W // 2
CY    = 255   # centre of animation area


class JarvisGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S")
        self.root.configure(bg=BG)
        self.root.geometry(f"{W}x{H}")
        self.root.resizable(False, False)

        # State
        self._status        = "STANDBY"
        self._command_text  = ""
        self._response_text = ""
        self._queue: queue.Queue = queue.Queue()

        # Animation vars
        self._rot1   = 0.0    # outer ring (clockwise)
        self._rot2   = 0.0    # middle ring (counter-clockwise)
        self._rot3   = 0.0    # inner arc (fast)
        self._pulse_t = 0.0   # drives sine pulse on core
        self._bars   = [random.uniform(0.05, 0.2) for _ in range(28)]
        self._bar_tgt = list(self._bars)

        self._build_ui()
        self._tick()          # start animation loop

    # ── UI layout ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.canvas = tk.Canvas(
            self.root, width=W, height=490,
            bg=BG, highlightthickness=0,
        )
        self.canvas.pack()

        panel = tk.Frame(self.root, bg="#07071a", height=170)
        panel.pack(fill=tk.X)
        panel.pack_propagate(False)

        divider = tk.Frame(panel, bg=C_MID, height=1)
        divider.pack(fill=tk.X)

        self._lbl_you = tk.Label(
            panel, text="",
            font=("Consolas", 10), fg="#005577", bg="#07071a",
            anchor="w", wraplength=860, justify="left",
        )
        self._lbl_you.pack(padx=24, pady=(14, 2), fill=tk.X)

        self._lbl_jarvis = tk.Label(
            panel, text="",
            font=("Consolas", 12), fg=C_BRIGHT, bg="#07071a",
            anchor="w", wraplength=860, justify="left",
        )
        self._lbl_jarvis.pack(padx=24, pady=(2, 14), fill=tk.X)

    # ── Thread-safe API ───────────────────────────────────────────────────────

    def set_status(self, status: str):
        """Call from any thread."""
        self._queue.put(("status", status))

    def set_texts(self, command: str = None, response: str = None):
        """Call from any thread."""
        self._queue.put(("texts", command, response))

    # ── Animation loop ────────────────────────────────────────────────────────

    def _tick(self):
        self._drain_queue()
        self._draw()
        self.root.after(16, self._tick)   # ~60 fps

    def _drain_queue(self):
        while not self._queue.empty():
            item = self._queue.get_nowait()
            if item[0] == "status":
                self._status = item[1]
            elif item[0] == "texts":
                _, cmd, resp = item
                if cmd  is not None: self._command_text  = cmd
                if resp is not None: self._response_text = resp
                self._lbl_you.config(
                    text=f"  YOU      {self._command_text}" if self._command_text else "")
                self._lbl_jarvis.config(
                    text=f"  JARVIS   {self._response_text}" if self._response_text else "")

    # ── Main draw ─────────────────────────────────────────────────────────────

    def _draw(self):
        c = self.canvas
        c.delete("all")

        colour = STATUS_COLOURS.get(self._status, C_BRIGHT)

        # Advance animation
        self._rot1    = (self._rot1 + 0.35) % 360
        self._rot2    = (self._rot2 - 0.55) % 360
        self._rot3    = (self._rot3 + 1.1)  % 360
        self._pulse_t += 0.05
        pulse = (math.sin(self._pulse_t) + 1) / 2   # 0..1

        self._update_bars()

        # ── Grid ─────────────────────────────────────────────────────────────
        for x in range(0, W, 60):
            c.create_line(x, 0, x, 490, fill="#09091f", width=1)
        for y in range(0, 490, 60):
            c.create_line(0, y, W, y, fill="#09091f", width=1)

        # ── Outer decorative tick ring ────────────────────────────────────────
        self._tick_ring(c, CX, CY, r=235, n=72, col=C_DIM,  length=6,  width=1)
        self._tick_ring(c, CX, CY, r=235, n=12, col=C_MID,  length=14, width=2)

        # ── Outer rotating arcs ───────────────────────────────────────────────
        self._arc(c, CX, CY, 225, self._rot1,         120, colour, 2)
        self._arc(c, CX, CY, 225, self._rot1 + 145,    60, colour, 2)
        self._arc(c, CX, CY, 225, self._rot1 + 220,    90, colour, 2)

        # ── Middle ring ───────────────────────────────────────────────────────
        self._ring(c, CX, CY, 175, C_DIM, 1)
        self._arc(c, CX, CY, 175, self._rot2,         140, C_ACCENT, 2)
        self._arc(c, CX, CY, 175, self._rot2 + 165,    45, C_ACCENT, 2)
        self._arc(c, CX, CY, 175, self._rot2 + 230,    80, C_ACCENT, 2)

        # Ring labels
        labels = ["SYS", "NET", "MEM", "CPU", "I/O", "PWR", "SEC", "COM"]
        for i, lbl in enumerate(labels):
            angle = math.radians(i * 45 - 90)
            x = CX + 203 * math.cos(angle)
            y = CY + 203 * math.sin(angle)
            c.create_text(x, y, text=lbl, font=("Consolas", 7), fill=C_MID)

        # ── Inner spinning arc ────────────────────────────────────────────────
        self._arc(c, CX, CY, 125, self._rot3,         210, colour, 3)
        self._arc(c, CX, CY, 125, self._rot3 + 230,    55, colour, 3)

        # ── Pulsing rings ─────────────────────────────────────────────────────
        pr = 85 + pulse * 9
        self._ring(c, CX, CY, pr,     colour,                    1)
        self._ring(c, CX, CY, pr - 7, self._blend(C_DIM, colour, pulse * 0.25), 1)

        # ── Core glow ─────────────────────────────────────────────────────────
        gr = 44 + pulse * 6
        c.create_oval(CX - gr, CY - gr, CX + gr, CY + gr,
                      fill=self._blend(BG, colour, 0.12), outline="")
        c.create_oval(CX - 26, CY - 26, CX + 26, CY + 26,
                      fill=self._blend(BG, colour, 0.35 + pulse * 0.2),
                      outline=colour, width=1)
        c.create_oval(CX - 9, CY - 9, CX + 9, CY + 9,
                      fill=colour, outline="")

        # ── Status text ───────────────────────────────────────────────────────
        c.create_text(CX, CY + 118,
                      text=f"◉  {self._status}",
                      font=("Consolas", 12, "bold"), fill=colour)

        # ── Title ─────────────────────────────────────────────────────────────
        c.create_text(CX, 26,
                      text="J . A . R . V . I . S",
                      font=("Consolas", 17, "bold"), fill=C_BRIGHT)
        c.create_text(CX, 48,
                      text="JUST A RATHER VERY INTELLIGENT SYSTEM",
                      font=("Consolas", 8), fill=C_MID)

        # ── Audio bars ────────────────────────────────────────────────────────
        if self._status in ("LISTENING", "SPEAKING"):
            self._draw_bars(c, colour)

        # ── Corner brackets ───────────────────────────────────────────────────
        sz = 22
        corners = [
            (12, 12, 12 + sz, 12, 12, 12, 12, 12 + sz),          # TL
            (W-12-sz, 12, W-12, 12, W-12, 12, W-12, 12+sz),       # TR
            (12, 478-sz, 12, 478, 12, 478, 12+sz, 478),           # BL
            (W-12-sz, 478, W-12, 478, W-12, 478, W-12, 478-sz),   # BR
        ]
        for x1,y1,x2,y2,x3,y3,x4,y4 in corners:
            c.create_line(x1,y1,x2,y2, fill=colour, width=2)
            c.create_line(x3,y3,x4,y4, fill=colour, width=2)

    # ── Drawing helpers ───────────────────────────────────────────────────────

    def _ring(self, c, cx, cy, r, col, width=1):
        c.create_oval(cx-r, cy-r, cx+r, cy+r, outline=col, width=width)

    def _arc(self, c, cx, cy, r, start, extent, col, width=2):
        c.create_arc(cx-r, cy-r, cx+r, cy+r,
                     start=start, extent=extent,
                     outline=col, style=tk.ARC, width=width)

    def _tick_ring(self, c, cx, cy, r, n, col, length=8, width=1):
        for i in range(n):
            a = math.radians(i * 360 / n)
            x1 = cx + r * math.cos(a)
            y1 = cy - r * math.sin(a)
            x2 = cx + (r + length) * math.cos(a)
            y2 = cy - (r + length) * math.sin(a)
            c.create_line(x1, y1, x2, y2, fill=col, width=width)

    def _draw_bars(self, c, colour):
        n       = len(self._bars)
        spacing = 14
        bar_w   = 8
        total_w = n * spacing
        x0      = CX - total_w // 2
        base_y  = CY + 152

        for i, h in enumerate(self._bars):
            bh = max(3, int(h * 45))
            x  = x0 + i * spacing
            c.create_rectangle(x, base_y - bh, x + bar_w, base_y,
                                fill=colour, outline="")

    def _update_bars(self):
        active = self._status in ("LISTENING", "SPEAKING")
        for i in range(len(self._bars)):
            if active:
                if random.random() < 0.25:
                    self._bar_tgt[i] = random.uniform(0.15, 1.0)
            else:
                self._bar_tgt[i] = random.uniform(0.03, 0.12)
            self._bars[i] += (self._bar_tgt[i] - self._bars[i]) * 0.2

    @staticmethod
    def _blend(c1: str, c2: str, t: float) -> str:
        t = max(0.0, min(1.0, t))
        r1,g1,b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
        r2,g2,b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
        r = int(r1 + (r2-r1)*t)
        g = int(g1 + (g2-g1)*t)
        b = int(b1 + (b2-b1)*t)
        return f"#{r:02x}{g:02x}{b:02x}"

    # ── Run ───────────────────────────────────────────────────────────────────

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.root.mainloop()
