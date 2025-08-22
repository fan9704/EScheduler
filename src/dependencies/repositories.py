from src.repositories import *


def get_team_repository() -> TeamRepository:
    return TeamRepository()