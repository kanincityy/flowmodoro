# flowmodoro

A small, cute, vibe-coded flowmodoro timer with St. Bernard mascot inspired by my dog, Thor 🐶 Focus on a task for as long as you like. When you press pause, it suggests a break of one fifth of your focus time.

Language: Python 3.1
GUI: Tkinter. The mascot and the button are drawn on a Tkinter Canvas, not built from ready-made widgets
Project and dependency management: uv
Testing: pytest, dev-only
Packaging: PyInstaller, dev-only
Version control: git

The app has no runtime dependencies beyond Python's standard library (tkinter, time, enum).

The code is split into three parts:
- `flowmodoro/logic.py`: the break maths and time formatting.
- `flowmodoro/timer.py`: the timer state machine.
- `flowmodoro/ui.py`: the window and the mascot.

## Run

```
uv run main.py
```

## Test

```
uv run pytest
```
