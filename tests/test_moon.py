from datetime import datetime, timezone
from unittest.mock import patch

from bonfire.moon import KNOWN_NEW_MOON, SYNODIC_MONTH, moon_phase


def test_moon_phase_returns_float():
    result = moon_phase()
    assert isinstance(result, float)


def test_moon_phase_in_valid_range():
    result = moon_phase()
    assert 0.0 <= result < 1.0


def test_moon_phase_at_known_new_moon():
    """At the exact known new moon epoch, phase should be ~0.0."""
    with patch("bonfire.moon.datetime") as mock_dt:
        mock_dt.now.return_value = KNOWN_NEW_MOON
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        result = moon_phase()
    assert result < 0.01, f"Expected near 0.0, got {result}"


def test_moon_phase_at_full_moon():
    """Half a synodic month after new moon should be ~0.5 (full moon)."""
    from datetime import timedelta

    full_moon_time = KNOWN_NEW_MOON + timedelta(days=SYNODIC_MONTH / 2)
    with patch("bonfire.moon.datetime") as mock_dt:
        mock_dt.now.return_value = full_moon_time
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        result = moon_phase()
    assert 0.49 < result < 0.51, f"Expected near 0.5, got {result}"


def test_moon_phase_at_first_quarter():
    """Quarter synodic month after new moon should be ~0.25."""
    from datetime import timedelta

    quarter_time = KNOWN_NEW_MOON + timedelta(days=SYNODIC_MONTH / 4)
    with patch("bonfire.moon.datetime") as mock_dt:
        mock_dt.now.return_value = quarter_time
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        result = moon_phase()
    assert 0.24 < result < 0.26, f"Expected near 0.25, got {result}"


def test_moon_phase_wraps_around():
    """After exactly one synodic month, should be back near 0 (or very close to 1.0)."""
    from datetime import timedelta

    one_cycle = KNOWN_NEW_MOON + timedelta(days=SYNODIC_MONTH)
    with patch("bonfire.moon.datetime") as mock_dt:
        mock_dt.now.return_value = one_cycle
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        result = moon_phase()
    # Due to floating point, result may be very close to 0.0 or very close to 1.0
    assert result < 0.01 or result > 0.99, f"Expected near 0.0 or 1.0, got {result}"


def test_synodic_month_constant():
    """Sanity check: synodic month should be ~29.53 days."""
    assert 29.5 < SYNODIC_MONTH < 29.6
