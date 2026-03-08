package com.autotest.controller;

import com.autotest.domain.Project;
import com.autotest.domain.UserProject;
import com.autotest.mapper.ProjectMapper;
import com.autotest.request.AiChatStreamRequest;
import com.autotest.request.AiGenerateCaseRequest;
import com.autotest.service.AiService;
import com.autotest.service.CaseService;
import com.autotest.service.ProjectService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.core.task.TaskExecutor;
import org.springframework.web.client.RestTemplate;
import org.springframework.test.util.ReflectionTestUtils;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.anyMap;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.mockito.Mockito.timeout;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.doAnswer;

@ExtendWith(MockitoExtension.class)
class AiControllerTest {

    @Mock
    private AiService aiService;
    @Mock
    private ProjectService projectService;
    @Mock
    private ProjectMapper projectMapper;
    @Mock
    private CaseService caseService;
    @Mock
    private HttpServletRequest request;
    @Mock
    private HttpSession session;
    @Mock
    private RestTemplate restTemplate;
    @Mock
    private TaskExecutor aiStreamTaskExecutor;
    @Mock
    private HttpServletResponse response;

    private AiController buildController() {
        AiController controller = new AiController();
        ReflectionTestUtils.setField(controller, "aiService", aiService);
        ReflectionTestUtils.setField(controller, "projectService", projectService);
        ReflectionTestUtils.setField(controller, "projectMapper", projectMapper);
        ReflectionTestUtils.setField(controller, "caseService", caseService);
        ReflectionTestUtils.setField(controller, "objectMapper", new ObjectMapper());
        ReflectionTestUtils.setField(controller, "restTemplate", restTemplate);
        ReflectionTestUtils.setField(controller, "aiStreamTaskExecutor", aiStreamTaskExecutor);
        return controller;
    }

    @Test
    void saveGeneratedCaseShouldCallCaseService() {
        AiController controller = buildController();

        Project project = new Project();
        project.setId("p1");
        UserProject userProject = new UserProject();
        userProject.setUserId("u1");
        userProject.setProjectId("p1");

        when(request.getSession(true)).thenReturn(session);
        when(session.getAttribute("userId")).thenReturn("u1");
        when(projectService.getProjectInfo("p1")).thenReturn(project);
        when(projectMapper.getProjectUser("p1", "u1")).thenReturn(userProject);

        Map<String, Object> caseMap = new HashMap<>();
        caseMap.put("projectId", "p1");
        caseMap.put("name", "AI草稿");
        caseMap.put("type", "API");
        caseMap.put("caseApis", java.util.Collections.emptyList());
        doNothing().when(aiService).validateCaseApiIds(eq("p1"), any());
        Map<String, Object> body = new HashMap<>();
        body.put("case", caseMap);

        Map<String, Object> result = controller.saveGeneratedCase(body, request);
        ArgumentCaptor<com.autotest.request.CaseRequest> captor = ArgumentCaptor
                .forClass(com.autotest.request.CaseRequest.class);
        verify(caseService).saveCase(captor.capture());
        verify(aiService).validateCaseApiIds(eq("p1"), any());
        assertEquals("p1", captor.getValue().getProjectId());
        assertEquals("u1", captor.getValue().getUpdateUser());
        assertEquals("用例保存成功", result.get("msg"));
    }

    @Test
    void saveGeneratedCaseShouldFailWhenCaseMissing() {
        AiController controller = buildController();
        Map<String, Object> body = new HashMap<>();
        assertThrows(RuntimeException.class, () -> controller.saveGeneratedCase(body, request));
    }

    @Test
    void saveGeneratedCaseShouldRejectNonApiType() {
        AiController controller = buildController();
        Map<String, Object> caseMap = new HashMap<>();
        caseMap.put("projectId", "p1");
        caseMap.put("name", "AI草稿");
        caseMap.put("type", "WEB");
        caseMap.put("caseApis", java.util.Collections.emptyList());
        Map<String, Object> body = new HashMap<>();
        body.put("case", caseMap);
        assertThrows(RuntimeException.class, () -> controller.saveGeneratedCase(body, request));
    }

