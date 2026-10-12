"""Alembic 数据库迁移运行环境。"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from data_engineer_agent.config import Settings
from data_engineer_agent.repository import _to_sqlalchemy_url


config = context.config
"""当前 Alembic 命令加载的配置。"""

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 当前服务采用 SQL-first 仓储，没有 ORM 元数据；结构变化必须显式编写迁移。
target_metadata = None


def _database_url() -> str:
    """读取并转换迁移使用的 PostgreSQL 地址。

    Returns:
        显式使用 psycopg 3 方言的 SQLAlchemy 数据库地址。
    """

    return _to_sqlalchemy_url(Settings().database_url)


def run_migrations_offline() -> None:
    """在不建立数据库连接时生成迁移 SQL。"""

    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """建立一次性连接并执行待应用迁移。"""

    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _database_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
