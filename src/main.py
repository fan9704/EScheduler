import logging
import uvicorn

from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.configs import OPENAPI_API_NAME, OPENAPI_API_VERSION, OPENAPI_API_DESCRIPTION, APPLICATION_PORT
from src.initializer import init
from prometheus_fastapi_instrumentator import Instrumentator

logger = logging.getLogger(__name__)
instrumentator = Instrumentator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Setting up FastAPI Lifespan")
    yield


app = FastAPI(
    title=OPENAPI_API_NAME,
    version=OPENAPI_API_VERSION,
    description=OPENAPI_API_DESCRIPTION,
    # lifespan=lifespan,
)

instrumentator.instrument(app)
logger.info("Starting application initialization...")
init(app)
logger.info("Successfully initialized!")
instrumentator.expose(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=APPLICATION_PORT, reload=True)
