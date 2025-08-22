from src.services.team import TeamService
from src.services.scheduler import SchedulerService


def get_team_service() -> TeamService:
    return TeamService()


def get_scheduler_service() -> SchedulerService:
    return SchedulerService()
