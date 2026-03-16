package com.autotest.service.ai;

import feign.Request;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AiFeignClientConfig {

    @Bean
    public Request.Options aiFeignRequestOptions(
            @Value("${ai.service.connect-timeout-ms:5000}") int connectTimeoutMs,
            @Value("${ai.service.read-timeout-ms:360000}") int readTimeoutMs) {
        return new Request.Options(connectTimeoutMs, readTimeoutMs);
    }
}
