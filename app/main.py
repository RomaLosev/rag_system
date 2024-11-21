import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from loguru import logger

from app.api.chat import chat_router
from app.core.config import settings
from app.dependencies.containers import Container

ROUTES = ("app.api.chat",)
ROUTERS = (chat_router,)


def init_containers(fastapi_app: FastAPI):
    container = Container()
    container.wire(modules=ROUTES)
    fastapi_app.container = container

    @fastapi_app.on_event("startup")
    async def initialize_vector_store():
        logger.info("Initializing VectorStore...")
        container.vector_store()
        logger.info("VectorStore initialized successfully.")


def include_routers(fastapi_app: FastAPI):
    for route in ROUTERS:
        fastapi_app.include_router(route)


def create_app():
    fastapi_app = FastAPI(
        title=settings.app_title,
        docs_url="/api/docs",
        openapi_url="/api/docs.json",
        default_response_class=ORJSONResponse,
        debug=settings.debug,
    )
    init_containers(fastapi_app)
    include_routers(fastapi_app)
    return fastapi_app


app = create_app()


@app.get("/", include_in_schema=False)
def hello():
    return "Hi there!"


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        log_level="info",
        reload=True,
    )
