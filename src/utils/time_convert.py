from datetime import datetime, timezone


def timestamptz_to_ms(timestamp: datetime) -> int:
    return int(timestamp.timestamp() * 1000) if timestamp else None


def ms_to_timestamptz(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc) if ms else None
