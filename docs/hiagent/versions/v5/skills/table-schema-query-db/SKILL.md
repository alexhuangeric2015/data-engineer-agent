---
name: table-schema-query-db
description: 通过 HiAgent 内置数据库能力只读查询 table_schema，核验结构 KB 定位的对象，取得精准表字段及代码名称映射。按确认范围批量补全数据，返回存在性、原始行、缺口、冲突及完整性；不承担知识库语义发现。
---

# 结构数据库核验与取数

## 输入与门槛

输入为结构 KB 实际返回的候选标识、问题编号、查询目的、已确认范围及剩余额度。已有本问题的 KB 定位和 DB 证据可复用，无需再召回。没有定位证据、KB 未召回或上游分支已结束时，不执行探索性 DB 查询。

通过实际绑定的内置数据库能力（NL2SQL）只读查询。必须收到执行结果；生成 SQL、加载技能都不算查询。仅交还证据和状态，由主流程决定确认、继续或展示，不调用其他 SKILL。

## 字段契约

| 字段 | 实际含义 |
| --- | --- |
| `table_name_en`、`table_name_cn` | 元数据中的表英文、中文名称 |
| `column_name`、`column_cn_name` | 所属表内的列英文、中文名称 |
| `column_type` | 字段类型原值 |
| `is_key`、`is_related` | 标记原值；未给值域时不猜含义 |
| `related_column_en`、`related_column_cn` | 当前字段对应码值字典的英文、中文名称，分别核对字典表类型代码、中文名 |
| `biz_desc` | 字段业务描述，可能含明确引用或内联取值 |

独立表注释和列注释未提供，不造列、不用业务描述代替。空名称视为缺失，非空标识保留原文。表有元数据不证明已检查物理业务表，零行不证明物理表不存在。

## 查询方式

先批量核验候选表；表确定后按表读取所需字段。字段过滤无精确结果时，可在该已确认表内取完整字段，供主流程判断相似项或列全。纯跨表集合反查按 KB 已定位的列标识和用户明确范围精确过滤，返回所属表；不借此为某张未确定表猜字段。

同阶段集合合批；特定表字段请求要保留成组配对条件。一次取数复用表中文名、字段属性及映射，共用表不逐列重复查询。用户明确要求名称目录才取对应去重目录，不把定位失败改成全库扫描。

下面是通用 SQL 条件模板，参数数量按真实目标扩展，空条件组删除。冒号只是逻辑参数表示，不假设平台支持此接口；按实际 NL2SQL 契约传递目标、范围、字段、只读要求和原始值，由工具实际生成并执行。字段过滤和反查可在同一投影上改为成组精确条件，不直接拼接用户文本。

<!-- query: T1 -->
```sql
SELECT DISTINCT table_name_en, table_name_cn
FROM table_schema
WHERE table_name_en IN (:table_en_1, :table_en_2)
   OR table_name_cn IN (:table_cn_1, :table_cn_2)
ORDER BY table_name_en, table_name_cn;
```

<!-- query: T2 -->
```sql
SELECT table_name_en, table_name_cn, column_name, column_cn_name,
       column_type, is_key, is_related, related_column_en,
       related_column_cn, biz_desc
FROM table_schema
WHERE table_name_en IN (:table_en_1, :table_en_2)
ORDER BY table_name_en, column_name, column_cn_name, column_type, biz_desc;
```

<!-- query: T3 -->
```sql
SELECT table_name_en, COUNT(*) AS total_rows
FROM table_schema
WHERE table_name_en IN (:table_en_1, :table_en_2)
GROUP BY table_name_en;
```

T3 对照 T2 原始行数。其他过滤必须同步替换 WHERE；去重候选计数要包相同 DISTINCT 投影，不能与字段原始行数混比。仅需完整性而工具未给依据时计数，不默认额外查询。

## 代码名称与结果

返回当前表当前字段的 related 名称，不借跨表同名列补映射。英文优先，中文辅助核对；仅中文时判断唯一性；名称矛盾或与明确业务描述矛盾时报告冲突。两个名称缺失才提取 `biz_desc` 中的明确引用，不把示例、否定或提及当声明。内联取值只能按当前字段原文解释，不生成字典或未列值。

引用反查按已定位类型的代码名称精确过滤 related 两列，再逐行核对；描述线索与名称映射分开，不能声称业务实际引用已查全。

逐目标交还：已核验 / 待确认 / 本次未匹配 / 冲突 / 结果不完整 / 查询失败 / 额度用尽，附 DB 原始行、过滤范围、完整性依据和缺失项。来源为数据库表 `table_schema`，未被 DB 核验的 KB 数据不混入。

本阶段定位与 KB、计数、修正共用最多三次，全局 DB 最多八次。候选核验零行就结束该分支，不回 KB，不扩大词义搜索。同条件成功不重复，异常与零行分别处理。全量不自行限行；实际 SQL 截断核对、一次纠正及真实分页按主提示词执行，无进展或超预算时报告部分范围。
