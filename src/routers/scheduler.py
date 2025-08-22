from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path
from fastapi.responses import JSONResponse

from src.services.scheduler import SchedulerService
from src.models.pydantic.scheduler import (
    ScheduledTaskCreate, ScheduledTaskUpdate, ScheduledTaskResponse,
    TaskExecutionResponse, SchedulerStatsResponse, TaskStateUpdateRequest
)
from src.models.enum.scheduler import TaskState
from src.dependencies.services import get_scheduler_service

router = APIRouter()


@router.post("/",
             summary="創建排程任務",
             description="創建新的排程任務",
             response_model=ScheduledTaskResponse)
async def create_task(
    task_data: ScheduledTaskCreate,
    service: SchedulerService = Depends(get_scheduler_service)
) -> ScheduledTaskResponse:
    """創建新的排程任務"""
    return await service.create_task(task_data)


@router.get("/",
            summary="獲取所有排程任務",
            description="獲取所有排程任務列表",
            response_model=List[ScheduledTaskResponse])
async def get_all_tasks(
    state: Optional[TaskState] = Query(None, description="任務狀態過濾"),
    service: SchedulerService = Depends(get_scheduler_service)
) -> List[ScheduledTaskResponse]:
    """獲取所有排程任務"""
    return await service.get_all_tasks(state)


@router.get("/stats",
            summary="獲取排程器統計信息",
            description="獲取排程器的統計數據",
            response_model=SchedulerStatsResponse)
async def get_scheduler_stats(
    service: SchedulerService = Depends(get_scheduler_service)
) -> SchedulerStatsResponse:
    """獲取排程器統計信息"""
    return await service.get_scheduler_stats()


@router.get("/search",
            summary="搜索排程任務",
            description="根據關鍵字搜索排程任務",
            response_model=List[ScheduledTaskResponse])
async def search_tasks(
    keyword: str = Query(..., description="搜索關鍵字"),
    service: SchedulerService = Depends(get_scheduler_service)
) -> List[ScheduledTaskResponse]:
    """搜索排程任務"""
    return await service.search_tasks(keyword)


@router.get("/{task_id}",
            summary="獲取單個排程任務",
            description="根據 ID 獲取特定的排程任務",
            response_model=ScheduledTaskResponse)
async def get_task(
    task_id: int = Path(..., description="任務 ID"),
    service: SchedulerService = Depends(get_scheduler_service)
) -> ScheduledTaskResponse:
    """獲取單個排程任務"""
    return await service.get_task(task_id)


@router.put("/{task_id}",
            summary="更新排程任務",
            description="更新指定的排程任務",
            response_model=ScheduledTaskResponse)
async def update_task(
    task_id: int = Path(..., description="任務 ID"),
    task_data: ScheduledTaskUpdate = ...,
    service: SchedulerService = Depends(get_scheduler_service)
) -> ScheduledTaskResponse:
    """更新排程任務"""
    return await service.update_task(task_id, task_data)


@router.delete("/{task_id}",
               summary="刪除排程任務",
               description="刪除指定的排程任務")
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


@router.patch("/{task_id}/state",
              summary="更新任務狀態",
              description="更新指定任務的狀態",
              response_model=ScheduledTaskResponse)
async def update_task_state(
    task_id: int = Path(..., description="任務 ID"),
    state_data: TaskStateUpdateRequest = ...,
    service: SchedulerService = Depends(get_scheduler_service)
) -> ScheduledTaskResponse:
    """更新任務狀態"""
    return await service.update_task_state(task_id, state_data)


@router.get("/{task_id}/executions",
            summary="獲取任務執行記錄",
            description="獲取指定任務的執行歷史記錄",
            response_model=List[TaskExecutionResponse])
async def get_task_executions(
    task_id: int = Path(..., description="任務 ID"),
    limit: int = Query(50, ge=1, le=200, description="返回記錄數量限制"),
    service: SchedulerService = Depends(get_scheduler_service)
) -> List[TaskExecutionResponse]:
    """獲取任務執行記錄"""
    return await service.get_task_executions(task_id, limit)


@router.post("/{task_id}/trigger",
             summary="手動觸發任務執行",
             description="立即執行指定的排程任務")
async def trigger_task(
    task_id: int = Path(..., description="任務 ID"),
    service: SchedulerService = Depends(get_scheduler_service)
) -> JSONResponse:
    """手動觸發任務執行"""
    try:
        success = await service.trigger_task_now(task_id)
        return JSONResponse(
            content={"message": "任務已成功觸發", "task_id": task_id},
            status_code=200 if success else 400
        )
    except Exception as e:
        return JSONResponse(
            content={"message": f"觸發任務失敗: {str(e)}", "task_id": task_id},
            status_code=500
        )