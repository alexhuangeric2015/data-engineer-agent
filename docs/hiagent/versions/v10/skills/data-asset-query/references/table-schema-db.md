# 结构数据库核验

本文件是 data-asset-query 的按需参考，不是独立注册 SKILL。按总入口已确定的阶段、证据及额度执行，记录结果后由总入口决定继续或结束。

## 阶段前置条件

使用总入口项编号/轮次、阶段/结果集、原目标/标识、确认父对象、三个范围、有效证据、完整性与剩余额度。KB 相关定位或本任务有效父对象定位证据在先；字段请求先确认表，集合反查按授权原范围。无必要输入/额度未知回待补信息，无额度回额度用尽，上游待选择/分支停止不调用。只使用已绑定 HiAgent NL2SQL 只读能力，由总入口决定下一阶段。

## 核验步骤与阶段结束

1. 明确查询合同：身份/指定字段/枚举/授权补查/计数，数据源、预期投影、原限定及配对。原中文名唯一性核验须覆盖原名与限定，候选 ID 子集不够。
2. 实际执行：身份投影取名称，指定列按表—列配对过滤；完整字段仅为枚举或一次同表补查。字段返回复用表名、属性、映射；集合按任一/同时条件与原范围，不代选父对象。
3. 核对实际 SQL/条件（可见时）、执行行及完整性。修正/计数/分页按总入口结果集与剩余额度，修正保持预期合同，不自行分裂结果集重获额度。旧轮次行不作为新核验证据。
4. 身份零行回定位终止；已确认表内指定列零行回成员未匹配；有执行行回已取证，受限回部分结果，实际错误回查询失败。歧义/冲突建议待选择。结束当前结构阶段，由总入口判断是否具备进入字典定位阶段的条件，不在本阶段自行执行字典查询。

## 字段与引用解释

| 实际列 | 含义 |
| --- | --- |
| table_name_en / table_name_cn | 元数据表英文/中文名 |
| column_name / column_cn_name | 当前表字段英文/中文名 |
| column_type | 字段类型原值 |
| is_key / is_related | 标记原值；未给值域保持原值 |
| related_column_en / related_column_cn | 当前字段代码名称英文/中文，分别对应字典类型英文/中文 |
| biz_desc | 当前字段业务描述 |

related 英文提供精确字典定位标识，中文用于一致性或唯一中文定位；报告当前表当前列的原值、引用依据和冲突，供总入口决定。名称与明确描述矛盾保留冲突。两列都缺失才提取 biz_desc 明确引用声明；提及、示例、否定不作绑定。明确内联值仅解释字段原文，标字段描述来源，不造字典/额外值。跨表同名列不能补映射。

独立表/字段注释未提供，显示未提供；biz_desc 不代替注释。元数据记录不证明物理业务表存在或业务实存取值/频率。零行仅说明本次元数据未匹配。

名称 NULL/空字符串视为缺失；非空名称保留原文，只有空白的名称先标待核实。码值原字符串另按其自身契约处理。

## 阶段结果记录

逐项返回轮次/目标/父对象/结果集、状态与建议、DB 原始行及执行凭据/时点、三个范围及实际条件、引用原值/依据/冲突、完整性口径/已取得范围、实际调用与剩余缺口。来源 table_schema。只更新本次有效范围；执行条件或覆盖未知则如实记录，不宣称唯一或全部。

## 通用 SQL 形状参考

冒号仅为逻辑占位；依真实 NL2SQL 契约传达条件，不直接拼接用户文本。可扩展参数组，删除无输入条件并保留原限定。以下均无默认限行。计数用实际执行 SELECT 去掉排序后作子查询，保留 WHERE 和 DISTINCT；原始成员行用原始口径。计数、修正和分页由总入口授权，不在本参考自动循环。

英文名称集合同时保留用户原始完整英文标识与相关 KB 候选；仅有中文时删除无输入的英文条件，不造占位值。

<!-- query: T_ID -->
```sql
SELECT DISTINCT table_name_en, table_name_cn
FROM table_schema
WHERE table_name_en IN (:table_en_1, :table_en_2)
   OR table_name_cn = :original_table_cn
ORDER BY table_name_en, table_name_cn;
```

T_ID 同时核验候选及原精确中文名；若用户另有限定须给两侧条件整体加括号后再 AND 限定。只有查询完整且原名逐字匹配的对象标识唯一、名称无冲突时，总入口才能按原名确定。候选中的近似中文名不能代替 original_table_cn。

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
