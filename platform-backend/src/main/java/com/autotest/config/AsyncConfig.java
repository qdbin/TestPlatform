package com.autotest.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import java.util.concurrent.Executor;

@Configuration
public class AsyncConfig {

    /**
     * AI流式专用线程池。
     * 与默认异步池隔离，避免其他异步任务影响SSE首包时延。
     */
    @Bean(name = "aiStreamTaskExecutor")
    public Executor aiStreamTaskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(16);
        executor.setMaxPoolSize(64);
        executor.setQueueCapacity(200);
        executor.setThreadNamePrefix("ai-stream-");
        executor.initialize();
        return executor;
    }
}
