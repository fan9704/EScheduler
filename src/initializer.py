import logging
from inspect import getmembers

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from tortoise import Tortoise

from src.configs import tortoise_config, ALLOW_ORIGINS, SECRET_KEY
from src.utils.api.router import TypedAPIRouter

logger = logging.getLogger(__name__)


def init(app: FastAPI):
    """
    Init routers and etc.
    :return:
    """
    # init_db(app)
    init_routers(app)
    # 初始化 Middleware
    init_cors(app)
    init_middleware(app)
    # 初始化 Scheduler
    init_scheduler()
    # 設定靜態文件的目錄（上傳檔案的存放位置）
    app.mount("/media", StaticFiles(directory="media"), name="media")


async def init_db(app: FastAPI):
    """初始化資料庫模型"""
    config = {
        "use_tz": True,
        "timezone": "Asia/Taipei",
        "connections": {
            "default": tortoise_config.db_url
        },
        "apps": {
            "models": {
                "models": [
                    "src.models.tortoise.scheduler",
                    "src.models.tortoise.team",
                    "src.models.tortoise.email_template"
                ],
                'default_connection': 'default',
            }
        }
    }
    await Tortoise.init(
        config=config
    )
    await Tortoise.generate_schemas()


def init_routers(app: FastAPI):
    """
    Initialize routers defined in `app.api`
    :param app:
    :return:
    """

    from src import routers

    routers = [o[1] for o in getmembers(routers) if isinstance(o[1], TypedAPIRouter)]

    for router in routers:
        app.include_router(**router.dict())


def init_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def init_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.start()


def init_middleware(app: FastAPI):
    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
