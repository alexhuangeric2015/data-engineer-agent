---
name: dictionary-query-db
description: 字典核验：在 data_asset_code_kb 核验 KB 类型候选、解释指定值或完整枚举；支持成组配对与原范围反查，回传真实含义、冲突及完整性。
---

# 字典数据库核验

## 条件

接收主控项编号/轮次、阶段/结果集、原目标/标识、确认父对象、三个范围、有效证据及剩余额度。字典 KB 定位在先，已定位父类型的成员可复用。字段入口须有效结构 DB 证据及确认表字段；独立入口无需表。缺必要输入/额度未知回待补信息，无额度回额度用尽，上游待选/分支停止不调用。仅使用绑定 NL2SQL 只读能力，不互调技能。

## 步骤与结束

1. 明确身份/指定值/枚举/补查/反查/计数合同，带原标识、父对象、限定/配对和预期投影。中文唯一性核验覆盖原名范围；无类型反查覆盖用户原范围，不局限 KB 类型子集。
2. 批量实际执行：身份用类型去重投影，指定值按类型—值成组过滤，完整成员按确认类型集合。反查按原值/真实文本及原限定；模糊描述由 KB 定位，字面通配符按真实方言转义。成员及已得身份属性复用。
3. 核对实际条件/行与完整性，按主控结果集额度执行计数、一次修正或真实分页，旧轮次证据不冒充新结果。字段映射英文精确逐字匹配，中文非空时核对一致性；仅中文需原范围唯一。KB 推断不作绑定，用户选择只证明本次查值选择。
4. 身份零行回定位终止；已确认类型内指定值零行回成员未匹配；有行回已取证、受限回部分结果、错误回查询失败。冲突/歧义交主控待选择，返回即结束，不自行取下一阶段。

## 字段与含义解释

| 实际列 | 含义 |
| --- | --- |
| code_table_en_name / code_table_cn_name | 类型英文代码/中文名称，保留版本限定 |
| code_value | 字符串原码值 |
| code_desc | 当前码值含义，不是字典整体注释 |

没有独立类型主表，身份零行不能区分空类型与不存在。没有独立字典注释、层级、父级列，未知写未提供/无法核验，不按码长推断。登记码值不等于业务实存值/频率。保留前导零、大小写和空白，空字符串与 NULL 分开；宽松匹配不当逐字精确。完全重复可展示合并，同码不同义/名称冲突保留，空含义标未提供。

名称 NULL/空字符串视为缺失；非空名称保留原文，只有空白的名称先标待核实。码值原字符串另按其自身契约处理。

## 回传

逐项返回轮次/目标/父对象/结果集、状态/建议、实际 DB 行及执行凭据/时点、三个范围与配对、映射核对/冲突、原始与展示口径/覆盖、实际调用和缺口。来源 data_asset_code_kb。身份成功是中间结果，枚举完成条件按主控原目标。执行条件或完整性未知就明确未知。

## 通用 SQL 形状参考

逻辑占位按实际契约传给 NL2SQL，不拼接用户文本。参数可按目标扩展，无输入条件删除；原限定需覆盖所有 OR 分支。完整性计数复用实际 SELECT 去排序后的子查询，保持 WHERE 和 DISTINCT 口径；计数本身也需完整。修正、计数、分页只按主控额度，不自动循环。

英文名称集合同时保留用户原始完整英文标识、当前字段有效 DB 映射标识与相关 KB 候选；仅有中文时删除无输入的英文条件，不造占位值。

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
