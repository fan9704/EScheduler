from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from src.dependencies.services import get_statistic_service
from src.services.statistic import StatisticService
from src.models.pydantic.statistic import StatisticDashboardMetricResponse
router = APIRouter()

@router.get("/dashboard-metrics", response_model=StatisticDashboardMetricResponse)
async def get_dashboard_metrics(
    service: StatisticService = Depends(get_statistic_service)
) -> Dict[str, Any]:
    """獲取統計儀表板指標"""
    return await service.get_dashboard_metrics()