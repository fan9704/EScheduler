import pytest
import pytest_asyncio
from tortoise import Tortoise


@pytest_asyncio.fixture(scope="function", autouse=False)
async def in_memory_db():
    """
    建立 in-memory SQLite 測試資料庫
    每個測試 function 都會重新建立 schema，確保測試互不影響
    """
    # 初始化 ORM
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={
            "models": [
                "src.models.tortoise.scheduler",
                "src.models.tortoise.team",
                "src.models.tortoise.email_template"
            ],
        }
    )

    # 生成資料表
    await Tortoise.generate_schemas()

    yield  # 測試在這裡執行

    # 測試結束後清除所有連線
    await Tortoise.close_connections()
