---
name: table-schema-query-db
description: 实际执行 HiAgent 内置数据库查询，只读核验 table_schema。表未确定时仅定位表；表字段确认后读取 related_column_en/related_column_cn 的码值字典英文/中文名称。支持批量配对和引用反查，定位最多三次，未命中不全库兜底。
---

# 表与字段数据库查询（V4）

## 输入、输出与边界

输入是主流程整理的目标清单：原始名称/描述、问题编号、已确定的表、待查字段、查询目的及已有 DB 结果。先检查可复用结果，再把同一阶段未完成目标合并查询。只有收到 HiAgent 实际绑定的内置数据库能力（NL2SQL）的执行结果，才提交已核验事实。

输出为逐目标状态、实际 DB 行、查询范围、来源、完整性依据、代码名称和取值/引用原文。主流程负责语义确认与最终展示。本 SKILL 不执行字典查询、不决定近似对象、不访问物理业务表，不靠知识库补答案。

## 调用门槛与退出

- 表尚未确认时仅用 T1 定位/核验表，不能先解释字段或返回字典结论。用户直接给精确英文表名时，可用 T2/T3 一次带回表字段证据，但先判断表存在于结果，再使用字段；无行不证明任何字段存在。
- 同目标同定位阶段最多 3 次实际执行，与 KB、计数、纠错共用，不是本 SKILL 自己有 3 次。没有剩余次数、主流程已停止或待用户选择时，不调用 DB，返回当前原因。
- 精确未匹配只能交还主流程按固定路径考虑一次结构 KB；**KB 未召回后不能再用 T5 或无 WHERE 查询兜底**。KB 候选在 DB 全部未匹配时结束该分支，不继续定位字段/字典。
- 单次精确查询零行返回“本次未匹配”，只允许主流程执行尚未用过的固定 KB 步骤；不是允许自由搜索。KB 候选仍未匹配则返回“定位结束未找到”。待确认、失败、额度用尽均结束该阶段；不自行调用 KB，不为了“整理答案”重开查询。

来源统一为“数据库表 `table_schema`”。只知道下列字段，不猜注释列、库名列或字典绑定列：

| 字段 | 含义与使用边界 |
| --- | --- |
| `table_name_en`、`table_name_cn` | 表英文名、中文名；不是物理表存在性证明 |
| `column_name`、`column_cn_name` | 当前表内的字段英文名、中文名；跨表同名列不能合并 |
| `column_type` | 字段类型原值 |
| `is_key`、`is_related` | 标记原值；没有值域说明时不猜 0/1 含义，不以标记值代替代码名称 |
| `related_column_en` | 当前字段对应码值字典的英文名称，核对字典表 `code_table_en_name`；不是普通关联字段名 |
| `related_column_cn` | 当前字段对应码值字典的中文名称，核对字典表 `code_table_cn_name`；保留版本字样 |
| `biz_desc` | 当前字段的业务描述，可包含明确的取值说明或引用声明；不是表注释/独立列注释 |

以上两个 related 字段的含义由本部署用户确认，不按字段英文命名推翻它。独立表注释、独立列注释仍未提供，显示“未提供”。空字符串/纯空白名称视为缺失，非空值按原文核对，不从字段名生成字典代码，不新增 `code_name` 列。

代码英文名称非空时优先按代码核验，中文名称用于一致性核对；只有中文名称时精确定位字典。两者指向不同类型，或与业务描述中的明确声明矛盾时报告冲突。两个名称均缺失时才把 `biz_desc` 的明确引用声明作为补充依据；只出现代码、示例或否定语句不算引用。

## 合并原则

- 表标识列表、中文名列表、候选核验均使用集合条件。多个字段按所属表成组；用 `(表 A AND 列 x/y) OR (表 B AND 列 z)`，不能用 `表 IN(A,B) AND 列 IN(x,y,z)` 产生额外交叉目标。
- 精确字段有明确表时优先过滤；同表需要多列、模糊选列或整表字段时，可一次取该表字段并复用，不逐列查。表信息只需名称时使用候选投影，不为展示名称读取所有字段。
- 每行必须保留所属表。批量有返回不代表每个请求都匹配；按请求标识逐一对账。没查到字段时，只给涉及的表批量补查整表元数据，区分“表有记录但字段未匹配”和“表未匹配元数据”。
- 纯字段跨表反查须用户没有限定表，或明确要求所有出现位置。已限定表的字段不存在时不能偷偷换到其他表。

## SQL 逻辑模板

