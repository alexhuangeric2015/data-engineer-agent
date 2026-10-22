---
name: dictionary-query-db
description: 实际执行 HiAgent 内置数据库查询，只读核验 data_asset_code_kb。直接回答字典与码值问题；字段问题先检查表字段已确认，再按 related_column_en/cn 映射核验类型。枚举问题必须继续取码值，相似版本由用户选，核对实际 SQL 的 LIMIT 100 与全量状态。
---

# 字典与码值数据库查询（V4）

## 输入、输出与边界

输入：带问题编号的字典名称、待核验代码、原样码值/描述、确定的类型范围、要查全量还是指定项，以及已有 DB 证据。将同阶段目标去重合并，只读调用 HiAgent 实际绑定的内置数据库能力（NL2SQL）。必须收到实际执行结果，加载本 SKILL 或生成 SQL 都不能代替查询。

输出：每项状态、真实类型/码值行、缺失目标、来源与完整性。由主流程确认歧义、解释字段引用并组织答案。本 SKILL 不决定近似名称相同、不证明字段绑定、不查业务数据。

## 调用前的门槛与完成条件

- 直接问题“交易类型有哪些类型？”属于字典码值枚举，不要求表/字段、不转结构 SKILL。目标输出是码值时，类型定位成功仅是中间结果，必须继续取值；不能以“字典定位完成”结束。
- 字段问题先检查当前表和字段已经由 DB 确认。上游未确认、未找到、失败或已结束时，**不执行任何字典查询**，返回阻断原因；KB 提到 FIN_PROD_CD、代码本身存在都不能越过门槛。
- 当前字段的 `related_column_en` 对应 `code_table_en_name`，`related_column_cn` 对应 `code_table_cn_name`。优先非空英文代码；中文用于核对或在仅中文时定位。英文命中却中文非空不一致时报告映射冲突，不能改用别的类型。若字典中文名缺失，说明该项未能核对，不编造名称。
- 当前字段映射明确给出精确英文代码时，可一次取值同时核验类型名称；发现代码名称冲突则不输出确定含义。只有中文名称时必须先判断唯一性；只有 KB 线索/名称近似时先确认，不加载候选整类码值。
- 两个 related 名称都缺失时，可采用当前字段业务描述中的明确声明；单纯字段同名/后缀不构成映射。用户选择用于查值要标“引用未核实”，不能反过来证明实际绑定。
- 类型定位最多 3 次实际执行，包含字典 KB、DB、计数和修正。单次精确查零行记“本次未匹配”，主流程可继续尚未用过的固定 KB 步骤；KB 空或候选 DB 核验空才是“定位结束未找到”。候选需选择、错误或额度用尽也立即交还，不转查表、不重新启动已结束的类型定位。
- “行业代码”与“行业代码（2017版）”没有精确匹配时是待选项，保留完整名称；不默认某个版本更适用。确认后继续原始的层级/码值问题。没有级别/父级字段时，只有实际 DB 描述明确说明的层级可展示，不凭码长或前缀分级。

来源为“数据库表 `data_asset_code_kb`”，不能与同名知识库混用。仅知道四个字段：

| 字段 | 含义与边界 |
| --- | --- |
| `code_table_en_name` | 字典类型英文名/代码；保留原值，不按字段名生成 |
| `code_table_cn_name` | 字典中文名；不是独立字典注释 |
| `code_value` | 字符串码值；保留前导零、大小写、空白，不转数字比较 |
| `code_desc` | 码值含义原文；不是字典整体描述，缺失则未提供 |

无独立字典注释、类型主表或字段绑定列。某类型无任何行时，只能说“当前字典表未匹配该类型的码值记录”，不能区分空类型与不存在的类型。不能根据此表判断实际业务中用了哪些值、值频率或字段引用。

## 合并与选择

- 已给英文类型代码：直接按需求取全量或指定值，一次返回类型名称；有结果不用先后重复验证类型。中文全名先批量定位类型，唯一精确匹配且候选完整时再继续；多个代码、相似版本或名称冲突交还确认。
- 多个确定类型的全集用 `IN`；指定值按类型成组。`(类型 A AND 值 x/y) OR (类型 B AND 值 z)` 保留配对关系，禁止两个独立 `IN` 产生额外组合。某类型已查全集时，从已有结果回答其单值，不再查。
- 无类型的多个码值反查可以 `code_value IN (...)`，每行必须带字典代码。用户问出现位置时是集合结果；用户问其业务含义而缺少范围时是适用类型候选，不自行选一个。
- 描述反查有类型就限定类型；无类型才跨类型。按字典的“描述”找类型时，码值描述命中只作为候选依据，不宣称它是字典定义。
- 每个请求项分别记录匹配状态。某类型/值缺失而其他项成功，不能遗漏；将缺失项涉及的类型合并做一次存在性核验，避免逐值查询。

