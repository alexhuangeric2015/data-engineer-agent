package com.dataengineer.agent.chat;

/** 计划中可执行的数据资产阶段；计划不能指定任意表或 SQL。 */
public enum AssetKind {
    /** 先定位并核验 table_schema 中的表与字段。 */
    TABLE,
    /** 先定位并核验 data_asset_code_kb 中的字典与原始码值。 */
    DICTIONARY
}
