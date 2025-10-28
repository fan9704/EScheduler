from src.dependencies.repositories import get_scheduled_task_repository
from src.dependencies.repositories import get_task_execution_repository
from src.repositories.scheduler import TaskExecutionRepository,ScheduledTaskRepository

class TestRepositoryDependencies:

    def test_get_scheduler_service_returns_new_instance(self):
        r1 = get_task_execution_repository()
        r2 = get_task_execution_repository()
        assert isinstance(r1, TaskExecutionRepository)
        assert isinstance(r2, TaskExecutionRepository)
        assert r1 is not r2

    def test_get_schedule_helper_service_returns_new_instance(self):
        r1 = get_scheduled_task_repository()
        r2 = get_scheduled_task_repository()
        assert isinstance(r1, ScheduledTaskRepository)
        assert isinstance(r2, ScheduledTaskRepository)
        assert r1 is not r2
