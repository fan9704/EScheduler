import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime
from zoneinfo import ZoneInfo

from src.repositories.scheduler import ScheduledTaskRepository, TaskExecutionRepository
from src.models.tortoise.scheduler import ScheduledTask, TaskExecution
from src.models.enum.scheduler import TaskState, ExecutionStatus


@pytest.mark.asyncio
async def test_get_by_name(mocker):
    repo = ScheduledTaskRepository()

    # 創建一個假的 ScheduledTask instance
    mock_task = MagicMock(ScheduledTask)

    # mock filter().first() 連鎖
    mock_first = AsyncMock(return_value=mock_task)
    mock_filter = MagicMock()
    mock_filter.first = mock_first
    mocker.patch.object(ScheduledTask, "filter", return_value=mock_filter)

    # 執行
    result = await repo.get_by_name("test_task")

    # 驗證
    ScheduledTask.filter.assert_called_once_with(name="test_task")
    mock_first.assert_awaited_once()
    assert result == mock_task

@pytest.mark.asyncio
async def test_get_tasks_by_state(mocker):
    repo = ScheduledTaskRepository()
    mock_tasks = [MagicMock(ScheduledTask), MagicMock(ScheduledTask)]
    mocker.patch.object(ScheduledTask, "filter", AsyncMock(return_value=mock_tasks))

    result = await repo.get_tasks_by_state(TaskState.ENABLED)

    ScheduledTask.filter.assert_called_once_with(state=TaskState.ENABLED)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_tasks_by_target_type(mocker):
    repo = ScheduledTaskRepository()
    mock_tasks = [MagicMock(ScheduledTask)]
    mocker.patch.object(ScheduledTask, "filter", AsyncMock(return_value=mock_tasks))

    result = await repo.get_tasks_by_target_type("system")

    ScheduledTask.filter.assert_called_once_with(target_type="system")
    assert result == mock_tasks


@pytest.mark.asyncio
async def test_get_tasks_by_state_and_target_type(mocker):
    repo = ScheduledTaskRepository()
    mock_tasks = [MagicMock(ScheduledTask)]
    mocker.patch.object(ScheduledTask, "filter", AsyncMock(return_value=mock_tasks))

    result = await repo.get_tasks_by_state_and_target_type(TaskState.PAUSED, "api")

    ScheduledTask.filter.assert_called_once_with(state=TaskState.PAUSED, target_type="api")
    assert result == mock_tasks


@pytest.mark.asyncio
async def test_update_execution_time_with_next(mocker):
    repo = ScheduledTaskRepository()
    mock_update = AsyncMock()
    mocker.patch.object(ScheduledTask, "filter", return_value=MagicMock(update=mock_update))

    now = datetime.now()
    next_time = datetime.now()
    await repo.update_execution_time(1, now, next_time)

    mock_update.assert_awaited_once_with(last_execution_time=now, next_execution_time=next_time)


@pytest.mark.asyncio
async def test_update_execution_time_without_next(mocker):
    repo = ScheduledTaskRepository()
    mock_update = AsyncMock()
    mocker.patch.object(ScheduledTask, "filter", return_value=MagicMock(update=mock_update))

    now = datetime.now()
    await repo.update_execution_time(1, now)

    mock_update.assert_awaited_once_with(last_execution_time=now)


@pytest.mark.asyncio
async def test_increment_execution_count(mocker):
    repo = ScheduledTaskRepository()
    mock_task = MagicMock(ScheduledTask)
    mock_task.execution_count = 5
    mock_task.save = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=mock_task)

    await repo.increment_execution_count(1)

    assert mock_task.execution_count == 6
    mock_task.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_state(mocker):
    repo = ScheduledTaskRepository()
    mock_update = AsyncMock()
    mocker.patch.object(ScheduledTask, "filter", return_value=MagicMock(update=mock_update))

    await repo.update_state(1, TaskState.ENABLED)
    mock_update.assert_awaited_once_with(state=TaskState.ENABLED)


@pytest.mark.asyncio
async def test_search_tasks(mocker):
    repo = ScheduledTaskRepository()
    mock_tasks = [MagicMock(ScheduledTask)]
    mocker.patch.object(ScheduledTask, "filter", AsyncMock(return_value=mock_tasks))

    result = await repo.search_tasks("backup")

    ScheduledTask.filter.assert_called_once_with(name__icontains="backup")
    assert result == mock_tasks


