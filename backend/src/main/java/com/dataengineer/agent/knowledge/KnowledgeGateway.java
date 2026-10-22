package com.dataengineer.agent.knowledge;

import java.util.List;

/** HiAgent 知识库边界：输入检索类别与问句，输出片段；不核验资产存在性。 */
public interface KnowledgeGateway {
    /** 查询表结构或数据字典知识库。 */
    List<KnowledgeHit> search(String kind, String query);
}
