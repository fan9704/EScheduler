from typing import List, Optional
from datetime import datetime
from src.repositories.base import Repository
from src.models.tortoise.scheduler import ScheduledTask, TaskExecution
from src.models.enum.scheduler import TaskState, ExecutionStatus


class ScheduledTaskRepository(Repository):
    def __init__(self):
        self.model = ScheduledTask

    async def get_by_name(self, name: str) -> Optional[ScheduledTask]:
        """根據名稱獲取任務"""
        return await self.model.filter(name=name).first()

    async def get_enabled_tasks(self) -> List[ScheduledTask]:
        """獲取所有啟用的任務"""
        return await self.model.filter(state=TaskState.ENABLED)

    async def get_tasks_by_state(self, state: TaskState) -> List[ScheduledTask]:
        """根據狀態獲取任務"""
        return await self.model.filter(state=state)

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


class TaskExecutionRepository(Repository):
    def __init__(self):
        self.model = TaskExecution

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
            "completed_at": datetime.now()
        }
        if response_code is not None:
            update_data["response_code"] = response_code
        if response_body is not None:
            update_data["response_body"] = response_body
        if error_message is not None:
            update_data["error_message"] = error_message
            
        await self.model.filter(id=execution_id).update(**update_data)