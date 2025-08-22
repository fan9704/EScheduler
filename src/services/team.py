from fastapi import HTTPException

from src.models.pydantic import TeamAuthResponse
from src.repositories import TeamRepository
from src.dependencies.repositories import get_team_repository
from src.utils import jwt


class TeamService:
    def __init__(self):
        self.repository: TeamRepository = get_team_repository()

    async def get_all_team(self):
        return await self.repository.find_all()

    async def get_team_by_token(self, token: str):
        team = await self.repository.get_team_by_token(token=token)
        if not team:
            raise HTTPException(status_code=400, detail="Token is invalid")
        return team

    async def auth_team(self, token: str) -> TeamAuthResponse:
        team = await self.repository.get_team_by_token(token=token)
        status = False
        token = None

        if team:
            token = jwt.create_team_access_token(team)
            status = True
        return TeamAuthResponse(
            status=status,
            team=team,
            access_token=token
        )
