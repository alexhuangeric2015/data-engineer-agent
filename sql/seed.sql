-- 本地开发与集成测试数据。
-- 表结构由 Alembic 管理；本脚本只写入数据，并且可以重复执行。

INSERT INTO dictionary_type (
    type_code, type_name, aliases, source_system, status, version, search_text
)
VALUES
    ('IDENTITY_DOCUMENT_TYPE', '证件类型', ARRAY['证件类别', '证件种类'], '本地测试数据', 'ACTIVE', '1.0', '证件类型 证件类别 证件种类 身份证明'),
    ('GENDER', '性别', ARRAY['性别类型'], '本地测试数据', 'ACTIVE', '1.0', '性别 性别类型'),
    ('ORDER_STATUS', '订单状态', ARRAY['订单生命周期状态'], '本地测试数据', 'ACTIVE', '1.0', '订单状态 订单生命周期状态')
ON CONFLICT (source_system, type_code) DO UPDATE SET
    type_name = EXCLUDED.type_name,
    aliases = EXCLUDED.aliases,
    status = EXCLUDED.status,
    version = EXCLUDED.version,
    search_text = EXCLUDED.search_text,
    updated_at = CURRENT_TIMESTAMP;

INSERT INTO dictionary_item (
    dictionary_type_id, item_code, item_name, aliases, description,
    status, sort_order, search_text
)
SELECT type_record.id, seed.item_code, seed.item_name, seed.aliases,
       seed.description, seed.status, seed.sort_order, seed.search_text
FROM dictionary_type AS type_record
JOIN (
    VALUES
        ('IDENTITY_DOCUMENT_TYPE', '01', '身份证', ARRAY['居民身份证']::TEXT[], '居民身份证件', 'ACTIVE', 10, '身份证 居民身份证 身份证明'),
        ('IDENTITY_DOCUMENT_TYPE', '02', '军官证', ARRAY['军人证件']::TEXT[], '军官身份证明', 'ACTIVE', 20, '军官证 军人证件 身份证明'),
        ('IDENTITY_DOCUMENT_TYPE', '03', '护照', ARRAY['Passport']::TEXT[], '出入境身份证件', 'ACTIVE', 30, '护照 Passport 出入境 身份证明'),
        ('IDENTITY_DOCUMENT_TYPE', '04', '驾驶证', ARRAY['驾照']::TEXT[], '机动车驾驶证', 'ACTIVE', 40, '驾驶证 驾照 身份证明'),
        ('IDENTITY_DOCUMENT_TYPE', '99', '旧版证件', ARRAY[]::TEXT[], '已停止使用的测试项', 'INACTIVE', 99, '旧版证件 停用'),
        ('GENDER', '01', '男', ARRAY['男性']::TEXT[], '男性', 'ACTIVE', 10, '男 男性'),
        ('GENDER', '02', '女', ARRAY['女性']::TEXT[], '女性', 'ACTIVE', 20, '女 女性'),
        ('GENDER', '00', '未知', ARRAY['未说明']::TEXT[], '性别未知或未说明', 'ACTIVE', 30, '未知 未说明'),
        ('ORDER_STATUS', 'PENDING', '待支付', ARRAY['等待支付']::TEXT[], '订单已经创建但尚未支付', 'ACTIVE', 10, '待支付 等待支付'),
        ('ORDER_STATUS', 'PAID', '已支付', ARRAY['支付成功']::TEXT[], '订单已经支付成功', 'ACTIVE', 20, '已支付 支付成功'),
        ('ORDER_STATUS', 'CANCELLED', '已取消', ARRAY['取消']::TEXT[], '订单已经取消', 'ACTIVE', 30, '已取消 取消'),
        ('ORDER_STATUS', 'UNKNOWN', '未知', ARRAY[]::TEXT[], '订单状态未知', 'ACTIVE', 40, '未知 订单状态')
) AS seed(
    type_code, item_code, item_name, aliases, description,
    status, sort_order, search_text
) ON type_record.type_code = seed.type_code
   AND type_record.source_system = '本地测试数据'
ON CONFLICT (dictionary_type_id, item_code) DO UPDATE SET
    item_name = EXCLUDED.item_name,
    aliases = EXCLUDED.aliases,
    description = EXCLUDED.description,
    status = EXCLUDED.status,
    sort_order = EXCLUDED.sort_order,
    search_text = EXCLUDED.search_text,
    updated_at = CURRENT_TIMESTAMP;
