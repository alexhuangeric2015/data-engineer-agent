"""FastAPI 应用工厂。"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from data_engineer_agent.api.routes import router
from data_engineer_agent.config import Settings
from data_engineer_agent.repository import DictionaryRepository
from data_engineer_agent.server import create_server
from data_engineer_agent.service import DictionaryQueryService


APPLICATION_NAME = "数据字典查询服务"
APPLICATION_VERSION = "0.2.0"


def create_app(
    *,
    settings: Settings | None = None,
    service: DictionaryQueryService | None = None,
) -> FastAPI:
    """创建同时提供 REST API 与 MCP 的 FastAPI 应用。

    Args:
        settings: 生产启动配置；未注入业务服务时必须可从环境加载。
        service: 测试或组合部署时注入的业务服务；为空时创建 PostgreSQL 仓储。

    Returns:
        尚未开始监听端口的 FastAPI 应用。

    Raises:
        pydantic.ValidationError: 环境配置不完整或端口范围非法时抛出。
        sqlalchemy.exc.SQLAlchemyError: PostgreSQL 不可连接时抛出。
    """

    repository: DictionaryRepository | None = None
    if service is None:
        resolved_settings = settings or Settings()
        repository = DictionaryRepository(resolved_settings.database_url)
        service = DictionaryQueryService(repository)

    mcp_app = create_server(service).streamable_http_app(
        streamable_http_path="/mcp",
        host=(settings.mcp_host if settings else "127.0.0.1"),
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        """启动 MCP 会话管理器，并在退出时释放数据库连接池。"""

        try:
            async with mcp_app.router.lifespan_context(mcp_app):
                yield
        finally:
            if repository is not None:
                repository.close()

    app = FastAPI(
        title=APPLICATION_NAME,
        version=APPLICATION_VERSION,
        lifespan=lifespan,
    )
    app.state.dictionary_service = service
    app.include_router(router)
    # MCP 应用放在最后，避免根路径挂载抢先匹配 REST 与 OpenAPI 路由。
    app.mount("/", mcp_app, name="mcp")
    return app
