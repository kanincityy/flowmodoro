from flowmodoro.timer import FocusTimer, State


class FakeClock:
    """A clock we control by hand, so tests never sleep."""

    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def make_timer():
    clock = FakeClock()
    return FocusTimer(clock=clock), clock


def test_starts_idle_with_zero_elapsed():
    timer, _ = make_timer()
    assert timer.state is State.IDLE
    assert timer.elapsed() == 0


def test_elapsed_grows_while_focusing():
    timer, clock = make_timer()
    timer.start()
    clock.advance(65)
    assert timer.state is State.FOCUSING
    assert timer.elapsed() == 65


def test_pause_freezes_elapsed():
    timer, clock = make_timer()
    timer.start()
    clock.advance(30)
    timer.pause()
    clock.advance(100)
    assert timer.state is State.PAUSED
    assert timer.elapsed() == 30


def test_pause_when_not_focusing_is_ignored():
    timer, _ = make_timer()
    timer.pause()
    assert timer.state is State.IDLE


def test_start_while_focusing_does_not_restart():
    timer, clock = make_timer()
    timer.start()
    clock.advance(10)
    timer.start()
    clock.advance(5)
    assert timer.elapsed() == 15


def test_start_after_pause_begins_fresh_session():
    timer, clock = make_timer()
    timer.start()
    clock.advance(30)
    timer.pause()
    timer.start()
    assert timer.elapsed() == 0
    clock.advance(7)
    assert timer.elapsed() == 7


def test_reset_returns_to_idle():
    timer, clock = make_timer()
    timer.start()
    clock.advance(30)
    timer.pause()
    timer.reset()
    assert timer.state is State.IDLE
    assert timer.elapsed() == 0
