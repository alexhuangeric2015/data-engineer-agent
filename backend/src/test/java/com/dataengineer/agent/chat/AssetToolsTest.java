package com.dataengineer.agent.chat;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import com.dataengineer.agent.asset.AssetMapper;
import com.dataengineer.agent.knowledge.KnowledgeGateway;
import com.dataengineer.agent.knowledge.KnowledgeHit;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** 验证 KB 定位先于数据库核验的硬门禁，避免模型直接猜表名查库。 */
class AssetToolsTest {
    /** 未检索知识库时，任何表名都不能直接送给 Mapper。 */
    @Test
    void rejectsDatabaseQueryBeforeKnowledgeHit() {
        AssetMapper mapper = mock(AssetMapper.class);
        AssetTools tools = new AssetTools(mock(KnowledgeGateway.class), mapper, new ObjectMapper(),
                new SkillPromptLoader());
        assertThrows(IllegalStateException.class, () -> tools.verifyTable("demo_table"));
        verifyNoInteractions(mapper);
    }

    /** 只允许原片段中出现的候选名称进入参数化数据库查询。 */
    @Test
    void verifiesOnlyLocatedCandidate() {
        KnowledgeGateway gateway = mock(KnowledgeGateway.class);
        AssetMapper mapper = mock(AssetMapper.class);
        when(gateway.search("TABLE", "用户表")).thenReturn(List.of(
                new KnowledgeHit("表结构", "segment-1", 0.9, "表英文名 demo_table，表中文名 用户表")));
        when(mapper.findTable("demo_table")).thenReturn(List.of(Map.of("table_name_en", "demo_table")));
        AssetTools tools = new AssetTools(gateway, mapper, new ObjectMapper(), new SkillPromptLoader());
        tools.readSkillReference("table-schema-kb.md");
        tools.readSkillReference("table-schema-db.md");
        tools.searchKnowledge("TABLE", "用户表");
        assertThrows(IllegalArgumentException.class, () -> tools.verifyTable("other_table"));
        assertTrue(tools.verifyTable("demo_table").contains("demo_table"));
        verify(mapper).findTable("demo_table");
    }
}
