package com.dataengineer.agent.chat;

/** SSE 事件，type 为 session、plan、delta、error 或 done。 */
public record ChatEvent(
        /** 前端处理事件的协议类型。 */ String type,
        /** 当前事件正文或提示。 */ String text,
        /** 所属会话 UUID。 */ String sessionId) {
}
