"""检查 HiAgent 文档契约与逻辑 SQL；不连接用户的数据库或 HiAgent。"""

import re
import sqlite3
from pathlib import Path

# 按本文件定位文档，便于从不同工作目录运行；只加载用户授权的 HiAgent 文件。
DOCS = Path(__file__).resolve().parents[1]
# 保持注册名称不变，防止替换文档后平台仍绑定旧名称。
SKILL_NAMES = (
    "table-schema-query-kb",
    "table-schema-query-db",
    "dictionary-query-kb",
    "dictionary-query-db",
)


def read_contracts():
    """读取运行文档并检查入口；不模拟模型遵守提示词的能力。"""
    prompt = (DOCS / "agent-prompt" / "数据建模师.md").read_text(encoding="utf-8")
    skills = {}
    for name in SKILL_NAMES:
        content = (DOCS / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        assert content.startswith(f"---\nname: {name}\ndescription: "), name
        assert name in prompt, f"主提示词缺少 {name}"
        skills[name] = content

    # 这些旧规则会绕过 DB 或把局部返回夸大成全量，不能再次出现在运行正文。
    combined = prompt + "\n" + "\n".join(skills.values())
    for obsolete in ("数据库表索引.csv", "table-structure-query", "完整性 =", "直接给出即可，无需"):
        assert obsolete not in combined, f"旧规则残留：{obsolete}"
    assert "没有相似字段时" in prompt and "所有资产事实必须有数据库证据" in prompt
    assert "DB 最多 6 次" in prompt and "不代表工具返回完整" in prompt
    assert "数据库表 `table_schema`" in prompt and "数据库表 `data_asset_code_kb`" in prompt
    return skills


def query_templates(content):
    """提取原文 SQL，保证测试随文档修改而变化，不复制另一份查询实现。"""
    queries = re.findall(r"```sql\n(.*?)```", content, flags=re.DOTALL)
    assert queries, "DB SKILL 缺少可校验的查询模板"
    for query in queries:
        assert query.lstrip().startswith("SELECT"), "逻辑模板必须是只读查询"
        assert not re.search(r"\bLIMIT\b", query, re.IGNORECASE), "全量模板不能静默截断"
    return queries


def seed_samples(db):
    """仅建立内存样本，包含重复字段名、歧义类型和冲突描述。"""
    db.execute("""CREATE TABLE table_schema (
        table_name_en TEXT, table_name_cn TEXT, column_name TEXT,
        column_cn_name TEXT, column_type TEXT, is_key TEXT, is_related TEXT,
        related_column_en TEXT, related_column_cn TEXT, biz_desc TEXT)""")
    db.executemany("INSERT INTO table_schema VALUES (?,?,?,?,?,?,?,?,?,?)", [
        ("TEST_TRADE", "测试交易表", "STATUS", "交易状态", "TEXT", "否", "否", None, None, "状态描述"),
        ("TEST_TRADE", "测试交易表", "TRADE_ID", "交易编号", "TEXT", "是", "否", None, None, None),
        ("TEST_OTHER", "测试其他表", "STATUS", "其他状态", "TEXT", "否", "否", None, None, "其他表字段"),
    ])
    db.execute("""CREATE TABLE data_asset_code_kb (
        code_table_en_name TEXT, code_table_cn_name TEXT,
        code_value TEXT, code_desc TEXT)""")
    rows = [("TEST_STATUS", "测试状态", f"{i:03}", f"测试含义{i}") for i in range(301)]
    rows.extend([
        ("TEST_STATUS", "测试状态", "010", "冲突描述"),
        ("TEST_ROLE", "角色类型", "010", "仅属于角色候选的含义"),
        ("TEST_PERCENT", "测试百分比", "P", "收益100%"),
        ("TEST_PERCENT", "测试百分比", "Q", "收益1000"),
    ])
    db.executemany("INSERT INTO data_asset_code_kb VALUES (?,?,?,?)", rows)


def check_tables(db, queries):
    """验证当前表隔离、候选存在性与中文名称精确匹配。"""
    assert len(queries) == 4, "结构 DB 查询模式发生变化，请同步检查"
    exact, candidates, chinese, count = queries
    rows = db.execute(exact, {"table_name_en": "TEST_TRADE"}).fetchall()
    assert len(rows) == 2 and all(row[0] == "TEST_TRADE" for row in rows)
    assert {row[2] for row in rows} == {"STATUS", "TRADE_ID"}
    verified = db.execute(candidates, {
        "candidate_1": "TEST_TRADE", "candidate_2": "MISSING", "candidate_3": "TEST_OTHER",
    }).fetchall()
    assert {row[0] for row in verified} == {"TEST_TRADE", "TEST_OTHER"}
    assert not db.execute(chinese, {"table_name_cn": "交易"}).fetchall()
    assert db.execute(count, {"table_name_en": "TEST_TRADE"}).fetchone()[0] == len(rows)
    assert not db.execute(exact, {"table_name_en": "' OR 1=1 --"}).fetchall()


def check_dictionaries(db, queries):
    """验证全量、前导零、冲突保留以及文字值不会扩大查询范围。"""
    assert len(queries) == 7, "字典 DB 查询模式发生变化，请同步检查"
    candidates, chinese, all_codes, one_code, by_value, by_desc, count = queries
    verified = db.execute(candidates, {
        "candidate_1": "TEST_STATUS", "candidate_2": "MISSING", "candidate_3": "TEST_ROLE",
    }).fetchall()
    assert {row[0] for row in verified} == {"TEST_STATUS", "TEST_ROLE"}
    assert not db.execute(chinese, {"code_table_cn_name": "身份类型"}).fetchall()
    rows = db.execute(all_codes, {"code_table_en_name": "TEST_STATUS"}).fetchall()
    assert len(rows) == 302 and len({row[2] for row in rows}) == 301
    assert db.execute(count, {"code_table_en_name": "TEST_STATUS"}).fetchone()[0] == len(rows)
    matched = db.execute(one_code, {"code_table_en_name": "TEST_STATUS", "code_value": "010"}).fetchall()
    assert len(matched) == 2 and all(row[2] == "010" for row in matched)
    assert len({row[3] for row in matched}) == 2, "冲突描述不得静默合并"
    assert not db.execute(one_code, {"code_table_en_name": "TEST_STATUS", "code_value": "10"}).fetchall()
    assert not db.execute(one_code, {"code_table_en_name": "TEST_STATUS", "code_value": "' OR 1=1 --"}).fetchall()
    assert {row[0] for row in db.execute(by_value, {"code_value": "010"})} == {"TEST_STATUS", "TEST_ROLE"}
    assert db.execute(by_desc, {"code_desc_pattern": "%100!%%"}).fetchall() == [
        ("TEST_PERCENT", "测试百分比", "P", "收益100%"),
    ]


def main():
    """检查文档后执行隔离查询；失败直接暴露断言，不伪称平台已验收。"""
    skills = read_contracts()
    db = sqlite3.connect(":memory:")
    try:
        seed_samples(db)
        check_tables(db, query_templates(skills["table-schema-query-db"]))
        check_dictionaries(db, query_templates(skills["dictionary-query-db"]))
    finally:
        db.close()
    print("[HiAgent文档校验] 通过：4 个注册名称、11 个 SQL 模板及边界样本；未执行平台实测。")


if __name__ == "__main__":
    main()
