import json
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from src.models.enum.scheduler import TaskState, ExecutionStatus
from src.models.pydantic.scheduler import ScheduledTaskCreate, TaskStateUpdateRequest
from src.models.pydantic.scheduler import TaskExecutionResponse
from src.services.scheduler import SchedulerService


@pytest.mark.asyncio
class TestSchedulerService:

    async def async_set_up_service(self):
        service = SchedulerService()

        # mock repositories
        service.task_repository.get_by_id = AsyncMock()
        service.task_repository.get_by_name = AsyncMock()
        service.task_repository.create = AsyncMock()
        service.task_repository.update_state = AsyncMock()
        service.task_repository.get_tasks_by_state = AsyncMock()
        service.task_repository.get_tasks_by_state_and_target_type = AsyncMock()
        service.task_repository.get_tasks_by_target_type = AsyncMock()
        service.task_repository.find_all = AsyncMock()
        service.task_repository.search_tasks = AsyncMock()
        service.task_repository.increment_execution_count = AsyncMock()
        service.task_repository.update_execution_time = AsyncMock()
        service.task_repository.delete_object = AsyncMock()

        service.execution_repository.create = AsyncMock()
        service.execution_repository.get_by_task_id = AsyncMock()
        service.execution_repository.update_execution_result = AsyncMock()
        service.execution_repository.count_today_executions = AsyncMock()

        # mock scheduler engine
        service.scheduler_engine.add_job = AsyncMock()
        service.scheduler_engine.remove_job = AsyncMock()

        # mock strategy
        service.strategy_factory.create_strategy = MagicMock()
        mock_strategy = AsyncMock()
        mock_strategy.execute = AsyncMock(return_value=MagicMock(
            success=True, status_code=200, message="ok", execution_time=0.1
        ))
        service.strategy_factory.create_strategy.return_value = mock_strategy

        return service

    async def test_create_task_success(self):
        service = await self.async_set_up_service()
        payload = ScheduledTaskCreate(
            name="task1",
            target_type="http",
            target_arn="http://example.com/endpoint",
            schedule_expression="rate(5 minutes)",
            timezone="Asia/Taipei",
            state=TaskState.ENABLED
        )

        now = datetime.now(timezone.utc)
        # mock task 要有 ScheduledTaskResponse 所需欄位
        mock_task = SimpleNamespace(
            id=1,
            name="task1",
            description="test task",
            schedule_expression=payload.schedule_expression,
            timezone="Asia/Taipei",
            target_type=payload.target_type,
            target_arn=payload.target_arn,
            target_input={},
            state=TaskState.ENABLED,
            last_execution_time=None,
            next_execution_time=None,
            execution_count=0,
            max_retry_attempts=3,
            retry_policy={},
            dead_letter_config={},
            created_at=now,
            updated_at=now
        )

        service.task_repository.get_by_name.return_value = None
        service.task_repository.create.return_value = mock_task

        result = await service.create_task(payload)
        assert result.id == 1
        service.scheduler_engine.add_job.assert_awaited_once()

    async def test_create_task_duplicate_name_raises(self):
        service = await self.async_set_up_service()
        payload = ScheduledTaskCreate(
            name="task1",
            target_type="http",  # ✅ 改成合法 enum 值
            target_arn="http://example.com/endpoint",
            schedule_expression="rate(5 minutes)",
            timezone="Asia/Taipei",
            state=TaskState.ENABLED
        )
        service.task_repository.get_by_name.return_value = MagicMock()
        with pytest.raises(HTTPException):
            await service.create_task(payload)

    async def test_trigger_task_now_success(self):
        service = await self.async_set_up_service()

        now = datetime.now(timezone.utc)
        mock_task = SimpleNamespace(
            id=1,
            name="task1",
            target_type="http",
            target_arn="http://example.com/endpoint",
            target_input={},
            schedule_expression="rate(5 minutes)",
            timezone="Asia/Taipei",  # ✅ 必須是字串
            state=TaskState.ENABLED,
            last_execution_time=None,
            next_execution_time=None,
            execution_count=0,
            max_retry_attempts=3,
            retry_policy={},
            dead_letter_config={},
            created_at=now,
            updated_at=now
        )

        service.task_repository.get_by_id.return_value = mock_task

        result = await service.trigger_task_now(task_id=1)

        assert result is True
        service.execution_repository.create.assert_awaited()
        service.task_repository.increment_execution_count.assert_awaited()
        service.scheduler_engine.add_job.assert_not_called()

    async def test_delete_task_success(self):
        service = await self.async_set_up_service()
        mock_task = MagicMock(id=1, name="task1")
        service.task_repository.get_by_id.return_value = mock_task
        result = await service.delete_task(task_id=1)
        assert result is True
        service.scheduler_engine.remove_job.assert_awaited_once()
        service.task_repository.delete_object.assert_awaited_once_with(mock_task)

    async def test_delete_task_not_found(self):
        service = await self.async_set_up_service()
        service.task_repository.get_by_id.return_value = None
        with pytest.raises(HTTPException):
            await service.delete_task(task_id=1)

    async def test_update_task_state_success(self):
        service = await self.async_set_up_service()
        now = datetime.now(timezone.utc)

        # ✅ 使用 SimpleNamespace 並填寫 ScheduledTaskResponse 需要的欄位
        mock_task = SimpleNamespace(
            id=1,
            name="task1",
            description="test task",
            schedule_expression="rate(5 minutes)",
            timezone="Asia/Taipei",
            target_type="http",
            target_arn="http://example.com/endpoint",
            target_input={},
            state=TaskState.DISABLED,
            last_execution_time=None,
            next_execution_time=None,
            execution_count=0,
            max_retry_attempts=3,
            retry_policy={},
            dead_letter_config={},
            created_at=now,
            updated_at=now
        )

        service.task_repository.get_by_id.return_value = mock_task

        state_data = TaskStateUpdateRequest(state=TaskState.DISABLED)
        result = await service.update_task_state(task_id=1, state_data=state_data)

        assert result.id == 1
        service.task_repository.update_state.assert_awaited_once()

    async def test_get_all_tasks(self):
        service = await self.async_set_up_service()
        now = datetime.now(timezone.utc)

        # ✅ 使用 SimpleNamespace 填入完整欄位
        mock_task = SimpleNamespace(
            id=1,
            name="task1",
            description="test task",
            schedule_expression="rate(5 minutes)",
            timezone="Asia/Taipei",
            target_type="http",
            target_arn="http://example.com/endpoint",
            target_input={},
            state=TaskState.ENABLED,
            last_execution_time=None,
            next_execution_time=None,
            execution_count=0,
            max_retry_attempts=3,
            retry_policy={},
            dead_letter_config={},
            created_at=now,
            updated_at=now
        )

        service.task_repository.find_all.return_value = [mock_task]

        result = await service.get_all_tasks()
        assert len(result) == 1
        assert result[0].id == 1

    async def test_get_task_executions(self):
        service = await self.async_set_up_service()
        now = datetime.now(timezone.utc)
        response_body_str = json.dumps({"message": "ok"})

        mock_execution = SimpleNamespace(
            id=1,
            task_id=1,
            status=ExecutionStatus.SUCCEEDED,
            execution_time=0.1,
            result="ok",
            created_at=now,
            updated_at=now,
            started_at=now,
            completed_at=now,
            response_code=200,
            response_body=response_body_str,
            error_message=None,
            attempt_number=1
        )

        service.execution_repository.get_by_task_id.return_value = [mock_execution]

        result = await service.get_task_executions(task_id=1)
        assert len(result) == 1
        assert isinstance(result[0], TaskExecutionResponse)