package com.dataengineer.agent.chat;

import com.alibaba.cloud.ai.graph.agent.ReactAgent;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.messages.AssistantMessage;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.scheduler.Schedulers;

/**
 * 单轮对话编排。ReAct 直接调用工具；PlanAndExecute 先规划后由执行 Agent 调用同一组工具。
 * 两种模式均复用 V10 技能和数据库核验门禁，并向控制器返回实时事件。
 */
@Service
public class ChatService {
    /** 对话关键阶段日志。 */
    private static final Logger log = LoggerFactory.getLogger(ChatService.class);
    /** 一次会话服务的模型。 */
    private final ChatModel chatModel;
    /** 技能模板读取边界。 */
    private final SkillPromptLoader prompts;
    /** 每轮创建独立 KB 与 DB 工具。 */
    private final AssetToolsFactory toolsFactory;
    /** 对话历史持久化边界。 */
    private final ChatHistoryMapper historyMapper;
    /** 依赖注入由 Spring 完成；每轮工具实例在方法内创建以隔离候选。 */
    public ChatService(ChatModel chatModel, SkillPromptLoader prompts, AssetToolsFactory toolsFactory,
                       ChatHistoryMapper historyMapper) {
        this.chatModel = chatModel;
        this.prompts = prompts;
        this.toolsFactory = toolsFactory;
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

    /** 保持一次请求的会话、计划、知识与数据库执行顺序。 */
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

        // 先把会话 ID 推给浏览器，再执行可能耗时的规划、知识检索和模型输出。
        return Flux.just(new ChatEvent("session", "", currentSession))
                .concatWith(Flux.defer(() -> runAgent(request, currentSession, input)));
    }

    /** 规划模式先生成计划，两模式随后都执行同一组受限工具并输出文本增量。 */
    private Flux<ChatEvent> runAgent(ChatRequest request, String currentSession, String input) {
        // PlanAndExecute 先产出可见计划，随后仍经过与 ReAct 相同的 KB→DB 工具门禁。
        String plan = request.mode() == ChatMode.PLAN_AND_EXECUTE
                ? ChatClient.create(chatModel).prompt().user(prompts.planningPrompt(request.question())).call().content()
                : null;
        AssetTools tools = toolsFactory.create();
        ReactAgent agent = ReactAgent.builder().name("data-asset-query")
                .model(chatModel).systemPrompt(prompts.executionPrompt(request.mode(), plan))
                .methodTools(tools).parallelToolExecution(false).build();
        StringBuilder answer = new StringBuilder();
        Flux<ChatEvent> preface = plan == null
                ? Flux.empty()
                : Flux.just(new ChatEvent("plan", plan, currentSession));
        Flux<ChatEvent> tokens = Flux.defer(() -> {
            try { return agent.streamMessages(input); }
            catch (com.alibaba.cloud.ai.graph.exception.GraphRunnerException error) {
                return Flux.error(error);
            }
        })
                .filter(message -> message instanceof AssistantMessage && message.getText() != null
                        && !message.getText().isEmpty())
                .map(message -> {
                    String delta = message.getText();
                    answer.append(delta);
                    return new ChatEvent("delta", delta, currentSession);
                });
        return preface.concatWith(tokens).concatWith(Flux.defer(() -> {
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
