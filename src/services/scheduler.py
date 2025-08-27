import logging
from datetime import datetime, timedelta
from typing import List, Optional
from zoneinfo import ZoneInfo

from croniter import croniter
from fastapi import HTTPException

from src.dependencies.repositories import get_scheduled_task_repository, get_task_execution_repository
from src.dependencies.utils import get_scheduler_engine
from src.models.enum.scheduler import TaskState, ExecutionStatus
from src.models.pydantic.scheduler import (
    ScheduledTaskCreate, ScheduledTaskUpdate, ScheduledTaskResponse,
    SchedulerStatsResponse, TaskStateUpdateRequest, TaskExecutionResponse, SchedulerJob
)
from src.repositories.scheduler import ScheduledTaskRepository, TaskExecutionRepository
from src.services.execution_strategies.strategy_factory import ExecutionStrategyFactory
from src.services.scheduler_engine import SchedulerEngine
from src.utils.schedule import match_rate_expression_return_delta

logger = logging.getLogger(__name__)




class SchedulerService:
    def __init__(self):
        self.task_repository: ScheduledTaskRepository = get_scheduled_task_repository()
        self.execution_repository: TaskExecutionRepository = get_task_execution_repository()
        self.strategy_factory = ExecutionStrategyFactory()
        # 使用單例實例
        self.scheduler_engine: SchedulerEngine = get_scheduler_engine()

    @staticmethod
    def _get_timezone_aware_now(timezone: str = "Asia/Taipei") -> datetime:
        """獲取帶時區的當前時間"""
        tz = ZoneInfo(timezone)
        return datetime.now(tz)

    async def trigger_task_now(self, task_id: int) -> bool:
        """立即觸發任務執行（使用策略模式）"""
        execution_start_time = self._get_timezone_aware_now()
        task = None
        execution_id = None
        
        try:
            # 獲取任務信息
            task = await self.task_repository.get_by_id(task_id)
            logger.info(f"開始執行任務: {task.name} (ID: {task.id})")
            logger.info(f"任務目標: {task.target_type} - {task.target_arn}")
            
            # 創建 TaskExecution 記錄
            execution_record = await self.execution_repository.create(
                task_id=task_id,
                status=ExecutionStatus.RUNNING,
                started_at=execution_start_time,
                attempt_number=1
            )
            execution_id = execution_record.id
            
            # 更新執行次數
            await self.task_repository.increment_execution_count(task_id)
            
            # 創建執行策略
            strategy = self.strategy_factory.create_strategy(task.target_type)
            
            # 執行任務
            execution_result = await strategy.execute(task.target_arn, task.target_input or {})
            
            # 計算下次執行時間
            next_execution = self._calculate_next_execution(task.schedule_expression, task.timezone)
            
            # 更新最後執行時間
            await self.task_repository.update_execution_time(
                task_id, 
                execution_start_time,
                next_execution
            )
            
            # 更新 TaskExecution 記錄
            status = ExecutionStatus.SUCCEEDED if execution_result.success else ExecutionStatus.FAILED
            await self.execution_repository.update_execution_result(
                execution_id=execution_id,
                status=status,
                response_code=execution_result.status_code,
                response_body=execution_result.message,
                error_message=None if execution_result.success else execution_result.message
            )
            
            if execution_result.success:
                logger.info(f"任務 {task.name} 執行成功，耗時 {execution_result.execution_time:.2f} 秒")
                logger.info(f"執行結果: {execution_result.message}")
            else:
                logger.error(f"任務 {task.name} 執行失敗: {execution_result.message}")
                raise Exception(execution_result.message)
            
            return execution_result.success
            
        except Exception as e:
            execution_end_time = self._get_timezone_aware_now()
            execution_duration = (execution_end_time - execution_start_time).total_seconds()
            
            # 更新執行記錄為失敗狀態
            if execution_id:
                await self.execution_repository.update_execution_result(
                    execution_id=execution_id,
                    status=ExecutionStatus.FAILED,
                    error_message=str(e)
                )
            
            error_msg = f"任務執行失敗: {str(e)}"
            logger.error(f"任務 {task.name if task else task_id} 執行失敗，耗時 {execution_duration:.2f} 秒")
            logger.error(f"錯誤詳情: {error_msg}")
            
            raise HTTPException(status_code=500, detail=error_msg)

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
        
        # 🔥 新增：添加到排程引擎
        if task.state == TaskState.ENABLED:

            await self.scheduler_engine.add_job(task.id, task.schedule_expression, SchedulerJob(
                id=task.id,
                name=task.name,
                target_type=task.target_type,
                target_arn=task.target_arn,
                target_input=task.target_input
            ))
            logger.info(f"任務 {task.name} 已添加到排程引擎")
        
        return ScheduledTaskResponse.from_orm(task)

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
        
        # 🔥 新增：更新排程引擎
        if task.state == TaskState.ENABLED:

            await self.scheduler_engine.add_job(task.id, task.schedule_expression,             SchedulerJob(
                id=task.id,
                name=task.name,
                target_type=task.target_type,
                target_arn=task.target_arn,
                target_input=task.target_input
            ))
        else:
            await self.scheduler_engine.remove_job(task.id)
        
        return ScheduledTaskResponse.from_orm(task)
    
    # 修改 delete_task 方法
    async def delete_task(self, task_id: int) -> bool:
        """刪除任務"""
        try:
            task = await self.task_repository.get_by_id(task_id)
            
            # 🔥 新增：從排程引擎移除
            await self.scheduler_engine.remove_job(task_id)
            
            await self.task_repository.delete_object(task)
            logger.info(f"刪除任務: {task.name} (ID: {task.id})")
            return True
        except Exception:
            raise HTTPException(status_code=404, detail="任務不存在")

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

    async def update_task_state(self, task_id: int, state_data: TaskStateUpdateRequest) -> ScheduledTaskResponse:
        """更新任務狀態"""
        try:
            await self.task_repository.update_state(task_id, state_data.state)
            task = await self.task_repository.get_by_id(task_id)
            logger.info(f"更新任務狀態: {task.name} -> {state_data.state}")
            return ScheduledTaskResponse.from_orm(task)
        except Exception:
            raise HTTPException(status_code=404, detail="任務不存在")

    # 修改這個方法，讓它真正返回執行記錄
    
    async def get_task_executions(self, task_id: int, limit: int = 50):
        """獲取任務執行記錄"""
        try:
            executions = await self.execution_repository.get_by_task_id(task_id)
            return [TaskExecutionResponse.from_orm(execution) for execution in executions[:limit]]
        except Exception as e:
            logger.error(f"獲取任務執行記錄失敗: {e}")
            return []

    async def get_scheduler_stats(self) -> SchedulerStatsResponse:
        """獲取排程器統計信息（簡化版）"""
        all_tasks = await self.task_repository.find_all()
        enabled_tasks = await self.task_repository.get_tasks_by_state(TaskState.ENABLED)
        disabled_tasks = await self.task_repository.get_tasks_by_state(TaskState.DISABLED)
        
        return SchedulerStatsResponse(
            total_tasks=len(all_tasks),
            enabled_tasks=len(enabled_tasks),
            disabled_tasks=len(disabled_tasks),
            total_executions_today=0,
            successful_executions_today=0,
            failed_executions_today=0
        )

    async def search_tasks(self, keyword: str) -> List[ScheduledTaskResponse]:
        """搜索任務"""
        tasks = await self.task_repository.search_tasks(keyword)
        return [ScheduledTaskResponse.from_orm(task) for task in tasks]

    @staticmethod
    def _calculate_next_execution(schedule_expression: str, timezone: str = "Asia/Taipei") -> datetime:
        """計算下次執行時間（帶時區）"""
        try:
            tz = ZoneInfo(timezone)
            current_time = datetime.now(tz)
            
            if schedule_expression.startswith('cron(') and schedule_expression.endswith(')'):
                cron_expr = schedule_expression[5:-1]
                cron = croniter(cron_expr, current_time)
                return cron.get_next(datetime)
            
            elif schedule_expression.startswith('rate(') and schedule_expression.endswith(')'):
                rate_expr = schedule_expression[5:-1]
                delta = match_rate_expression_return_delta(rate_expr)
                return current_time + delta
            
            elif schedule_expression.startswith('at(') and schedule_expression.endswith(')'):
                datetime_str = schedule_expression[3:-1]
                # 解析 ISO 格式的日期時間，如果沒有時區信息則添加指定時區
                dt = datetime.fromisoformat(datetime_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=tz)
                return dt
            
            elif schedule_expression == 'once':
                return current_time + timedelta(seconds=1)
            
            else:
                raise ValueError("無效的排程表達式格式")
                
        except Exception as e:
            logger.error(f"計算下次執行時間失敗: {e}")
            raise HTTPException(status_code=400, detail=f"無效的排程表達式: {str(e)}")