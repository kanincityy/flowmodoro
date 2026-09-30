import pytest

from flowmodoro.logic import break_seconds, format_mmss


@pytest.mark.parametrize(
    "focus, expected",
    [
        (0, 0),
        (4, 0),  # under 5s rounds down to no break
        (5, 1),
        (1620, 324),  # 27:00 focus -> 5:24 break
    ],
)
def test_break_seconds(focus, expected):
    assert break_seconds(focus) == expected


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (0, "00:00"),
        (65, "01:05"),
        (324, "05:24"),
        (3600, "60:00"),
    ],
)
def test_format_mmss(seconds, expected):
    assert format_mmss(seconds) == expected
