from src.services.email_template import EmailTemplateService
from src.services.statistic import StatisticService
from src.services.team import TeamService
from src.services.scheduler import SchedulerService


def get_team_service() -> TeamService:
    return TeamService()


def get_scheduler_service() -> SchedulerService:
    return SchedulerService()


def get_statistic_service() -> StatisticService:
    return StatisticService()

def get_email_template_service() -> EmailTemplateService:
    return EmailTemplateService()