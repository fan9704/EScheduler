import logging
import re
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException
from croniter import croniter

from src.models.pydantic.scheduler import (
    ScheduledTaskCreate, ScheduledTaskUpdate, ScheduledTaskResponse,
    TaskExecutionResponse, SchedulerStatsResponse, TaskStateUpdateRequest
)
from src.models.enum.scheduler import TaskState, ExecutionStatus
from src.repositories.scheduler import ScheduledTaskRepository, TaskExecutionRepository
from src.dependencies.repositories import get_scheduled_task_repository, get_task_execution_repository
from src.services.scheduler_engine import scheduler_engine

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self):
        self.task_repository: ScheduledTaskRepository = get_scheduled_task_repository()
        self.execution_repository: TaskExecutionRepository = get_task_execution_repository()
        self.engine = scheduler_engine

    def _task_to_dict(self, task) -> Dict[str, Any]:
        """將 Tortoise ORM 模型轉換為字典"""
        return {
            'id': task.id,
            'name': task.name,
            'description': task.description,
            'schedule_expression': task.schedule_expression,
            'timezone': task.timezone,
            'target_type': task.target_type,
            'target_arn': task.target_arn,
            'target_input': task.target_input,
            'state': task.state,
            'max_retry_attempts': task.max_retry_attempts,
            'retry_policy': task.retry_policy,
            'dead_letter_config': task.dead_letter_config
        }

    async def create_task(self, task_data: ScheduledTaskCreate) -> ScheduledTaskResponse:
        """創建新的排程任務"""
        # 檢查任務名稱是否已存在
        existing_task = await self.task_repository.get_by_name(task_data.name)
        if existing_task:
            raise HTTPException(status_code=400, detail="任務名稱已存在")

        # 驗證排程表達式
        next_execution = self._calculate_next_execution(task_data.schedule_expression, task_data.timezone)
        
        # 創建任務
        task_dict = task_data.dict()
        task_dict["next_execution_time"] = next_execution
        task_dict["state"] = TaskState.ENABLED
        
        task = await self.task_repository.create(**task_dict)
        logger.info(f"創建新任務: {task.name} (ID: {task.id})")
        
        # 添加到排程引擎
        if task.state == TaskState.ENABLED:
            await self.engine.add_job(task.id, task.schedule_expression, self._task_to_dict(task))
        
        return ScheduledTaskResponse.from_orm(task)

    async def get_task(self, task_id: int) -> ScheduledTaskResponse:
        """獲取單個任務"""
        try:
            task = await self.task_repository.get_by_id(task_id)
            return ScheduledTaskResponse.from_orm(task)
        except Exception:
            raise HTTPException(status_code=404, detail="任務不存在")

    async def get_all_tasks(self, state: Optional[TaskState] = None) -> List[ScheduledTaskResponse]:
        """獲取所有任務"""
        if state:
            tasks = await self.task_repository.get_tasks_by_state(state)
        else:
            tasks = await self.task_repository.find_all()
        
        return [ScheduledTaskResponse.from_orm(task) for task in tasks]

    async def update_task(self, task_id: int, task_data: ScheduledTaskUpdate) -> ScheduledTaskResponse:
        """更新任務"""
        try:
            task = await self.task_repository.get_by_id(task_id)
        except Exception:
            raise HTTPException(status_code=404, detail="任務不存在")

        # 更新數據
        update_dict = task_data.dict(exclude_unset=True)
        
        # 如果更新了排程表達式，重新計算下次執行時間
        if "schedule_expression" in update_dict:
            timezone = update_dict.get("timezone", task.timezone)
            next_execution = self._calculate_next_execution(update_dict["schedule_expression"], timezone)
            update_dict["next_execution_time"] = next_execution

        # 執行更新
        for key, value in update_dict.items():
            setattr(task, key, value)
        
        await task.save()
        logger.info(f"更新任務: {task.name} (ID: {task.id})")
        
        # 更新排程引擎中的任務
        if task.state == TaskState.ENABLED:
            await self.engine.add_job(task.id, task.schedule_expression, self._task_to_dict(task))
        else:
            await self.engine.remove_job(task.id)
        
        return ScheduledTaskResponse.from_orm(task)

    async def delete_task(self, task_id: int) -> bool:
        """刪除任務"""
        try:
            task = await self.task_repository.get_by_id(task_id)
            
            # 從排程引擎移除
            await self.engine.remove_job(task_id)
            
            await self.task_repository.delete_object(task)
            logger.info(f"刪除任務: {task.name} (ID: {task.id})")
            return True
        except Exception:
            raise HTTPException(status_code=404, detail="任務不存在")

    async def update_task_state(self, task_id: int, state_data: TaskStateUpdateRequest) -> ScheduledTaskResponse:
        """更新任務狀態"""
        try:
            await self.task_repository.update_state(task_id, state_data.state)
            task = await self.task_repository.get_by_id(task_id)
            
            # 根據狀態更新排程引擎
            if state_data.state == TaskState.ENABLED:
                await self.engine.add_job(task.id, task.schedule_expression, self._task_to_dict(task))
            else:
                await self.engine.remove_job(task.id)
            
            logger.info(f"更新任務狀態: {task.name} -> {state_data.state}")
            return ScheduledTaskResponse.from_orm(task)
        except Exception:
            raise HTTPException(status_code=404, detail="任務不存在")

    async def trigger_task_now(self, task_id: int) -> bool:
        """立即觸發任務執行"""
        try:
            task = await self.task_repository.get_by_id(task_id)
            await self.engine.trigger_job_now(task.id, self._task_to_dict(task))
            return True
        except Exception as e:
            logger.error(f"觸發任務 {task_id} 失敗: {e}")
            raise HTTPException(status_code=400, detail=f"觸發任務失敗: {str(e)}")

    async def get_task_executions(self, task_id: int, limit: int = 50) -> List[TaskExecutionResponse]:
        """獲取任務執行記錄"""
        executions = await self.execution_repository.get_by_task_id(task_id)
        return [TaskExecutionResponse.from_orm(execution) for execution in executions[:limit]]

    async def get_scheduler_stats(self) -> SchedulerStatsResponse:
        """獲取排程器統計信息"""
        # 任務統計
        all_tasks = await self.task_repository.find_all()
        enabled_tasks = await self.task_repository.get_tasks_by_state(TaskState.ENABLED)
        disabled_tasks = await self.task_repository.get_tasks_by_state(TaskState.DISABLED)
        
        # 今日執行統計
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        today_executions = await self.execution_repository.get_executions_by_date_range(today_start, today_end)
        successful_executions = [e for e in today_executions if e.status == ExecutionStatus.SUCCEEDED]
        failed_executions = [e for e in today_executions if e.status == ExecutionStatus.FAILED]
        
        return SchedulerStatsResponse(
            total_tasks=len(all_tasks),
            enabled_tasks=len(enabled_tasks),
            disabled_tasks=len(disabled_tasks),
            total_executions_today=len(today_executions),
            successful_executions_today=len(successful_executions),
            failed_executions_today=len(failed_executions)
        )

    async def search_tasks(self, keyword: str) -> List[ScheduledTaskResponse]:
        """搜索任務"""
        tasks = await self.task_repository.search_tasks(keyword)
        return [ScheduledTaskResponse.from_orm(task) for task in tasks]

    def _calculate_next_execution(self, schedule_expression: str, timezone: str = "Asia/Taipei") -> datetime:
        """計算下次執行時間"""
        try:
            if schedule_expression.startswith('cron(') and schedule_expression.endswith(')'):
                # 提取 cron 表達式
                cron_expr = schedule_expression[5:-1]
                cron = croniter(cron_expr, datetime.now())
                return cron.get_next(datetime)
            
            elif schedule_expression.startswith('rate(') and schedule_expression.endswith(')'):
                # 提取 rate 表達式
                rate_expr = schedule_expression[5:-1]
                match = re.match(r'(\d+)\s+(minute|minutes|hour|hours|day|days)', rate_expr)
                if not match:
                    raise ValueError("無效的 rate 表達式格式")
                
                value, unit = match.groups()
                value = int(value)
                
                if unit.startswith('minute'):
                    delta = timedelta(minutes=value)
                elif unit.startswith('hour'):
                    delta = timedelta(hours=value)
                elif unit.startswith('day'):
                    delta = timedelta(days=value)
                else:
                    raise ValueError(f"不支援的時間單位: {unit}")
                
                return datetime.now() + delta
            
            else:
                raise ValueError("無效的排程表達式格式")
                
        except Exception as e:
            logger.error(f"計算下次執行時間失敗: {e}")
            raise HTTPException(status_code=400, detail=f"無效的排程表達式: {str(e)}")