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
import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

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

    @Test
    void saveGeneratedCaseShouldCallCaseService() {
        AiController controller = new AiController();
        ReflectionTestUtils.setField(controller, "aiService", aiService);
        ReflectionTestUtils.setField(controller, "projectService", projectService);
        ReflectionTestUtils.setField(controller, "projectMapper", projectMapper);
        ReflectionTestUtils.setField(controller, "caseService", caseService);
        ReflectionTestUtils.setField(controller, "objectMapper", new ObjectMapper());

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
        AiController controller = new AiController();
        ReflectionTestUtils.setField(controller, "projectService", projectService);
        ReflectionTestUtils.setField(controller, "projectMapper", projectMapper);
        ReflectionTestUtils.setField(controller, "objectMapper", new ObjectMapper());
        Map<String, Object> body = new HashMap<>();
        assertThrows(RuntimeException.class, () -> controller.saveGeneratedCase(body, request));
    }
}
