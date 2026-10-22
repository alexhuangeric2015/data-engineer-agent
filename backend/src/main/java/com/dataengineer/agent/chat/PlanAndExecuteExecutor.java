package com.dataengineer.agent.chat;

import com.dataengineer.agent.knowledge.KnowledgeHit;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.ArrayList;
import java.util.EnumSet;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Flux;

/**
 * PlanAndExecute 模式：模型只生成受限结构化计划及候选名；Java 按阶段确定性执行。
 * 每阶段固定“读 SKILL 参考→HiAgent KB→MySQL 核验”，最后由模型流式整理 DB 证据。
 * 不复用 ReactAgent 的工具循环，也不允许计划携带 SQL 或任意工具名。
 */
@Component
public class PlanAndExecuteExecutor implements ChatModeExecutor {
    /** 关键阶段和分支日志。 */
    private static final Logger log = LoggerFactory.getLogger(PlanAndExecuteExecutor.class);
    /** 每轮最多一个表阶段和一个字典阶段。 */
    private static final int MAX_PLAN_STEPS = 2;
    /** 与 V10 SKILL 一致的可见数据库调用上限。 */
    private static final int MAX_DB_CALLS = 8;
    /** 每阶段最多核验的 KB 候选数量。 */
    private static final int MAX_CANDIDATES = 5;
    /** 计划、候选提取和流式总结共用模型。 */
    private final ChatModel chatModel;
    /** 所有提示词正文和 SKILL 参考的文件入口。 */
    private final SkillPromptLoader prompts;
    /** 一次回合内共享 KB 命中门禁的工具实例来源。 */
    private final AssetToolsFactory toolsFactory;
    /** 严格解析模型提出的 JSON 与工具证据。 */
    private final ObjectMapper objectMapper;

    /** 四个依赖分别对应模型、规则、受限工具与结构化数据。 */
    public PlanAndExecuteExecutor(ChatModel chatModel, SkillPromptLoader prompts,
                                  AssetToolsFactory toolsFactory, ObjectMapper objectMapper) {
        this.chatModel = chatModel;
        this.prompts = prompts;
        this.toolsFactory = toolsFactory;
        this.objectMapper = objectMapper;
    }

    /** 声明本执行器只接受 PlanAndExecute 请求。 */
    @Override
    public ChatMode mode() { return ChatMode.PLAN_AND_EXECUTE; }

    /** 先发计划，再逐阶段发状态，最后流式发答案。 */
    @Override
    public Flux<ChatEvent> execute(String question, String input, String sessionId) {
        return Flux.defer(() -> {
            QueryPlan plan = createPlan(question);
            AssetTools tools = toolsFactory.create();
            ExecutionState state = new ExecutionState();
            String planText = describePlan(plan);
            log.info("[智能对话][计划生成] sessionId={}, steps={}", sessionId, plan.steps().size());

            Flux<ChatEvent> stages = Flux.fromIterable(plan.steps())
                    .concatMap(step -> Flux.defer(() -> Flux.just(
                            new ChatEvent("stage", executeStep(step, question, tools, state), sessionId))));
            Flux<ChatEvent> summary = Flux.defer(() -> {
                String prompt = prompts.summaryPrompt(input, planText, json(state.evidence));
                return ChatClient.create(chatModel).prompt().user(prompt).stream().content()
                        .filter(part -> part != null && !part.isEmpty())
                        .map(part -> new ChatEvent("delta", part, sessionId));
            });
            return Flux.just(new ChatEvent("plan", planText, sessionId))
                    .concatWith(stages).concatWith(summary);
        });
    }

    /** 解析并校验模型计划，拒绝重复阶段、倒序和未声明类别。 */
    private QueryPlan createPlan(String question) {
        String raw = ChatClient.create(chatModel).prompt().user(prompts.planningPrompt(question))
                .call().content();
        try {
            QueryPlan plan = objectMapper.readValue(raw, QueryPlan.class);
            if (plan.steps() == null || plan.steps().isEmpty() || plan.steps().size() > MAX_PLAN_STEPS) {
                throw new IllegalArgumentException("计划阶段数量不符合约束");
            }
            EnumSet<AssetKind> seen = EnumSet.noneOf(AssetKind.class);
            for (QueryPlan.PlanStep step : plan.steps()) {
                if (step == null || step.kind() == null || step.query() == null || step.query().isBlank()
                        || !seen.add(step.kind())) {
                    throw new IllegalArgumentException("计划阶段缺少目标或重复");
                }
                if (step.kind() == AssetKind.TABLE && seen.contains(AssetKind.DICTIONARY)) {
                    throw new IllegalArgumentException("关联查询必须先核验表字段");
                }
            }
            return plan;
        } catch (JsonProcessingException error) {
            throw new IllegalStateException("规划模型未返回可解析的结构化计划", error);
        }
    }

