---
name: table-schema-query-db
description: 使用 HiAgent 已绑定数据库能力只读查询 table_schema，核验 KB 定位对象并精准取得表字段和代码名称映射。支持批量配对及范围明确的集合反查，回传执行证据、缺口和完整性；不做知识库语义发现。
---

# 结构数据库核验与取数

## 调用条件

接收主控六组记录及本次授权目的：身份定位、指定成员、完整成员、同父对象补查或完整性核对。需有相关 KB 定位证据或本任务可复用的父对象/成员证据；无证据、上游待选择、分支停止、无额度时交还原因，不做 DB 探索。字段取数须有已确认表；独立集合反查按主控授权的原集合范围执行，不代选父对象。

仅使用已绑定 HiAgent 数据库能力（NL2SQL），取得真实执行结果。不调用其他 SKILL，记录请求、实际 SQL/过滤条件（可见时）、行与执行凭据。逻辑参数不是平台工具接口。

必要输入缺失或剩余额度未知时回传待补信息及缺口，不自行补造参数或执行；成员查找复用已确认父对象的定位证据。

## 工作步骤

1. **明确查询合同**：目的、原始表/字段标识、已确认父对象、原请求限定、配对条件、返回列、指定项或全部。身份核验覆盖 KB 候选；原中文名自动唯一需要同时覆盖该原精确名称和明确限定，不能仅查询候选英文名。需要的限定无对应字段时报告不可核验。
2. **批量执行**：身份查询使用名称投影；指定字段使用成组表—列过滤；完整字段仅用于枚举或主控授权的一次同父对象补查。获取字段时同时取表中文名、属性与代码名称，不重复查展示信息。目录/反查须明确实际覆盖原范围，任一/同时谓词按原意构造。
3. **核对执行**：按主控查询合同检查实际数据源、投影、WHERE 配对及范围，再核对限行/完整性。条件错误、能力未知或执行错误返回原因及已用调用；修正、计数和分页只按主控额度执行。原始行与去重口径一致，完整性证据仅覆盖实际执行范围。
4. **逐项交还**：身份零行是定位终止；已确认表内指定字段零行是成员未匹配，交给主控决定复用或一次补查；行已取得为已取证；受限为部分结果；实际错误为查询失败；预算不足为额度用尽。相似候选及映射冲突列出原值，建议待选择，不自行选择或查字典。

## 完成与回传

六组记录均回传：任务目的与父对象、状态/原因/建议下一步、DB 原始行与执行凭据、原范围/KB 范围/实际过滤范围、完整性依据及计数口径、实际调用/签名/缺口。事实来源为数据库表 table_schema。证据缺失或范围不完整时不能宣称唯一、全部或不存在；技能结束不等于用户原目标完成。

## 字段与解释参考

| 字段 | 含义与边界 |
| --- | --- |
| table_name_en / table_name_cn | 元数据表英文/中文名，非物理业务表检查结果 |
| column_name / column_cn_name | 当前表内字段英文/中文名 |
| column_type | 字段类型原值 |
| is_key / is_related | 标记原值；未声明值域不猜含义 |
| related_column_en / related_column_cn | 当前字段对应的代码名称英文/中文，核对字典类型英文/中文 |
| biz_desc | 当前字段业务描述，不代替表注释或独立列注释 |

独立表注释/字段注释未提供，展示未提供。related 名称冲突或与明确引用声明矛盾时保留冲突；两者都缺失才提取 biz_desc 明确引用，内联取值仅按字段原文解释，不生成字典。跨表同名列不能补映射。仅元数据有记录不证明业务数据取值/频率。

## 通用 SQL 形状参考

冒号仅为逻辑占位；依真实 NL2SQL 契约传达条件，不直接拼接用户文本。可扩展参数组，删除无输入条件并保留原限定。以下均无默认限行。计数用实际执行 SELECT 去掉排序后作子查询，保留 WHERE 和 DISTINCT；原始成员行用原始口径。计数、修正和分页由主控授权，不在本技能自动循环。

英文名称集合同时保留用户原始完整英文标识与相关 KB 候选；仅有中文时删除无输入的英文条件，不造占位值。

<!-- query: T_ID -->
```sql
SELECT DISTINCT table_name_en, table_name_cn
FROM table_schema
WHERE table_name_en IN (:table_en_1, :table_en_2)
   OR table_name_cn = :original_table_cn
ORDER BY table_name_en, table_name_cn;
```

T_ID 同时核验候选及原精确中文名；若用户另有限定须给两侧条件整体加括号后再 AND 限定。只有查询完整且原名逐字匹配的对象标识唯一、名称无冲突时，主控才能按原名确定。候选中的近似中文名不能代替 original_table_cn。

<!-- query: T_PAIR -->
```sql
SELECT table_name_en, table_name_cn, column_name, column_cn_name,
       column_type, is_key, is_related, related_column_en, related_column_cn, biz_desc
FROM table_schema
WHERE (table_name_en = :table_en_1 AND column_name = :field_1)
   OR (table_name_en = :table_en_2 AND column_name = :field_2)
ORDER BY table_name_en, column_name, column_cn_name, column_type, biz_desc;
```

指定中文列名时换为 column_cn_name 精确条件，并在已确认表内核对逐字精确及同名歧义；无类型码值不用于本查询。反查按授权字段名或 related 名称过滤，结果保留每行所属表。

<!-- query: T_MEMBERS -->
```sql
SELECT table_name_en, table_name_cn, column_name, column_cn_name,
       column_type, is_key, is_related, related_column_en, related_column_cn, biz_desc
FROM table_schema
WHERE table_name_en IN (:table_en_1, :table_en_2)
ORDER BY table_name_en, column_name, column_cn_name, column_type, biz_desc;
```

T_MEMBERS 只用于已确认表的完整成员或一次范围内补查。不得把身份定位失败转换成全表目录。完整成员数据可复用回答指定项；精确查询部分结果不能替代完整成员覆盖。
