package com.dataengineer.agent.chat;

/** 对话执行模式，两个模式最终都向浏览器逐段输出。 */
public enum ChatMode {
    /** ReAct 自主决定下一次知识库或数据库工具调用。 */
    REACT,
    /** 先生成计划，再由执行 Agent 按计划调用工具。 */
    PLAN_AND_EXECUTE
}
