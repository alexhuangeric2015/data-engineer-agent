"""建立数据字典结构基线。

Revision ID: 20261001_0001
Revises: None
Create Date: 2026-10-01
"""

from typing import Sequence

from alembic import op
from pgvector.sqlalchemy import Vector
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20261001_0001"
"""本次迁移的唯一版本号。"""

down_revision: str | None = None
"""初始基线没有前置迁移。"""

branch_labels: str | Sequence[str] | None = None
"""当前项目没有迁移分支。"""

depends_on: str | Sequence[str] | None = None
"""当前迁移不依赖外部迁移。"""


def upgrade() -> None:
    """创建 pgvector 扩展、数据字典表和查询索引。

    为兼容已经通过旧版 ``sql/init.sql`` 初始化的本地数据库，本基线会先检查
    表是否存在；已有表不重复创建，但仍由 Alembic 登记为当前版本。
    """

    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table("dictionary_type"):
        _create_dictionary_type()
    if not inspector.has_table("dictionary_item"):
        _create_dictionary_item()
    _create_indexes()


def downgrade() -> None:
    """拒绝自动删除首个生产数据结构基线。

    初始基线可能接管已有数据库，自动回退会误删原有表和业务数据，因此显式标记
    为不可逆。需要回收测试环境时应创建专用清理脚本并人工确认目标数据库。
    """

    raise RuntimeError("初始数据字典基线不可自动回退")


def _create_dictionary_type() -> None:
    """创建字典类型主表。"""

    op.create_table(
        "dictionary_type",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("type_code", sa.String(128), nullable=False),
        sa.Column("type_name", sa.String(256), nullable=False),
        sa.Column(
            "aliases",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::text[]"),
        ),
        sa.Column("source_system", sa.String(128), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="ACTIVE"),
        sa.Column("version", sa.String(64)),
        sa.Column("search_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("embedding", Vector()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="ck_dictionary_type_status",
        ),
        sa.UniqueConstraint(
            "source_system",
            "type_code",
            name="uk_dictionary_type_source_code",
        ),
    )


def _create_dictionary_item() -> None:
    """创建字典项明细表。"""

    op.create_table(
        "dictionary_item",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column(
            "dictionary_type_id",
            sa.BigInteger(),
            sa.ForeignKey("dictionary_type.id"),
            nullable=False,
        ),
        sa.Column("item_code", sa.String(128), nullable=False),
        sa.Column("item_name", sa.String(256), nullable=False),
        sa.Column(
            "aliases",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::text[]"),
        ),
        sa.Column("description", sa.Text()),
        sa.Column("status", sa.String(16), nullable=False, server_default="ACTIVE"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("effective_from", sa.DateTime(timezone=True)),
        sa.Column("effective_to", sa.DateTime(timezone=True)),
        sa.Column("search_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("embedding", Vector()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="ck_dictionary_item_status",
        ),
        sa.UniqueConstraint(
            "dictionary_type_id",
            "item_code",
            name="uk_dictionary_item_type_code",
        ),
    )


def _create_indexes() -> None:
    """幂等创建当前精确查询和键集分页使用的索引。"""

    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_dictionary_type_name "
        "ON dictionary_type (LOWER(type_name))"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_dictionary_item_type_name "
        "ON dictionary_item (dictionary_type_id, LOWER(item_name))"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_dictionary_item_type_sort "
        "ON dictionary_item (dictionary_type_id, sort_order, id)"
    )
