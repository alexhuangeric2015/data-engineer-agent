# Data Engineer Agent：数据字典查询 MVP

## 价值主张

面向数据开发工程师，通过自然语言查询企业权威数据字典，减少人工检索字典类型、码值和含义的时间，并避免模型凭记忆生成错误码值。

## 首版目标

通过一个只读 MCP Tool `query_data_dictionary` 完成：

1. 批量查询多个字典类型下的有效字典项；
2. 在指定字典类型中批量执行码值到名称的查询；
3. 在指定字典类型中批量执行名称到码值的查询；
4. 未指定字典类型时，批量按字典项名称全局反查；
5. 为后续别名和向量候选检索保留数据结构与参数边界。

## 用户交互

- 用户在 HiAgent 中向数据开发工程师助手提问；
- HiAgent 调用一个业务级 MCP Tool；
- MCP 根据参数组合自动识别列举、码值查询或名称反查；
- 唯一命中直接返回，多条命中返回候选项；
- 无结果或存在歧义时不得猜测。

本轮实现并测试 FastAPI REST 与 MCP 两种接口，不实施 HiAgent 配置和端到端联调。

REST 与 MCP 使用同一份请求、响应模型和业务服务。REST 地址为
`POST /api/v1/data-dictionaries/query`；MCP Tool 名称仍为
`query_data_dictionary`。

## MCP Tool 契约

### `query_data_dictionary`

输入：

```json
{
  "requests": [
    {
      "dictionary_type": "证件类型",
      "item_codes": ["01", "02"],
      "item_names": ["军官证", "护照"],
      "keywords": [],
      "cursor": null
    },
    {
      "dictionary_type": "性别",
      "item_codes": [],
      "item_names": [],
      "keywords": [],
      "cursor": null
    },
    {
      "dictionary_type": null,
      "item_codes": [],
      "item_names": ["驾驶证"],
      "keywords": [],
      "cursor": null
    }
  ],
  "include_inactive": false,
  "page_size": 100
}
```

参数规则：

- `requests` 数量范围为 1～20；
- 所有 `item_codes`、`item_names` 和 `keywords` 合计不超过 100 个；
- `page_size` 范围为 1～200；
- 仅提供 `dictionary_type` 时列出该类型下的字典项；
- `dictionary_type + item_codes` 用于批量查询码值；
- `dictionary_type + item_names` 用于在指定类型内批量反查码值；
- 未提供 `dictionary_type` 时只允许使用 `item_names` 或 `keywords`；
- 字典码值始终使用字符串，保留前导零；
- `keywords` 为向量候选检索预留，本轮调用时返回明确的未启用状态。

返回：

```json
{
  "results": [
    {
      "request_index": 0,
      "dictionary_type_status": "FOUND",
      "matched_type": {
        "type_code": "IDENTITY_DOCUMENT_TYPE",
        "type_name": "证件类型",
        "source_system": "本地测试数据"
      },
      "lookups": [
        {
          "input_type": "ITEM_CODE",
          "input_value": "01",
          "status": "FOUND",
          "matches": [
            {
              "item_code": "01",
              "item_name": "身份证",
              "status": "ACTIVE",
              "match_method": "EXACT_CODE"
            }
          ]
        }
      ],
      "items": [],
      "candidates": [],
      "next_cursor": null,
      "error": null
    }
  ],
  "summary": {
    "request_count": 1,
    "lookup_count": 1,
    "succeeded": 1,
    "not_found": 0,
    "ambiguous": 0,
    "invalid": 0
  }
}
```

结果规则：

- 外层结果顺序与 `requests` 一致；
- `lookups` 顺序为当前请求的 `item_codes`、`item_names`、`keywords` 顺序；
- 单项状态为 `FOUND`、`NOT_FOUND`、`AMBIGUOUS`、`INVALID` 或 `NOT_ENABLED`；
- 批量中的单项失败不影响其他结果；
- 只有精确命中才能返回事实码值；向量结果只作为 `candidates`。

## PostgreSQL

