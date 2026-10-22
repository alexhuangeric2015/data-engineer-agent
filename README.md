# 数据资产智能对话 Demo

技术栈：Spring Boot、Spring AI Alibaba、Vue 3、MyBatis-Plus、MySQL。提供 ReAct 和 PlanAndExecute 两种模式，均通过 SSE 向浏览器流式返回内容。

## 工作链路

```text
Vue3 对话页 → Spring Boot SSE → Spring AI Alibaba Agent
                                  ├─ HiAgent 知识库定位候选
                                  ├─ MySQL 核验表字段/字典码值
                                  └─ 大模型根据数据库证据总结
```

运行时加载 [V10 单一 data-asset-query SKILL](docs/hiagent/versions/v10/skills/data-asset-query/SKILL.md)，并按查询阶段读取四份参考，不把知识库片段当作资产事实。MySQL 的 `table_schema` 与 `data_asset_code_kb` 只包含当前已确认的事实字段；会话另存于 `agent_chat_session` 和 `agent_chat_message`。MyBatis 查询均定义在 Mapper XML，无 Wrapper、动态表名或任意 SQL 执行入口。

ReAct 模式由 `ReactAgent` 自行选择检索和核验工具。PlanAndExecute 模式先由模型输出执行计划，再交给执行 Agent 使用同一套工具；两个模式使用同样的知识库先行门禁。计划和回答分别作为 `plan`、`delta` SSE 事件输出。

## 本地启动

需要 JDK 21、Maven、Node 22 和 MySQL 8。先在 MySQL 执行 [建库脚本](backend/src/main/resources/db/schema.sql)。该脚本创建 `data_engineer_agent` 库及四张表，不导入虚构的业务资产数据。真实表结构与字典数据需来自治理成果。

HiAgent 官方 Java SDK 3.1.0 尚未通过 Maven Central 获取。仓库提供固定提交的 [安装脚本](scripts/install-hiagent-sdk.sh)，先运行它，将 SDK 知识库模块装入本机 Maven 缓存。

```bash
bash scripts/install-hiagent-sdk.sh
# 设置 MYSQL_URL、MYSQL_USER、MYSQL_PASSWORD、AI_DASHSCOPE_API_KEY 等环境变量
mvn -f backend/pom.xml spring-boot:run
cd frontend && npm install && npm run dev
```

前端为 `http://127.0.0.1:5173`，后端 SSE 为 `POST http://127.0.0.1:8080/api/chat/stream`。首次提问 `sessionId` 可为空，服务返回新会话 ID。配置项清单见 [.env.example](.env.example)，配置文件仅作参考，Spring Boot 从环境变量读取，不自动加载 `.env`。

## HiAgent 知识库接入

后端使用官方 Java SDK 的 `KbsClient.query(QueryRequest)`。分别通过 `HIAGENT_TABLE_KB_ID`、`HIAGENT_DICTIONARY_KB_ID` 选择知识库，传入工作空间 ID、用户目标关键词、TopK 5 和混合检索。返回片段保留文件名、分段 ID、分数和内容；实际表/字典事实仍由 MySQL 核验。SDK 根据 `VOLC_ACCESSKEY`、`VOLC_SECRETKEY` 和 `HIAGENT_TOP_REGION` 完成请求签名，不在项目中重复实现。

目前缺少此租户的 endpoint、AK/SK、工作空间 ID 与两个知识库 dataset ID，故真实 HiAgent 检索尚待联调。没有配置时会明确报错，不会伪造命中。模型 Key 和治理数据也未提供，编译通过不代表外部调用与两模式效果已验收。

官方参考：[Spring AI Alibaba Agent Framework](https://github.com/alibaba/spring-ai-alibaba)、[HiAgent Java SDK](https://github.com/volcengine/hiagent-java-sdk)。
