package com.autotest.dto;

import com.autotest.domain.Database;
import lombok.Getter;
import lombok.Setter;

/**
 * DTO：数据库配置扩展视图（继承 Database）
 * 用途：追加连接信息详情，便于前端展示与配置
 */


@Getter
@Setter
public class DatabaseDTO extends Database {

    private DBConnectInfo info; // 连接信息（主机/端口/账号/密码）

}
