from datetime import datetime, timezone

# Known new moon: January 6, 2000 at 18:14 UTC
KNOWN_NEW_MOON = datetime(2000, 1, 6, 18, 14, 0, tzinfo=timezone.utc)
SYNODIC_MONTH = 29.530588853  # days


def moon_phase() -> float:
    """Return lunation fraction 0.0 to 1.0 (0 = new moon, 0.5 = full)."""
    now = datetime.now(timezone.utc)
    days_since = (now - KNOWN_NEW_MOON).total_seconds() / 86400
    return (days_since % SYNODIC_MONTH) / SYNODIC_MONTH
