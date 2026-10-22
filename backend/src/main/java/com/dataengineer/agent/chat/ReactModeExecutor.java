package com.dataengineer.agent.chat;

import com.alibaba.cloud.ai.graph.agent.ReactAgent;
import com.alibaba.cloud.ai.graph.exception.GraphRunnerException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.messages.AssistantMessage;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Flux;

/**
 * ReAct 模式：Spring AI Alibaba ReactAgent 在模型与工具之间自主循环。
 * 工具实例仅属于当前请求，且代码层强制“读参考→KB→DB”顺序。
 */
@Component
public class ReactModeExecutor implements ChatModeExecutor {
    /** 模式执行日志。 */
    private static final Logger log = LoggerFactory.getLogger(ReactModeExecutor.class);
    /** Spring AI Alibaba 使用的对话模型。 */
    private final ChatModel chatModel;
    /** V10 SKILL 主入口与 ReAct 模板。 */
    private final SkillPromptLoader prompts;
    /** 创建本轮独立工具。 */
    private final AssetToolsFactory toolsFactory;

    /** 装配 ReAct 执行依赖。 */
    public ReactModeExecutor(ChatModel chatModel, SkillPromptLoader prompts, AssetToolsFactory toolsFactory) {
        this.chatModel = chatModel;
        this.prompts = prompts;
        this.toolsFactory = toolsFactory;
    }

    /** 声明本执行器只接受 ReAct 请求。 */
    @Override
    public ChatMode mode() { return ChatMode.REACT; }

    /** Agent 的 assistant 消息逐段映射为 SSE delta。 */
    @Override
    public Flux<ChatEvent> execute(String question, String input, String sessionId) {
        return Flux.defer(() -> {
            log.info("[智能对话][ReAct开始] sessionId={}", sessionId);
            ReactAgent agent = ReactAgent.builder().name("data-asset-query-react")
                    .model(chatModel).systemPrompt(prompts.reactPrompt())
                    .methodTools(toolsFactory.create()).parallelToolExecution(false).build();
            try {
                return agent.streamMessages(input)
                        .filter(message -> message instanceof AssistantMessage
                                && message.getText() != null && !message.getText().isEmpty())
                        .map(message -> new ChatEvent("delta", message.getText(), sessionId));
            } catch (GraphRunnerException error) {
                return Flux.error(error);
            }
        });
    }
}
