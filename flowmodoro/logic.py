"""Pure functions for flowmodoro maths. No GUI code here, so they are easy to test."""

BREAK_DIVISOR = 5


def break_seconds(focus_seconds: int) -> int:
    """Suggested break length: one fifth of the focus time, rounded down."""
    return focus_seconds // BREAK_DIVISOR


def format_mmss(seconds: int) -> str:
    """Turn 1620 into '27:00'. Minutes keep growing past 59 (no hours)."""
    minutes, secs = divmod(seconds, 60)
    return f"{minutes:02d}:{secs:02d}"
