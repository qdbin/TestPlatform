package com.autotest.service;

import com.autotest.common.exception.LMException;
import com.autotest.domain.AiKnowledge;
import com.autotest.dto.ApiDTO;
import com.autotest.mapper.AiKnowledgeMapper;
import com.autotest.mapper.ApiMapper;
import com.autotest.request.CaseApiRequest;
import com.autotest.request.CaseRequest;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.RestTemplate;

import java.util.Collections;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AiServiceTest {

    @Mock
    private AiKnowledgeMapper aiKnowledgeMapper;
    @Mock
    private RestTemplate restTemplate;
    @Mock
    private ApiMapper apiMapper;

    private AiService buildService() {
        AiService service = new AiService();
        ReflectionTestUtils.setField(service, "aiKnowledgeMapper", aiKnowledgeMapper);
        ReflectionTestUtils.setField(service, "restTemplate", restTemplate);
        ReflectionTestUtils.setField(service, "objectMapper", new ObjectMapper());
        ReflectionTestUtils.setField(service, "apiMapper", apiMapper);
        ReflectionTestUtils.setField(service, "aiServiceBaseUrl", "http://localhost:8001");
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
}
