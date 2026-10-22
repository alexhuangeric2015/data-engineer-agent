package com.dataengineer.agent.chat;

import jakarta.validation.Valid;
import org.springframework.http.MediaType;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;

/** 对话 HTTP 入口，只校验请求并转发流，不直接访问 Mapper。 */
@RestController
@RequestMapping("/api/chat")
public class ChatController {
    /** 两模式共同的对话编排。 */
    private final ChatService service;

    /** 注入服务层。 */
    public ChatController(ChatService service) { this.service = service; }

    /** 用 POST + SSE 输出会话、计划、文本增量及完成/错误事件。 */
    @PostMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<ChatEvent>> stream(@Valid @RequestBody ChatRequest request) {
        return service.stream(request).map(event -> ServerSentEvent.<ChatEvent>builder()
                .event(event.type()).data(event).build());
    }
}
