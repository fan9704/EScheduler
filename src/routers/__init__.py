from src.utils.api.router import TypedAPIRouter
from . import team, scheduler, schedule_helper, statistic


scheduler_router = TypedAPIRouter(
    router=scheduler.router,
    prefix="/api/scheduler",
    tags=["Scheduler"]
)

# 新增排程輔助路由器
schedule_helper_router = TypedAPIRouter(
    router=schedule_helper.router,
    prefix="/api/schedule-helper",
    tags=["Schedule Helper"]
)

static_router = TypedAPIRouter(
    router=statistic.router,
    prefix="/api/statistic",
    tags=["Statistic"]
)
