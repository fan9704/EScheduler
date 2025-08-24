from typing import List
from fastapi import APIRouter, Depends

from src.services.schedule_helper import ScheduleHelperService
from src.models.pydantic.schedule_helper import (
    RateExpressionRequest, CronExpressionRequest, QuickScheduleRequest,
    ScheduleExpressionResponse, ScheduleValidationRequest, ScheduleValidationResponse,
    ScheduleTemplateResponse, CronHelpResponse
)

router = APIRouter()


def get_schedule_helper_service() -> ScheduleHelperService:
    return ScheduleHelperService()


@router.post("/rate", response_model=ScheduleExpressionResponse)
async def generate_rate_expression(
    request: RateExpressionRequest,
    service: ScheduleHelperService = Depends(get_schedule_helper_service)
) -> ScheduleExpressionResponse:
    """生成 Rate 排程表達式"""
    return service.generate_rate_expression(request)


@router.post("/cron", response_model=ScheduleExpressionResponse)
async def generate_cron_expression(
    request: CronExpressionRequest,
    service: ScheduleHelperService = Depends(get_schedule_helper_service)
) -> ScheduleExpressionResponse:
    """生成 Cron 排程表達式"""
    return service.generate_cron_expression(request)


@router.post("/quick", response_model=ScheduleExpressionResponse)
async def generate_quick_schedule(
    request: QuickScheduleRequest,
    service: ScheduleHelperService = Depends(get_schedule_helper_service)
) -> ScheduleExpressionResponse:
    """生成快速排程表達式"""
    return service.generate_quick_schedule(request)


@router.post("/validate", response_model=ScheduleValidationResponse)
async def validate_schedule_expression(
    request: ScheduleValidationRequest,
    service: ScheduleHelperService = Depends(get_schedule_helper_service)
) -> ScheduleValidationResponse:
    """驗證排程表達式"""
    return service.validate_expression(request)


@router.get("/templates", response_model=List[ScheduleTemplateResponse])
async def get_schedule_templates(
    service: ScheduleHelperService = Depends(get_schedule_helper_service)
) -> List[ScheduleTemplateResponse]:
    """獲取排程模板"""
    return service.get_schedule_templates()


@router.get("/cron-help", response_model=List[CronHelpResponse])
async def get_cron_help(
    service: ScheduleHelperService = Depends(get_schedule_helper_service)
) -> List[CronHelpResponse]:
    """獲取 Cron 表達式幫助信息"""
    return service.get_cron_help()