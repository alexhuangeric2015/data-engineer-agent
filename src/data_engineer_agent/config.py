"""应用运行配置。"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_MCP_HOST = "127.0.0.1"
DEFAULT_MCP_PORT = 8000


class Settings(BaseSettings):
    """保存 FastAPI、MCP 和 PostgreSQL 的运行配置。

    配置只从环境变量和项目根目录 ``.env`` 读取；类本身不创建连接，因而可以在
    启动前完成格式校验，也便于测试显式传入替代配置。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    database_url: str = Field(description="PostgreSQL 数据字典库连接地址。")
    mcp_host: str = Field(
        default=DEFAULT_MCP_HOST,
        description="FastAPI 与 MCP 统一 HTTP 服务的监听地址。",
    )
    mcp_port: int = Field(
        default=DEFAULT_MCP_PORT,
        ge=1,
        le=65535,
        description="FastAPI 与 MCP 统一 HTTP 服务的监听端口。",
    )
