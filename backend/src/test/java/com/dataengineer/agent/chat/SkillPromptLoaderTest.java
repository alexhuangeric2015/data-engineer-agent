package com.dataengineer.agent.chat;

import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.Test;

/** 验证打包后两种模式读取 V10 唯一入口，阶段参考仍可按需读取。 */
class SkillPromptLoaderTest {
    /** 两个执行模式均包含实际业务字段与 V10 技能入口。 */
    @Test
    void loadsCurrentSkillForBothModes() {
        SkillPromptLoader loader = new SkillPromptLoader();
        for (ChatMode mode : ChatMode.values()) {
            String prompt = loader.executionPrompt(mode, "核验计划");
            assertTrue(prompt.contains("data-asset-query"));
            assertTrue(prompt.contains("table_schema"));
            assertTrue(prompt.contains("data_asset_code_kb"));
        }
        assertTrue(loader.reference("dictionary-db.md").contains("data_asset_code_kb"));
    }
}
