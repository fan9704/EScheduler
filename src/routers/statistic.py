from typing import Dict, Any

from fastapi import APIRouter, Depends

from src.dependencies.services import get_statistic_service
from src.models.pydantic.statistic import StatisticDashboardMetricResponse
from src.services.statistic import StatisticService

router = APIRouter()


@router.get("/dashboard-metrics", response_model=StatisticDashboardMetricResponse)
async def get_dashboard_metrics(
        service: StatisticService = Depends(get_statistic_service)
) -> Dict[str, Any]:
    """獲取統計儀表板指標"""
    return await service.get_dashboard_metrics()
