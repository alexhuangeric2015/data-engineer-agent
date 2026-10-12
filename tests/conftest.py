"""测试共享配置与 PostgreSQL 可用性检查。"""

from __future__ import annotations

import pytest

from data_engineer_agent.config import Settings


@pytest.fixture(scope="session")
def database_url() -> str:
    """从环境变量或项目 ``.env`` 返回集成测试数据库地址。"""

    try:
        return Settings().database_url
    except ValueError as error:
        pytest.skip(f"集成测试缺少 PostgreSQL 配置：{error}")
