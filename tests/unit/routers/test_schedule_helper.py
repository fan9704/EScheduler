from unittest.mock import AsyncMock

import pytest

from src.models.pydantic.schedule_helper import (
    RateExpressionRequest,
    CronExpressionRequest,
    QuickScheduleRequest,
    ScheduleValidationRequest,
)
from src.routers import schedule_helper


# ---------------------------------------------------------------------------
# ✅ 測試 Rate Expression
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_rate_expression_success():
    """測試成功生成 Rate 排程表達式"""
    mock_service = AsyncMock()
    # ⚠️ 注意：使用 AsyncMock.return_value 要設成 coroutine 回傳值
    mock_service.generate_rate_expression = AsyncMock(
        return_value={"expression": "rate(5 minutes)"}
    )

    payload = RateExpressionRequest(value=5, unit="minutes")

    result = await schedule_helper.generate_rate_expression(
        payload, service=mock_service
    )

    assert result["expression"] == "rate(5 minutes)"
    mock_service.generate_rate_expression.assert_awaited_once_with(payload)


# ---------------------------------------------------------------------------
# ✅ 測試 Cron Expression
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_cron_expression_success():
    """測試成功生成 Cron 排程表達式"""
    mock_service = AsyncMock()
    mock_service.generate_cron_expression = AsyncMock(
        return_value={"expression": "cron(0 12 * * ? *)"}
    )

    payload = CronExpressionRequest(
        minute="0",
        hour="12",
        day_of_month="*",
        month="*",
        day_of_week="?",
        year="*",
    )

    result = await schedule_helper.generate_cron_expression(
        payload, service=mock_service
    )

    assert "cron" in result["expression"]
    mock_service.generate_cron_expression.assert_awaited_once_with(payload)


# ---------------------------------------------------------------------------
# ✅ 測試 Quick Schedule
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_quick_schedule_success():
    """測試成功生成快速排程"""
    mock_service = AsyncMock()
    mock_service.generate_quick_schedule = AsyncMock(
        return_value={"expression": "rate(1 hour)"}
    )

    payload = QuickScheduleRequest(
        type="custom_time", time="09:30", weekdays=[1, 2, 3, 4, 5]
    )

    result = await schedule_helper.generate_quick_schedule(
        payload, service=mock_service
    )

    assert result["expression"] == "rate(1 hour)"
    mock_service.generate_quick_schedule.assert_awaited_once_with(payload)


# ---------------------------------------------------------------------------
# ✅ 測試 Validate Expression
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_validate_schedule_expression_success():
    """測試排程表達式驗證成功"""
    mock_service = AsyncMock()
    mock_service.validate_expression = AsyncMock(
        return_value={"valid": True, "message": "Valid expression"}
    )

    payload = ScheduleValidationRequest(expression="rate(5 minutes)")

    result = await schedule_helper.validate_schedule_expression(
        payload, service=mock_service
    )

    assert result["valid"] is True
    assert result["message"] == "Valid expression"
    mock_service.validate_expression.assert_awaited_once_with(payload)


# ---------------------------------------------------------------------------
# ✅ 測試取得排程模板
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_schedule_templates_success():
    """測試成功取得排程模板"""
    mock_service = AsyncMock()
    mock_service.get_schedule_templates = AsyncMock(
        return_value=[{"name": "Hourly", "expression": "rate(1 hour)"}]
    )

    result = await schedule_helper.get_schedule_templates(service=mock_service)

    assert isinstance(result, list)
    assert result[0]["name"] == "Hourly"
    mock_service.get_schedule_templates.assert_awaited_once()


# ---------------------------------------------------------------------------
# ✅ 測試取得 Cron Help
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_cron_help_success():
    """測試成功取得 Cron Help"""
    mock_service = AsyncMock()
    mock_service.get_cron_help = AsyncMock(
        return_value=[{"field": "minute", "description": "Minute field"}]
    )

    result = await schedule_helper.get_cron_help(service=mock_service)

    assert isinstance(result, list)
    assert result[0]["field"] == "minute"
    mock_service.get_cron_help.assert_awaited_once()
