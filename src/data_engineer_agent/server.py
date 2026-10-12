"""数据字典 MCP Tool 注册与统一 HTTP 服务启动入口。"""

from __future__ import annotations

import logging

from mcp.server import MCPServer
from mcp.types import ToolAnnotations
import uvicorn

from data_engineer_agent.config import Settings
from data_engineer_agent.models import (
    DEFAULT_PAGE_SIZE,
    DictionaryQueryInput,
    DictionaryQueryRequest,
    DictionaryQueryResponse,
)
from data_engineer_agent.service import DictionaryQueryService


LOGGER = logging.getLogger(__name__)
SERVER_NAME = "data-dictionary-mcp"
SERVER_VERSION = "0.2.0"


def create_server(service: DictionaryQueryService) -> MCPServer:
    """创建只暴露一个批量数据字典查询 Tool 的 MCP Server。

    Args:
        service: 已注入仓储的数据字典业务服务。

    Returns:
        尚未启动传输层、可用于 HTTP 或进程内测试的 MCP Server。
    """

    server = MCPServer(
        name=SERVER_NAME,
        title="数据字典查询服务",
        description="批量查询字典类型、码值和字典项名称。",
        version=SERVER_VERSION,
    )

    @server.tool(
        name="query_data_dictionary",
        title="批量查询数据字典",
        description=(
            "一次调用可列举多个字典类型、批量按码值查询名称、"
            "批量按名称反查码值。码值必须使用字符串。"
        ),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
        structured_output=True,
    )
    def query_data_dictionary(
        requests: list[DictionaryQueryRequest],
        include_inactive: bool = False,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> DictionaryQueryResponse:
        """执行支持部分成功的批量数据字典查询。

        Args:
            requests: 按字典类型分组的查询请求，支持多组批量提交。
            include_inactive: 是否允许返回停用或超过有效期的数据。
            page_size: 每个纯列举请求最多返回的字典项数量。

        Returns:
            与请求顺序一致的结构化结果和汇总统计。

        Raises:
            pydantic.ValidationError: 输入数量或字段约束不合法时抛出。
        """

        query_input = DictionaryQueryInput(
            requests=requests,
            include_inactive=include_inactive,
            page_size=page_size,
        )
        return service.query(query_input)

    return server


def main() -> None:
    """读取环境配置并启动 FastAPI 与 MCP 共用的 HTTP 服务。

    FastAPI 提供 REST/OpenAPI，挂载的 MCP 应用继续提供 ``/mcp``。应用工厂负责
    PostgreSQL 连接池和 MCP 会话生命周期；本入口不创建数据库或导入基础数据。
    """

    # 延迟导入用于打破应用工厂与 MCP 注册函数之间的模块循环依赖。
    from data_engineer_agent.api.app import create_app

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    settings = Settings()
    app = create_app(settings=settings)
    LOGGER.info(
        "[数据字典][统一HTTP服务启动] host=%s, port=%s",
        settings.mcp_host,
        settings.mcp_port,
    )
    uvicorn.run(
        app,
        host=settings.mcp_host,
        port=settings.mcp_port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