    /** 执行一个确定性阶段；技术失败保留已完成证据，不重复查询。 */
    private String executeStep(QueryPlan.PlanStep step, String question, AssetTools tools, ExecutionState state) {
        AssetKind kind = step.kind();
        if (state.blocked) return kind + "：上游尚未确认，本阶段未执行";
        log.info("[智能对话][阶段开始] kind={}, queryLength={}", kind, step.query().length());
        try {
            tools.readSkillReference(kbReference(kind));
            tools.searchKnowledge(kind.name(), step.query());
            List<KnowledgeHit> hits = tools.locatedHits(kind);
            if (hits.isEmpty()) return stop(state, kind + "：知识库没有可核验的候选");

            List<String> names = extractCandidates(kind, question, hits, state.evidence);
            if (names.isEmpty()) return stop(state, kind + "：命中片段没有明确对象标识");
            tools.readSkillReference(dbReference(kind));
            int verified = verifyCandidates(kind, names, tools, state);
            if (verified == 0) return stop(state, kind + "：数据库没有核验到候选");
            if (names.size() > 1) state.blocked = true;
            String status = kind + "：已核验 " + verified + " 个候选";
            state.evidence.add(status);
            log.info("[智能对话][阶段完成] kind={}, verified={}, dbCalls={}", kind, verified, state.dbCalls);
            return status;
        } catch (RuntimeException error) {
            log.error("[智能对话][阶段失败] kind={}", kind, error);
            return stop(state, kind + "：执行失败，" + error.getMessage());
        }
    }

    /** 只取知识片段中逐字出现的标识；候选仍需数据库证明。 */
    private List<String> extractCandidates(AssetKind kind, String question, List<KnowledgeHit> hits,
                                           List<String> priorEvidence) {
        String raw = ChatClient.create(chatModel).prompt().user(
                prompts.candidatePrompt(kind, question, json(priorEvidence), json(hits))).call().content();
        try {
            CandidateNames candidates = objectMapper.readValue(raw, CandidateNames.class);
            if (candidates.names() == null) return List.of();
            return candidates.names().stream().filter(name -> name != null && !name.isBlank())
                    .filter(name -> hits.stream().anyMatch(hit -> hit.content() != null
                            && hit.content().contains(name)))
                    .distinct().limit(MAX_CANDIDATES).toList();
        } catch (JsonProcessingException error) {
            throw new IllegalStateException("候选提取结果不是可解析的 JSON", error);
        }
    }

    /** 在数据库预算内逐个核验；字典明细与统计各算一次查询。 */
    private int verifyCandidates(AssetKind kind, List<String> names, AssetTools tools, ExecutionState state) {
        int verified = 0;
        int cost = kind == AssetKind.TABLE ? 1 : 2;
        for (String name : names) {
            if (state.dbCalls + cost > MAX_DB_CALLS) {
                state.evidence.add("数据库调用额度已用尽，剩余候选未核验");
                break;
            }
            state.dbCalls += cost;
            String result = kind == AssetKind.TABLE ? tools.verifyTable(name) : tools.verifyDictionary(name);
            JsonNode rows;
            try { rows = objectMapper.readTree(result).path("rows"); }
            catch (JsonProcessingException error) { throw new IllegalStateException("数据库证据无法解析", error); }
            state.evidence.add(result);
            if (rows.isArray() && !rows.isEmpty()) verified++;
        }
        return verified;
    }

    /** 停止当前依赖链并保留可解释的缺口。 */
    private String stop(ExecutionState state, String reason) {
        state.blocked = true;
        state.evidence.add(reason);
        return reason;
    }

    /** KB 参考与资产类别一一对应。 */
    private String kbReference(AssetKind kind) {
        return kind == AssetKind.TABLE ? "table-schema-kb.md" : "dictionary-kb.md";
    }

    /** DB 参考与资产类别一一对应。 */
    private String dbReference(AssetKind kind) {
        return kind == AssetKind.TABLE ? "table-schema-db.md" : "dictionary-db.md";
    }

    /** 将经过校验的执行顺序展示给用户。 */
    private String describePlan(QueryPlan plan) {
        StringBuilder text = new StringBuilder(plan.summary() == null ? "数据资产核验计划" : plan.summary());
        for (int index = 0; index < plan.steps().size(); index++) {
            QueryPlan.PlanStep step = plan.steps().get(index);
            text.append('\n').append(index + 1).append(". ").append(step.kind()).append("：")
                    .append(step.query());
        }
        return text.toString();
    }

    /** 序列化阶段证据给模型，保留原始码值与 SQL 统计。 */
    private String json(Object value) {
        try { return objectMapper.writeValueAsString(value); }
        catch (JsonProcessingException error) { throw new IllegalStateException("计划阶段证据序列化失败", error); }
    }

    /** 一次计划执行的业务状态，包含证据、数据库预算和上游确认门禁。 */
    private static class ExecutionState {
        /** 已核验 DB 原始响应及未完成原因。 */
        private final List<String> evidence = new ArrayList<>();
        /** 当前回合显式数据库查询次数。 */
        private int dbCalls;
        /** 上游无定位、无核验或有歧义时停止下游。 */
        private boolean blocked;
    }
}
