from src.repositories.team import TeamRepository
from src.repositories.scheduler import ScheduledTaskRepository, TaskExecutionRepository

def get_team_repository() -> TeamRepository:
    return TeamRepository()


def get_scheduled_task_repository() -> ScheduledTaskRepository:
    return ScheduledTaskRepository()


def get_task_execution_repository() -> TaskExecutionRepository:
    return TaskExecutionRepository()