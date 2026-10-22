package com.dataengineer.agent.chat;

import java.util.List;
import java.util.Map;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 对话记录持久化边界。只负责写入与按会话读取；不负责模型上下文裁剪和权限控制。
 */
@Mapper
public interface ChatHistoryMapper {
    /** 新建会话，ID 由服务层生成。 */
    void insertSession(@Param("id") String id, @Param("mode") String mode);
    /** 保存一条已完成的用户或助手消息。 */
    void insertMessage(@Param("sessionId") String sessionId, @Param("role") String role,
                       @Param("content") String content);
    /** 按原始顺序取得会话消息。 */
    List<Map<String, String>> listMessages(@Param("sessionId") String sessionId);
}
