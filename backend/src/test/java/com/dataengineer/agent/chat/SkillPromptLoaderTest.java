package com.dataengineer.agent.chat;

import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.Test;

/** 验证 ReAct 读取 V10 唯一入口，计划模式读取自己的模板。 */
class SkillPromptLoaderTest {
    /** 两种路径各自加载需要的模板，阶段参考仍可按需读取。 */
    @Test
    void loadsPromptsForBothModes() {
        SkillPromptLoader loader = new SkillPromptLoader();
        String prompt = loader.reactPrompt();
        assertTrue(prompt.contains("data-asset-query"));
        assertTrue(prompt.contains("table_schema"));
        assertTrue(prompt.contains("data_asset_code_kb"));
        assertTrue(loader.planningPrompt("查找表字段").contains("查找表字段"));
        assertTrue(loader.summaryPrompt("问题", "计划", "证据").contains("证据"));
        assertTrue(loader.reference("dictionary-db.md").contains("data_asset_code_kb"));
    }
}
