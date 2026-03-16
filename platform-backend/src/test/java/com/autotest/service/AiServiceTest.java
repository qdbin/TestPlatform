package com.autotest.service;

import com.autotest.common.exception.LMException;
import com.autotest.domain.AiKnowledge;
import com.autotest.dto.ApiDTO;
import com.autotest.mapper.AiKnowledgeMapper;
import com.autotest.mapper.ApiMapper;
import com.autotest.request.CaseApiRequest;
import com.autotest.request.CaseRequest;
import com.autotest.service.ai.AiFeignClient;
import com.fasterxml.jackson.databind.ObjectMapper;
import feign.Request;
import feign.Response;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AiServiceTest {

    @Mock
    private AiKnowledgeMapper aiKnowledgeMapper;
    @Mock
    private ApiMapper apiMapper;
    @Mock
    private AiFeignClient aiFeignClient;

    private static class CaptureEmitter extends SseEmitter {
        private final List<Object> events = new ArrayList<>();
        private boolean completed = false;

        CaptureEmitter() {
            super(30000L);
        }

        @Override
        public synchronized void send(SseEventBuilder builder) {
            events.add(builder);
        }

        @Override
        public synchronized void complete() {
            completed = true;
        }
    }

    private AiService buildService() {
        AiService service = new AiService();
        ReflectionTestUtils.setField(service, "aiKnowledgeMapper", aiKnowledgeMapper);
        ReflectionTestUtils.setField(service, "aiFeignClient", aiFeignClient);
        ReflectionTestUtils.setField(service, "objectMapper", new ObjectMapper());
        ReflectionTestUtils.setField(service, "apiMapper", apiMapper);
        return service;
    }

    @Test
    void indexKnowledgeShouldRejectFolder() {
        AiService service = buildService();
        AiKnowledge folder = new AiKnowledge();
        folder.setId("k1");
        folder.setDocType("folder");
        when(aiKnowledgeMapper.getKnowledgeById("k1")).thenReturn(folder);
        assertThrows(LMException.class, () -> service.indexKnowledge("k1"));
    }

    @Test
    void validateCaseApiIdsShouldRejectCrossProjectApi() {
        AiService service = buildService();
        CaseApiRequest step = new CaseApiRequest();
        step.setApiId("a1");
        CaseRequest request = new CaseRequest();
        request.setCaseApis(Collections.singletonList(step));
        ApiDTO api = new ApiDTO();
        api.setId("a1");
        api.setProjectId("p2");
        when(apiMapper.getApiDetail("a1")).thenReturn(api);
        assertThrows(LMException.class, () -> service.validateCaseApiIds("p1", request));
    }

    @Test
    void validateCaseApiIdsShouldPassWhenApiBelongsToProject() {
        AiService service = buildService();
        CaseApiRequest step = new CaseApiRequest();
        step.setApiId("a1");
        CaseRequest request = new CaseRequest();
        request.setCaseApis(Collections.singletonList(step));
        ApiDTO api = new ApiDTO();
        api.setId("a1");
        api.setProjectId("p1");
        when(apiMapper.getApiDetail("a1")).thenReturn(api);
        assertDoesNotThrow(() -> service.validateCaseApiIds("p1", request));
    }

    @Test
    void validateCaseApiIdsShouldRejectEmptySteps() {
        AiService service = buildService();
        CaseRequest request = new CaseRequest();
        request.setCaseApis(Collections.emptyList());
        assertThrows(LMException.class, () -> service.validateCaseApiIds("p1", request));
    }

    @Test
    void streamChatShouldForwardEverySseEvent() throws Exception {
        AiService service = buildService();
        String body = "data: {\"type\":\"content\",\"delta\":\"A\"}\n\n"
                + "data: {\"type\":\"content\",\"delta\":\"B\"}\n\n"
                + "data: {\"type\":\"end\"}\n\n";
        Request request = Request.create(
                Request.HttpMethod.POST,
                "http://127.0.0.1:8001/ai/chat/stream",
                new HashMap<>(),
                null,
                StandardCharsets.UTF_8);
        Response response = Response.builder()
                .status(200)
                .reason("OK")
                .request(request)
                .headers(new HashMap<>())
                .body(new ByteArrayInputStream(body.getBytes(StandardCharsets.UTF_8)), body.length())
                .build();
        when(aiFeignClient.streamChat(org.mockito.ArgumentMatchers.anyMap(), org.mockito.ArgumentMatchers.anyString()))
                .thenReturn(response);
        CaptureEmitter emitter = new CaptureEmitter();
        Map<String, Object> payload = new HashMap<>();
        payload.put("project_id", "p1");
        payload.put("message", "hello");
        service.streamChat(payload, "tok", emitter);
        assertEquals(3, emitter.events.size());
        assertEquals(true, emitter.completed);
    }
}
