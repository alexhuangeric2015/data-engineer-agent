package com.dataengineer.agent.chat;

import reactor.core.publisher.Flux;

/**
 * 一种对话执行模式的边界。输入当前问题、历史语境和会话 ID；输出实时事件。
 * 不负责 HTTP、会话建档或持久化完整消息。
 */
public interface ChatModeExecutor {
    /** 本执行器处理的模式。 */
    ChatMode mode();

    /** 执行一个用户回合并流式返回计划、阶段和正文事件。 */
    Flux<ChatEvent> execute(String question, String input, String sessionId);
}
