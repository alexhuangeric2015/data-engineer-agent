"""PostgreSQL 数据字典只读仓储。"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.sql.elements import TextClause

from data_engineer_agent.models import DictionaryItemRecord, DictionaryTypeRecord
from data_engineer_agent.queries import (
    FIND_DICTIONARY_ITEMS,
    FIND_DICTIONARY_TYPES,
    LIST_DICTIONARY_ITEMS,
)


LOGGER = logging.getLogger(__name__)

POOL_SIZE = 5
"""单实例常驻连接池容量；后续按压测结果调整。"""

MAX_OVERFLOW = 5
"""连接池耗尽时允许临时增加的连接数；用于吸收短时请求峰值。"""

POOL_RECYCLE_SECONDS = 1800
"""连接回收周期，避免基础设施主动断开长期空闲连接。"""

PSYCOPG_DIALECT = "postgresql+psycopg://"
"""SQLAlchemy 使用 psycopg 3 驱动时的地址前缀。"""


def _to_sqlalchemy_url(database_url: str) -> str:
    """把普通 PostgreSQL 地址转换为 psycopg 3 方言地址。

    Args:
        database_url: 环境配置中的 PostgreSQL 连接地址。

    Returns:
        可交给 SQLAlchemy ``create_engine`` 的连接地址。
    """

    if database_url.startswith("postgresql+"):
        return database_url
    for prefix in ("postgresql://", "postgres://"):
        if database_url.startswith(prefix):
            return PSYCOPG_DIALECT + database_url[len(prefix) :]
    return database_url


class DictionaryRepository:
    """执行外置 SQL 并把只读结果映射为仓储记录。

    仓储不判断 ``FOUND``、``AMBIGUOUS`` 等业务状态，也不负责 HTTP 或 MCP
    协议转换；这些职责分别属于应用服务和接口适配层。
    """

    def __init__(self, database_url: str) -> None:
        """创建连接池并立即验证数据库可连接。

        Args:
            database_url: 已初始化数据字典表的 PostgreSQL 连接地址。

        Raises:
            sqlalchemy.exc.SQLAlchemyError: 地址无效或数据库不可连接时抛出。
        """

        self._engine = self._create_engine(database_url)
        self._verify_connection()
        LOGGER.info(
            "[数据字典][连接池创建] poolSize=%s, maxOverflow=%s",
            POOL_SIZE,
            MAX_OVERFLOW,
        )

    def close(self) -> None:
        """关闭连接池并释放所有 PostgreSQL 连接。"""

        self._engine.dispose()
        LOGGER.info("[数据字典][连接池关闭]")

    def find_dictionary_types(
        self,
        dictionary_type: str,
        source_system: str | None,
        include_inactive: bool,
    ) -> list[DictionaryTypeRecord]:
        """按编码、名称或别名精确查询字典类型。

        Args:
            dictionary_type: 字典类型编码、名称或别名，不允许为空。
            source_system: 权威来源系统；为空时不限制来源。
            include_inactive: 是否包含停用类型。

        Returns:
            按来源系统和类型编码排序的记录；多条表示类型有歧义。
        """

        rows = self._execute(
            FIND_DICTIONARY_TYPES,
            {
                "dictionary_type": dictionary_type,
                "source_system": source_system,
                "include_inactive": include_inactive,
            },
        )
        LOGGER.info(
            "[数据字典][类型查询] dictionaryType=%s, sourceSystem=%s, resultCount=%s",
            dictionary_type,
            source_system,
            len(rows),
        )
        return [DictionaryTypeRecord.model_validate(row) for row in rows]

    def list_dictionary_items(
        self,
        dictionary_type_id: int,
        include_inactive: bool,
        after_sort_order: int | None,
        after_id: int | None,
        limit: int,
    ) -> list[DictionaryItemRecord]:
        """按稳定键集游标列举一个字典类型下的字典项。

        Args:
            dictionary_type_id: 唯一字典类型的数据库主键。
            include_inactive: 是否包含停用或已失效字典项。
            after_sort_order: 上一页最后一项的排序值；首页为空。
            after_id: 上一页最后一项的主键；首页为空。
            limit: 本次数据库查询最多返回的记录数。

        Returns:
            按 ``sort_order``、``id`` 升序排列的字典项记录。
        """

        rows = self._execute(
            LIST_DICTIONARY_ITEMS,
            {
                "dictionary_type_id": dictionary_type_id,
                "include_inactive": include_inactive,
                "after_sort_order": after_sort_order,
                "after_id": after_id,
                "limit": limit,
            },
        )
        LOGGER.info(
            "[数据字典][字典项列举] dictionaryTypeId=%s, resultCount=%s",
            dictionary_type_id,
            len(rows),
        )
        return [DictionaryItemRecord.model_validate(row) for row in rows]

    def find_dictionary_items(
        self,
        dictionary_type_id: int | None,
        item_codes: list[str],
        item_names: list[str],
        include_inactive: bool,
    ) -> list[DictionaryItemRecord]:
        """批量精确查询码值、名称和名称别名。

        Args:
            dictionary_type_id: 限定类型主键；为空时执行全局名称反查。
            item_codes: 待查询的字符串码值；全局反查时必须为空。
            item_names: 待查询的字典项名称或别名。
            include_inactive: 是否包含停用或已失效字典数据。

        Returns:
            所有命中的字典项；没有查询条件时直接返回空列表。
        """

        if not item_codes and not item_names:
            return []
        normalized_names = [name.casefold() for name in item_names]
        rows = self._execute(
            FIND_DICTIONARY_ITEMS,
            {
                "dictionary_type_id": dictionary_type_id,
                "item_codes": item_codes,
                "normalized_names": normalized_names,
                "include_inactive": include_inactive,
            },
        )
        LOGGER.info(
            "[数据字典][字典项查询] dictionaryTypeId=%s, codeCount=%s, "
            "nameCount=%s, resultCount=%s",
            dictionary_type_id,
            len(item_codes),
            len(item_names),
            len(rows),
        )
        return [DictionaryItemRecord.model_validate(row) for row in rows]

    @staticmethod
    def _create_engine(database_url: str) -> Engine:
        """创建带连接健康检查和上限约束的 SQLAlchemy 引擎。

        Args:
            database_url: 原始数据库连接地址。

        Returns:
            尚未检出连接的 SQLAlchemy 同步引擎。
        """

        return create_engine(
            _to_sqlalchemy_url(database_url),
            pool_size=POOL_SIZE,
            max_overflow=MAX_OVERFLOW,
            pool_pre_ping=True,
            pool_recycle=POOL_RECYCLE_SECONDS,
        )

    def _verify_connection(self) -> None:
        """检出一条连接，使数据库不可用时在启动阶段直接失败。"""

        with self._engine.connect() as connection:
            connection.execute(select(1))

    def _execute(
        self,
        statement: TextClause,
        parameters: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """执行一条参数化只读语句并返回列名映射。

        Args:
            statement: 启动时从固定 SQL 资源加载的查询语句。
            parameters: 只通过 SQLAlchemy 绑定、不参与字符串拼接的参数。

        Returns:
            以数据库列名为键的全部查询结果。
        """

        with self._engine.connect() as connection:
            result = connection.execute(statement, parameters)
            return [dict(row) for row in result.mappings()]
