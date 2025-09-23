from src.dependencies.repositories import get_scheduled_task_repository, get_task_execution_repository
from src.models.enum.scheduler import TaskState
from src.models.pydantic.statistic import StatisticDashboardMetricResponse
from src.repositories.scheduler import ScheduledTaskRepository, TaskExecutionRepository


class StatisticService:
    def __init__(self):
        self.task_repository: ScheduledTaskRepository = get_scheduled_task_repository()
        self.execution_repository: TaskExecutionRepository = get_task_execution_repository()

    async def get_dashboard_metrics(self):
        """獲取儀表板統計數據"""
        total_tasks = await self.task_repository.count_all_tasks()
        enabled_tasks = await self.task_repository.count_tasks_by_state(TaskState.ENABLED)
        disabled_tasks = await self.task_repository.count_tasks_by_state(TaskState.DISABLED)
        today_executions_count = await self.execution_repository.count_today_executions()

        return StatisticDashboardMetricResponse(
            total_tasks=total_tasks,
            enabled_tasks=enabled_tasks,
            disabled_tasks=disabled_tasks,
            today_executions_count=today_executions_count
        )