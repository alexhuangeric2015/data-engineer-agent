package com.dataengineer.agent.knowledge;

import com.volcengine.ApiException;
import com.volcengine.hiagent.api.ApiClient;
import com.volcengine.hiagent.api.KbsClient;
import com.volcengine.hiagent.api.model.QueryRequest;
import com.volcengine.hiagent.api.model.QueryResponse;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * 用火山引擎官方 HiAgent Java SDK 调用知识库 Query API。
 * 本类仅做 KB 定位和响应映射；不解释片段、不查询业务数据库。
 */
@Component
@EnableConfigurationProperties(HiAgentGatewayProperties.class)
public class HiAgentKnowledgeGateway implements KnowledgeGateway {
    /** 业务阶段日志。 */
    private static final Logger log = LoggerFactory.getLogger(HiAgentKnowledgeGateway.class);
    /** SDK 中知识库类型协议值。 */
    private static final int KNOWLEDGE_BASE_TYPE = 1;
    /** SDK 中混合检索协议值。 */
    private static final int HYBRID_SEARCH = 2;
    /** 本地 Demo 的候选召回上限，非数据库明细上限。 */
    private static final int TOP_K = 5;
    /** 表结构工具参数协议值。 */
    private static final String TABLE = "TABLE";
    /** 字典工具参数协议值。 */
    private static final String DICTIONARY = "DICTIONARY";
    /** 租户连接信息。 */
    private final HiAgentGatewayProperties properties;

    /** 配置仅在首次真正查询时校验，允许服务先启动并呈现清晰错误。 */
    public HiAgentKnowledgeGateway(HiAgentGatewayProperties properties) {
        this.properties = properties;
    }

    /** 一次用户目标只检索对应知识库，不指定知识文件。 */
    @Override
    public List<KnowledgeHit> search(String kind, String query) {
        String datasetId = switch (kind) {
            case TABLE -> properties.tableKbId();
            case DICTIONARY -> properties.dictionaryKbId();
            default -> throw new IllegalArgumentException("未知知识库类型: " + kind);
        };
        if (blank(properties.endpoint()) || blank(properties.region()) || blank(properties.accessKey())
                || blank(properties.secretKey()) || blank(properties.workspaceId()) || blank(datasetId)) {
            throw new IllegalStateException("HiAgent endpoint、AK/SK、工作空间或知识库 ID 未配置");
        }
        QueryRequest request = new QueryRequest();
        request.setWorkspaceID(properties.workspaceId());
        request.setDatasetIDs(List.of(datasetId));
        request.setKeywords(List.of(query));
        request.setTopK(TOP_K);
        request.setType(KNOWLEDGE_BASE_TYPE);
        request.setRetrievalSearchMethod(HYBRID_SEARCH);
        log.info("[知识库定位][开始] kind={}, queryLength={}", kind, query.length());
        try {
            // 官方 SDK 负责 Volcengine 签名；不在本项目重写鉴权协议。
            ApiClient client = new ApiClient(properties.endpoint(), properties.accessKey(),
                    properties.secretKey(), properties.region());
            QueryResponse response = new KbsClient(client).query(request);
            if (response == null || response.getResults() == null) {
                throw new IllegalStateException("HiAgent Query 响应缺少 Results");
            }
            List<KnowledgeHit> hits = response.getResults().stream()
                    .map(item -> new KnowledgeHit(item.getDocumentName(), item.getSegmentID(),
                            item.getScore(), item.getContent())).toList();
            log.info("[知识库定位][完成] kind={}, hitCount={}", kind, hits.size());
            return hits;
        } catch (ApiException error) {
            log.error("[知识库定位][失败] kind={}, status={}", kind, error.getCode(), error);
            throw new IllegalStateException("HiAgent 知识库查询失败，状态码: " + error.getCode(), error);
        }
    }

    /** 空配置不可传给 SDK，否则错误会难以定位。 */
    private boolean blank(String value) { return value == null || value.isBlank(); }
}
