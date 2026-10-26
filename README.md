# 数据资产智能对话 Demo

技术栈：Spring Boot、Spring AI Alibaba、Vue 3、MyBatis-Plus、MySQL。提供 ReAct 和 PlanAndExecute 两种模式，均通过 SSE 向浏览器流式返回内容。

## 工作链路

```text
Vue3 对话页 → Spring Boot SSE → Spring AI Alibaba Agent
                                  ├─ HiAgent 知识库定位候选
                                  ├─ MySQL 核验表字段/字典码值
                                  └─ 大模型根据数据库证据总结
```

运行时加载 [V10 单一 data-asset-query SKILL](docs/hiagent/skills/versions/v10/skills/data-asset-query/SKILL.md)，并按查询阶段读取四份参考，不把知识库片段当作资产事实。MySQL 的 `table_schema` 与 `data_asset_code_kb` 只包含当前已确认的事实字段；会话另存于 `agent_chat_session` 和 `agent_chat_message`。MyBatis 查询均定义在 Mapper XML，无 Wrapper、动态表名或任意 SQL 执行入口。

两种模式有独立的代码路径，入口 [ChatService](backend/src/main/java/com/dataengineer/agent/chat/ChatService.java) 按 `ChatMode` 分派：

| 模式 | 执行代码 | 流程 |
| --- | --- | --- |
| ReAct | [ReactModeExecutor](backend/src/main/java/com/dataengineer/agent/chat/ReactModeExecutor.java) | Spring AI Alibaba `ReactAgent` 在模型与工具之间循环，自行选择下一步；工具层强制阶段参考、知识库命中和数据库核验门禁。 |
| PlanAndExecute | [PlanAndExecuteExecutor](backend/src/main/java/com/dataengineer/agent/chat/PlanAndExecuteExecutor.java) | 模型输出受限 JSON 计划；Java 校验步骤、按顺序执行“读 SKILL 参考→HiAgent 检索→候选提取→MySQL 核验”，最后模型根据数据库证据流式总结。此模式不调用 `ReactAgent`。 |

计划模式是一次有界的“规划→执行→总结”，目前没有自动重规划。计划和阶段进度分别以 `plan`、`stage` SSE 事件推送，回答以 `delta` 流式推送。两种模式共享同一个 [AssetTools](backend/src/main/java/com/dataengineer/agent/chat/AssetTools.java) 门禁。模型的规划和候选提取为非流式调用，因此首个计划事件会在规划完成后出现；答案文本是流式的。

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