## SQL 逻辑模板

`:参数` 只是表达条件，不代表工具有此接口。遵循实际 NL2SQL 契约：优先参数绑定；若只支持自然语言则明确目标表、字段、原始字符串、成组过滤和只读要求，由工具按实际方言执行，不直接拼接用户文本。

参数个数按实际列表生成，空组删除，不传虚构参数值。`LIKE` 包含匹配先转义原文中的 `!`、`%`、`_`，再加外围 `%`；`ESCAPE '!'` 按真实方言适配，不猜接口，不盲目试错。

### D1：按英文代码 / 中文全名批量核验类型

<!-- query: D1 -->
```sql
SELECT DISTINCT code_table_en_name, code_table_cn_name
FROM data_asset_code_kb
WHERE code_table_en_name IN (:dict_en_1, :dict_en_2)
   OR code_table_cn_name IN (:dict_cn_1, :dict_cn_2)
ORDER BY code_table_en_name, code_table_cn_name;
```

用途包括精确名称定位、KB 候选核验、指定值未命中后的类型核验。近似候选存在不代表用户要的类型；尚未确认时不加载整类码值。代码缺失但中文名真实已知，也可去掉英文条件后查询。

“有哪些类型/状态/取值/码值”在 D1 确认目标后必须继续 D2；只有“是哪个字典/引用哪个类型”才允许以已核验身份作为完成结果。用户选择候选后沿用原目标，不让用户重新要求列码值。

用户明确要求“列出当前全部字典类型”时，去掉 WHERE，仅取此去重类型目录，不取全部码值；相应计数使用同样去掉 WHERE 的 D8。不能将目录未出现的类型断言为不存在：当前表只记录有码值的类型。

### D2：多个确定类型的完整码值

<!-- query: D2 -->
```sql
SELECT code_table_en_name, code_table_cn_name, code_value, code_desc
FROM data_asset_code_kb
WHERE code_table_en_name IN (:dict_en_1, :dict_en_2)
ORDER BY code_table_en_name, code_value, code_desc, code_table_cn_name;
```

直接字典请求用用户指定或已确认代码；字段问题必须已有确认的表和字段及代码名称映射、明确声明或“用户选定用于查询”的范围，后者不证明引用关系。多个字段共用字典只执行一次 D2，再映射回各字段。

本模板没有行数限制。向 NL2SQL 提交时明确要求“返回指定类型的全部匹配行，不能自行追加 LIMIT 100、TOP、FETCH FIRST 或抽样；如被工具限制，请返回实际截断和分页信息”。只把这些作为查询说明，不伪造工具参数。

### D3：类型与指定码值配对批查

<!-- query: D3 -->
```sql
SELECT code_table_en_name, code_table_cn_name, code_value, code_desc
FROM data_asset_code_kb
WHERE (code_table_en_name = :dict_en_1
       AND code_value IN (:value_1, :value_2))
   OR (code_table_en_name = :dict_en_2 AND code_value = :value_3)
ORDER BY code_table_en_name, code_value, code_desc, code_table_cn_name;
```

按 `(类型代码, 原样码值)` 对账。没命中时不能用另一个类型的同值补齐。若类型已由本次其他行证明有记录，不必再次核验存在；没有类型证据时，对全部缺失类型执行一次 D1。候选值查询仅在已确定类型内，无码值命中不视为工具异常重试。

### D4：未限定类型的多个码值反查

<!-- query: D4 -->
```sql
SELECT code_table_en_name, code_table_cn_name, code_value, code_desc
FROM data_asset_code_kb
WHERE code_value IN (:value_1, :value_2)
ORDER BY code_value, code_table_en_name, code_desc, code_table_cn_name;
```

返回所有实际取得的类型与对应含义，不把一个命中当成全业务唯一含义。当前上下文已明确类型时用 D3，不因本句只说“010 呢”而丢掉范围。

### D5：按含义跨类型反查

<!-- query: D5 -->
```sql
SELECT code_table_en_name, code_table_cn_name, code_value, code_desc
FROM data_asset_code_kb
WHERE code_desc LIKE :desc_pattern_1 ESCAPE '!'
   OR code_desc LIKE :desc_pattern_2 ESCAPE '!'
ORDER BY code_table_en_name, code_value, code_desc, code_table_cn_name;
```

按原问题描述查候选，不把同义推测称为精确对应。只有一个描述就删第二个条件，不用 `%` 填空。多个描述分别映射回请求；如果用户要求完全一致，改为 `code_desc = :description`，不能用包含命中冒充等义。

### D6：已确定类型内按含义反查

<!-- query: D6 -->
```sql
SELECT code_table_en_name, code_table_cn_name, code_value, code_desc
FROM data_asset_code_kb
WHERE code_table_en_name IN (:dict_en_1, :dict_en_2)
  AND (code_desc LIKE :desc_pattern_1 ESCAPE '!'
       OR code_desc LIKE :desc_pattern_2 ESCAPE '!')
ORDER BY code_table_en_name, code_value, code_desc, code_table_cn_name;
```

