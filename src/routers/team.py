from typing import Optional, List

from fastapi import APIRouter, Depends

from src.services.team import TeamService
from src.models.pydantic import Team, TeamAuthRequest, TeamAuthResponse
from src.dependencies.services import get_team_service

router = APIRouter()


@router.get("/",
            summary="取得所有 Team",
            description="Get All Teams",
            response_model=List[Team],
            response_description="All Teams")
async def get(service: TeamService = Depends(get_team_service)) -> List[Team]:
    return await service.get_all_team()


@router.get("/{token}/",
            summary="認證 Team 透過 Token",
            description="Get Team by Tokens",
            response_model=Optional[Team],
            response_description="Your Team")
async def get_team_by_token(token: str, service: TeamService = Depends(get_team_service)) -> Optional[Team]:
    return await service.get_team_by_token(token=token)


@router.post("/auth/token/",
             summary="認證 Team 透過 Token 並取得 JWT",
             description="Team Auth with Token API",
             response_model=TeamAuthResponse,
             response_description="Your Team Information")
async def auth_team(request: TeamAuthRequest,
                    service: TeamService = Depends(get_team_service)) -> TeamAuthResponse:
    return await service.auth_team(token=request.token)
