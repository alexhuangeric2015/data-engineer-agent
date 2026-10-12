"""外置 SQL 查询与数据库连接地址测试。"""

from __future__ import annotations

import pytest

from data_engineer_agent.queries import (
    FIND_DICTIONARY_ITEMS,
    FIND_DICTIONARY_TYPES,
    LIST_DICTIONARY_ITEMS,
)
from data_engineer_agent.repository import _to_sqlalchemy_url


@pytest.mark.unit
def test_type_query_supports_code_name_alias_and_source() -> None:
    """类型查询应支持编码、名称、别名、来源和启停状态过滤。"""

    sql = str(FIND_DICTIONARY_TYPES).lower()

    assert "lower(type_code)" in sql
    assert "lower(type_name)" in sql
    assert "unnest(aliases)" in sql
    assert ":source_system" in sql
    assert ":include_inactive" in sql


@pytest.mark.unit
def test_list_query_uses_keyset_pagination_and_effective_time() -> None:
    """字典项列举应使用键集分页并过滤无效时间区间。"""

    sql = str(LIST_DICTIONARY_ITEMS).lower()

    assert "(item.sort_order, item.id)" in sql
    assert ":after_sort_order" in sql
    assert ":after_id" in sql
    assert "current_timestamp" in sql
    assert "limit :limit" in sql


@pytest.mark.unit
def test_item_query_uses_bound_array_parameters() -> None:
    """批量码值和名称查询应使用数组绑定，不拼接外部输入。"""

    sql = str(FIND_DICTIONARY_ITEMS).lower()

    assert "item.item_code = any" in sql
    assert "lower(item.item_name) = any" in sql
    assert "unnest(item.aliases)" in sql
    assert ":item_codes" in sql
    assert ":normalized_names" in sql


@pytest.mark.unit
@pytest.mark.parametrize(
    ("raw_url", "expected"),
    [
        (
            "postgresql://user:secret@127.0.0.1:5432/data-engineer",
            "postgresql+psycopg://user:secret@127.0.0.1:5432/data-engineer",
        ),
        (
            "postgres://user:secret@127.0.0.1:5432/data-engineer",
            "postgresql+psycopg://user:secret@127.0.0.1:5432/data-engineer",
        ),
        (
            "postgresql+psycopg://user:secret@127.0.0.1:5432/data-engineer",
            "postgresql+psycopg://user:secret@127.0.0.1:5432/data-engineer",
        ),
        ("dbname=data-engineer", "dbname=data-engineer"),
    ],
)
def test_database_url_uses_psycopg_dialect(raw_url: str, expected: str) -> None:
    """普通 PostgreSQL URL 应显式选择 psycopg 3 方言。"""

    assert _to_sqlalchemy_url(raw_url) == expected
