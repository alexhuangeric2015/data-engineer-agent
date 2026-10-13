#!/usr/bin/env python3
"""校验 V3 文档内的逻辑 SQL；只使用内存样本，不连接 HiAgent 或业务库。"""

from collections import Counter
from pathlib import Path
import re
import sqlite3


# 测试数据和查询来自本版本目录，避免误用或改写 V1/V2。
ROOT = Path(__file__).resolve().parent
SKILLS = (
    "table-schema-query-kb",
    "table-schema-query-db",
    "dictionary-query-kb",
    "dictionary-query-db",
)


def load_queries():
    """读取运行文档，检查注册名和查询编号，再返回可直接执行的模板。"""
    prompt = (ROOT / "agent-prompt/数据建模师.md").read_text()
    queries = {}
    for name in SKILLS:
        body = (ROOT / "skills" / name / "SKILL.md").read_text()
        assert body.startswith(f"---\nname: {name}\n"), name
        assert name in prompt, name
        if name.endswith("-db"):
            assert "DB 最多 8 次" in body, name
        for key, sql in re.findall(
            r"<!-- query: (\w+) -->\n```sql\n(.*?)\n```", body, re.S
        ):
            assert key not in queries, key
            assert sql.startswith("SELECT ") and "LIMIT" not in sql.upper(), key
            queries[key] = sql
    assert set(queries) == {f"T{i}" for i in range(1, 8)} | {
        f"D{i}" for i in range(1, 9)
    }
    assert "DB 最多 8 次" in prompt
    assert "没有相似字段时，展示该表全部已获取字段" in prompt
    assert "引用未核实" in prompt and "字段业务描述中的取值说明" in prompt
    return queries


