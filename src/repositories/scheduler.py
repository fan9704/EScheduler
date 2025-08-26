from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo

from src.models.enum.scheduler import TaskState, ExecutionStatus
from src.models.tortoise.scheduler import ScheduledTask, TaskExecution
from src.repositories.base import Repository


class ScheduledTaskRepository(Repository):
    def __init__(self):
        self.model = ScheduledTask

    async def get_by_name(self, name: str) -> ScheduledTask:
        """根據名稱獲取任務"""
        return await self.model.filter(name=name).first()

    async def get_tasks_by_state(self, state: TaskState) -> List[ScheduledTask]:
        """根據狀態獲取任務"""
        return await self.model.filter(state=state)

    def _get_timezone_aware_now(self, timezone: str = "Asia/Taipei") -> datetime:
        """獲取帶時區的當前時間"""
        tz = ZoneInfo(timezone)
        return datetime.now(tz)

    async def update_execution_time(self, task_id: int, last_execution: datetime, next_execution: datetime = None):
        """更新任務執行時間"""
        update_data = {
            "last_execution_time": last_execution,
        }
        if next_execution:
            update_data["next_execution_time"] = next_execution
            
        await self.model.filter(id=task_id).update(**update_data)

    async def increment_execution_count(self, task_id: int):
        """增加執行次數"""
        task = await self.get_by_id(task_id)
        task.execution_count += 1
        await task.save()

    async def update_state(self, task_id: int, state: TaskState):
        """更新任務狀態"""
        await self.model.filter(id=task_id).update(state=state)

    async def search_tasks(self, keyword: str) -> List[ScheduledTask]:
        """搜索任務"""
        return await self.model.filter(name__icontains=keyword)
    
    # Statistic methods
    async def count_tasks_by_state(self, state: TaskState) -> int:
        """統計特定狀態的任務數量"""
        return await self.model.filter(state=state).count()
    async def count_all_tasks(self) -> int:
        """統計所有任務數量"""
        return await self.model.all().count()


class TaskExecutionRepository(Repository):
    def __init__(self):
        self.model = TaskExecution

    def _get_timezone_aware_now(self, timezone: str = "Asia/Taipei") -> datetime:
        """獲取帶時區的當前時間"""
        tz = ZoneInfo(timezone)
        return datetime.now(tz)

    async def get_by_task_id(self, task_id: int) -> List[TaskExecution]:
        """獲取特定任務的執行記錄"""
        return await self.model.filter(task_id=task_id).order_by("-started_at")

    async def get_recent_executions(self, limit: int = 100) -> List[TaskExecution]:
        """獲取最近的執行記錄"""
        return await self.model.all().order_by("-started_at").limit(limit)

    async def get_executions_by_status(self, status: ExecutionStatus) -> List[TaskExecution]:
        """根據狀態獲取執行記錄"""
        return await self.model.filter(status=status)

    async def get_executions_by_date_range(self, start_date: datetime, end_date: datetime) -> List[TaskExecution]:
        """根據日期範圍獲取執行記錄"""
        return await self.model.filter(
            started_at__gte=start_date,
            started_at__lte=end_date
        )

    async def update_execution_result(self, execution_id: int, status: ExecutionStatus, 
                                    response_code: int = None, response_body: str = None, 
                                    error_message: str = None):
        """更新執行結果"""
        update_data = {
            "status": status,
            "completed_at": self._get_timezone_aware_now()  # 使用帶時區的時間
        }
        if response_code is not None:
            update_data["response_code"] = response_code
        if response_body is not None:
            update_data["response_body"] = response_body
        if error_message is not None:
            update_data["error_message"] = error_message
            
        await self.model.filter(id=execution_id).update(**update_data)

    async def count_today_executions(self) -> int:
        """統計今天的執行次數"""
        now = self._get_timezone_aware_now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return await self.model.filter(
            started_at__gte=start_of_day,
            started_at__lte=end_of_day
        ).count()