以下只是按已知字段表达查询条件，`:参数` 不代表 HiAgent 支持该参数接口。使用实际 NL2SQL 契约；支持绑定就绑定，只有自然语言接口则提交明确的目标表、原始值、允许字段、配对关系和只读要求，由工具按实际方言生成并执行。生成 SQL 不能当执行成功。

`IN` 项数和成组条件数量按实际目标扩展；空组删除，不传虚构占位值或空 `IN`。不插入用户文本生成 SQL。包含匹配先转义原文中的 `!`、`%`、`_`，再添加外围 `%`；模板的 `ESCAPE '!'` 需适配真实方言，不通过盲目报错猜方言。

### T1：批量表候选 / 精确名称核验

<!-- query: T1 -->
```sql
SELECT DISTINCT table_name_en, table_name_cn
FROM table_schema
WHERE table_name_en IN (:table_en_1, :table_en_2)
   OR table_name_cn IN (:table_cn_1, :table_cn_2)
ORDER BY table_name_en, table_name_cn;
```

适用于中文全名、英文全名和 KB 提供的候选。返回后按各输入精确名称分组；DB 证实存在不等于语义相同。中文名多个英文标识、同一英文标识多个中文名都保留，不自动选第一行。

用户明确要求“列出元数据中全部表”时，去掉 WHERE，只返回此去重名称目录，不读取全库字段。完整性计数使用同样去掉 WHERE 的 T7。模糊定位失败不能自行改为此全目录模式。

### T2：已确定表的字段批量读取

<!-- query: T2 -->
```sql
SELECT table_name_en, table_name_cn, column_name, column_cn_name,
       column_type, is_key, is_related, related_column_en,
       related_column_cn, biz_desc
FROM table_schema
WHERE table_name_en IN (:table_en_1, :table_en_2)
ORDER BY table_name_en, column_name, column_cn_name, column_type, biz_desc;
```

同时提供表名、字段、代码名称和取值/引用原文；无需另查表名或逐列取数。映射取当前表当前字段行的 related 两列，不从同名跨表字段借用。排序只是显示顺序，不代表物理列顺序。单表按实际条件缩为一个目标。

### T3：表与字段配对批查

<!-- query: T3 -->
```sql
SELECT table_name_en, table_name_cn, column_name, column_cn_name,
       column_type, is_key, is_related, related_column_en,
       related_column_cn, biz_desc
FROM table_schema
WHERE (table_name_en = :table_en_1
       AND (column_name = :field_1 OR column_cn_name = :field_1))
   OR (table_name_en = :table_en_2
       AND (column_name = :field_2 OR column_cn_name = :field_2))
ORDER BY table_name_en, column_name, column_cn_name, column_type, biz_desc;
```

同一表的多个英文列名也可在该表条件内用 `IN` 合并。若某输入恰好等于一列英文名、另一列中文名，保留两者为待确认项，不按过滤顺序认定。没有匹配就用 T2 读取相关表，供主流程展示相似列或全部列。

### T4：未限定表时，按字段名称反查

<!-- query: T4 -->
```sql
SELECT table_name_en, table_name_cn, column_name, column_cn_name,
       column_type, is_key, is_related, related_column_en,
       related_column_cn, biz_desc
FROM table_schema
WHERE column_name IN (:field_1, :field_2)
   OR column_cn_name IN (:field_1, :field_2)
ORDER BY table_name_en, column_name, column_cn_name, column_type, biz_desc;
```

用户问“哪些表有这些字段”时返回集合。用户要某一业务字段的含义但未给表时，带所属表展示实际候选，请其选适用范围；同名不等于相同含义。

“同时包含 X、Y”时，以完整返回的匹配行为依据按表归集，只保留两个请求字段都精确匹配的表；“包含任一个”才取并集。不完整的返回不能证明某表缺少另一字段。

### T5：名称、用途、字段描述的文本候选

<!-- query: T5 -->
```sql
SELECT table_name_en, table_name_cn, column_name, column_cn_name,
       column_type, is_key, is_related, related_column_en,
       related_column_cn, biz_desc
FROM table_schema
WHERE table_name_en LIKE :text_pattern ESCAPE '!'
   OR table_name_cn LIKE :text_pattern ESCAPE '!'
   OR column_name LIKE :text_pattern ESCAPE '!'
   OR column_cn_name LIKE :text_pattern ESCAPE '!'
   OR biz_desc LIKE :text_pattern ESCAPE '!'
ORDER BY table_name_en, column_name, column_cn_name, column_type, biz_desc;
```

