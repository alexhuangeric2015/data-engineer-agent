package com.dataengineer.agent.chat;

import java.util.List;

/** 从知识库原片段抽取的待核验名称；是否可查仍由工具核对片段。 */
public record CandidateNames(
        /** 原样保留的英文名或中文名；空列表代表没有可核验名称。 */ List<String> names) {
}
