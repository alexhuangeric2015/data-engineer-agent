---
name: dictionary-query-db
description: 使用 HiAgent 已绑定数据库能力只读查询 data_asset_code_kb，核验 KB 字典候选、精准解释指定码值或取得完整成员。支持批量配对和授权范围的反查，保留原字符串、冲突及完整性；不代选近似类型。
---

# 字典数据库核验与取数

## 调用条件

接收主控六组记录及查询许可。新类型需有相关字典 KB 定位；本任务已定位/核验的父对象及其成员范围证据可复用，不逐成员重新 KB。字段请求须先有结构 DB 核验且主控确认的表字段；独立字典/码值请求不要求表。上游待选择、无定位证据、分支停止、无额度时交还原因，不做探索或调用其他 SKILL。

使用实际绑定的 HiAgent 内置数据库能力（NL2SQL），取得实际执行行与凭据；SQL 生成不算完成执行。不假定工具参数绑定或分页协议。

必要输入缺失或剩余额度未知时回传待补信息及缺口，不自行补造参数或执行；成员查找复用已确认父对象的定位证据。

## 工作步骤

1. **查询合同**：明确目的、原始类型/值/含义、父对象、原限定、配对、返回字段、指定项/全部。身份核验覆盖原精确中文名及其范围时才支持中文名唯一性；KB 类型子集不能证明唯一。类型英文与中文核验结果冲突保留原值。无类型的值或含义反查是集合查询，按原授权范围过滤，不默认只查 KB 召回的类型。
2. **批量取数**：身份用类型去重投影，指定值用类型—值成组条件，成员枚举用已确认类型集合条件；裸值或精确含义反查用实际值/文本条件及原限定。模糊描述由 KB 定位，不 DB 扩词兜底；字面文本匹配按真实方言处理通配符。共用类型及已取得完整范围复用。
3. **核对结果**：检查执行合同、实际过滤、限行及覆盖范围；依主控授权核对计数或前进分页。代码逐字比对，宽松命中不冒充原值。完全重复可展示去重，同码不同义或类型名称不一致保留冲突。字段引用仅在实际结构映射和类型一致时支持；用户选择查值不证明引用。
4. **回传**：身份查询零行是定位终止；已确认类型内指定值零行是成员未匹配，由主控决定复用/一次补查；取得行是已取证；受限是部分结果；执行错误是查询失败；预算不足是额度用尽。歧义/冲突建议待选择，未经主控确认不继续取成员。

## 完成与回传

回传六组记录：原任务/父对象、状态/原因/建议动作、DB 原始行与执行凭据、三个范围及配对、原始/展示行数和完整性依据、实际调用/签名/缺口。来源为数据库表 data_asset_code_kb。类型定位完成不等于枚举目标完成，需取得并展示成员及含义或说明未完成范围。未执行或未知完整性不能宣称唯一或全部。字段未提供引用依据时返回缺口，用户指定类型可查值但不补造绑定。

## 字段与解释参考

| 字段 | 含义与边界 |
| --- | --- |
| code_table_en_name | 类型英文名称/代码，保持原文 |
| code_table_cn_name | 类型中文名，保留实际版本限定 |
| code_value | 字符串码值，保留前导零、大小写和空白；空字符串与 NULL 区分 |
| code_desc | 单一码值含义，非字典整体注释；缺失标未提供 |

没有独立类型主表，身份零行只说明本次未匹配码值记录，不能区分空字典与不存在。没有独立字典注释、层级、父级列，不能补造；未知层级不按码长推断。字典登记值不等于业务实存值/频率。字段的 related_column_en / related_column_cn 分别对应类型英文/中文；仅中文的绑定需原名范围唯一，英文优先但中文矛盾仍是冲突。

## 通用 SQL 形状参考

逻辑占位按实际契约传给 NL2SQL，不拼接用户文本。参数可按目标扩展，无输入条件删除；原限定需覆盖所有 OR 分支。完整性计数复用实际 SELECT 去排序后的子查询，保持 WHERE 和 DISTINCT 口径；计数本身也需完整。修正、计数、分页只按主控额度，不自动循环。

英文名称集合同时保留用户原始完整英文标识与相关 KB 候选；仅有中文时删除无输入的英文条件，不造占位值。

<!-- query: D_ID -->
```sql
SELECT DISTINCT code_table_en_name, code_table_cn_name
FROM data_asset_code_kb
WHERE code_table_en_name IN (:dict_en_1, :dict_en_2)
   OR code_table_cn_name = :original_dict_cn
ORDER BY code_table_en_name, code_table_cn_name;
```

D_ID 同时核验候选及原精确中文名；限定需包裹整个 OR 条件。原名对象唯一还需完整执行证据及逐字比对，不能把候选近似名填入 original_dict_cn。每个英文类型的中文名矛盾也交还冲突。

<!-- query: D_PAIR -->
```sql
SELECT code_table_en_name, code_table_cn_name, code_value, code_desc
FROM data_asset_code_kb
WHERE (code_table_en_name = :dict_en_1 AND code_value = :value_1)
   OR (code_table_en_name = :dict_en_2 AND code_value = :value_2)
ORDER BY code_table_en_name, code_value, code_desc, code_table_cn_name;
```

D_PAIR 用于已确认类型的指定值；没有类型的反查使用下方 D_REVERSE，不猜类型补配对。

<!-- query: D_MEMBERS -->
```sql
SELECT code_table_en_name, code_table_cn_name, code_value, code_desc
FROM data_asset_code_kb
WHERE code_table_en_name IN (:dict_en_1, :dict_en_2)
ORDER BY code_table_en_name, code_value, code_desc, code_table_cn_name;
```

D_MEMBERS 仅完整枚举或主控许可的一次已确认类型内补查，不用于默认单值请求。

<!-- query: D_REVERSE -->
```sql
SELECT code_table_en_name, code_table_cn_name, code_value, code_desc
FROM data_asset_code_kb
WHERE code_value IN (:value_1, :value_2)
ORDER BY code_table_en_name, code_value, code_desc, code_table_cn_name;
```

D_REVERSE 是原问题明确无类型的值反查；用户有类型限定时加原限定。精确含义反查改为 code_desc 原文本过滤，不凭 KB 候选截断原范围。反查集合仍不证明某业务字段实际引用。全量不自行加 LIMIT/TOP/FETCH FIRST；如有实际限制，按主控规则交还部分范围。
