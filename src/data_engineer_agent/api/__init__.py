"""FastAPI 接口层。

本包只负责 HTTP 协议、边界校验和依赖获取；数据字典规则仍由应用服务负责，
数据库访问仍由仓储负责，避免 Controller 直接操作数据库。
"""

from data_engineer_agent.api.app import create_app

__all__ = ["create_app"]
