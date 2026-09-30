"""Tkinter window: cute mascot, timer, task entry, one big button."""

import tkinter as tk

from flowmodoro.logic import break_seconds, format_mmss
from flowmodoro.timer import FocusTimer, State

WIDTH, HEIGHT = 320, 480
TICK_MS = 200
FONT = "Arial Rounded MT Bold"

BG = "#FFF1F5"
BODY = "#FFD6E8"
BODY_OUTLINE = "#F7A8C8"
CHEEK = "#FF9EBB"
INK = "#6B4E71"
BUTTON = "#FF8FB1"
BUTTON_HOVER = "#FF7AA3"
SPARKLE = "#B39DDB"
PLACEHOLDER = "to do: ..."
PLACEHOLDER_FG = "#C9B3CF"
MASCOT_Y = 165


class App:
    def __init__(self, root: tk.Tk, timer: FocusTimer | None = None):
        self.root = root
        self.timer = timer or FocusTimer()
        self._frame = 0
        self._drawn_key = None
        self._current_task = ""

        root.title("flowmodoro")
        root.configure(bg=BG)
        root.geometry(f"{WIDTH}x{HEIGHT}")
        root.resizable(False, False)
        root.attributes("-topmost", True)

        self.canvas = tk.Canvas(
            root, width=WIDTH, height=HEIGHT, bg=BG, highlightthickness=0
        )
        self.canvas.pack()

        self.time_id = self.canvas.create_text(
            WIDTH // 2, 290, text="00:00", font=(FONT, 46), fill=INK
        )
        self.status_id = self.canvas.create_text(
            WIDTH // 2, 346, text="", font=(FONT, 13), fill=INK,
            width=WIDTH - 40, justify="center",
        )

        self.task = tk.Entry(
            root, font=(FONT, 13), justify="center", relief="flat",
            bg="white", fg=INK, insertbackground=INK,
            highlightthickness=2, highlightbackground=BODY,
            highlightcolor=BODY_OUTLINE,
        )
        self.canvas.create_window(WIDTH // 2, 36, window=self.task, width=260, height=34)
        self.task.bind("<FocusIn>", lambda _e: self._hide_placeholder())
        self.task.bind("<FocusOut>", lambda _e: self._show_placeholder())
        self.task.bind("<Return>", lambda _e: self._on_enter())
        self._show_placeholder()

        self._build_button()
        self.reset_id = self.canvas.create_text(
            WIDTH // 2, 456, text="reset", font=(FONT, 10), fill=SPARKLE,
            state="hidden", tags="reset",
        )
        self.canvas.tag_bind("reset", "<Button-1>", lambda _e: self._on_reset())
        self.canvas.tag_bind("reset", "<Enter>", lambda _e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("reset", "<Leave>", lambda _e: self.canvas.config(cursor=""))

        self._render()
        self._tick()

    # --- button -----------------------------------------------------------

    def _build_button(self) -> None:
        x1, y1, x2, y2, r = 80, 402, 240, 444, 20
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        self.button_bg = self.canvas.create_polygon(
            points, smooth=True, fill=BUTTON, outline="", tags="button"
        )
        self.button_text = self.canvas.create_text(
            WIDTH // 2, (y1 + y2) // 2, text="Start", font=(FONT, 15),
            fill="white", tags="button",
        )
        self.canvas.tag_bind("button", "<Button-1>", lambda _e: self._on_button())
        self.canvas.tag_bind("button", "<Enter>", self._hover_on)
        self.canvas.tag_bind("button", "<Leave>", self._hover_off)

    def _hover_on(self, _event) -> None:
        self.canvas.itemconfig(self.button_bg, fill=BUTTON_HOVER)
        self.canvas.config(cursor="hand2")

    def _hover_off(self, _event) -> None:
        self.canvas.itemconfig(self.button_bg, fill=BUTTON)
        self.canvas.config(cursor="")

    # --- actions ----------------------------------------------------------

    def _on_button(self) -> None:
        if self.timer.state is State.FOCUSING:
            self.timer.pause()
        else:
            # Move the typed to-do out of the box and into the status text.
            self._current_task = self._typed_task() or "Untitled focus"
            self.task.delete(0, "end")
            self.root.focus_set()
            self._show_placeholder()
            self.timer.start()
        self._render()

    def _on_enter(self) -> None:
        # Enter starts a session but never pauses one by accident.
        if self.timer.state is not State.FOCUSING:
            self._on_button()

    def _on_reset(self) -> None:
        self.timer.reset()
        self._render()

    # --- drawing ----------------------------------------------------------

    def _typed_task(self) -> str:
        """Text the user typed, ignoring the grey placeholder."""
        text = self.task.get()
        return "" if text == PLACEHOLDER and self.task.cget("fg") == PLACEHOLDER_FG else text.strip()

    def _show_placeholder(self) -> None:
        if not self.task.get():
            self.task.insert(0, PLACEHOLDER)
            self.task.config(fg=PLACEHOLDER_FG)

    def _hide_placeholder(self) -> None:
        if self.task.cget("fg") == PLACEHOLDER_FG:
            self.task.delete(0, "end")
            self.task.config(fg=INK)

    def _task_name(self) -> str:
        return self._current_task

    def _tick(self) -> None:
        self._frame += 1
        self._render()
        self.root.after(TICK_MS, self._tick)

    def _render(self) -> None:
        state = self.timer.state
        elapsed = self.timer.elapsed()
        self.canvas.itemconfig(self.time_id, text=format_mmss(elapsed))

        if state is State.IDLE:
            status = "What are we focusing on?"
            button = "Start"
        elif state is State.FOCUSING:
            status = f"{self._task_name()}\nyou're in the zone"
            button = "Pause"
        else:
            brk = break_seconds(elapsed)
            if brk == 0:
                status = "Quick one! No break needed, keep going"
            else:
                status = f"Nice work on {self._task_name()}!\nTake a {format_mmss(brk)} break"
            button = "New focus"
        self.canvas.itemconfig(self.status_id, text=status)
        self.canvas.itemconfig(self.button_text, text=button)
        self.canvas.itemconfig(
            self.reset_id, state="normal" if state is State.PAUSED else "hidden"
        )

        # Redraw the mascot only when its look changes.
        sparkle_phase = (self._frame // 3) % 2 if state is State.FOCUSING else 0
        key = (state, sparkle_phase)
        if key != self._drawn_key:
            self._draw_mascot(state, sparkle_phase)
            self._drawn_key = key

    def _draw_mascot(self, state: State, phase: int) -> None:
        c = self.canvas
        c.delete("mascot")
        cx, cy = WIDTH // 2, MASCOT_Y
        bob = -4 if phase else 0

        # body blob + little ears
        for dx in (-46, 46):
            c.create_oval(cx + dx - 18, cy - 82 + bob, cx + dx + 18, cy - 44 + bob,
                          fill=BODY, outline=BODY_OUTLINE, width=3, tags="mascot")
        c.create_oval(cx - 74, cy - 64 + bob, cx + 74, cy + 70 + bob,
                      fill=BODY, outline=BODY_OUTLINE, width=3, tags="mascot")
        # cheeks
        for dx in (-44, 44):
            c.create_oval(cx + dx - 12, cy + 16 + bob, cx + dx + 12, cy + 30 + bob,
                          fill=CHEEK, outline="", stipple="gray50", tags="mascot")

        ey = cy + 2 + bob
        if state is State.IDLE:
            for dx in (-28, 28):  # sleepy closed eyes
                c.create_arc(cx + dx - 12, ey - 8, cx + dx + 12, ey + 10, start=200,
                             extent=140, style="arc", outline=INK, width=3, tags="mascot")
            c.create_arc(cx - 8, cy + 24, cx + 8, cy + 38, start=200, extent=140,
                         style="arc", outline=INK, width=3, tags="mascot")
            c.create_text(cx + 70, cy - 60, text="z z", font=(FONT, 16),
                          fill=SPARKLE, tags="mascot")
        elif state is State.FOCUSING:
            for dx in (-28, 28):  # determined round eyes + brows
                c.create_oval(cx + dx - 7, ey - 7, cx + dx + 7, ey + 7,
                              fill=INK, outline="", tags="mascot")
                c.create_oval(cx + dx - 3, ey - 4, cx + dx, ey - 1,
                              fill="white", outline="", tags="mascot")
            c.create_line(cx - 38, ey - 18, cx - 18, ey - 14, fill=INK, width=3,
                          capstyle="round", tags="mascot")
            c.create_line(cx + 38, ey - 18, cx + 18, ey - 14, fill=INK, width=3,
                          capstyle="round", tags="mascot")
            c.create_line(cx - 8, cy + 30, cx + 8, cy + 30, fill=INK, width=3,
                          capstyle="round", tags="mascot")
            spark = "✦" if phase else "✧"
            for sx, sy in ((cx - 100, cy - 30), (cx + 100, cy - 10), (cx + 84, cy - 76)):
                c.create_text(sx, sy, text=spark, font=(FONT, 20),
                              fill=SPARKLE, tags="mascot")
        else:  # PAUSED: happy
            for dx in (-28, 28):
                c.create_arc(cx + dx - 12, ey - 6, cx + dx + 12, ey + 14, start=20,
                             extent=140, style="arc", outline=INK, width=3, tags="mascot")
            c.create_arc(cx - 12, cy + 16, cx + 12, cy + 40, start=200, extent=140,
                         style="chord", fill=CHEEK, outline=INK, width=2, tags="mascot")
            c.create_text(cx + 92, cy + 48, text="☕", font=(FONT, 26), tags="mascot")
            c.create_text(cx - 96, cy - 40, text="♡", font=(FONT, 20),
                          fill=CHEEK, tags="mascot")
