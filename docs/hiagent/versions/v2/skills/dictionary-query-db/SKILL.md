---
name: dictionary-query-db
description: 必须实际调用 HiAgent 内置数据库能力（NL2SQL），查询数据库表 data_asset_code_kb，核验字典类型、查询全部码值或单码值，并支持无类型时的候选查询。所有字典事实与候选含义都需数据库证据，保留前导零，确认类型和关联后再给码值结论。
---

# 字典与码值数据库核验

## 职责与边界

通过 HiAgent 实际绑定的内置数据库能力（NL2SQL）只读查询数据库表 `data_asset_code_kb`。输入为精确字典代码/名称、有限候选代码，或用户原样提供的码值/描述；输出为实际存在的类型、码值、含义及完整性状态。不以同名知识库检索代替 SQL 执行，不自行把近似类型认作目标，不证明字段与字典的关联；关联依据由主流程的结构 DB 证据或用户确认提供。

必须收到数据库工具的实际执行结果才输出已核验事实，加载 SKILL 或生成 SQL 不够。来源写“数据库表 `data_asset_code_kb`”，与同名知识库明确区分。

## 已知字段契约

| 数据库字段 | 业务含义与边界 |
| --- | --- |
| `code_table_en_name` | 字典类型英文名/字典代码；不根据字段名自行生成 |
| `code_table_cn_name` | 字典中文名；不自动充当独立字典注释 |
| `code_value` | 字符串码值，原样保留前导零、大小写和空白 |
| `code_desc` | 码值含义；缺失显示“未提供”，冲突含义均保留 |

当前契约没有独立字典注释或字段→字典绑定字段，不能编造这些字段或其内容。数据库仅有码值行时，类型无对应行只能报告“当前库未匹配到该类型的码值记录”，不能区分不存在的类型与已建但暂无码值的类型。

## 查询模式

以下 SQL 是逻辑模板；`:参数` 仅示意参数，不假定 HiAgent 支持该接口。遵循实际 NL2SQL 契约：优先参数绑定；若工具仅接受自然语言，明确只读目标、允许字段和原始查询值，由工具按真实方言执行，不自行拼接用户文本。候选代码最多 5 个，`IN` 的参数数目按实际候选生成。

### 批量核验候选类型

```sql
SELECT DISTINCT code_table_en_name, code_table_cn_name
FROM data_asset_code_kb
WHERE code_table_en_name IN (:candidate_1, :candidate_2, :candidate_3)
ORDER BY code_table_en_name, code_table_cn_name;
```

有近似名称或多个类型时提交主流程确认，不在此阶段查询整个类型的码值。

### 按用户明确给出的类型中文名精确核验

```sql
SELECT DISTINCT code_table_en_name, code_table_cn_name
FROM data_asset_code_kb
WHERE code_table_cn_name = :code_table_cn_name
ORDER BY code_table_en_name, code_table_cn_name;
```

例如原词为“身份类型”，不能私自替换为“角色类型”。若只命中 KB 推荐的近似类型，需主流程向用户确认；数据库存在该候选不等于已确认语义等价。

### 查询已确定类型的全部码值

```sql
SELECT code_table_en_name, code_table_cn_name, code_value, code_desc
FROM data_asset_code_kb
WHERE code_table_en_name = :code_table_en_name
ORDER BY code_value, code_desc;
```

一次同时读取类型名和码值，避免为展示名称再查询。字段相关问题必须已有 DB 关联证据或用户确认，直接字典问题可按用户明确代码查询。

### 查询已确定类型的一个码值

```sql
SELECT code_table_en_name, code_table_cn_name, code_value, code_desc
FROM data_asset_code_kb
WHERE code_table_en_name = :code_table_en_name
  AND code_value = :code_value
ORDER BY code_value, code_desc;
```

优先数据库过滤，不为一个值默认读取全部字典。若返回零行，用预算内的一次类型核验区分“本次类型记录未匹配”与“类型存在但这个值未匹配”。如需候选，可在已确定类型内获取其码值，用实际数据找相似值；没有相似项时展示该类型全部已获取码值供判断，不把候选当成原值答案。

### 只有码值、未给类型时查询候选对照

```sql
SELECT DISTINCT code_table_en_name, code_table_cn_name, code_value, code_desc
FROM data_asset_code_kb
WHERE code_value = :code_value
ORDER BY code_table_en_name, code_value, code_desc;
```

结果只供用户确认字典类型；即使只返回一个类型，用户没有类型/字段/业务范围时也不宣称该含义在全业务中唯一。返回可能被截断时，不声称列出了所有类型。

### 按描述查询候选或在已确认类型内反查

```sql
SELECT DISTINCT code_table_en_name, code_table_cn_name, code_value, code_desc
FROM data_asset_code_kb
WHERE code_desc LIKE :code_desc_pattern ESCAPE '!'
ORDER BY code_table_en_name, code_value, code_desc;
```

这是含义反查，不是精确码值命中。`:code_desc_pattern` 是对用户描述按实际 SQL 方言转义后构成的包含匹配值；模板用 `!` 转义 `%`、`_` 和 `!`，不能把用户的通配符当成扩大查询范围的指令。用户已确定类型时增加 `code_table_en_name = :code_table_en_name` 条件；无类型时提交候选让用户确认，不直接选定一个字典。不会按平台不支持的语法反复试错。

### 缺少完整性信息时核对行数

```sql
SELECT COUNT(*) AS total_rows
FROM data_asset_code_kb
WHERE code_table_en_name = :code_table_en_name;
```

仅为需要全量且缺少明确完整性信息的结果增加一次计数；计入 DB 预算。单值/描述过滤结果需核对时，计数使用与取数相同的过滤条件。去重前原始行数与 `total_rows` 一致且无截断时才确认完整；跨快照数量不一致不反复查询，标记不完整。

## 结果处理与停止条件

1. 先核验类型再给码值结论。有多个类型、中文名不一致、只有近似匹配或类型名冲突时，交还主流程确认；不存在的 KB 候选不能混进用户候选表。
2. 相似类型只是待确认候选。没有相似类型时，只有用户已明确有限业务范围且当前字段支持过滤，才查该范围全部类型；否则请补充代码/名称/范围，不为字段强行选全库类型。
3. 码值和描述按原值输出；完全相同的重复行可展示时去重并说明数量，同类型同码值的不同描述保留为冲突。不根据数字格式重建丢失的前导零，不通过常识补含义。
4. 用户问全部就全部展示，包括 300 多条；不设置“超过 30 条先问是否列全”，不以若干向量片段替代全量。问一个值则只展示匹配行，无码值命中则明确区分候选。
5. 检查实际工具总数、分页和截断信息；无完整性依据则报告未知。已获取行数、去重后的码值数和已展示行数分别计算，不把一次返回行数当数据库总量。
6. 优先一次完整取数；实际工具支持分页时每个列表本回合最多 3 页且计入主流程每回合 DB 最多 6 次预算。页码/游标不前进、达到预算或输出不足即报告已完成范围，不能宣称“已全部列出”。
7. 工具缺失、无权限、超时和网络异常立即停止，不转 KB 补答案。明确可修正的参数/语法错误最多修正一次；成功零行不重试同一查询，不反复换关键词。

提交给主流程：状态（已核验 / 候选类型待确认 / 本次未匹配 / 元数据冲突 / 结果不完整 / 工具不可用 / 查询失败）、精确类型/过滤范围、实际 DB 行、来源、完整性依据及原样码值。使用主提示词的数据字典、码值或候选表模板；不展示推理过程，不提前宣称字段已绑定该字典。
