from unittest.mock import AsyncMock

import pytest

from src.models.pydantic.statistic import StatisticDashboardMetricResponse
from src.routers import statistic


# ---------------------------------------------------------------------------
# ✅ 測試 get_dashboard_metrics
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_dashboard_metrics_success():
    mock_service = AsyncMock()

    # 模擬 service 回傳 Pydantic 物件
    mock_service.get_dashboard_metrics.return_value = StatisticDashboardMetricResponse(
        total_tasks=10, enabled_tasks=7, disabled_tasks=3, today_executions_count=22
    )

    result = await statistic.get_dashboard_metrics(service=mock_service)

    assert isinstance(result, StatisticDashboardMetricResponse)
    assert result.total_tasks == 10
    assert result.enabled_tasks == 7
    assert result.disabled_tasks == 3
    assert result.today_executions_count == 22
    mock_service.get_dashboard_metrics.assert_awaited_once()
