package com.autotest.controller;

import com.autotest.domain.AiKnowledge;
import com.autotest.request.AiChatStreamRequest;
import com.autotest.request.AiGenerateCaseRequest;
import com.autotest.request.AiKnowledgeRequest;
import com.autotest.service.AiService;
import com.autotest.service.ai.AiPermissionService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.core.task.TaskExecutor;
import org.springframework.test.util.ReflectionTestUtils;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.anyMap;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.mockito.Mockito.timeout;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.never;

@ExtendWith(MockitoExtension.class)
class AiControllerTest {

    @Mock
    private AiService aiService;
    @Mock
    private AiPermissionService aiPermissionService;
    @Mock
    private TaskExecutor aiStreamTaskExecutor;
    @Mock
    private HttpServletRequest request;
    @Mock
    private HttpServletResponse response;

    private AiController buildController() {
        AiController controller = new AiController();
        ReflectionTestUtils.setField(controller, "aiService", aiService);
        ReflectionTestUtils.setField(controller, "aiPermissionService", aiPermissionService);
        ReflectionTestUtils.setField(controller, "aiStreamTaskExecutor", aiStreamTaskExecutor);
        return controller;
    }

    @Test
    void saveKnowledgeShouldInjectUpdateUser() {
        AiController controller = buildController();
        AiKnowledgeRequest req = new AiKnowledgeRequest();
        req.setProjectId("p1");
        req.setName("AI文档");
        req.setDocType("manual");
        req.setContent("test");
        when(aiPermissionService.getLoginUserId(request)).thenReturn("u1");
        when(aiService.saveKnowledge(req)).thenReturn("kid1");
        String id = controller.saveKnowledge(req, request);
        verify(aiPermissionService).assertProjectAccess(request, "p1");
        verify(aiService).saveKnowledge(req);
        assertEquals("kid1", id);
        assertEquals("u1", req.getUpdateUser());
    }

    @Test
    void chatStreamShouldForwardHistoryMessages() {
        AiController controller = buildController();
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
        verify(response).setHeader("Cache-Control", "no-cache");
        verify(response).setHeader("Connection", "keep-alive");
        verify(response).setHeader("X-Accel-Buffering", "no");
        verify(aiStreamTaskExecutor).execute(any());
        ArgumentCaptor<Map<String, Object>> captor = ArgumentCaptor.forClass(Map.class);
        verify(aiService, timeout(1000)).streamChat(captor.capture(), eq("tok"), any());
        Map<String, Object> aiRequest = captor.getValue();
        assertEquals("p1", aiRequest.get("project_id"));
        assertEquals(history, aiRequest.get("messages"));
    }

    @Test
    void generateCaseShouldForwardMessages() {
        AiController controller = buildController();
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

        controller.generateCase(req, "tok", request);
        ArgumentCaptor<Map<String, Object>> captor = ArgumentCaptor.forClass(Map.class);
        verify(aiService).generateCase(captor.capture(), eq("tok"));
        assertEquals(messages, captor.getValue().get("messages"));
    }

    @Test
    void getKnowledgeListShouldMapIndexedStatus() {
        AiController controller = buildController();
        when(aiPermissionService.getLoginUserId(request)).thenReturn("u1");
        when(aiPermissionService.canManageKnowledge(request, "p1")).thenReturn(false);
        AiKnowledge knowledge = new AiKnowledge();
        knowledge.setId("k1");
        knowledge.setProjectId("p1");
        knowledge.setCreateUser("u1");
        knowledge.setStatus("indexed");
        when(aiService.getKnowledgeList("p1")).thenReturn(java.util.Collections.singletonList(knowledge));
        List<Map<String, Object>> list = controller.getKnowledgeList("p1", request);
        assertEquals("ready", list.get(0).get("indexedStatus"));
    }

    @Test
    void generateCaseShouldHandleNullLists() {
        AiController controller = buildController();
        when(aiService.generateCase(anyMap(), eq("tok"))).thenReturn(new HashMap<>());
        AiGenerateCaseRequest req = new AiGenerateCaseRequest();
        req.setProjectId("p1");
        req.setUserRequirement("生成用例");
        controller.generateCase(req, "tok", request);
        ArgumentCaptor<Map<String, Object>> captor = ArgumentCaptor.forClass(Map.class);
        verify(aiService).generateCase(captor.capture(), eq("tok"));
        List<String> selected = (List<String>) captor.getValue().get("selected_apis");
        List<Map<String, Object>> msgs = (List<Map<String, Object>>) captor.getValue().get("messages");
        assertEquals(0, selected.size());
        assertEquals(0, msgs.size());
        verify(aiService, never()).streamChat(anyMap(), any(), any());
    }
}