def sample_database():
    """建立与已知字段契约一致的隔离样本，名称都不是用户真实资产。"""
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE table_schema (
        table_name_en TEXT, table_name_cn TEXT, column_name TEXT,
        column_cn_name TEXT, column_type TEXT, is_key TEXT, is_related TEXT,
        related_column_en TEXT, related_column_cn TEXT, biz_desc TEXT
    )""")
    db.execute("""CREATE TABLE data_asset_code_kb (
        code_table_en_name TEXT, code_table_cn_name TEXT,
        code_value TEXT, code_desc TEXT
    )""")
    table_rows = [
        ("TEST_DEPOSIT", "存款记录表", "STATUS", "存款状态", "varchar",
         "0", "0", None, None, "引用字典 TEST_DEPOSIT_STATUS。"),
        ("TEST_DEPOSIT", "存款记录表", "AMOUNT", "存款金额", "decimal",
         "0", "0", None, None, "本笔存款金额"),
        ("TEST_DEPOSIT", "存款记录表", "ACTIVE", "有效标志", "char",
         "0", "0", None, None, "取值说明：0=否，1=是。"),
        ("TEST_TRADE", "交易表", "STATUS", "交易状态", "varchar",
         "0", "0", None, None, "引用字典 TEST_TRADE_STATUS。"),
        ("TEST_TRADE", "交易表", "AMOUNT", "交易金额", "decimal",
         "0", "0", None, None, "成交金额"),
        ("TEST_TRADE", "交易表", "ROLE", "身份角色", "varchar",
         "0", "1", "TEST_ROLE_TYPE", "角色类型", "相关字段，无字典引用声明"),
        ("TEST_ARCHIVE", "交易表", "STATUS", "归档状态", "char",
         "0", "0", None, None, "归档标记，不引用 TEST_TRADE_STATUS。"),
        ("TEST_LITERAL", "字面文本表", "LITERAL", "字面符号", "varchar",
         "0", "0", None, None, "文本100%_!"),
        ("TEST_LITERAL", "字面文本表", "OTHER", "非字面符号", "varchar",
         "0", "0", None, None, "文本1000XY"),
        ("TEST_CONFLICT", "冲突样本", "FLAG", "标志", "char",
         "0", "0", None, None, "取值说明一"),
        ("TEST_CONFLICT", "冲突样本", "FLAG", "标志", "int",
         "0", "0", None, None, "取值说明二"),
    ]
    table_rows.append(table_rows[-1])  # 完全重复行不得影响原始行数核对。
    db.executemany("INSERT INTO table_schema VALUES (?,?,?,?,?,?,?,?,?,?)", table_rows)
    # 301 个唯一字符串值，另有同值冲突和完全重复，区分三种计数口径。
    code_rows = [("TEST_TRADE_STATUS", "交易状态", f"{n:03}", f"状态{n}")
                 for n in range(301)]
    code_rows += [
        ("TEST_TRADE_STATUS", "交易状态", "010", "冲突含义"),
        ("TEST_TRADE_STATUS", "交易状态", "010", "状态10"),
        ("TEST_DEPOSIT_STATUS", "存款状态", "010", "已结清"),
        ("TEST_DEPOSIT_STATUS", "存款状态", "099", "未结清"),
        ("TEST_ROLE_TYPE", "角色类型", "010", "共借人配偶"),
        ("TEST_ROLE_TYPE", "角色类型", "10", "另一字符串值"),
        ("TEST_LITERAL", "字面类型", "01", "收益100%_!"),
        ("TEST_LITERAL", "字面类型", "02", "收益1000XY"),
        ("TEST_NULL", "空描述", "01", None),
        ("TEST_ALIAS_A", "同名类型", "1", "甲"),
        ("TEST_ALIAS_B", "同名类型", "1", "乙"),
    ]
    db.executemany("INSERT INTO data_asset_code_kb VALUES (?,?,?,?)", code_rows)
    return db


def execute(db, queries, key, **params):
    """用真实绑定执行文档原模板；返回全部行，模拟工具截断在检查中单独处理。"""
    return [dict(row) for row in db.execute(queries[key], params).fetchall()]


def contains_literal(value):
    """按模板的转义约定构造包含匹配，避免把用户符号当通配符。"""
    return "%" + value.replace("!", "!!").replace("%", "!%").replace("_", "!_") + "%"


def check_tables(db, queries):
    """覆盖七个表查询模板，以及错配、同名、冲突、空结果和作用检索。"""
    names = dict(table_en_1="TEST_DEPOSIT", table_en_2="MISSING",
                 table_cn_1="交易表", table_cn_2="不存在的表")
    candidates = execute(db, queries, "T1", **names)
    assert {row["table_name_en"] for row in candidates} == {
        "TEST_DEPOSIT", "TEST_TRADE", "TEST_ARCHIVE"
    }
    assert execute(db, queries, "T7", **names)[0]["total_rows"] == len(candidates)
    targets = dict(table_en_1="TEST_DEPOSIT", table_en_2="TEST_TRADE")
    full = execute(db, queries, "T2", **targets)
    counts = execute(db, queries, "T6", **targets)
    assert Counter(row["table_name_en"] for row in full) == {
        row["table_name_en"]: row["total_rows"] for row in counts
    }
    paired = execute(db, queries, "T3", **targets, field_1="STATUS", field_2="交易金额")
    assert {(r["table_name_en"], r["column_name"]) for r in paired} == {
        ("TEST_DEPOSIT", "STATUS"), ("TEST_TRADE", "AMOUNT")
    }, "不能跨表串列"
    cross = execute(db, queries, "T4", field_1="STATUS", field_2="有效标志")
    assert len(cross) == 4 and {r["table_name_en"] for r in cross} == {
        "TEST_DEPOSIT", "TEST_TRADE", "TEST_ARCHIVE"
    }
    both = execute(db, queries, "T4", field_1="STATUS", field_2="AMOUNT")
    by_table = {}
    for row in both:
        by_table.setdefault(row["table_name_en"], set()).add(row["column_name"])
    assert {table for table, fields in by_table.items() if {"STATUS", "AMOUNT"} <= fields} == {
        "TEST_DEPOSIT", "TEST_TRADE"
    }
    purpose = execute(db, queries, "T5", text_pattern=contains_literal("存款"))
    assert purpose and all(row["table_name_en"] == "TEST_DEPOSIT" for row in purpose)
    literal = execute(db, queries, "T5", text_pattern=contains_literal("100%_!"))
    assert len(literal) == 1 and literal[0]["column_name"] == "LITERAL"
    partial = execute(db, queries, "T3", **targets, field_1="STATUS", field_2="ABSENT")
    assert len(partial) == 1  # 有返回不代表两个输入目标都匹配。
    fallback = execute(db, queries, "T2", table_en_1="TEST_TRADE", table_en_2="MISSING")
    assert {r["column_name"] for r in fallback} == {"STATUS", "AMOUNT", "ROLE"}
    conflict = execute(db, queries, "T2", table_en_1="TEST_CONFLICT", table_en_2="MISSING")
    assert len(conflict) == 3 and len({tuple(r.values()) for r in conflict}) == 2
    assert {r["column_type"] for r in conflict} == {"char", "int"}
    inline = next(r for r in full if r["column_name"] == "ACTIVE")
    assert inline["biz_desc"] == "取值说明：0=否，1=是。"
    related = next(r for r in full if r["column_name"] == "ROLE")
    assert related["related_column_en"] == "TEST_ROLE_TYPE"
    assert "无字典引用声明" in related["biz_desc"]


def check_dictionaries(db, queries):
    """覆盖八个字典模板，以及批量配对、前导零、反查范围和全量口径。"""
    names = dict(dict_en_1="TEST_ROLE_TYPE", dict_en_2="MISSING",
                 dict_cn_1="同名类型", dict_cn_2="身份类型")
    candidates = execute(db, queries, "D1", **names)
    assert {r["code_table_en_name"] for r in candidates} == {
        "TEST_ROLE_TYPE", "TEST_ALIAS_A", "TEST_ALIAS_B"
    }
    assert all(r["code_table_cn_name"] != "身份类型" for r in candidates)
    assert execute(db, queries, "D8", **names)[0]["total_rows"] == len(candidates)
    targets = dict(dict_en_1="TEST_TRADE_STATUS", dict_en_2="TEST_DEPOSIT_STATUS")
    full = execute(db, queries, "D2", **targets)
    counts = execute(db, queries, "D7", **targets)
    expected = {r["code_table_en_name"]: r["total_rows"] for r in counts}
    assert Counter(r["code_table_en_name"] for r in full) == expected
    assert expected == {"TEST_TRADE_STATUS": 303, "TEST_DEPOSIT_STATUS": 2}
    trade = [r for r in full if r["code_table_en_name"] == "TEST_TRADE_STATUS"]
    assert len({r["code_value"] for r in trade}) == 301
    assert len({tuple(r.values()) for r in trade}) == 302
    assert Counter(r["code_table_en_name"] for r in full[:100]) != expected
    assert len({r["code_table_en_name"] for r in full[:1]}) < len(expected)
    paired = execute(db, queries, "D3", **targets,
                     value_1="000", value_2="001", value_3="010")
    assert {(r["code_table_en_name"], r["code_value"]) for r in paired} == {
        ("TEST_TRADE_STATUS", "000"), ("TEST_TRADE_STATUS", "001"),
        ("TEST_DEPOSIT_STATUS", "010")
    }, "不能把别的类型的同码值混入目标"
    bare = execute(db, queries, "D4", value_1="010", value_2="ABSENT")
    assert {r["code_table_en_name"] for r in bare} == {
        "TEST_TRADE_STATUS", "TEST_DEPOSIT_STATUS", "TEST_ROLE_TYPE"
    }
    assert all(r["code_value"] == "010" for r in bare)
    descriptions = dict(desc_pattern_1=contains_literal("结清"),
                        desc_pattern_2=contains_literal("100%_!"))
    reverse = execute(db, queries, "D5", **descriptions)
    assert {(r["code_table_en_name"], r["code_value"]) for r in reverse} == {
        ("TEST_DEPOSIT_STATUS", "010"), ("TEST_DEPOSIT_STATUS", "099"),
        ("TEST_LITERAL", "01")
    }
    scoped = execute(db, queries, "D6", **targets, **descriptions)
    assert {r["code_table_en_name"] for r in scoped} == {"TEST_DEPOSIT_STATUS"}
    missing = execute(db, queries, "D3", **targets,
                      value_1="ABSENT", value_2="MISSING", value_3="010")
    assert len(missing) == 1 and missing[0]["code_table_en_name"] == "TEST_DEPOSIT_STATUS"
    null = execute(db, queries, "D4", value_1="01", value_2="ABSENT")
    assert any(r["code_desc"] is None for r in null)


def check_boundaries(db, queries):
    """绑定输入不能改变条件；截断/筛选的计数必须保持原取数条件。"""
    hostile = "x' OR 1=1 --"
    assert not execute(db, queries, "T2", table_en_1=hostile, table_en_2="MISSING")
    assert not execute(db, queries, "D4", value_1=hostile, value_2="MISSING")
    assert not execute(db, queries, "D2", dict_en_1="MISSING", dict_en_2="ABSENT")
    # 只有明确目录请求才去掉筛选，仍只保留名称投影，不读取所有成员。
    for key in ("T1", "D1"):
        catalog = queries[key].split("\nWHERE ", 1)[0]
        result = db.execute(catalog).fetchall()
        assert result and all(len(row) == 2 for row in result)
        count = db.execute(f"SELECT COUNT(*) FROM ({catalog}) AS candidates").fetchone()[0]
        assert count == len(result)
    # 验证按文档要求替换 WHERE 后，可对配对/反查结果一次分组计数。
    for key, source, group, params in [
        ("T3", "table_schema", "table_name_en",
         dict(table_en_1="TEST_DEPOSIT", table_en_2="TEST_TRADE",
              field_1="STATUS", field_2="AMOUNT")),
        ("D3", "data_asset_code_kb", "code_table_en_name",
         dict(dict_en_1="TEST_TRADE_STATUS", dict_en_2="TEST_DEPOSIT_STATUS",
              value_1="010", value_2="011", value_3="099")),
        ("D4", "data_asset_code_kb", "code_table_en_name",
         dict(value_1="010", value_2="10")),
    ]:
        where = queries[key].split("\nWHERE ", 1)[1].split("\nORDER BY ", 1)[0]
        # source/group 仅来自上面固定白名单；用户输入仍全部绑定。
        sql = f"SELECT {group}, COUNT(*) AS total_rows FROM {source} WHERE {where} GROUP BY {group}"
        counts = {r[group]: r["total_rows"] for r in db.execute(sql, params)}
        result = execute(db, queries, key, **params)
        assert Counter(row[group] for row in result) == counts


def main():
    """执行一次聚合自检；失败直接报断言，成功仅说明本地模板通过。"""
    queries = load_queries()
    db = sample_database()
    try:
        check_tables(db, queries)
        check_dictionaries(db, queries)
        check_boundaries(db, queries)
    finally:
        db.close()
    print(f"通过：4 个 SKILL 注册名、{len(queries)} 个 SQL 模板及批量/边界样本。")
    print("范围：本地文档与 SQLite 逻辑 SQL；未验证 HiAgent 模型、真实方言和性能。")


if __name__ == "__main__":
    main()
