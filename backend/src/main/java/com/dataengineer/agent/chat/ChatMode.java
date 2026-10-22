package com.dataengineer.agent.chat;

/** 对话执行模式，两个模式最终都向浏览器逐段输出。 */
public enum ChatMode {
    /** ReAct 自主决定下一次知识库或数据库工具调用。 */
    REACT,
    /** 生成受限 JSON 计划后，由 Java 按阶段执行知识检索和数据库核验。 */
    PLAN_AND_EXECUTE
}
