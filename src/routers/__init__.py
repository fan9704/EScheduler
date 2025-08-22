from src.routers.team import router as team_router
from src.utils.api import TypedAPIRouter

teams_router = TypedAPIRouter(router=team_router, prefix="/api/team", tags=["team"])
