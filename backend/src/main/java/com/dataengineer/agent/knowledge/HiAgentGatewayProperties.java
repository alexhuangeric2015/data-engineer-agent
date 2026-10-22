package com.dataengineer.agent.knowledge;

import org.springframework.boot.context.properties.ConfigurationProperties;

/** HiAgent 知识库网关配置。密钥和实际库 ID 由环境注入。 */
@ConfigurationProperties(prefix = "app.hiagent")
public record HiAgentGatewayProperties(
        /** HiAgent TOP API endpoint，由租户提供。 */ String endpoint,
        /** HiAgent API 区域。 */ String region,
        /** 火山引擎 AccessKey。 */ String accessKey,
        /** 火山引擎 SecretKey。 */ String secretKey,
        /** HiAgent 工作空间 ID。 */ String workspaceId,
        /** 表结构知识库 ID。 */ String tableKbId,
        /** 字典知识库 ID。 */ String dictionaryKbId) {
}
