"""数据字典查询服务的核心业务规则测试。"""

from __future__ import annotations

from collections.abc import Iterable

import pytest

from data_engineer_agent.models import (
    DictionaryItemRecord,
    DictionaryQueryInput,
    DictionaryQueryRequest,
    DictionaryTypeRecord,
    ResultStatus,
)
from data_engineer_agent.service import DictionaryQueryService


class InMemoryDictionaryRepository:
    """只用于单元测试的内存仓储，模拟 PostgreSQL 查询结果。"""

    def __init__(self) -> None:
        """初始化覆盖唯一命中、歧义和停用状态的测试数据。"""

        self.types = [
            DictionaryTypeRecord(
                id=1,
                type_code="IDENTITY_DOCUMENT_TYPE",
                type_name="证件类型",
                aliases=["证件类别"],
                source_system="本地测试数据",
                status="ACTIVE",
            ),
            DictionaryTypeRecord(
                id=2,
                type_code="GENDER",
                type_name="性别",
                aliases=[],
                source_system="本地测试数据",
                status="ACTIVE",
            ),
            DictionaryTypeRecord(
                id=3,
                type_code="ORDER_STATUS",
                type_name="订单状态",
                aliases=[],
                source_system="本地测试数据",
                status="ACTIVE",
            ),
        ]
        self.items = [
            self._item(1, 1, "01", "身份证", 10),
            self._item(2, 1, "02", "军官证", 20),
            self._item(3, 1, "03", "护照", 30),
            self._item(4, 1, "04", "驾驶证", 40),
            self._item(5, 1, "99", "旧版证件", 99, status="INACTIVE"),
            self._item(6, 2, "00", "未知", 10),
            self._item(7, 2, "01", "男", 20),
            self._item(8, 3, "UNKNOWN", "未知", 10),
        ]

    @staticmethod
    def _item(
        item_id: int,
        type_id: int,
        code: str,
        name: str,
        order: int,
        *,
        status: str = "ACTIVE",
    ) -> DictionaryItemRecord:
        """构造测试字典项并关联所属字典类型。"""

        type_map = {
            1: ("IDENTITY_DOCUMENT_TYPE", "证件类型"),
            2: ("GENDER", "性别"),
            3: ("ORDER_STATUS", "订单状态"),
        }
        type_code, type_name = type_map[type_id]
        return DictionaryItemRecord(
            id=item_id,
            dictionary_type_id=type_id,
            type_code=type_code,
            type_name=type_name,
            source_system="本地测试数据",
            item_code=code,
            item_name=name,
            aliases=[],
            description=None,
            status=status,
            sort_order=order,
        )

    def find_dictionary_types(
        self,
        dictionary_type: str,
        source_system: str | None,
        include_inactive: bool,
    ) -> list[DictionaryTypeRecord]:
        """按编码、名称或别名精确匹配测试字典类型。"""

        normalized = dictionary_type.casefold()
        return [
            record
            for record in self.types
            if (include_inactive or record.status == "ACTIVE")
            and (source_system is None or record.source_system == source_system)
            and normalized
            in {
                record.type_code.casefold(),
                record.type_name.casefold(),
                *(alias.casefold() for alias in record.aliases),
            }
        ]

    def list_dictionary_items(
        self,
        dictionary_type_id: int,
        include_inactive: bool,
        after_sort_order: int | None,
        after_id: int | None,
        limit: int,
    ) -> list[DictionaryItemRecord]:
        """按稳定顺序返回测试字典项分页。"""

        records = [
            item
            for item in self.items
            if item.dictionary_type_id == dictionary_type_id
            and (include_inactive or item.status == "ACTIVE")
            and (
                after_sort_order is None
                or (item.sort_order, item.id) > (after_sort_order, after_id or 0)
            )
        ]
        return sorted(records, key=lambda item: (item.sort_order, item.id))[:limit]

    def find_dictionary_items(
        self,
        dictionary_type_id: int | None,
        item_codes: list[str],
        item_names: list[str],
        include_inactive: bool,
    ) -> list[DictionaryItemRecord]:
        """批量查找测试码值和名称。"""

        normalized_names = {name.casefold() for name in item_names}
        return [
            item
            for item in self.items
            if (dictionary_type_id is None or item.dictionary_type_id == dictionary_type_id)
            and (include_inactive or item.status == "ACTIVE")
            and (
                item.item_code in item_codes
                or item.item_name.casefold() in normalized_names
                or any(alias.casefold() in normalized_names for alias in item.aliases)
            )
        ]


@pytest.fixture
def service() -> DictionaryQueryService:
    """创建不依赖数据库的查询服务。"""

    return DictionaryQueryService(InMemoryDictionaryRepository())


