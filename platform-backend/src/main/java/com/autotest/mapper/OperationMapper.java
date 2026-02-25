package com.autotest.mapper;

import com.autotest.domain.Operation;
import com.autotest.dto.OperationDTO;
import com.autotest.request.QueryRequest;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：操作数据访问
 * 用途：提供操作的新增、更新、详情、分组与分页查询等接口，
 *      由 MyBatis XML 完成具体 SQL 绑定（见 OperationMapper.xml）。
 */
@Mapper
public interface OperationMapper {
    /**
     * 新增操作
     * @param operation // 操作实体（含元素/数据/项目等）
     * @return void     // 无返回
     */
    void addOperation(Operation operation);

    /**
     * 更新操作
     * @param operation // 操作实体（按ID更新）
     * @return void     // 无返回
     */
    void updateOperation(Operation operation);

    /**
     * 操作详情查询
     * @param id     // 操作ID
     * @param uiType // UI类型（web/app）
     * @return Operation // 操作实体详情
     */
    Operation getOperationDetail(String id, String uiType);

    /**
     * 按名称查询操作（校验重名）
     * @param name      // 操作名称
     * @param projectId // 项目ID
     * @param uiType    // UI类型
     * @param system    // 系统标识（app）
     * @return Operation // 匹配到的操作（可能为系统级）
     */
    Operation getOperationByName(String name, String projectId, String uiType, String system);

    /**
     * 分组获取操作列表（按类型分组）
     * @param projectId     // 项目ID
     * @param uiType        // UI类型
     * @param system        // 系统标识（app）
     * @param operationType // 操作类型
     * @return List<OperationDTO> // 分组内的操作列表
     */
    List<OperationDTO> getGroupOperationList(String projectId, String uiType, String system, String operationType);

    /**
     * 删除操作（软删除）
     * @param id     // 操作ID
     * @param uiType // UI类型
     * @return void  // 无返回
     */
    void deleteOperation(String id, String uiType);

    /**
     * 分页查询操作列表
     * @param request // 查询请求（含项目、类型、条件、系统）
     * @return List<OperationDTO> // 操作列表（带创建人等）
     */
    List<OperationDTO> getOperationList(QueryRequest request);
}