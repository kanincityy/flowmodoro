"""Focus timer state machine. No GUI code, and the clock is injectable for tests."""

import time
from enum import Enum, auto
from typing import Callable


class State(Enum):
    IDLE = auto()
    FOCUSING = auto()
    PAUSED = auto()


class FocusTimer:
    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self._clock = clock
        self.state = State.IDLE
        self._started_at = 0.0
        self._frozen_elapsed = 0.0

    def start(self) -> None:
        """Begin a fresh focus session. Ignored if already focusing."""
        if self.state is State.FOCUSING:
            return
        self._started_at = self._clock()
        self._frozen_elapsed = 0.0
        self.state = State.FOCUSING

    def pause(self) -> None:
        """Stop the clock and freeze elapsed time. Ignored unless focusing."""
        if self.state is not State.FOCUSING:
            return
        self._frozen_elapsed = self._clock() - self._started_at
        self.state = State.PAUSED

    def reset(self) -> None:
        self._frozen_elapsed = 0.0
        self.state = State.IDLE

    def elapsed(self) -> int:
        """Whole seconds focused in the current session."""
        if self.state is State.FOCUSING:
            return int(self._clock() - self._started_at)
        return int(self._frozen_elapsed)
