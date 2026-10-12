"""FastAPI 数据字典接口测试。"""

from __future__ import annotations

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from data_engineer_agent.api.app import create_app
from data_engineer_agent.models import DictionaryQueryResponse, QuerySummary
from data_engineer_agent.service import DictionaryQueryService


@pytest.fixture
def service() -> Mock:
    """创建返回空批量结果的业务服务替身。"""

    service = Mock(spec=DictionaryQueryService)
    service.query.return_value = DictionaryQueryResponse(
        results=[],
        summary=QuerySummary(
            request_count=0,
            lookup_count=0,
            succeeded=0,
            not_found=0,
            ambiguous=0,
            invalid=0,
            not_enabled=0,
        ),
    )
    return service


@pytest.fixture
def client(service: Mock) -> TestClient:
    """创建不连接 PostgreSQL 的 FastAPI 测试客户端。"""

    return TestClient(create_app(service=service))


@pytest.mark.unit
def test_query_endpoint_validates_and_delegates_batch_request(
    client: TestClient,
    service: Mock,
) -> None:
    """HTTP 接口应保留前导零，并把完整请求交给应用服务。"""

    response = client.post(
        "/api/v1/data-dictionaries/query",
        json={
            "requests": [
                {
                    "dictionary_type": "证件类型",
                    "item_codes": ["01"],
                }
            ]
        },
    )

    assert response.status_code == 200
    query_input = service.query.call_args.args[0]
    assert query_input.requests[0].item_codes == ["01"]
    assert response.json()["summary"]["request_count"] == 0


@pytest.mark.unit
def test_query_endpoint_rejects_unknown_request_fields(client: TestClient) -> None:
    """HTTP 边界应拒绝未声明字段，避免调用方误以为参数已经生效。"""

    response = client.post(
        "/api/v1/data-dictionaries/query",
        json={
            "requests": [{"dictionary_type": "证件类型"}],
            "unknown_option": True,
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "extra_forbidden"


@pytest.mark.unit
def test_openapi_exposes_typed_dictionary_contract(client: TestClient) -> None:
    """OpenAPI 文档应公开稳定的请求和响应模型。"""

    document = client.get("/openapi.json").json()
    operation = document["paths"]["/api/v1/data-dictionaries/query"]["post"]

    assert operation["operationId"] == "query_data_dictionary"
    assert "DictionaryQueryInput" in document["components"]["schemas"]
    assert "DictionaryQueryResponse" in document["components"]["schemas"]
