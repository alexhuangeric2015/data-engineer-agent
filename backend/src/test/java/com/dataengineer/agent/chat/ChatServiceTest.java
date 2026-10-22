package com.dataengineer.agent.chat;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.List;
import org.junit.jupiter.api.Test;
import reactor.core.publisher.Flux;

/** 验证模式分派和 SSE 事件保留，避免计划模式再次落回 ReAct。 */
class ChatServiceTest {
    /** 计划请求只运行计划执行器，并保留计划、阶段和增量事件。 */
    @Test
    void dispatchesPlanRequestToPlanExecutor() {
        ChatHistoryMapper history = mock(ChatHistoryMapper.class);
        when(history.listMessages("session-1")).thenReturn(List.of());
        ChatModeExecutor react = new StubExecutor(ChatMode.REACT, "react");
        ChatModeExecutor plan = new StubExecutor(ChatMode.PLAN_AND_EXECUTE, "plan");
        ChatService service = new ChatService(List.of(react, plan), new SkillPromptLoader(), history);

        List<ChatEvent> events = service.stream(new ChatRequest("session-1", "查询用户表", ChatMode.PLAN_AND_EXECUTE))
                .collectList().block();

        assertEquals(List.of("session", "plan", "stage", "delta", "done"),
                events.stream().map(ChatEvent::type).toList());
        assertEquals("plan", events.get(3).text());
        assertTrue(events.stream().noneMatch(event -> "react".equals(event.text())));
        verify(history).insertMessage("session-1", "ASSISTANT", "plan");
    }

    /** 只模拟模式边界，不模拟真实模型、知识库或数据库。 */
    private record StubExecutor(ChatMode mode, String answer) implements ChatModeExecutor {
        /** 返回能看出实际执行分支的事件序列。 */
        @Override
        public Flux<ChatEvent> execute(String question, String input, String sessionId) {
            if (mode == ChatMode.REACT) return Flux.just(new ChatEvent("delta", answer, sessionId));
            return Flux.just(new ChatEvent("plan", "结构化计划", sessionId),
                    new ChatEvent("stage", "表已核验", sessionId), new ChatEvent("delta", answer, sessionId));
        }
    }
}
