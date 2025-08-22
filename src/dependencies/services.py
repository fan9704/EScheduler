from src.services.team import TeamService


def get_team_service() -> TeamService:
    return TeamService()
