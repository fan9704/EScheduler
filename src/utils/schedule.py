import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, Match


def get_timezone_aware_now(timezone: str = "Asia/Taipei") -> datetime:
    """獲取帶時區的當前時間"""
    tz = ZoneInfo(timezone)
    return datetime.now(tz)


def match_rate_expression(rate_expr: str) -> Match[str]:
    """
    驗證並匹配 rate 表達式
    回傳 Match 物件，若不匹配則拋出 ValueError
    """
    match = re.match(
        r"(\d+)\s+(second|seconds|minute|minutes|hour|hours|day|days)", rate_expr
    )
    if not match:
        raise ValueError(f"無效的 rate 表達式格式: {rate_expr}")

    # 這裡 mypy 會知道回傳的一定是 Match[str] 而不是 Optional
    return match


def match_rate_expression_return_delta(rate_expr: str) -> timedelta:
    """將 rate 表達式轉換為 timedelta"""
    match = match_rate_expression(rate_expr)

    # 使用 .groups() 時，mypy 需要確認這些值不是 None
    value_str, unit = match.groups()

    # 顯式轉型以確保型別安全
    value = int(value_str)

    if unit.startswith("second"):
        return timedelta(seconds=value)
    if unit.startswith("minute"):
        return timedelta(minutes=value)
    if unit.startswith("hour"):
        return timedelta(hours=value)
    if unit.startswith("day"):
        return timedelta(days=value)

    raise ValueError(f"不支援的時間單位: {unit}")
