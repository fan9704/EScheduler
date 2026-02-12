# import pytest
# from unittest.mock import AsyncMock, patch
# from fastapi import FastAPI
#
# # ✅ mock 掉 init_scheduler 以避免 APScheduler 啟動錯誤
# with patch("src.initializer.init_scheduler", lambda: None):
#     from src import main
#
#
# @pytest.mark.asyncio
# async def test_lifespan_starts_and_stops_scheduler(monkeypatch):
#     """確認 lifespan 中會啟動與關閉 SchedulerEngine"""
#     mock_scheduler = AsyncMock()
#     mock_scheduler.start = AsyncMock()
#     mock_scheduler.stop = AsyncMock()
#
#     monkeypatch.setattr(main, "init_db", AsyncMock())
#     monkeypatch.setattr(main, "get_scheduler_engine", lambda: mock_scheduler)
#     monkeypatch.setattr(main, "SchedulerEngine", lambda: mock_scheduler)
#
#     app = FastAPI(lifespan=main.lifespan)
#
#     async with app.router.lifespan_context(app):
#         mock_scheduler.start.assert_awaited_once()
#
#     mock_scheduler.stop.assert_awaited_once()
