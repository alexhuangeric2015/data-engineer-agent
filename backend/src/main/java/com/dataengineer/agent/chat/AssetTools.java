package com.dataengineer.agent.chat;

import com.dataengineer.agent.asset.AssetMapper;
import com.dataengineer.agent.knowledge.KnowledgeGateway;
import com.dataengineer.agent.knowledge.KnowledgeHit;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.tool.annotation.Tool;

/**
 * 单轮 Agent 工具边界。先登记 HiAgent 命中片段，后续数据库查询仅接受片段中出现的候选名称。
 * 每轮创建新实例，避免不同用户之间共享候选状态。
 */
public class AssetTools {
    /** 工具审计日志。 */
    private static final Logger log = LoggerFactory.getLogger(AssetTools.class);
    /** 结构 KB 阶段参考。 */
    private static final String TABLE_KB_REFERENCE = "table-schema-kb.md";
    /** 结构 DB 阶段参考。 */
    private static final String TABLE_DB_REFERENCE = "table-schema-db.md";
    /** 字典 KB 阶段参考。 */
    private static final String DICTIONARY_KB_REFERENCE = "dictionary-kb.md";
    /** 字典 DB 阶段参考。 */
    private static final String DICTIONARY_DB_REFERENCE = "dictionary-db.md";
    /** 当前轮次的知识库检索入口。 */
    private final KnowledgeGateway gateway;
    /** 仅访问已声明的两张事实表。 */
    private final AssetMapper mapper;
    /** 工具响应序列化器。 */
    private final ObjectMapper objectMapper;
    /** 本轮按需读取的 V10 参考。 */
    private final Set<String> loadedReferences = ConcurrentHashMap.newKeySet();
    /** V10 技能文件读取边界。 */
    private final SkillPromptLoader prompts;
    /** 表结构 KB 原片段。 */
    private volatile List<KnowledgeHit> tableHits = List.of();
    /** 字典 KB 原片段。 */
    private volatile List<KnowledgeHit> dictionaryHits = List.of();

    /** 装配本轮工具依赖。 */
    public AssetTools(KnowledgeGateway gateway, AssetMapper mapper, ObjectMapper objectMapper,
                      SkillPromptLoader prompts) {
        this.gateway = gateway;
        this.mapper = mapper;
        this.objectMapper = objectMapper;
        this.prompts = prompts;
    }

    /** 按 V10 当前业务阶段读取指定参考；未列入包的路径被拒绝。 */
    @Tool(description = "读取 V10 SKILL 阶段参考。fileName 只能是 table-schema-kb.md、table-schema-db.md、dictionary-kb.md、dictionary-db.md。")
    public String readSkillReference(String fileName) {
        String content = prompts.reference(fileName);
        loadedReferences.add(fileName);
        log.info("[技能参考][已读取] fileName={}", fileName);
        return content;
    }

    /** 检索 HiAgent 的 TABLE 或 DICTIONARY 知识库，只返回候选片段。 */
    @Tool(description = "先在 HiAgent 知识库定位候选。kind 只能为 TABLE 或 DICTIONARY；query 是用户目标。")
    public String searchKnowledge(String kind, String query) {
        requireReference("TABLE".equals(kind) ? TABLE_KB_REFERENCE : DICTIONARY_KB_REFERENCE);
        List<KnowledgeHit> hits = gateway.search(kind, query);
        if ("TABLE".equals(kind)) tableHits = hits;
        if ("DICTIONARY".equals(kind)) dictionaryHits = hits;
        return json(Map.of("source", "HiAgent 知识库，仅用于定位", "hits", hits));
    }

    /** 对知识库片段中出现的表名进行 MySQL 精确核验。 */
    @Tool(description = "用 MySQL table_schema 核验已由知识库命中的表英文名或中文名，返回表及字段原始事实。")
    public String verifyTable(String name) {
        requireReference(TABLE_DB_REFERENCE);
        requireHit(tableHits, name, "表结构");
        List<Map<String, Object>> rows = mapper.findTable(name);
        log.info("[资产核验][表字段] name={}, rowCount={}", name, rows.size());
        return json(Map.of("source", "table_schema", "rows", rows));
    }

    /** 对知识库片段中出现的字典名进行 MySQL 精确核验并统计原始行。 */
    @Tool(description = "用 MySQL data_asset_code_kb 核验已由知识库命中的字典类型名，返回全部原始码值和 SQL 统计。")
    public String verifyDictionary(String name) {
        requireReference(DICTIONARY_DB_REFERENCE);
        requireHit(dictionaryHits, name, "字典");
        List<Map<String, Object>> rows = mapper.findDictionary(name);
        Map<String, Object> stats = mapper.dictionaryStats(name);
        log.info("[资产核验][字典码值] name={}, rowCount={}", name, rows.size());
        return json(Map.of("source", "data_asset_code_kb", "rows", rows, "stats", stats));
    }

    /** 防止模型跳过知识库，或把未命中的名称直接交给数据库。 */
    private void requireHit(List<KnowledgeHit> hits, String name, String kind) {
        if (name == null || name.isBlank() || hits.stream().noneMatch(hit -> hit.content() != null && hit.content().contains(name))) {
            throw new IllegalArgumentException(kind + "名称未在本轮知识库片段中定位，禁止数据库查询");
        }
    }

    /** 代码层确保阶段参考已经实际加载。 */
    private void requireReference(String fileName) {
        if (!loadedReferences.contains(fileName)) {
            throw new IllegalStateException("当前阶段尚未读取 SKILL 参考: " + fileName);
        }
    }

    /** 保留原始结果结构供 Agent 解释，不用模型编造计数。 */
    private String json(Object value) {
        try { return objectMapper.writeValueAsString(value); }
        catch (JsonProcessingException e) { throw new IllegalStateException("资产查询结果序列化失败", e); }
    }
}
