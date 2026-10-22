package com.dataengineer.agent.knowledge;

/** 知识库检索片段；仅作候选定位。 */
public record KnowledgeHit(
        /** 命中知识文件名称。 */ String documentName,
        /** HiAgent 原始分段 ID。 */ String segmentId,
        /** HiAgent 原始检索分数。 */ Double score,
        /** 原始片段内容。 */ String content) {
}
