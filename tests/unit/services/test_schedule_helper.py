import pytest

from src.models.pydantic.schedule_helper import (
    RateExpressionRequest, CronExpressionRequest, QuickScheduleRequest,
    ScheduleValidationRequest, ScheduleType
)
from src.services.schedule_helper import ScheduleHelperService


@pytest.mark.asyncio
class TestScheduleHelperService:

    @pytest.fixture
    def service(self):
        return ScheduleHelperService()

    async def test_generate_rate_expression(self, service):
        req = RateExpressionRequest(value=5, unit="minute")
        res = await service.generate_rate_expression(req)
        assert res.expression == "rate(5 minute)"
        assert res.type == ScheduleType.RATE
        assert "每5" in res.description
        assert len(res.next_runs) == 5

    async def test_generate_cron_expression(self, service):
        req = CronExpressionRequest(minute="0", hour="9", day="*", month="*", weekday="1-5")
        res = await service.generate_cron_expression(req)
        assert res.expression == "cron(0 9 * * 1-5)"
        assert res.type == ScheduleType.CRON
        assert "每天9:00" in res.description or "週一到週五" in res.description
        assert len(res.next_runs) == 5

    async def test_generate_quick_schedule_predefined(self, service):
        req = QuickScheduleRequest(type="every_minute")
        res = await service.generate_quick_schedule(req)
        assert res.expression == "rate(1 minute)"
        assert res.type == ScheduleType.RATE
        assert res.description == "每分鐘執行"
        assert len(res.next_runs) == 5

    async def test_generate_quick_schedule_custom_time(self, service):
        req = QuickScheduleRequest(type="custom_time", time="08:30", weekdays=[1,2])
        res = await service.generate_quick_schedule(req)
        assert res.expression.startswith("cron(")
        assert res.type == ScheduleType.CRON
        assert "08:30" in res.description
        assert len(res.next_runs) == 5

    async def test_generate_quick_schedule_custom_interval(self, service):
        req = QuickScheduleRequest(type="custom_interval", interval=2, unit="hour")
        res = await service.generate_quick_schedule(req)
        assert res.expression == "rate(2 hour)"
        assert res.type == ScheduleType.RATE
        assert "每2hour" in res.description
        assert len(res.next_runs) == 5

    async def test_validate_expression_rate(self, service):
        req = ScheduleValidationRequest(expression="rate(10 minutes)")
        res = await service.validate_expression(req)
        assert res.valid
        assert res.type == ScheduleType.RATE
        assert "10" in res.description
        assert len(res.next_runs) == 5

    async def test_validate_expression_cron(self, service):
        req = ScheduleValidationRequest(expression="cron(0 9 * * 1-5)")
        res = await service.validate_expression(req)
        assert res.valid
        assert res.type == ScheduleType.CRON
        assert "每天9:00" in res.description or "週一到週五" in res.description
        assert len(res.next_runs) == 5

    async def test_validate_expression_invalid(self, service):
        req = ScheduleValidationRequest(expression="rate(-5 minutes)")
        res = await service.validate_expression(req)
        assert not res.valid
        assert "格式錯誤" in res.error

    async def test_get_schedule_templates(self, service):
        res = await service.get_schedule_templates()
        assert len(res) > 0
        assert any(t.type in [ScheduleType.RATE, ScheduleType.CRON] for t in res)

    async def test_get_cron_help(self, service):
        res = await service.get_cron_help()
        assert len(res) == 5
        assert all(hasattr(r, "field") for r in res)
