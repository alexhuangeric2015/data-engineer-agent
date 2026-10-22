package com.dataengineer.agent.asset;

import java.util.List;
import java.util.Map;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 数据资产只读查询边界。输入为知识库命中的名称；输出是原始数据库行。
 * 不负责知识检索、模型解释、动态 SQL 拼接或业务表数据查询。
 */
@Mapper
public interface AssetMapper {
    /** 核验表名并返回该表的字段事实。 */
    List<Map<String, Object>> findTable(@Param("name") String name);
    /** 核验字典类型并返回原始码值；重复行不合并。 */
    List<Map<String, Object>> findDictionary(@Param("name") String name);
    /** 取得字典类型全范围统计，不能以单值匹配数冒充总量。 */
    Map<String, Object> dictionaryStats(@Param("name") String name);
}
