package com.autotest.controller;

import com.autotest.domain.Project;
import com.autotest.domain.UserProject;
import com.autotest.mapper.ProjectMapper;
import com.autotest.service.AiService;
import com.autotest.service.CaseService;
import com.autotest.service.ProjectService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import javax.servlet.http.HttpServletRequest;
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

    private AiController buildController() {
        AiController controller = new AiController();
        ReflectionTestUtils.setField(controller, "aiService", aiService);
        ReflectionTestUtils.setField(controller, "projectService", projectService);
        ReflectionTestUtils.setField(controller, "projectMapper", projectMapper);
        ReflectionTestUtils.setField(controller, "caseService", caseService);
        ReflectionTestUtils.setField(controller, "objectMapper", new ObjectMapper());
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
        Map<String, Object> body = new HashMap<>();
        body.put("case", caseMap);

        Map<String, Object> result = controller.saveGeneratedCase(body, request);
        ArgumentCaptor<com.autotest.request.CaseRequest> captor = ArgumentCaptor.forClass(com.autotest.request.CaseRequest.class);
        verify(caseService).saveCase(captor.capture());
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

        Map<String, Object> body = new HashMap<>();
        body.put("projectId", "p1");
        body.put("message", "继续回答");
        body.put("useRag", true);
        body.put("conversationId", "conv_1");
        List<Map<String, Object>> history = new ArrayList<>();
        Map<String, Object> userMessage = new HashMap<>();
        userMessage.put("role", "user");
        userMessage.put("content", "上一个问题");
        history.add(userMessage);
        body.put("historyMessages", history);

        controller.chatStream(body, "tok", request);
        ArgumentCaptor<Map<String, Object>> captor = ArgumentCaptor.forClass(Map.class);
        verify(aiService, timeout(1000)).streamChat(captor.capture(), eq("tok"), any());
        Map<String, Object> aiRequest = captor.getValue();
        assertEquals("p1", aiRequest.get("project_id"));
        assertEquals("conv_1", aiRequest.get("conversation_id"));
        assertEquals(history, aiRequest.get("history_messages"));
    }
}
