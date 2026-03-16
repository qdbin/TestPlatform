package com.autotest.service.ai;

import com.autotest.common.exception.LMException;
import com.autotest.domain.AiKnowledge;
import com.autotest.domain.Project;
import com.autotest.mapper.ProjectMapper;
import com.autotest.service.ProjectService;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;

/**
 * AI权限服务
 * 职责：统一处理 AI 模块项目权限、知识库操作权限、登录用户读取。
 */
@Service
public class AiPermissionService {

    @Resource
    private ProjectService projectService;

    @Resource
    private ProjectMapper projectMapper;

    public String getLoginUserId(HttpServletRequest request) {
        Object userId = request.getSession(true).getAttribute("userId");
        return userId != null ? userId.toString() : "";
    }

    /**
     * 校验当前用户是否有项目访问权限。
     */
    public void assertProjectAccess(HttpServletRequest request, String projectId) {
        if (projectId == null || projectId.isEmpty()) {
            throw new LMException("projectId不能为空");
        }
        String userId = getLoginUserId(request);
        if (userId.isEmpty()) {
            throw new LMException("未登录");
        }
        Project project = projectService.getProjectInfo(projectId);
        if (project == null) {
            throw new LMException("项目不存在");
        }
        if ("system_admin_user".equals(userId)) {
            return;
        }
        if (projectMapper.getProjectUser(projectId, userId) == null) {
            throw new LMException("无项目权限");
        }
    }

    public boolean canManageKnowledge(HttpServletRequest request, String projectId) {
        String userId = getLoginUserId(request);
        if (userId.isEmpty()) {
            return false;
        }
        if ("system_admin_user".equals(userId)) {
            return true;
        }
        Project project = projectService.getProjectInfo(projectId);
        return project != null && userId.equals(project.getProjectAdmin());
    }

    public boolean canManageKnowledgeItem(HttpServletRequest request, AiKnowledge knowledge) {
        if (knowledge == null) {
            return false;
        }
        String userId = getLoginUserId(request);
        if (userId.isEmpty()) {
            return false;
        }
        if ("system_admin_user".equals(userId)) {
            return true;
        }
        Project project = projectService.getProjectInfo(knowledge.getProjectId());
        if (project != null && userId.equals(project.getProjectAdmin())) {
            return true;
        }
        return userId.equals(knowledge.getCreateUser());
    }
}
