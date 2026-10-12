"""真实 PostgreSQL 上的数据字典 MCP Tool 集成测试。"""

from __future__ import annotations

import pytest
from mcp import Client

from data_engineer_agent.repository import DictionaryRepository
from data_engineer_agent.server import create_server
from data_engineer_agent.service import DictionaryQueryService


@pytest.fixture
def mcp_server(database_url: str):
    """创建连接本地 PostgreSQL 的 MCP Server，并在测试后释放连接池。"""

    repository = DictionaryRepository(database_url)
    service = DictionaryQueryService(repository)
    server = create_server(service)
    yield server
    repository.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tool_queries_multiple_types_and_values(mcp_server) -> None:
    """MCP 客户端应在一次调用中获得多个类型和多个码值结果。"""

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "query_data_dictionary",
            {
                "requests": [
                    {
                        "dictionary_type": "证件类型",
                        "item_codes": ["01", "02"],
                        "item_names": ["护照"],
                    },
                    {"dictionary_type": "性别"},
                ],
                "include_inactive": False,
                "page_size": 100,
            },
        )

    output = result.structured_content
    assert output is not None
    assert output["results"][0]["lookups"][0]["matches"][0]["item_code"] == "01"
    assert output["results"][0]["lookups"][1]["matches"][0]["item_code"] == "02"
    assert output["results"][0]["lookups"][2]["matches"][0]["item_code"] == "03"
    assert [item["item_code"] for item in output["results"][1]["items"]] == [
        "01",
        "02",
        "00",
    ]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tool_returns_partial_success_for_global_names(mcp_server) -> None:
    """批量全局反查应同时返回唯一命中、歧义和未命中结果。"""

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "query_data_dictionary",
            {
                "requests": [
                    {"item_names": ["军官证", "未知", "不存在"]},
                ]
            },
        )

    output = result.structured_content
    assert output is not None
    statuses = [lookup["status"] for lookup in output["results"][0]["lookups"]]
    assert statuses == ["FOUND", "AMBIGUOUS", "NOT_FOUND"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tool_keeps_leading_zero_and_hides_inactive_item(mcp_server) -> None:
    """真实数据库查询必须保留前导零，并默认过滤停用数据。"""

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "query_data_dictionary",
            {
                "requests": [
                    {
                        "dictionary_type": "证件类型",
                        "item_codes": ["01", "99"],
                    }
                ]
            },
        )

    output = result.structured_content
    assert output is not None
    lookups = output["results"][0]["lookups"]
    assert lookups[0]["matches"][0]["item_code"] == "01"
    assert lookups[1]["status"] == "NOT_FOUND"
