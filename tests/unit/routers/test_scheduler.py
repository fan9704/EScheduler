from datetime import datetime
from fastapi import HTTPException
from unittest.mock import AsyncMock

import pytest
from fastapi.responses import JSONResponse

from src.models.enum.scheduler import TaskState, TargetType
from src.models.pydantic.scheduler import (
    ScheduledTaskCreate, ScheduledTaskUpdate, ScheduledTaskResponse,
    SchedulerStatsResponse, TaskStateUpdateRequest
)
from src.routers import scheduler


# ---------------------------------------------------------------------------
# ✅ 測試 create_task
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_task_success():
    mock_service = AsyncMock()
    mock_service.create_task.return_value = ScheduledTaskResponse(
        id=1,
        name="Test Task",
        description="Desc",
        schedule_expression="rate(5 minutes)",
        timezone="Asia/Taipei",
        target_type="email",
        target_arn="arn:aws:email",
        target_input={},
        state=TaskState.ENABLED.value,
        last_execution_time=None,
        next_execution_time=None,
        execution_count=0,
        max_retry_attempts=3,
        retry_policy=None,
        dead_letter_config=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    payload = ScheduledTaskCreate(
        name="Test Task",
        description="Desc",
        schedule_expression="rate(5 minutes)",
        target_type=TargetType.EMAIL,
        target_arn="arn:aws:email"
    )

    result = await scheduler.create_task(payload, service=mock_service)

    assert result.name == "Test Task"
    mock_service.create_task.assert_awaited_once_with(payload)


# ---------------------------------------------------------------------------
# ✅ 測試 get_all_tasks
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_all_tasks_success():
    mock_service = AsyncMock()
    mock_service.get_all_tasks.return_value = [
        ScheduledTaskResponse(
            id=1,
            name="Task 1",
            description=None,
            schedule_expression="rate(5 minutes)",
            timezone="Asia/Taipei",
            target_type="email",
            target_arn="arn:aws:email1",
            target_input={},
            state=TaskState.ENABLED.value,
            last_execution_time=None,
            next_execution_time=None,
            execution_count=0,
            max_retry_attempts=3,
            retry_policy=None,
            dead_letter_config=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        ScheduledTaskResponse(
            id=2,
            name="Task 2",
            description=None,
            schedule_expression="rate(1 hour)",
            timezone="Asia/Taipei",
            target_type="email",
            target_arn="arn:aws:email2",
            target_input={},
            state=TaskState.ENABLED.value,
            last_execution_time=None,
            next_execution_time=None,
            execution_count=0,
            max_retry_attempts=3,
            retry_policy=None,
            dead_letter_config=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]

    result = await scheduler.get_all_tasks(state=None, target_type=None, service=mock_service)

    assert len(result) == 2
    mock_service.get_all_tasks.assert_awaited_once_with(None, None)


# ---------------------------------------------------------------------------
# ✅ 測試 get_scheduler_stats
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_scheduler_stats_success():
    mock_service = AsyncMock()
    mock_service.get_scheduler_stats.return_value = SchedulerStatsResponse(
        total_tasks=5,
        enabled_tasks=3,
        disabled_tasks=2,
        total_executions_today=10,
        successful_executions_today=8,
        failed_executions_today=2
    )

    result = await scheduler.get_scheduler_stats(service=mock_service)

    assert result.total_tasks == 5
    mock_service.get_scheduler_stats.assert_awaited_once()


# ---------------------------------------------------------------------------
# ✅ 測試 update_task
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_task_success():
    mock_service = AsyncMock()
    mock_service.update_task.return_value = ScheduledTaskResponse(
        id=10,
        name="Updated Task",
        description="Desc",
        schedule_expression="rate(5 minutes)",
        timezone="Asia/Taipei",
        target_type="email",
        target_arn="arn:aws:email",
        target_input={},
        state=TaskState.ENABLED.value,
        last_execution_time=None,
        next_execution_time=None,
        execution_count=0,
        max_retry_attempts=3,
        retry_policy=None,
        dead_letter_config=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    payload = ScheduledTaskUpdate(name="Updated Task")
    result = await scheduler.update_task(task_id=10, task_data=payload, service=mock_service)

    assert result.name == "Updated Task"
    mock_service.update_task.assert_awaited_once_with(10, payload)


# ---------------------------------------------------------------------------
# ✅ 測試 delete_task
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_task_success():
    mock_service = AsyncMock()
    mock_service.delete_task.return_value = True

    result = await scheduler.delete_task(task_id=3, service=mock_service)

    assert isinstance(result, JSONResponse)
    assert result.status_code == 200
    assert "任務已成功刪除" in result.body.decode()
    mock_service.delete_task.assert_awaited_once_with(3)


# ---------------------------------------------------------------------------
# test search_tasks
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_search_tasks_success():
    mock_service = AsyncMock()
    mock_service.search_tasks.return_value = [
        ScheduledTaskResponse(
            id=1,
            name="Task 1",
            description=None,
            schedule_expression="rate(5 minutes)",
            timezone="Asia/Taipei",
            target_type="email",
            target_arn="arn:aws:email1",
            target_input={},
            state=TaskState.ENABLED.value,
            last_execution_time=None,
            next_execution_time=None,
            execution_count=0,
            max_retry_attempts=3,
            retry_policy=None,
            dead_letter_config=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]
    result = await scheduler.search_tasks(keyword="Task", service=mock_service)
    assert len(result) == 1
    assert result[0].name == "Task 1"
    mock_service.search_tasks.assert_awaited_once_with("Task")


# ---------------------------------------------------------------------------
# test get_task
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_get_task_success():
    mock_service = AsyncMock()
    mock_service.get_task.return_value = ScheduledTaskResponse(
        id=1,
        name="Task 1",
        description=None,
        schedule_expression="rate(5 minutes)",
        timezone="Asia/Taipei",
        target_type="email",
        target_arn="arn:aws:email1",
        target_input={},
        state=TaskState.ENABLED.value,
        last_execution_time=None,
        next_execution_time=None,
        execution_count=0,
        max_retry_attempts=3,
        retry_policy=None,
        dead_letter_config=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    result = await scheduler.get_task(task_id=1, service=mock_service)
    assert result.id == 1
    mock_service.get_task.assert_awaited_once_with(1)


# ---------------------------------------------------------------------------
# test update_task_state
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_update_task_state_success():
    mock_service = AsyncMock()
    mock_service.update_task_state.return_value = ScheduledTaskResponse(
        id=1,
        name="Task 1",
        description="desc",
        schedule_expression="rate(5 minutes)",
        timezone="Asia/Taipei",
        target_type="email",
        target_arn="arn:aws:email1",
        target_input={},
        state=TaskState.DISABLED.value,
        last_execution_time=None,
        next_execution_time=None,
        execution_count=0,
        max_retry_attempts=3,
        retry_policy=None,
        dead_letter_config=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    state_data = TaskStateUpdateRequest(state=TaskState.DISABLED)
    result = await scheduler.update_task_state(task_id=1, state_data=state_data, service=mock_service)
    assert result.state == TaskState.DISABLED.value
    mock_service.update_task_state.assert_awaited_once_with(1, state_data)


# ---------------------------------------------------------------------------
# test trigger_task
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_trigger_task_success():
    mock_service = AsyncMock()
    mock_service.trigger_task_now.return_value = True
    result = await scheduler.trigger_task(task_id=1, service=mock_service)
    assert isinstance(result, JSONResponse)
    assert result.status_code == 200
    assert "任務觸發成功" in result.body.decode()
    mock_service.trigger_task_now.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_trigger_task_failed():
    mock_service = AsyncMock()
    mock_service.trigger_task_now.return_value = False
    result = await scheduler.trigger_task(task_id=2, service=mock_service)
    assert isinstance(result, JSONResponse)
    assert result.status_code == 500
    assert "任務執行失敗" in result.body.decode()
    mock_service.trigger_task_now.assert_awaited_once_with(2)

@pytest.mark.asyncio
async def test_trigger_task_http_exception():
    mock_service = AsyncMock()
    mock_service.trigger_task_now.side_effect = HTTPException(status_code=404, detail="Task not found")

    result = await scheduler.trigger_task(task_id=1, service=mock_service)

    assert isinstance(result, JSONResponse)
    assert result.status_code == 404
    assert "Task not found" in result.body.decode()
    mock_service.trigger_task_now.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_trigger_task_general_exception():
    mock_service = AsyncMock()
    mock_service.trigger_task_now.side_effect = Exception("Unexpected error")

    result = await scheduler.trigger_task(task_id=1, service=mock_service)

    assert isinstance(result, JSONResponse)
    assert result.status_code == 500
    assert "觸發任務失敗: Unexpected error" in result.body.decode()
    mock_service.trigger_task_now.assert_awaited_once_with(1)