from src.dependencies.services import get_team_service, get_scheduler_service, get_statistic_service, \
    get_schedule_helper_service, get_email_template_service
from src.services.email_template import EmailTemplateService
from src.services.schedule_helper import ScheduleHelperService
from src.services.scheduler import SchedulerService
from src.services.statistic import StatisticService
from src.services.team import TeamService


class TestServiceDependencies:
    def test_get_team_service_returns_new_instance(self):
        service1 = get_team_service()
        service2 = get_team_service()
        assert isinstance(service1, TeamService)
        assert isinstance(service2, TeamService)
        assert service1 is not service2  # 確保不是同一實例

    def test_get_scheduler_service_returns_new_instance(self):
        s1 = get_scheduler_service()
        s2 = get_scheduler_service()
        assert isinstance(s1, SchedulerService)
        assert isinstance(s2, SchedulerService)
        assert s1 is not s2

    def test_get_schedule_helper_service_returns_new_instance(self):
        s1 = get_schedule_helper_service()
        s2 = get_schedule_helper_service()
        assert isinstance(s1, ScheduleHelperService)
        assert isinstance(s2, ScheduleHelperService)
        assert s1 is not s2

    def test_get_statistic_service_returns_new_instance(self):
        s1 = get_statistic_service()
        s2 = get_statistic_service()
        assert isinstance(s1, StatisticService)
        assert isinstance(s2, StatisticService)
        assert s1 is not s2

    def test_get_email_template_service_returns_new_instance(self):
        s1 = get_email_template_service()
        s2 = get_email_template_service()
        assert isinstance(s1, EmailTemplateService)
        assert isinstance(s2, EmailTemplateService)
        assert s1 is not s2