    @Test
    void chatStreamShouldForwardHistoryMessages() {
        AiController controller = buildController();
        Project project = new Project();
        project.setId("p1");
        UserProject userProject = new UserProject();
        userProject.setProjectId("p1");
        userProject.setUserId("u1");
        when(request.getSession(true)).thenReturn(session);
        when(session.getAttribute("userId")).thenReturn("u1");
        when(projectService.getProjectInfo("p1")).thenReturn(project);
        when(projectMapper.getProjectUser("p1", "u1")).thenReturn(userProject);

        AiChatStreamRequest body = new AiChatStreamRequest();
        body.setProjectId("p1");
        body.setMessage("继续回答");
        body.setUseRag(true);
        List<Map<String, Object>> history = new ArrayList<>();
        Map<String, Object> userMessage = new HashMap<>();
        userMessage.put("role", "user");
        userMessage.put("content", "上一个问题");
        history.add(userMessage);
        body.setMessages(history);

        doNothing().when(response).setHeader(any(), any());
        doAnswer(invocation -> {
            Runnable runnable = invocation.getArgument(0);
            runnable.run();
            return null;
        }).when(aiStreamTaskExecutor).execute(any());
        controller.chatStream(body, "tok", request, response);
        verify(aiStreamTaskExecutor).execute(any());
        ArgumentCaptor<Map<String, Object>> captor = ArgumentCaptor.forClass(Map.class);
        verify(aiService, timeout(1000)).streamChat(captor.capture(), eq("tok"), any());
        Map<String, Object> aiRequest = captor.getValue();
        assertEquals("p1", aiRequest.get("project_id"));
        assertEquals(history, aiRequest.get("messages"));
    }

    @Test
    void getCaseSchemaShouldReturnComponents() {
        AiController controller = buildController();
        Project project = new Project();
        project.setId("p1");
        UserProject userProject = new UserProject();
        userProject.setProjectId("p1");
        userProject.setUserId("u1");
        when(request.getSession(true)).thenReturn(session);
        when(session.getAttribute("userId")).thenReturn("u1");
        when(projectService.getProjectInfo("p1")).thenReturn(project);
        when(projectMapper.getProjectUser("p1", "u1")).thenReturn(userProject);
        when(request.getScheme()).thenReturn("http");
        when(request.getServerName()).thenReturn("localhost");
        when(request.getServerPort()).thenReturn(8080);

        Map<String, Object> schemas = new HashMap<>();
        schemas.put("CaseRequest", new HashMap<>());
        schemas.put("CaseApiRequest", new HashMap<>());
        Map<String, Object> components = new HashMap<>();
        components.put("schemas", schemas);
        Map<String, Object> openapi = new HashMap<>();
        openapi.put("components", components);
        when(restTemplate.getForObject("http://localhost:8080/v3/api-docs", Map.class)).thenReturn(openapi);

        Map<String, Object> result = controller.getCaseSchema("p1", request);
        Map<String, Object> data = (Map<String, Object>) result.get("data");
        assertEquals(true, data.containsKey("CaseRequest"));
        assertEquals(true, data.containsKey("CaseApiRequest"));
    }

    @Test
    void generateCaseShouldForwardMessages() {
        AiController controller = buildController();
        Project project = new Project();
        project.setId("p1");
        UserProject userProject = new UserProject();
        userProject.setProjectId("p1");
        userProject.setUserId("u1");
        when(request.getSession(true)).thenReturn(session);
        when(session.getAttribute("userId")).thenReturn("u1");
        when(projectService.getProjectInfo("p1")).thenReturn(project);
        when(projectMapper.getProjectUser("p1", "u1")).thenReturn(userProject);
        when(aiService.generateCase(anyMap(), eq("tok"))).thenReturn(new HashMap<>());

        AiGenerateCaseRequest req = new AiGenerateCaseRequest();
        req.setProjectId("p1");
        req.setUserRequirement("生成登录用例");
        req.setSelectedApis(java.util.Arrays.asList("a1"));
        List<Map<String, Object>> messages = new ArrayList<>();
        Map<String, Object> m = new HashMap<>();
        m.put("role", "user");
        m.put("content", "历史问题");
        messages.add(m);
        req.setMessages(messages);

        ArgumentCaptor<Map<String, Object>> captor = ArgumentCaptor.forClass(Map.class);
        verify(aiService).generateCase(captor.capture(), eq("tok"));
        assertEquals(messages, captor.getValue().get("messages"));
    }
}
