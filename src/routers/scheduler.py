from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path
from fastapi.responses import JSONResponse

from src.services.scheduler import SchedulerService
from src.models.pydantic.scheduler import (
    ScheduledTaskCreate, ScheduledTaskUpdate, ScheduledTaskResponse,
    SchedulerStatsResponse, TaskStateUpdateRequest
)
from src.models.enum.scheduler import TaskState
from src.dependencies.services import get_scheduler_service

router = APIRouter()


@router.post("/", response_model=ScheduledTaskResponse)
async def create_task(
    task_data: ScheduledTaskCreate,
    service: SchedulerService = Depends(get_scheduler_service)
) -> ScheduledTaskResponse:
    """創建新的排程任務"""
    return await service.create_task(task_data)


@router.get("/", response_model=List[ScheduledTaskResponse])
async def get_all_tasks(
    state: Optional[TaskState] = Query(None, description="任務狀態過濾"),
    service: SchedulerService = Depends(get_scheduler_service)
) -> List[ScheduledTaskResponse]:
    """獲取所有排程任務"""
    return await service.get_all_tasks(state)


@router.get("/stats", response_model=SchedulerStatsResponse)
async def get_scheduler_stats(
    service: SchedulerService = Depends(get_scheduler_service)
) -> SchedulerStatsResponse:
    """獲取排程器統計信息"""
    return await service.get_scheduler_stats()


@router.get("/search", response_model=List[ScheduledTaskResponse])
async def search_tasks(
    keyword: str = Query(..., description="搜索關鍵字"),
    service: SchedulerService = Depends(get_scheduler_service)
) -> List[ScheduledTaskResponse]:
    """搜索排程任務"""
    return await service.search_tasks(keyword)


@router.get("/{task_id}", response_model=ScheduledTaskResponse)
async def get_task(
    task_id: int = Path(..., description="任務 ID"),
    service: SchedulerService = Depends(get_scheduler_service)
) -> ScheduledTaskResponse:
    """獲取單個排程任務"""
    return await service.get_task(task_id)


@router.put("/{task_id}", response_model=ScheduledTaskResponse)
async def update_task(
    task_id: int = Path(..., description="任務 ID"),
    task_data: ScheduledTaskUpdate = ...,
    service: SchedulerService = Depends(get_scheduler_service)
) -> ScheduledTaskResponse:
    """更新排程任務"""
    return await service.update_task(task_id, task_data)


# 修復：移除 response_model=JSONResponse，改為 response_model=None 或不指定
@router.delete("/{task_id}")
async def delete_task(
    task_id: int = Path(..., description="任務 ID"),
    service: SchedulerService = Depends(get_scheduler_service)
) -> JSONResponse:
    """刪除排程任務"""
    success = await service.delete_task(task_id)
    return JSONResponse(
        content={"message": "任務已成功刪除" if success else "刪除失敗"},
        status_code=200 if success else 400
    )


@router.patch("/{task_id}/state", response_model=ScheduledTaskResponse)
async def update_task_state(
    task_id: int = Path(..., description="任務 ID"),
    state_data: TaskStateUpdateRequest = ...,
    service: SchedulerService = Depends(get_scheduler_service)
) -> ScheduledTaskResponse:
    """更新任務狀態"""
    return await service.update_task_state(task_id, state_data)


# 修復：移除 response_model=JSONResponse
@router.post("/{task_id}/trigger")
async def trigger_task(
    task_id: int = Path(..., description="任務 ID"),
    service: SchedulerService = Depends(get_scheduler_service)
) -> JSONResponse:
    """立即觸發任務執行"""
    try:
        success = await service.trigger_task_now(task_id)
        if success:
            return JSONResponse(
                status_code=200,
                content={"message": "任務觸發成功", "task_id": task_id}
            )
        else:
            return JSONResponse(
                status_code=500,
                content={"message": "任務執行失敗", "task_id": task_id}
            )
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"message": e.detail, "task_id": task_id}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"觸發任務失敗: {str(e)}", "task_id": task_id}
        )