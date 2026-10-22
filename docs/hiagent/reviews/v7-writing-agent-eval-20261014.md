# HiAgent V7：Writing for Agents + Agent Eval 复审

2026-10-14。根据 V6 专项报告的 R1–R5 整改。范围是 V7 五份运行正文、固定测试任务、文档/SQL 检查与评测记录汇总；基线和 V1–V6 均保留。

**结论：本轮 R1–R5 的文档整改、评测准备和本地检查通过，可以进入内网 A/B 测试。实际 HiAgent 运行未执行，不作真实通过率、费用、时延或版本优越性结论。** 30 条评测记录均为 not_run。规则正确止步与业务目标完成分开记录，避免把部分结果算全量完成。

应用 [Writing for Agents](/Users/alexhuang/workspaces/github/codex-thirds/skills/mattpocock-skills/skills/productivity/writing-for-agents/SKILL.md) 及 SKILL-MECHANICS 的职责触发、步骤/完成条件、就近细则和单一权威原则；应用 [ECC Agent Eval](/Users/alexhuang/.codex/plugins/cache/ecc/ecc/2.0.0/skills/agent-eval/SKILL.md) 的固定任务、确定性判据、三次重复、通过率/耗时/成本/一致性方法。HiAgent 无运行连接，未安装编码代理 CLI、创建 worktree 或生成虚构 Agent 轨迹；由同一执行者复审，没有独立模型评分。

## R1–R5 关闭证据

| 项 | 整改与核对 | 证据 | 当前判定 |
| --- | --- | --- | --- |
| R1 | 用户明确英文、有效字段 DB 映射英文、用户选择分别确定；KB 英文推断不能自动确认。D_ID 集合明确含映射英文；英文-only 固定数据返回精确类型。 | [确认依据](/Users/alexhuang/workspaces/github/data-engineer-agent/docs/hiagent/versions/v7/agent-prompt/数据建模师.md:26) | 文档/SQL 数据通过，模型待测 |
| R2 | 结果集含轮次、项对象、来源、阶段、预期投影、业务范围；身份/成员/授权补查各自计数，修正/分页归原合同；固定字典身份计数1、成员计数301。 | [结果集定义](/Users/alexhuang/workspaces/github/data-engineer-agent/docs/hiagent/versions/v7/agent-prompt/数据建模师.md:52) | 文档/计数数据通过，实际次数待测 |
| R3 | 明确刷新/已知变化从最早失效层复核，撤销受影响确认和完整性，普通续问复用；同SQL条件在冻结前后快照返回不同含义。 | [刷新失效](/Users/alexhuang/workspaces/github/data-engineer-agent/docs/hiagent/versions/v7/agent-prompt/数据建模师.md:48) | 文档/快照数据通过，真实续问待测 |
| R4 | 五任务固定问句、DB快照、预期集合与KB条件；CSV30条未运行记录；人工按确定性判据评价，标准库汇总，成本未知不估算。 | [固定任务](/Users/alexhuang/workspaces/github/data-engineer-agent/docs/hiagent/versions/v7/README.md:44) | 评测材料与汇总通过，内网对比待测 |
| R5 | 主控集中协调规则，DB细则就近，四描述前置职责；成熟七SQL形状复用，无必读共享文件或业务例子进入运行正文。 | [协调职责](/Users/alexhuang/workspaces/github/data-engineer-agent/docs/hiagent/versions/v7/agent-prompt/数据建模师.md:5) | 文档组织通过，性能影响待测 |

## 复审过程中补齐的边界

- 英文锚点明确优先，中文非空仅核对一致；仅中文定位才要求其原名范围唯一，避免辅助中文同名引发多余确认。
- 代码映射不仅进入主控确认规则，还进入字典 DB 英文名称集合，避免工具请求只保留用户/KB 标识。
- 结果集加数据源和预期合同；错误 SQL 不能按错误投影/范围另开结果集，补查仍仅一次且占全局预算。
- 明确内联取值足够时直接按字段 DB 解释，减少无引用情况下无谓的字典调用；空名称按缺失处理，码值字符串规则保持独立。
- 业务完成度与约束通过分开；E4 全量和真实停滞变体分别记录，部分回答不能统计成全部取得。
- 汇总器不能把 not_run 看成实际失败或测得0%通过；失败/证据不足/不适用需原因，费用按币种，只报实际有记录数。
- 汇总自检使用临时合成记录，不依赖或改写用户后续实测数据；例子的“通过”只测试汇总算术，不是 Agent 的通过成绩。

## 本地检查证据

运行 `python3 -B docs/hiagent/versions/v7/check_contracts.py --results docs/hiagent/versions/v7/eval_results.csv`：

1. 原七个文档 SQL 直接执行；同名范围反例、配对、裸值反查、空白/空字符串/NULL、重复冲突与308原始行检查通过，LIMIT 100 数据不足反例成立。
2. 固定任务的仅英文映射、两近似类型、选定类型成员、身份1/成员301口径、甲010/乙020配对与刷新含义变更均匹配冻结 oracle。
3. 临时合成 CSV 检查通过数分母、三次一致性、中位耗时和未知费用；交付 CSV 仍两版本各15条 not_run，费用/时延/通过率未知。
4. 模型路由、主控状态、隐藏重试、NL2SQL实际输入/方言/限行、真实分页和最终展示未被本地检查覆盖；固定数据匹配不能证明这些行为。

字符统计（含空白，非 token）：主提示词 5489→4027，减少 26.6%；五正文合计 13716→11037，减少 19.5%。精简并不构成速度或费用改善证据。

## 下一步运行门槛

用 manifest 的五运行文件/任务/快照 SHA-256 固定部署与数据；每版本每固定任务至少三次独立运行，保存原始问题、选择/刷新、工具输入输出、SQL和回答。不能固定召回/注入故障时保存实际差异，并只在真实支持条件下运行对应 E4 变体。没有证据的能力不写已支持。

任一未核验事实、上游未确认越级、计数范围错误、无进展重查、次数越限或错误唯一/全量宣称阻断对应执行；技术失败与正常缺失分开。确定性事实/门槛用冻结预期和真实轨迹判，语言友好性另人工判；CSV脚本只汇总人工判断，不自动认证日志。复杂请求耗尽八次预算时应如实部分，不能要求为取得全量而越限。

31项扩展回归保存在 V7 README，具体业务问句继续仅在测试材料中。V6与V7同模型/配置/数据比较后再谈效果；三次重复仍不代表绝不会循环。当前没有已知文档阻断项，但本轮通过范围保持为文件规则、本地SQL/数据及评测准备。

最终交付校验：53 个基线/旧版本/已有评审文件 SHA-256 保持一致；V7 压缩包逐文件与当前目录核对。
