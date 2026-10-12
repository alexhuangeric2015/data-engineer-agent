"""加载数据字典只读 SQL，并声明数据库参数类型。

SQL 正文保存在同目录的 ``.sql`` 文件中，便于数据库工程师独立评审和执行计划
分析。本模块不实现动态 SQL 语言，只做包资源读取和 SQLAlchemy 安全参数绑定。
"""

from importlib.resources import files

from sqlalchemy import BigInteger, Boolean, Integer, String, Text, bindparam, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql.elements import TextClause


QUERY_PACKAGE = "data_engineer_agent.queries"
"""打包后查询文件所在的 Python 资源包。"""


def _load_query(file_name: str) -> str:
    """读取一个随应用发布的 UTF-8 SQL 文件。

    Args:
        file_name: 当前包内固定的 SQL 文件名，不接受外部请求参数。

    Returns:
        SQL 文件的完整文本。
    """

    return files(QUERY_PACKAGE).joinpath(file_name).read_text(encoding="utf-8")


FIND_DICTIONARY_TYPES: TextClause = text(
    _load_query("find_dictionary_types.sql")
).bindparams(
    bindparam("dictionary_type", type_=String()),
    bindparam("source_system", type_=String()),
    bindparam("include_inactive", type_=Boolean()),
)
"""按编码、名称或别名精确查询字典类型。"""

LIST_DICTIONARY_ITEMS: TextClause = text(
    _load_query("list_dictionary_items.sql")
).bindparams(
    bindparam("dictionary_type_id", type_=BigInteger()),
    bindparam("include_inactive", type_=Boolean()),
    bindparam("after_sort_order", type_=Integer()),
    bindparam("after_id", type_=BigInteger()),
    bindparam("limit", type_=Integer()),
)
"""使用排序值和主键组成的键集游标列举字典项。"""

FIND_DICTIONARY_ITEMS: TextClause = text(
    _load_query("find_dictionary_items.sql")
).bindparams(
    bindparam("dictionary_type_id", type_=BigInteger()),
    bindparam("item_codes", type_=ARRAY(Text())),
    bindparam("normalized_names", type_=ARRAY(Text())),
    bindparam("include_inactive", type_=Boolean()),
)
"""在指定类型或全局范围批量精确查找字典项。"""


__all__ = [
    "FIND_DICTIONARY_ITEMS",
    "FIND_DICTIONARY_TYPES",
    "LIST_DICTIONARY_ITEMS",
]
