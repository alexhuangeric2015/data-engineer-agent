package com.dataengineer.agent.chat;

import java.util.List;

/** 模型提出的结构化计划；服务层仍需校验阶段、数量和执行顺序。 */
public record QueryPlan(
        /** 展示给用户的简短计划摘要。 */ String summary,
        /** 有序执行阶段，最多各含一个表或字典阶段。 */ List<PlanStep> steps) {

    /** 一个可执行的知识定位与数据库核验阶段。 */
    public record PlanStep(
            /** 允许查询的资产类别。 */ AssetKind kind,
            /** 该阶段传给对应 HiAgent 知识库的用户目标。 */ String query) {
    }
}
