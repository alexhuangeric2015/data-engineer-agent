"""FastAPI 到真实 PostgreSQL 的接口联调测试。"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from data_engineer_agent.api.app import create_app
from data_engineer_agent.config import Settings


@pytest.mark.integration
def test_rest_endpoint_queries_dictionary_from_postgresql(database_url: str) -> None:
    """REST 请求应经过应用服务和仓储返回真实字典码值。"""

    settings = Settings(database_url=database_url)
    with TestClient(create_app(settings=settings)) as client:
        response = client.post(
            "/api/v1/data-dictionaries/query",
            json={
                "requests": [
                    {
                        "dictionary_type": "证件类型",
                        "item_codes": ["02"],
                    }
                ]
            },
        )

    assert response.status_code == 200
    match = response.json()["results"][0]["lookups"][0]["matches"][0]
    assert match["item_code"] == "02"
    assert match["item_name"] == "军官证"
