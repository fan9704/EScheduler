import re

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def get_timezone_aware_now(timezone: str = "Asia/Taipei") -> datetime:
    """獲取帶時區的當前時間"""
    tz = ZoneInfo(timezone)
    return datetime.now(tz)

def match_rate_expression(rate_expr: str):
    match = re.match(r'(\d+)\s+(second|seconds|minute|minutes|hour|hours|day|days)', rate_expr)
    if not match:
        raise ValueError("無效的 rate 表達式格式")
    return match

def match_rate_expression_return_delta(rate_expr: str):
    match = match_rate_expression(rate_expr)
    value, unit = match.groups()
    value = int(value)
    if unit.startswith('second'):
        delta = timedelta(seconds=value)
    elif unit.startswith('minute'):
        delta = timedelta(minutes=value)
    elif unit.startswith('hour'):
        delta = timedelta(hours=value)
    elif unit.startswith('day'):
        delta = timedelta(days=value)
    else:
        raise ValueError(f"不支援的時間單位: {unit}")
    return delta
