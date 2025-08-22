import logging
from inspect import getmembers

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from tortoise.contrib.starlette import register_tortoise

from src.configs import tortoise_config, GENERATE_DB_SCHEMA, ALLOW_ORIGINS, SECRET_KEY
from src.utils.api.router import TypedAPIRouter
logger = logging.getLogger(__name__)


def init(app: FastAPI):
    """
    Init routers and etc.
    :return:
    """
    init_routers(app)
    init_db(app)
    # 初始化 Middleware
    init_cors(app)
    init_middleware(app)
    # 初始化 Scheduler
    init_scheduler()
    # 設定靜態文件的目錄（上傳檔案的存放位置）
    app.mount("/media", StaticFiles(directory="media"), name="media")


def init_db(app: FastAPI):
    """
    Init database models.
    :param app:
    :return:
    """
    config = {
        "use_tz": True,
        "timezone": "Asia/Taipei",
        "connections": {
            "default": tortoise_config.db_url
        },
        "apps": {
            "models": {
                "models": ["src.models.tortoise"],
                'default_connection': 'default',
            }

        }
    }
    register_tortoise(
        app,
        config=config,
        generate_schemas=GENERATE_DB_SCHEMA
    )


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