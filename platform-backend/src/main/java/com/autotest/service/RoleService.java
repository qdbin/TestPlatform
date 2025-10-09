package com.autotest.service;

import com.autotest.domain.User;
import com.autotest.domain.UserRole;
import com.autotest.mapper.RoleMapper;
import com.autotest.dto.RoleDTO;
import com.autotest.request.QueryRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.List;

/**
 * 服务：角色与成员管理
 * 职责：按条件查询角色与成员列表，删除角色下指定成员。
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class RoleService {

    @Resource
    private RoleMapper roleMapper;

    /**
     * 条件查询角色列表（支持名称模糊）
     * @param request 查询请求（包含项目、分页与关键字）
     * @return List<RoleDTO> 角色列表
     */
    public List<RoleDTO> getRoleList(QueryRequest request){
        if(request.getCondition() != null && !request.getCondition().equals("")){
            request.setCondition("%"+request.getCondition()+"%");
        }
        return roleMapper.getRoleList(request);
    }

    /**
     * 条件查询角色成员列表（支持名称/账号模糊）
     * @param request 查询请求（包含项目、分页与关键字）
     * @return List<User> 角色成员列表
     */
    public List<User> getRoleUserList(QueryRequest request){
        if(request.getCondition() != null && !request.getCondition().equals("")){
            request.setCondition("%"+request.getCondition()+"%");
        }
        return roleMapper.getRoleUserList(request);
    }

    /**
     * 删除角色成员绑定
     * @param userRole 用户角色绑定实体（roleId、userId）
     */
    public void deleteRoleUser(UserRole userRole){
        roleMapper.deleteRoleUser(userRole.getRoleId(), userRole.getUserId());
    }
}
