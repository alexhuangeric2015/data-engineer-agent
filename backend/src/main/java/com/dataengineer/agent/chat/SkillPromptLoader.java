package com.dataengineer.agent.chat;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

/**
 * 读取仓库 V10 唯一 SKILL；四份参考由 Agent 工具按阶段读取。
 * 不从 Java 字符串定义提示词正文；技能文件缺失时明确失败。
 */
@Component
public class SkillPromptLoader {
    /** V10 技能包 classpath 根路径。 */
    private static final String SKILL_ROOT = "skills/data-asset-query/";
    /** 允许读取的四份业务参考，其他路径不能由模型指定。 */
    private static final java.util.Set<String> REFERENCES = java.util.Set.of(
            "table-schema-kb.md", "table-schema-db.md", "dictionary-kb.md", "dictionary-db.md");

    /** 将最新 SKILL 与 ReAct 模板组合为本轮系统提示词。 */
    public String reactPrompt() {
        String skill = read(SKILL_ROOT + "SKILL.md");
        return read("prompts/react.st").replace("{skill}", skill);
    }

    /** 只返回 V10 技能包中明确列出的阶段参考。 */
    public String reference(String fileName) {
        if (!REFERENCES.contains(fileName)) {
            throw new IllegalArgumentException("未知 SKILL 参考文件: " + fileName);
        }
        return read(SKILL_ROOT + "references/" + fileName);
    }

    /** 为 PlanAndExecute 生成仅用于规划的提示词。 */
    public String planningPrompt(String question) {
        return read("prompts/plan.st").replace("{skill}", read(SKILL_ROOT + "SKILL.md"))
                .replace("{question}", question);
    }

    /** 从 HiAgent 原片段提取待核验名称；模型只可提出候选。 */
    public String candidatePrompt(AssetKind kind, String question, String evidence, String hits) {
        return read("prompts/candidates.st").replace("{kind}", kind.name())
                .replace("{question}", question).replace("{evidence}", evidence)
                .replace("{hits}", hits);
    }

    /** 将数据库结果整理为用户回答；正文规则仅在 .st 中定义。 */
    public String summaryPrompt(String question, String plan, String evidence) {
        return read("prompts/summary.st").replace("{question}", question)
                .replace("{plan}", plan).replace("{evidence}", evidence);
    }

    /** 组装续问语境，规则文字仅存于 .st。 */
    public String historyPrompt(String history, String question) {
        return read("prompts/history.st").replace("{history}", history).replace("{question}", question);
    }

    /** 读取 UTF-8 文件，保留原技能正文。 */
    private String read(String path) {
        try { return new ClassPathResource(path).getContentAsString(StandardCharsets.UTF_8); }
        catch (IOException e) { throw new IllegalStateException("SKILL 或提示词文件不可读: " + path, e); }
    }
}
