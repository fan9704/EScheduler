from unittest.mock import AsyncMock

import pytest

from src.models.enum.scheduler import TaskState
from src.models.pydantic.statistic import StatisticDashboardMetricResponse
from src.services.statistic import StatisticService


@pytest.mark.asyncio
class TestStatisticService:

    async def async_set_up_service(self):
        """建立 StatisticService 並 mock repository"""
        service = StatisticService()

        # mock repository 方法
        service.task_repository.count_all_tasks = AsyncMock(return_value=10)
        service.task_repository.count_tasks_by_state = AsyncMock(side_effect=lambda state: {
            TaskState.ENABLED: 7,
            TaskState.DISABLED: 3
        }[state])
        service.execution_repository.count_today_executions = AsyncMock(return_value=5)

        return service

    async def test_get_dashboard_metrics_success(self):
        service = await self.async_set_up_service()

        result = await service.get_dashboard_metrics()

        # 檢查回傳類型
        assert isinstance(result, StatisticDashboardMetricResponse)

        # 檢查數據是否正確
        assert result.total_tasks == 10
        assert result.enabled_tasks == 7
        assert result.disabled_tasks == 3
        assert result.today_executions_count == 5

    async def test_get_dashboard_metrics_with_zero_tasks(self):
        """測試當沒有任何任務時的回傳結果"""
        service = StatisticService()

        service.task_repository.count_all_tasks = AsyncMock(return_value=0)
        service.task_repository.count_tasks_by_state = AsyncMock(return_value=0)
        service.execution_repository.count_today_executions = AsyncMock(return_value=0)

        result = await service.get_dashboard_metrics()

        assert result.total_tasks == 0
        assert result.enabled_tasks == 0
        assert result.disabled_tasks == 0
        assert result.today_executions_count == 0
