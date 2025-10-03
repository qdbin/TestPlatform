package com.autotest.dto;

import com.autotest.domain.User;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * 实体：用户信息扩展（permissions:list）
 * 用途：在用户基础信息上扩充权限集合
 */
@Getter
@Setter
public class UserDTO extends User {
    List<String> permissions; // 权限列表
}