@pytest.mark.asyncio
async def test_count_tasks_by_state(mocker):
    repo = ScheduledTaskRepository()
    mock_count = AsyncMock(return_value=10)
    mock_filter = MagicMock(count=mock_count)
    mocker.patch.object(ScheduledTask, "filter", return_value=mock_filter)

    count = await repo.count_tasks_by_state(TaskState.PAUSED)

    mock_count.assert_awaited_once()
    assert count == 10


@pytest.mark.asyncio
async def test_count_all_tasks(mocker):
    repo = ScheduledTaskRepository()
    mock_count = AsyncMock(return_value=5)
    mock_all = MagicMock(count=mock_count)
    mocker.patch.object(ScheduledTask, "all", return_value=mock_all)

    count = await repo.count_all_tasks()

    mock_count.assert_awaited_once()
    assert count == 5


# --- TaskExecutionRepository Tests ---


@pytest.mark.asyncio
async def test_get_by_task_id(mocker):
    repo = TaskExecutionRepository()
    mock_execs = [MagicMock(TaskExecution)]
    mocker.patch.object(TaskExecution, "filter", return_value=MagicMock(order_by=AsyncMock(return_value=mock_execs)))

    result = await repo.get_by_task_id(123)

    TaskExecution.filter.assert_called_once_with(task_id=123)
    assert result == mock_execs


@pytest.mark.asyncio
async def test_get_recent_executions(mocker):
    repo = TaskExecutionRepository()
    mock_execs = [MagicMock(TaskExecution)]
    mock_all = MagicMock(order_by=MagicMock(return_value=MagicMock(limit=AsyncMock(return_value=mock_execs))))
    mocker.patch.object(TaskExecution, "all", return_value=mock_all)

    result = await repo.get_recent_executions(10)

    TaskExecution.all.assert_called_once()
    assert result == mock_execs


@pytest.mark.asyncio
async def test_get_executions_by_status(mocker):
    repo = TaskExecutionRepository()
    mock_execs = [MagicMock(TaskExecution)]
    mocker.patch.object(TaskExecution, "filter", AsyncMock(return_value=mock_execs))

    result = await repo.get_executions_by_status(ExecutionStatus.FAILED)

    TaskExecution.filter.assert_called_once_with(status=ExecutionStatus.FAILED)
    assert result == mock_execs


@pytest.mark.asyncio
async def test_get_executions_by_date_range(mocker):
    repo = TaskExecutionRepository()
    mock_execs = [MagicMock(TaskExecution)]
    mocker.patch.object(TaskExecution, "filter", AsyncMock(return_value=mock_execs))

    start = datetime(2025, 1, 1)
    end = datetime(2025, 1, 2)
    result = await repo.get_executions_by_date_range(start, end)

    TaskExecution.filter.assert_called_once_with(
        started_at__gte=start, started_at__lte=end
    )
    assert result == mock_execs


@pytest.mark.asyncio
async def test_update_execution_result(mocker):
    repo = TaskExecutionRepository()
    mock_update = AsyncMock()
    mocker.patch.object(TaskExecution, "filter", return_value=MagicMock(update=mock_update))
    mocker.patch.object(repo, "_get_timezone_aware_now", return_value=datetime(2025, 1, 1))

    await repo.update_execution_result(
        execution_id=5,
        status=ExecutionStatus.SUCCEEDED,
        response_code=200,
        response_body="OK",
        error_message=None
    )

    mock_update.assert_awaited_once_with(
        status=ExecutionStatus.SUCCEEDED,
        completed_at=datetime(2025, 1, 1),
        response_code=200,
        response_body="OK"
    )


@pytest.mark.asyncio
async def test_count_today_executions(mocker):
    repo = TaskExecutionRepository()
    mock_count = AsyncMock(return_value=3)
    mock_filter = MagicMock(count=mock_count)
    mocker.patch.object(TaskExecution, "filter", return_value=mock_filter)
    mocker.patch.object(repo, "_get_timezone_aware_now", return_value=datetime(2025, 1, 1, 12, 0, tzinfo=ZoneInfo("Asia/Taipei")))

    result = await repo.count_today_executions()

    assert result == 3
    mock_count.assert_awaited_once()
