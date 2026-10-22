package com.dataengineer.agent;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/** 数据资产对话 Demo 入口。 */
@SpringBootApplication
public class AgentApplication {
    /** 启动 Web、Agent 与数据库组件。 */
    public static void main(String[] args) {
        SpringApplication.run(AgentApplication.class, args);
    }
}