- 运行方式：复用本机 `5432` 端口上的 Docker PostgreSQL；
- 当前本地镜像：`pgvector/pgvector:0.8.6-pg14-trixie`；
- 数据库名称：`data-engineer`；
- 数据库编码：`UTF8`；
- 开发用户：`root`；
- 密码通过环境变量注入，不提交到仓库；
- 启用 `vector` 扩展；
- 建立字典类型、字典项及别名数据结构；
- 预留字典类型和字典项向量字段；
- 初始化“证件类型”“性别”“订单状态”等测试数据。

## 技术范围

- Python 3.11+；
- FastAPI、OpenAPI 与 Uvicorn；
- 官方 MCP Python SDK；
- Pydantic 输入输出校验；
- SQLAlchemy 2 连接池与参数绑定，驱动为 psycopg 3；
- 独立 `.sql` 查询文件，不在 Python 中硬编码查询正文；
- Alembic 数据库结构迁移；
- Streamable HTTP 传输；
- 中文业务日志；
- pytest 单元测试；
- MCP Tool 接口测试。

## 首版交付物

```text
data-engineer-agent/
├── SPEC.md
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── alembic.ini
├── migrations/
│   └── versions/
├── docker-compose.yml
├── sql/
│   └── seed.sql
├── src/data_engineer_agent/
│   ├── config.py
│   ├── cursor.py
│   ├── api/
│   │   ├── app.py
│   │   ├── dependencies.py
│   │   └── routes.py
│   ├── models/
│   │   ├── enums.py
│   │   ├── records.py
│   │   ├── requests.py
│   │   └── responses.py
│   ├── queries/
│   │   ├── find_dictionary_types.sql
│   │   ├── list_dictionary_items.sql
│   │   └── find_dictionary_items.sql
│   ├── repository.py
│   ├── result_builder.py
│   ├── service.py
│   └── server.py
└── tests/
    ├── conftest.py
    ├── unit/
    │   ├── test_models.py
    │   └── test_service.py
    └── integration/
        └── test_mcp_tools.py
```

具体文件以最小可运行实现为准，不为空壳能力预建模块。

## 非目标

- 不开发数据字典管理后台；
- 不提供新增、修改、删除字典的 MCP Tool；
- 不引入 AgentScope；
- 不将字典项复制到 HiAgent 术语库或知识库；
- 本轮不实现向量生成和向量检索；
- 本轮不接入或测试 HiAgent；
- 不实现缓存、复杂工作流、多智能体或前端界面。

## 测试数据

测试数据由 `sql/seed.sql` 初始化，至少覆盖：

- 证件类型：身份证、军官证、护照、驾驶证及一个停用项；
- 性别：男、女、未知；
- 订单状态：待支付、已支付、已取消；
- 同名字典项：用于验证无类型名称反查时的歧义处理；
- 前导零码值：用于验证码值始终按字符串处理。

## 验收标准

1. 一个 MCP 调用可以查询多个字典类型；
2. 一个类型可以同时查询多个码值和多个名称；
3. 只提供类型时返回该类型下的有效字典项；
4. 全局名称反查唯一命中时返回码值和所属类型；
5. 全局名称反查多条命中时返回 `AMBIGUOUS`；
6. 不存在的数据返回 `NOT_FOUND`，不生成猜测结果；
7. 停用项默认不返回，显式允许时可以返回；
8. `01` 等码值保留前导零；
9. 批量结果保持输入顺序，并允许部分成功；
10. `keywords` 在本轮返回 `NOT_ENABLED`；
11. 自动化测试覆盖正常、无结果、歧义、停用项、非法参数和分页场景；
12. 服务日志可定位工具调用、查询条件、结果数量和异常原因。

## 产品环境

- 运行入口：HiAgent；
- 首版权威数据源：Docker 中的 PostgreSQL；
- 身份认证：首版仅用于本地开发验证，生产认证不在本次范围；
- 凭据管理：环境变量；
- 技术设计详情：`docs/data-dictionary-query-technical-design.md`。
