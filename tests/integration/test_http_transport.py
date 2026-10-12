"""通过真实 Streamable HTTP 端点执行 MCP 接口联调。"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from collections.abc import Iterator

import httpx
import pytest
from mcp import Client


HTTP_START_TIMEOUT_SECONDS = 5.0
PROCESS_STOP_TIMEOUT_SECONDS = 5.0
LOCAL_HOST = "127.0.0.1"


def _find_available_port() -> int:
    """向操作系统申请当前可用端口，避免测试占用固定业务端口。"""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind((LOCAL_HOST, 0))
        return int(listener.getsockname()[1])


def _wait_until_listening(process: subprocess.Popen[str], port: int) -> None:
    """等待子进程开始监听；提前退出时携带服务日志终止测试。"""

    deadline = time.monotonic() + HTTP_START_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout else ""
            pytest.fail(f"MCP HTTP 服务启动失败：\n{output}")
        try:
            with socket.create_connection((LOCAL_HOST, port), timeout=0.1):
                return
        except OSError:
            time.sleep(0.05)
    pytest.fail(f"MCP HTTP 服务未在 {HTTP_START_TIMEOUT_SECONDS} 秒内启动")


@pytest.fixture
def mcp_http_url(database_url: str) -> Iterator[str]:
    """启动真实 HTTP 服务，并在测试结束后可靠回收子进程。"""

    port = _find_available_port()
    environment = {
        **os.environ,
        "DATABASE_URL": database_url,
        "MCP_HOST": LOCAL_HOST,
        "MCP_PORT": str(port),
    }
    process = subprocess.Popen(
        [sys.executable, "-m", "data_engineer_agent.server"],
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        _wait_until_listening(process, port)
        yield f"http://{LOCAL_HOST}:{port}/mcp"
    finally:
        process.terminate()
        try:
            process.wait(timeout=PROCESS_STOP_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=PROCESS_STOP_TIMEOUT_SECONDS)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_streamable_http_endpoint_queries_postgresql(mcp_http_url: str) -> None:
    """真实 HTTP MCP 会话应查询数据库并返回预期字典项。"""

    async with Client(mcp_http_url) as client:
        listing = await client.list_tools()
        result = await client.call_tool(
            "query_data_dictionary",
            {
                "requests": [
                    {
                        "dictionary_type": "证件类型",
                        "item_codes": ["02"],
                    }
                ]
            },
        )

    assert [tool.name for tool in listing.tools] == ["query_data_dictionary"]
    assert result.structured_content is not None
    match = result.structured_content["results"][0]["lookups"][0]["matches"][0]
    assert match["item_code"] == "02"
    assert match["item_name"] == "军官证"


@pytest.mark.integration
def test_fastapi_http_endpoint_queries_postgresql(mcp_http_url: str) -> None:
    """真实 Uvicorn REST 端点应完成请求校验并查询 PostgreSQL。"""

    service_url = mcp_http_url.removesuffix("/mcp")
    response = httpx.post(
        f"{service_url}/api/v1/data-dictionaries/query",
        json={
            "requests": [
                {
                    "dictionary_type": "证件类型",
                    "item_names": ["军官证"],
                }
            ]
        },
        timeout=HTTP_START_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200
    match = response.json()["results"][0]["lookups"][0]["matches"][0]
    assert match["item_code"] == "02"
    assert match["item_name"] == "军官证"
