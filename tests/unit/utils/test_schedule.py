from datetime import datetime, timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

from src.utils import schedule


class TestGetTimezoneAwareNow:
    def test_returns_timezone_aware_datetime(self):
        tz_name = "Asia/Taipei"
        now = schedule.get_timezone_aware_now(tz_name)
        assert isinstance(now, datetime)
        assert now.tzinfo == ZoneInfo(tz_name)

    def test_different_timezone(self):
        tz_name = "UTC"
        now = schedule.get_timezone_aware_now(tz_name)
        assert now.tzinfo == ZoneInfo("UTC")

    @patch("src.utils.schedule.datetime")
    def test_now_called_with_correct_timezone(self, mock_datetime):
        mock_now = datetime(2025, 1, 1, tzinfo=ZoneInfo("Asia/Taipei"))
        mock_datetime.now.return_value = mock_now
        tz = "Asia/Taipei"
        result = schedule.get_timezone_aware_now(tz)
        mock_datetime.now.assert_called_once_with(ZoneInfo(tz))
        assert result == mock_now


class TestMatchRateExpression:
    def test_valid_expressions(self):
        valid_cases = [
            ("1 second", ("1", "second")),
            ("3 minute", ("3", "minute")),
            ("5 hour", ("5", "hour")),
            ("7 day", ("7", "day")),
        ]
        for expr, expected in valid_cases:
            match = schedule.match_rate_expression(expr)
            assert match.groups() == expected

    def test_invalid_expression_raises_value_error(self):
        invalid_cases = ["", "every 5 minutes", "5weeks", "five minutes"]
        for expr in invalid_cases:
            with pytest.raises(ValueError, match="無效的 rate 表達式格式"):
                schedule.match_rate_expression(expr)


class TestMatchRateExpressionReturnDelta:
    def test_second_unit(self):
        delta = schedule.match_rate_expression_return_delta("10 seconds")
        assert delta == timedelta(seconds=10)

    def test_minute_unit(self):
        delta = schedule.match_rate_expression_return_delta("5 minutes")
        assert delta == timedelta(minutes=5)

    def test_hour_unit(self):
        delta = schedule.match_rate_expression_return_delta("2 hours")
        assert delta == timedelta(hours=2)

    def test_day_unit(self):
        delta = schedule.match_rate_expression_return_delta("3 days")
        assert delta == timedelta(days=3)

    def test_invalid_unit_raises_error(self):
        # mock match_rate_expression 回傳不支援單位
        class FakeMatch:
            def groups(self):
                return ("5", "weeks")

        with patch(
            "src.utils.schedule.match_rate_expression", return_value=FakeMatch()
        ):
            with pytest.raises(ValueError, match="不支援的時間單位: weeks"):
                schedule.match_rate_expression_return_delta("5 weeks")

    def test_invalid_expression_propagates_error(self):
        with pytest.raises(ValueError, match="無效的 rate 表達式格式"):
            schedule.match_rate_expression_return_delta("every 5 minutes")