仅当这些类型共用描述筛选条件时用此模板。若用户是“A 字典查成功，B 字典查失败”，须如 D3 将每个描述条件与其类型配对，不能交叉。已有全量结果时直接从结果查，不额外调用。

### D7：多个类型结果的分组计数

<!-- query: D7 -->
```sql
SELECT code_table_en_name, COUNT(*) AS total_rows
FROM data_asset_code_kb
WHERE code_table_en_name IN (:dict_en_1, :dict_en_2)
GROUP BY code_table_en_name
ORDER BY code_table_en_name;
```

这是 D2 的原始行数。D3/D4/D5/D6 需要核对完整性时，将 WHERE 完整替换为那次取数的原条件，保留配对与范围；不能用某类型全部行数核对其指定值结果。计数本身也要检查是否截断。按类型比较原始返回行数，所有组均对应才报告整体完整。

### D8：类型候选的同投影计数

<!-- query: D8 -->
```sql
SELECT COUNT(*) AS total_rows
FROM (
    SELECT DISTINCT code_table_en_name, code_table_cn_name
    FROM data_asset_code_kb
    WHERE code_table_en_name IN (:dict_en_1, :dict_en_2)
       OR code_table_cn_name IN (:dict_cn_1, :dict_cn_2)
) AS candidates;
```

与 D1 的候选行数比较，不能用码值原始行数比较 `DISTINCT` 类型数。只有全量/唯一性结论需要且工具缺少完整性依据时才计数。

## 实际 SQL、100 行与完整性

1. 检查可见的实际执行 SQL 和返回状态，不能仅因模板没有 LIMIT 就认为执行未加限制。若执行 SQL 不可见，不猜限制来自哪里。正好返回 100 行是核对信号，不是完整或截断的证明。
2. 工具未明确证明全量时，对相同条件做一次计数（D7 或对应过滤）；完整性核对使用原始行数，批量按类型分组。若总量就是 100、取得 100、无其他截断/下一页且范围一致，可按本次核对报告完整；总量大于已取得量则不完整。
3. 可见 SQL 含非用户要求的 LIMIT 100 等截断，且全量确实未取完、工具允许调整时，只纠正一次全量请求。不要变成 LIMIT 1000/10000 轮番重试，也不改变权限或规避强制策略；移除限制的纠正与原请求属于不同的行数策略，计入 DB 次数。
4. 纠正后仍截断/工具明确分页时，只用已知且支持的页码/游标协议继续；每个结果集最多 5 页（含第 1 页），同时受 DB 剩余额度限制。没有真实分页能力即停止。不得通过聚合拼接或伪造下载/导出来绕过限制。
5. 页码/游标不前进、结果重叠无法消除、连续重复页、预算耗尽或输出不足时立即交还部分结果和未完成范围。已取得的第一页只能计一次，纠正得到同样 100 行不能累计为 200 行；不通过反复取第一页“凑够”计数。

## 结果规则与停止

1. 提交每个请求的状态：已核验 / 待确认 / 本次未匹配 / 元数据冲突 / 结果不完整 / 查询失败，并附真实行、来源、过滤范围、计数依据和未完成目标。
2. 值按字符串原样输出。宽松排序规则可能让 DB 等号命中大小写/空白近似值，回传时逐字核对目标与结果，近似项不能宣称精确命中。不根据常识补含义，也不猜回工具已丢失的前导零。
3. 同类型同码值多个含义保留为冲突；空描述是“未提供”。完全重复行可展示合并，但完整性比较仍用去重前行数；唯一码值数、含义条目数、原始行数分开。
4. 指定码值未匹配、类型存在时，按主流程需要取该类型的实际候选；无相似值就提供该类型全部已获取值供判断，不能替原值作答。近似类型也必须先确认。
5. 用户要求全部则列全，包括 300 多条，不自行加任意 `LIMIT`，不再问是否列全。“有哪些类型”同样需要码值表；只有类型、没有取得码值时，不允许假装完整答复，要继续取值或明确无法取得的原因。已知数据变化/数量不符时不宣称完整，未知快照时只说按本次取数与计数核对。

两类 DB 共用每回合 **DB 最多 8 次**。所有批次、取数、计数、分页、纠错都占预算；定位还有该阶段 3 次上限，已确定类型的取数分页不算重新定位。相同成功查询不重复；无法核对完整性或无法继续时立即返回实际范围，不退回结构/字典 KB 重新定位。

明确可修正的参数/语法错误最多改 1 次；未绑定、权限、网络、超时异常停止相关分支，不用 KB 补答案、不向其他 SKILL 循环转交。工具成功零行是查询结果，不能当异常重试。
