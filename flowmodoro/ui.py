"""Tkinter window: cute mascot, timer, task entry, one big button."""

import tkinter as tk

from flowmodoro.logic import break_seconds, format_mmss
from flowmodoro.timer import FocusTimer, State

WIDTH, HEIGHT = 320, 480
TICK_MS = 200
FONT = "Arial Rounded MT Bold"

BG = "#FDEBD3"
BODY = "#F3D3A8"
BODY_OUTLINE = "#D9A066"
CHEEK = "#F4A9A0"
INK = "#6B4A3A"
BUTTON = "#E9946A"
BUTTON_HOVER = "#DC8257"
SPARKLE = "#E8B26A"
FUR = "#FFFBF2"
NOSE = "#3E2C2A"
TONGUE = "#F58FA0"
BROWN = "#C48E5E"
BROWN_DARK = "#A9713F"
BARREL = "#DDA55E"
BARREL_DARK = "#B9803F"
CROSS = "#E0453A"
PLACEHOLDER = "to do: ..."
PLACEHOLDER_FG = "#CDB8A0"
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
        """Soft kawaii St. Bernard puppy: brown head, white blaze, tiny rescue barrel."""
        c = self.canvas
        c.delete("mascot")
        cx, cy = WIDTH // 2, MASCOT_Y
        bob = -4 if phase else 0
        cy += bob

        def oval(x1, y1, x2, y2, fill):
            c.create_oval(cx + x1, cy + y1, cx + x2, cy + y2, fill=fill, outline="", tags="mascot")

        # head, white blaze down the middle, white cheeks
        oval(-72, -62, 72, 70, BROWN)
        oval(-26, -60, 26, 30, FUR)
        oval(-58, 2, 58, 68, FUR)
        # floppy ears hang over the sides of the head
        for sign in (-1, 1):
            pts = [(44, -50), (76, -58), (98, -24), (96, 32), (76, 52), (54, 14)]
            flat = [v for x, y in pts for v in (cx + sign * x, cy + y)]
            c.create_polygon(flat, smooth=True, fill=BROWN_DARK, outline="", tags="mascot")
        # blush + nose
        for dx in (-50, 50):
            c.create_oval(cx + dx - 12, cy + 20, cx + dx + 12, cy + 34,
                          fill=CHEEK, outline="", stipple="gray50", tags="mascot")
        oval(-9, 12, 9, 25, NOSE)
        oval(-5, 14, -1, 17, "white")

        ey = cy - 4
        if state is State.PAUSED:
            # tongue out, happy smile
            oval(-6, 33, 6, 47, TONGUE)
            for x1, x2 in ((-14, 0), (0, 14)):
                c.create_arc(cx + x1, cy + 22, cx + x2, cy + 38, start=180, extent=180,
                             style="arc", outline=INK, width=3, tags="mascot")
            c.create_line(cx, cy + 25, cx, cy + 30, fill=INK, width=3,
                          capstyle="round", tags="mascot")
        else:
            # rescue barrel held in the mouth
            x1, y1, x2, y2, r = cx - 28, cy + 60, cx + 24, cy + 82, 9
            pts = [
                x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
                x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
            ]
            c.create_polygon(pts, smooth=True, fill=BARREL, outline="", tags="mascot")
            for rx in (cx - 17, cx + 13):
                c.create_line(rx, y1 + 2, rx, y2 - 2, fill=BARREL_DARK, width=2, tags="mascot")
            c.create_oval(cx - 8, cy + 65, cx + 4, cy + 77, fill="white", outline="", tags="mascot")
            c.create_line(cx - 6, cy + 71, cx + 2, cy + 71, fill=CROSS, width=3, tags="mascot")
            c.create_line(cx - 2, cy + 67, cx - 2, cy + 75, fill=CROSS, width=3, tags="mascot")

        if state is State.IDLE:
            for dx in (-38, 38):  # sleepy closed eyes
                c.create_arc(cx + dx - 11, ey - 8, cx + dx + 11, ey + 10, start=200,
                             extent=140, style="arc", outline=INK, width=3, tags="mascot")
            c.create_text(cx + 122, cy - 70, text="z z", font=(FONT, 16),
                          fill=SPARKLE, tags="mascot")
        elif state is State.FOCUSING:
            for dx in (-38, 38):  # determined round eyes + brows
                c.create_oval(cx + dx - 6, ey - 8, cx + dx + 6, ey + 8,
                              fill=NOSE, outline="", tags="mascot")
                c.create_oval(cx + dx - 3, ey - 5, cx + dx, ey - 2,
                              fill="white", outline="", tags="mascot")
            c.create_line(cx - 48, ey - 20, cx - 28, ey - 16, fill=INK, width=3,
                          capstyle="round", tags="mascot")
            c.create_line(cx + 48, ey - 20, cx + 28, ey - 16, fill=INK, width=3,
                          capstyle="round", tags="mascot")
            spark = "\u2726" if phase else "\u2727"
            for sx, sy in ((cx - 124, cy - 50), (cx + 124, cy - 30), (cx + 98, cy - 92)):
                c.create_text(sx, sy, text=spark, font=(FONT, 20),
                              fill=SPARKLE, tags="mascot")
        else:  # PAUSED: happy
            for dx in (-38, 38):
                c.create_arc(cx + dx - 11, ey - 4, cx + dx + 11, ey + 14, start=20,
                             extent=140, style="arc", outline=INK, width=3, tags="mascot")
            c.create_text(cx + 120, cy + 56, text="\u2615", font=(FONT, 26), tags="mascot")
            c.create_text(cx - 124, cy - 60, text="\u2661", font=(FONT, 20),
                          fill=CHEEK, tags="mascot")
