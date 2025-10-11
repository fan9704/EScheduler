from src.services.email_template import EmailTemplateService
from src.services.schedule_helper import ScheduleHelperService
from src.services.statistic import StatisticService
from src.services.scheduler import SchedulerService


def get_scheduler_service() -> SchedulerService:
    return SchedulerService()


def get_schedule_helper_service() -> ScheduleHelperService:
    return ScheduleHelperService()


def get_statistic_service() -> StatisticService:
    return StatisticService()


def get_email_template_service() -> EmailTemplateService:
    return EmailTemplateService()
