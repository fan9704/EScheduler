from src.routers.team import router as team_router
from src.utils.api import TypedAPIRouter
from src.routers.scheduler import router as scheduler_router
from src.utils.api.router import TypedAPIRouter

teams_router = TypedAPIRouter(router=team_router, prefix="/api/team", tags=["team"])

scheduler_api_router = TypedAPIRouter(
    router=scheduler_router, 
    prefix="/api/scheduler", 
    tags=["scheduler"]
)
