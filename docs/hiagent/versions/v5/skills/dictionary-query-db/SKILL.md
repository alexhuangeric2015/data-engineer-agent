---
name: dictionary-query-db
description: 通过 HiAgent 内置数据库能力只读查询 data_asset_code_kb，核验字典 KB 提供的类型和值标识，取得精准含义或完整码值。支持范围明确的批量、配对、反查与比较；保留原值、冲突和完整性，不自行发现或选择近似类型。
---

# 字典数据库核验与取数

## 输入与门槛

输入为字典 KB 的实际定位结果、原始输出目标、候选类型或值标识、已确认范围、字段来源及剩余额度。新字典目标必须先知识库定位；没有定位证据、KB 未召回、依赖的表字段未确认或分支已结束，不执行 DB 探索。

直接字典请求不要求表。字段请求须有结构 DB 核验的当前表字段；其 related 英文、中文名称分别对应字典类型代码、中文名。KB 只证实有线索，引用依据仍由结构 DB 提供；用户选定用于查值不证明真实引用。

只调用实际绑定的 HiAgent 内置数据库能力（NL2SQL）。输出真实执行数据和状态，主流程负责继续或展示；不调用 KB、结构工具或其他 SKILL。成员枚举目标的类型核验只是中间结果，必须继续取码值或说明无法取得的原因。

## 字段契约

| 字段 | 实际含义 |
| --- | --- |
| `code_table_en_name` | 字典类型英文名称/代码 |
| `code_table_cn_name` | 字典中文名称，保留实际版本限定 |
| `code_value` | 字符串码值，不数值化或自行裁剪 |
| `code_desc` | 当前码值含义，不是字典整体定义 |

没有独立字典注释、级别或父级字段，不补造。无类型主表，零行只能说明本次未匹配码值记录，不能区分不存在和空类型。不据字典推断业务实存值或频次。

## 查询方式

批量核验 KB 类型代码/中文名；唯一精确匹配才继续，相似、同名多类型、版本歧义交还确认。代码明确且范围已确认时，一次取值可同时核验类型名称，不为展示名称重复查询。仅中文时先核验类型，不直接猜英文代码。

多个确定类型的完整列表用集合过滤；指定值按类型成组过滤，保持原始配对。裸值反查或精确含义反查按已定位的值/文本及用户明确范围查询，不擅自只选一个类型。模糊描述由 KB 定位，不靠 DB 扩词；需要字面文本匹配时按真实方言转义通配符。

以下为通用 SQL 模板。参数按实际目标扩展，空组删除；冒号不代表平台一定支持绑定接口。按真实 NL2SQL 契约提供目标表、字段、过滤、原样值、只读及全量要求，再取得执行结果，不拼接用户文本。指定值、反查与目录请求按原目标调整同一投影的条件，不能把两个独立集合条件用于配对请求。

<!-- query: D1 -->
```sql
SELECT DISTINCT code_table_en_name, code_table_cn_name
FROM data_asset_code_kb
WHERE code_table_en_name IN (:dict_en_1, :dict_en_2)
   OR code_table_cn_name IN (:dict_cn_1, :dict_cn_2)
ORDER BY code_table_en_name, code_table_cn_name;
```

<!-- query: D2 -->
```sql
SELECT code_table_en_name, code_table_cn_name, code_value, code_desc
FROM data_asset_code_kb
WHERE code_table_en_name IN (:dict_en_1, :dict_en_2)
ORDER BY code_table_en_name, code_value, code_desc, code_table_cn_name;
```

<!-- query: D3 -->
```sql
SELECT code_table_en_name, COUNT(*) AS total_rows
FROM data_asset_code_kb
WHERE code_table_en_name IN (:dict_en_1, :dict_en_2)
GROUP BY code_table_en_name;
```

D3 对照 D2 去重前原始行数。指定值/描述反查的计数必须用相同 WHERE；DISTINCT 类型候选按同样 DISTINCT 子查询计数。计数也要核对是否完整返回。已有完整数据能回答指定值就复用，共用类型只查一次，批量缺失项单独交还。

## 完整性、冲突与退出

向工具传递全量目的，不自行追加 LIMIT、TOP、FETCH FIRST 或抽样。核对实际执行 SQL、总数和分页；看不到 SQL 不猜限制来源，固定返回条数本身不能证明完整或截断。缺少依据时一次同条件计数；工具允许调整的非必要截断最多纠正一次，仍受限只用真实分页协议。

每结果集最多五页，含第一页且计入全局 DB 最多八次；重复页、游标不前进、无法消除的重叠、无分页能力或预算耗尽就停止。纠正得到重复数据不能累计为新行；不轮换更大 LIMIT、不虚构导出或绕过强制策略。

保留前导零、大小写、空白及含义原文；宽松数据库比较命中的近似项不冒充逐字精确命中。同码不同义、名称或映射矛盾保留冲突；完全重复行仅展示去重。空描述为未提供；未知层级不凭码长推断。

逐目标交还状态、DB 原始行、来源、过滤范围、计数依据、缺失和未完成项。来源为数据库表 `data_asset_code_kb`。定位与 KB、计数、修正共用最多三次；核验零行、需确认、异常或额度耗尽即交还，不退回知识库重找。同条件成功不重复，工具异常不当作不存在。
