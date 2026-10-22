package com.dataengineer.agent.chat;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

/** 前端发起的一次对话请求。 */
public record ChatRequest(
        /** 现有会话 UUID；首次可以为 null。 */ String sessionId,
        /** 用户自然语言问题，不得为空。 */ @NotBlank String question,
        /** 本轮执行模式。 */ @NotNull ChatMode mode) {
}
