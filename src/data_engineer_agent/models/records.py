"""仓储层返回的 PostgreSQL 记录模型。"""

from pydantic import BaseModel, Field


class DictionaryTypeRecord(BaseModel):
    """仓储层返回的字典类型记录。"""

    id: int = Field(description="字典类型数据库主键。")
    type_code: str = Field(description="字典类型唯一编码。")
    type_name: str = Field(description="字典类型展示名称。")
    aliases: list[str] = Field(description="字典类型可用于精确匹配的别名。")
    source_system: str = Field(description="字典数据的权威来源系统。")
    status: str = Field(description="字典类型当前状态。")


class DictionaryItemRecord(BaseModel):
    """仓储层返回的字典项及所属类型记录。"""

    id: int = Field(description="字典项数据库主键。")
    dictionary_type_id: int = Field(description="所属字典类型数据库主键。")
    type_code: str = Field(description="所属字典类型编码。")
    type_name: str = Field(description="所属字典类型名称。")
    source_system: str = Field(description="字典数据的权威来源系统。")
    item_code: str = Field(description="字典码值。")
    item_name: str = Field(description="字典项名称。")
    aliases: list[str] = Field(description="字典项别名。")
    description: str | None = Field(description="字典项业务说明；无说明时为空。")
    status: str = Field(description="字典项当前状态。")
    sort_order: int = Field(description="字典项展示顺序。")
