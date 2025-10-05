import logging
import uvicorn
import asyncio
import os

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.configs import OPENAPI_API_NAME, OPENAPI_API_VERSION, OPENAPI_API_DESCRIPTION, APPLICATION_PORT, IS_CONTAINER
from src.initializer import init, init_db
from prometheus_fastapi_instrumentator import Instrumentator

logger = logging.getLogger(__name__)
instrumentator = Instrumentator()


# 在 lifespan 中啟動排程引擎
@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程序生命週期管理"""
    logger.info("啟動應用程序...")
    
    # 等待資料庫完全初始化
    await init_db(app)
    await asyncio.sleep(3)
    
    # 🔥 啟動排程引擎
    try:
        from src.dependencies.utils import get_scheduler_engine
        from src.services.scheduler_engine import SchedulerEngine
        scheduler_engine: SchedulerEngine = get_scheduler_engine()
        await scheduler_engine.start()
        logger.info("排程引擎啟動成功")
    except Exception as e:
        logger.error(f"排程引擎啟動失敗: {e}")
    
    yield
    
    # 關閉服務
    logger.info("關閉應用程序...")
    try:
        from src.services.scheduler_engine import scheduler_engine
        await scheduler_engine.stop()
    except Exception as e:
        logger.error(f"關閉排程引擎失敗: {e}")


app = FastAPI(
    title=OPENAPI_API_NAME,
    version=OPENAPI_API_VERSION,
    description=OPENAPI_API_DESCRIPTION,
    lifespan=lifespan,
)
if IS_CONTAINER is True:
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

    @app.get("/")
    async def index():
        return FileResponse("frontend/dist/index.html")
instrumentator.instrument(app)
logger.info("開始應用程序初始化...")
init(app)
logger.info("初始化成功完成！")
instrumentator.expose(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=APPLICATION_PORT, reload=True)
