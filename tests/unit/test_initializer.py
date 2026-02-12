# from unittest.mock import MagicMock, AsyncMock
#
# import pytest
# from fastapi import FastAPI
#
# from src import initializer
#
#
# @pytest.mark.asyncio
# async def test_init_calls_all_components(monkeypatch):
#     """確保 init() 會呼叫所有初始化流程"""
#     app = FastAPI()
#
#     called = {}
#
#     monkeypatch.setattr(initializer, "init_routers", lambda a: called.setdefault("routers", True))
#     monkeypatch.setattr(initializer, "init_cors", lambda a: called.setdefault("cors", True))
#     monkeypatch.setattr(initializer, "init_middleware", lambda a: called.setdefault("middleware", True))
#     monkeypatch.setattr(initializer, "init_scheduler", lambda: called.setdefault("scheduler", True))
#
#     initializer.init(app)
#
#     assert called == {"routers": True, "cors": True, "middleware": True, "scheduler": True}
#     # 確認 /media 靜態目錄已掛載
#     assert "/media" in app.routes[0].path
#
#
# @pytest.mark.asyncio
# async def test_init_db_calls_tortoise_methods(monkeypatch):
#     """確認 init_db 會初始化 Tortoise ORM"""
#     mock_init = AsyncMock()
#     mock_generate = AsyncMock()
#
#     monkeypatch.setattr(initializer.Tortoise, "init", mock_init)
#     monkeypatch.setattr(initializer.Tortoise, "generate_schemas", mock_generate)
#
#     app = FastAPI()
#     await initializer.init_db(app)
#
#     mock_init.assert_awaited_once()
#     mock_generate.assert_awaited_once()
#
#
# def test_init_cors_adds_middleware():
#     app = FastAPI()
#     initializer.init_cors(app)
#
#     middlewares = [m.cls.__name__ for m in app.user_middleware]
#     assert "CORSMiddleware" in middlewares
#
#
# def test_init_middleware_adds_session(monkeypatch):
#     app = FastAPI()
#     monkeypatch.setattr(initializer, "SECRET_KEY", "test_secret")
#     initializer.init_middleware(app)
#
#     middlewares = [m.cls.__name__ for m in app.user_middleware]
#     assert "SessionMiddleware" in middlewares
#
#
# def test_init_routers_includes_router(monkeypatch):
#     app = FastAPI()
#
#     mock_router = MagicMock()
#     mock_router.dict.return_value = {"router": "router_obj"}
#
#     mock_module = MagicMock()
#     mock_module.TypedAPIRouter = initializer.TypedAPIRouter
#     monkeypatch.setattr(initializer, "getmembers", lambda x: [("r", mock_router)])
#     monkeypatch.setattr(initializer, "routers", mock_module)
#
#     initializer.init_routers(app)
#     mock_router.dict.assert_called_once()