def _query(
    service: DictionaryQueryService,
    requests: Iterable[DictionaryQueryRequest],
    *,
    include_inactive: bool = False,
    page_size: int = 100,
):
    """执行测试查询并减少用例中的重复构造代码。"""

    return service.query(
        DictionaryQueryInput(
            requests=list(requests),
            include_inactive=include_inactive,
            page_size=page_size,
        )
    )


@pytest.mark.unit
def test_lists_multiple_dictionary_types_in_one_call(
    service: DictionaryQueryService,
) -> None:
    """一次调用应能列出多个字典类型的数据。"""

    response = _query(
        service,
        [
            DictionaryQueryRequest(dictionary_type="证件类型"),
            DictionaryQueryRequest(dictionary_type="性别"),
        ],
    )

    assert [result.matched_type.type_name for result in response.results] == [
        "证件类型",
        "性别",
    ]
    assert [item.item_code for item in response.results[0].items] == [
        "01",
        "02",
        "03",
        "04",
    ]


@pytest.mark.unit
def test_resolves_multiple_codes_and_names_in_input_order(
    service: DictionaryQueryService,
) -> None:
    """同一类型下多个码值和名称应按输入顺序分别返回。"""

    response = _query(
        service,
        [
            DictionaryQueryRequest(
                dictionary_type="证件类型",
                item_codes=["01", "99"],
                item_names=["军官证", "不存在"],
            )
        ],
    )

    lookups = response.results[0].lookups
    assert [(lookup.input_value, lookup.status) for lookup in lookups] == [
        ("01", ResultStatus.FOUND),
        ("99", ResultStatus.NOT_FOUND),
        ("军官证", ResultStatus.FOUND),
        ("不存在", ResultStatus.NOT_FOUND),
    ]
    assert lookups[0].matches[0].item_name == "身份证"
    assert lookups[0].matches[0].item_code == "01"


@pytest.mark.unit
def test_global_name_lookup_reports_unique_and_ambiguous_results(
    service: DictionaryQueryService,
) -> None:
    """无类型名称反查应区分唯一命中和跨类型歧义。"""

    response = _query(
        service,
        [DictionaryQueryRequest(item_names=["军官证", "未知"])],
    )

    unique_result, ambiguous_result = response.results[0].lookups
    assert unique_result.status is ResultStatus.FOUND
    assert unique_result.matches[0].type_name == "证件类型"
    assert ambiguous_result.status is ResultStatus.AMBIGUOUS
    assert {match.type_name for match in ambiguous_result.matches} == {
        "性别",
        "订单状态",
    }


@pytest.mark.unit
def test_inactive_items_are_hidden_by_default_and_can_be_included(
    service: DictionaryQueryService,
) -> None:
    """停用字典项仅在调用方显式允许时返回。"""

    request = DictionaryQueryRequest(
        dictionary_type="证件类型",
        item_codes=["99"],
    )

    hidden_response = _query(service, [request])
    visible_response = _query(service, [request], include_inactive=True)

    assert hidden_response.results[0].lookups[0].status is ResultStatus.NOT_FOUND
    assert visible_response.results[0].lookups[0].status is ResultStatus.FOUND
    assert visible_response.results[0].lookups[0].matches[0].status == "INACTIVE"


@pytest.mark.unit
def test_item_code_without_dictionary_type_is_invalid(
    service: DictionaryQueryService,
) -> None:
    """脱离字典类型的码值无法消除语义歧义，应返回非法参数。"""

    response = _query(service, [DictionaryQueryRequest(item_codes=["01"])])

    lookup = response.results[0].lookups[0]
    assert lookup.status is ResultStatus.INVALID
    assert lookup.error == "按码值查询时必须提供 dictionary_type"


@pytest.mark.unit
def test_keywords_return_not_enabled_without_vector_search(
    service: DictionaryQueryService,
) -> None:
    """首版未启用向量查询时必须返回明确状态而不是忽略关键词。"""

    response = _query(
        service,
        [DictionaryQueryRequest(keywords=["可以证明身份的证件"])],
    )

    lookup = response.results[0].lookups[0]
    assert lookup.status is ResultStatus.NOT_ENABLED
    assert lookup.input_value == "可以证明身份的证件"


@pytest.mark.unit
def test_list_pagination_returns_stable_cursor(
    service: DictionaryQueryService,
) -> None:
    """列举字典项时应返回可继续查询的稳定游标。"""

    first_page = _query(
        service,
        [DictionaryQueryRequest(dictionary_type="证件类型")],
        page_size=2,
    )
    second_page = _query(
        service,
        [
            DictionaryQueryRequest(
                dictionary_type="证件类型",
                cursor=first_page.results[0].next_cursor,
            )
        ],
        page_size=2,
    )

    assert [item.item_code for item in first_page.results[0].items] == ["01", "02"]
    assert [item.item_code for item in second_page.results[0].items] == ["03", "04"]
    assert second_page.results[0].next_cursor is None