仅用于用户明确的字段描述检索或独立文本搜索，不用于 KB 未召回、表定位已终止后的补救；不传无关键词的 `%`。多个明确关键词可合成同一查询，按命中依据分组。已有表范围时必须把以上 OR 整体括起，再 `AND table_name_en IN (...)`。已有完整字段结果就从结果匹配，不重查。

字典引用反查优先 T8 查询真实代码名称映射。若用户还要求描述线索，可将 T5 谓词收窄为 `biz_desc LIKE :reference_pattern ESCAPE '!'`，逐行辨别明确声明、仅提及和否定语句；不要把文本命中等同引用，不把描述中未写出理解为没有引用。

### T6：多个表全字段结果的分组计数

<!-- query: T6 -->
```sql
SELECT table_name_en, COUNT(*) AS total_rows
FROM table_schema
WHERE table_name_en IN (:table_en_1, :table_en_2)
GROUP BY table_name_en
ORDER BY table_name_en;
```

与 T2 按表比较去重前原始行数。用于 T3/T4/T5 时，必须同步使用那次查询的完整 WHERE，不可沿用 T2 条件。计数本身也要检查工具是否完整返回；缺少某组不能在截断时当成 0。

### T7：名称候选的同投影计数

<!-- query: T7 -->
```sql
SELECT COUNT(*) AS total_rows
FROM (
    SELECT DISTINCT table_name_en, table_name_cn
    FROM table_schema
    WHERE table_name_en IN (:table_en_1, :table_en_2)
       OR table_name_cn IN (:table_cn_1, :table_cn_2)
) AS candidates;
```

这是 T1 的候选行数，不能拿 `table_schema` 原始字段行数与候选数比较。仅在全量/唯一性判断需要、工具未提供完整性依据时计数，不默认每次都取数再计数。

### T8：按码值字典名称批量反查字段

<!-- query: T8 -->
```sql
SELECT table_name_en, table_name_cn, column_name, column_cn_name,
       column_type, is_key, is_related, related_column_en,
       related_column_cn, biz_desc
FROM table_schema
WHERE related_column_en IN (:dict_en_1, :dict_en_2)
   OR related_column_cn IN (:dict_cn_1, :dict_cn_2)
ORDER BY table_name_en, column_name, related_column_en, related_column_cn;
```

只在用户明确反查引用、目标字典已核验后使用。结果按完整表字段标识逐行与该字典代码/中文名核对；英文中文只匹配其一而另一项非空且矛盾时，标记映射冲突，不认定为正常引用。完整性仍只限当前可见元数据映射记录，不证明业务系统实际使用情况；计数复用 T6 但替换为 T8 的相同 WHERE。

## 解释与交还

1. 提交每个目标：已核验 / 本次未匹配 / 待确认 / 元数据冲突 / 结果不完整 / 查询失败。保留 DB 原行和未匹配请求清单，不只交还成功行。来源、范围、完整性与原始行数一并提供。
2. 交还当前 `表.字段` 的 `related_column_en`、`related_column_cn` 原值，注明“代码英文名称/代码中文名称”；主流程按这些名称批量核验字典。没有代码名称时再附业务描述中的明确声明；不把普通字段名作为映射，不让未确认表的 KB 线索进入这一步。
3. `biz_desc` 明确给出的内联取值可以逐字提取为“字段业务描述中的取值说明”；不推算未列值，不声称完整枚举，不生成字典代码。描述同时声明字典时交还两个依据，由主流程查询字典、核对冲突。
4. 多个中文名、同字段不同类型/描述保留冲突；完全相同行只可展示去重，核对数量仍用原始行。英文标识做原样比较，宽松数据库比较命中的近似项不能冒充精确命中。
5. 零行仅说明 `table_schema` 在本次条件下未匹配，不等于业务物理表不存在；没有独立表记录，不能断言表存在但有零列。

本 SKILL 与字典 DB 共用每回合 **DB 最多 8 次**预算，定位同时受本阶段 3 次上限约束。成功相同查询不重复；已知可修正的语法/参数错误最多改 1 次；未绑定、权限、网络、超时错误停止相关分支。不循环调用 KB 或其他 SKILL。

全字段不任意截断，不因 300 多行而询问是否列全。工具分页协议已知才分页，每个结果集最多 5 页（含第 1 页）且计入预算；定位阶段仍受 3 次上限约束。无进展、截断、计数不符、预算耗尽或输出不足就注明未完成范围；生成 SQL、无 LIMIT、一次有返回都不能当完整性证明。
