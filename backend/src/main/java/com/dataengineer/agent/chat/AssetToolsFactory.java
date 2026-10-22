package com.dataengineer.agent.chat;

import com.dataengineer.agent.asset.AssetMapper;
import com.dataengineer.agent.knowledge.KnowledgeGateway;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Component;

/**
 * 为每轮对话创建独立工具实例，使 KB 候选门禁状态不会跨用户共享。
 * 只装配知识库、资产库和 JSON 边界，不负责模型或会话持久化。
 */
@Component
public class AssetToolsFactory {
    /** HiAgent 知识库边界。 */
    private final KnowledgeGateway knowledgeGateway;
    /** MySQL 资产事实边界。 */
    private final AssetMapper assetMapper;
    /** 工具结果序列化器。 */
    private final ObjectMapper objectMapper;
    /** 按阶段提供当前 V10 参考。 */
    private final SkillPromptLoader prompts;

    /** 装配工具生命周期所需的三个依赖。 */
    public AssetToolsFactory(KnowledgeGateway knowledgeGateway, AssetMapper assetMapper, ObjectMapper objectMapper,
                             SkillPromptLoader prompts) {
        this.knowledgeGateway = knowledgeGateway;
        this.assetMapper = assetMapper;
        this.objectMapper = objectMapper;
        this.prompts = prompts;
    }

    /** 新请求必须得到新工具，不能继承上一轮 KB 命中。 */
    public AssetTools create() {
        return new AssetTools(knowledgeGateway, assetMapper, objectMapper, prompts);
    }
}
