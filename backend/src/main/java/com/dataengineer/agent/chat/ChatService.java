package com.dataengineer.agent.chat;

import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.scheduler.Schedulers;

/**
 * 对话入口按模式选择独立执行器，并持久化最终回答。
 */
@Service
public class ChatService {
    /** 对话关键阶段日志。 */
    private static final Logger log = LoggerFactory.getLogger(ChatService.class);
    /** SSE 文本增量事件的协议类型。 */
    private static final String DELTA_EVENT = "delta";
    /** 两种模式的执行器注册表。 */
    private final Map<ChatMode, ChatModeExecutor> executors = new EnumMap<>(ChatMode.class);
    /** 技能模板读取边界。 */
    private final SkillPromptLoader prompts;
    /** 对话历史持久化边界。 */
    private final ChatHistoryMapper historyMapper;
    /** 由 Spring 注入执行器，启动时拒绝重复或缺失的模式实现。 */
    public ChatService(List<ChatModeExecutor> modeExecutors, SkillPromptLoader prompts,
                       ChatHistoryMapper historyMapper) {
        for (ChatModeExecutor executor : modeExecutors) {
            if (executors.putIfAbsent(executor.mode(), executor) != null) {
                throw new IllegalStateException("重复的对话模式执行器: " + executor.mode());
            }
        }
        if (executors.size() != ChatMode.values().length) {
            throw new IllegalStateException("对话模式执行器未全部注册");
        }
        this.prompts = prompts;
        this.historyMapper = historyMapper;
    }

    /** 构建冷流；订阅后才发生建会话、模型与工具调用。 */
    public Flux<ChatEvent> stream(ChatRequest request) {
        return Flux.defer(() -> execute(request))
                .subscribeOn(Schedulers.boundedElastic())
                .onErrorResume(error -> {
                    log.error("[智能对话][失败] mode={}, sessionId={}", request.mode(), request.sessionId(), error);
                    return Flux.just(new ChatEvent("error", error.getMessage(), request.sessionId()));
                });
    }

    /** 先返回会话 ID，再流式转发所选模式的计划、阶段和回答事件。 */
    private Flux<ChatEvent> execute(ChatRequest request) {
        String sessionId = request.sessionId();
        if (sessionId == null || sessionId.isBlank()) {
            sessionId = UUID.randomUUID().toString();
            historyMapper.insertSession(sessionId, request.mode().name());
        }
        final String currentSession = sessionId;
        List<Map<String, String>> history = historyMapper.listMessages(sessionId);
        String input = withHistory(history, request.question());
        log.info("[智能对话][开始] mode={}, sessionId={}, historyCount={}", request.mode(), sessionId, history.size());

        ChatModeExecutor executor = executors.get(request.mode());
        StringBuilder answer = new StringBuilder();

        // 执行器必须延迟到订阅后运行；只有成功完成的回答增量才写入历史。
        Flux<ChatEvent> events = Flux.defer(() -> executor.execute(request.question(), input, currentSession))
                .doOnNext(event -> {
                    if (DELTA_EVENT.equals(event.type())) answer.append(event.text());
                });
        return Flux.just(new ChatEvent("session", "", currentSession))
                .concatWith(events).concatWith(Flux.defer(() -> {
            historyMapper.insertMessage(currentSession, "USER", request.question());
            historyMapper.insertMessage(currentSession, "ASSISTANT", answer.toString());
            log.info("[智能对话][完成] mode={}, sessionId={}, answerLength={}", request.mode(), currentSession, answer.length());
            return Flux.just(new ChatEvent("done", "", currentSession));
        }));
    }

    /** 普通续问复用已保存的上下文；历史仅作语境，仍须重新满足本轮查询证据门槛。 */
    private String withHistory(List<Map<String, String>> history, String question) {
        if (history.isEmpty()) return question;
        StringBuilder context = new StringBuilder();
        for (Map<String, String> message : history) {
            context.append(message.get("role")).append(": ").append(message.get("content")).append('\n');
        }
        return prompts.historyPrompt(context.toString(), question);
    }
}
