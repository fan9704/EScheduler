from src.repositories.team import TeamRepository
from src.repositories.scheduler import ScheduledTaskRepository, TaskExecutionRepository

def get_team_repository() -> TeamRepository:
    return TeamRepository()


def get_scheduled_task_repository() -> ScheduledTaskRepository:
    return ScheduledTaskRepository()


def get_task_execution_repository() -> TaskExecutionRepository:
    """獲取任務執行記錄倉庫實例"""
    return TaskExecutionRepository()