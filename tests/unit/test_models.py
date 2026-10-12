"""数据字典 MCP 输入模型测试。"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from data_engineer_agent.models import DictionaryQueryInput, DictionaryQueryRequest


@pytest.mark.unit
def test_requests_must_not_be_empty() -> None:
    """批量入口必须至少包含一个查询请求。"""

    with pytest.raises(ValidationError):
        DictionaryQueryInput(requests=[])


@pytest.mark.unit
def test_total_lookup_terms_must_not_exceed_limit() -> None:
    """单次调用中的查询词总数不得超过一百个。"""

    request = DictionaryQueryRequest(
        dictionary_type="证件类型",
        item_codes=[str(index) for index in range(101)],
    )

    with pytest.raises(ValidationError, match="查询条件总数不能超过 100"):
        DictionaryQueryInput(requests=[request])


@pytest.mark.unit
def test_item_codes_keep_leading_zero() -> None:
    """码值模型不得把带前导零的字符串转换成数字。"""

    request = DictionaryQueryRequest(
        dictionary_type="证件类型",
        item_codes=["01"],
    )

    assert request.item_codes == ["01"]

