/**
 * 测试计划管理组件 - 管理测试计划的增删改查、执行与通知配置
 */
<template>
  <div>
    <!-- 搜索筛选区域 -->
    <el-form :inline="true" :model="searchForm">
        <!-- 计划名称搜索输入框 -->
        <el-form-item label="">
            <el-input size="small" v-model="searchForm.condition" prefix-icon="el-icon-search" placeholder="请输入计划名称"/>
        </el-form-item>
        <!-- 搜索和重置按钮 -->
        <el-form-item>
            <el-button size="small" type="primary" @click="search">搜索</el-button>
            <el-button size="small" @click="reset">重置</el-button>
        </el-form-item>
        <!-- 新增计划按钮 -->
        <el-form-item style="float: right">
            <el-button size="small" type="primary" icon="el-icon-plus" @click="addplan">新增计划</el-button>
        </el-form-item>
    </el-form>
    
    <!-- 测试计划列表表格 -->
    <el-table size="small" :data="planData" v-loading="loading">
        <!-- 序号列 -->
        <el-table-column label="序号" prop="index" width="50px" align="center"/>
        <!-- 计划名称列（可点击编辑） -->
        <el-table-column label="计划名称" prop="name" min-width="160px" :show-overflow-tooltip="true">
            <template slot-scope="scope">
                <el-button type="text" class="plan-name" @click="editPlan(scope.row)">
                    <a>{{scope.row.name}}</a>
                </el-button>
            </template>
        </el-table-column>
        <!-- 版本列 -->
        <el-table-column label="版本" prop="versionName" :show-overflow-tooltip="true"/>
        <!-- 计划描述列 -->
        <el-table-column label="计划描述" prop="description" min-width="180px" :show-overflow-tooltip="true"/>
        <!-- 创建人列 -->
        <el-table-column label="创建人" prop="username"/>
        <!-- 更新时间列 -->
        <el-table-column label="更新时间" prop="updateTime" width="150px"/>
        <!-- 操作列（执行、删除、通知） -->
        <el-table-column fixed="right" align="operation" label="操作" width="130px">
            <template slot-scope="scope">
                <el-button type="text" size="mini" @click="runPlan(scope.row)">执行</el-button>
                <el-button type="text" size="mini" @click="deletePlan(scope.row)">删除</el-button>
                <el-button type="text" size="mini" @click="editNotice(scope.row)">通知</el-button>
            </template>
        </el-table-column>
    </el-table>
    
    <!-- 分页组件 -->
    <Pagination v-bind:child-msg="pageparam" @callFather="callFather"/>
    
    <!-- 配置计划通知弹框 -->
    <edit-notice :noticeForm="noticeForm" :noticeVisible="noticeVisible" @closeNotice="closeNotice" @submitNotice="submitNotice($event)"/>
    
    <!-- 计划执行配置弹框（选择引擎和环境） -->
    <run-form :runForm="runForm" :runVisible="runVisible" :showEnvironment="showEnvironment" @closeRun="closeRun" @run="run($event)"/>
  </div>
</template>

<script>
// 导入所需组件和工具函数
import Pagination from '../common/components/pagination'  // 分页组件
import {timestampToTime} from '@/utils/util'  // 时间戳转换工具
import RunForm from '@/views/common/business/runForm'  // 执行配置表单组件
import EditNotice from './common/editNotice'  // 通知编辑组件

export default {
    // 注册子组件
    components: {
        Pagination, RunForm, EditNotice
    },
    
    /**
     * 组件数据定义
     * @returns {Object} 组件的响应式数据对象
     */
    data() {
        return{
            loading: false,  // 表格加载状态
            
            // 搜索表单数据
            searchForm: {
                page: 1,        // 当前页码
                limit: 10,      // 每页显示数量
                condition: ""   // 搜索条件（计划名称）
            },
            
            planData: [],  // 测试计划列表数据
            
            // 分页参数
            pageparam: {
                currentPage: 1,  // 当前页码
                pageSize: 10,    // 每页大小
                total: 0         // 总记录数
            },
            
            // 执行配置相关
            runVisible: false,      // 执行配置弹框显示状态
            showEnvironment: false, // 是否显示环境选择
            runForm: {
                engineId: "",       // 执行引擎ID
                environmentId: null, // 环境ID
                deviceId: null      // 设备ID
            },
            
            // 通知配置相关
            noticeVisible: false,  // 通知配置弹框显示状态
            noticeForm: {
                planId: null,         // 计划ID
                notificationId: null, // 通知ID
                condition: null       // 通知条件
            }
        }
    },
    
    /**
     * 组件创建时的生命周期钩子
     * 初始化面包屑导航并获取计划数据
     */
    created() {
        this.$root.Bus.$emit('initBread', ["计划中心", "测试计划"]);
        this.getPlanData(this.searchForm)
    },
    
    methods: {
        /**
         * 获取测试计划列表数据
         * @param {Object} searchParam - 搜索参数对象
         * @param {number} searchParam.page - 页码
         * @param {number} searchParam.limit - 每页数量
         * @param {string} searchParam.condition - 搜索条件
         */
        getPlanData(searchParam) {
            this.loading = true
            let url = '/autotest/plan/list/' + searchParam.page + '/' + searchParam.limit;
            let param = {
                condition: searchParam.condition,
                projectId: this.$store.state.projectId
            };
            
            // 发送请求获取计划列表
            this.$post(url, param, response => {
                let data = response.data;
                // 处理列表数据：格式化时间和添加序号
                for(let i =0; i<data.list.length; i++){
                    data.list[i].updateTime = timestampToTime(data.list[i].updateTime);
                    data.list[i].index = (searchParam.page-1) * searchParam.limit + i+1;
                }
                this.planData = data.list;
                this.loading = false;
                
                // 更新分页参数
                this.pageparam.currentPage = this.searchForm.page;
                this.pageparam.pageSize = this.searchForm.limit;
                this.pageparam.total = data.total;
            });
        },
        
        /**
         * 分页组件回调函数
         * @param {Object} param - 分页参数
         * @param {number} param.currentPage - 当前页码
         * @param {number} param.pageSize - 每页大小
         */
        callFather(param) {
            this.searchForm.page = param.currentPage;
            this.searchForm.limit = param.pageSize;
            this.getPlanData(this.searchForm);
        },
        
        /**
         * 搜索按钮点击事件
         * 根据搜索条件重新获取计划数据
         */
        search() {
            this.getPlanData(this.searchForm);
        },
        
        /**
         * 重置按钮点击事件
         * 清空搜索条件并重新获取数据
         */
        reset() {
            this.searchForm.condition = "";
            this.getPlanData(this.searchForm);
        },
        
        /**
         * 新增计划按钮点击事件
         * 跳转到新增计划页面
         */
        addplan(){
            this.$router.push({path: '/planManage/testplan/add'});
        },
        
        /**
         * 编辑计划事件
         * @param {Object} row - 计划行数据
         * @param {number} row.id - 计划ID
         */
        editPlan(row){
            this.$router.push({path: '/planManage/testplan/edit/' + row.id});
        },
        
        /**
         * 执行计划事件
         * @param {Object} row - 计划行数据
         * @param {number} row.id - 计划ID
         * @param {string} row.name - 计划名称
         * @param {string} row.engineId - 引擎ID
         * @param {string} row.environmentId - 环境ID
         */
        runPlan(row){
            // 根据计划配置决定是否显示环境选择
            if(row.environmentId != null){
                this.showEnvironment = true;
            }else{
                this.showEnvironment = false;
            }
            
            // 设置执行表单数据
            this.runForm.engineId = row.engineId;
            this.runForm.environmentId = row.environmentId;
            this.runForm.deviceId = null;
            this.runForm.sourceType = "plan";
            this.runForm.sourceId = row.id;
            this.runForm.sourceName = row.name;
            this.runForm.taskType = "run";
            this.runForm.projectId = this.$store.state.projectId;
            this.runVisible = true;
        },
        
        /**
         * 关闭执行配置弹框
         */
        closeRun(){
            this.runVisible = false;
        },
        
        /**
         * 执行计划
         * @param {Object} runForm - 执行配置表单数据
         */
        run(runForm){
            let url = '/autotest/run';
            this.$post(url, runForm, response =>{
                let reportId = response.data.reportId;
                // 执行成功后询问是否跳转到报告页面
                this.$confirm('执行成功，是否跳转执行报告？', '', {
                    type: "success",
                    distinguishCancelAndClose: true,
                    confirmButtonText: '跳转',
                    cancelButtonText: '关闭'
                })
                .then(() => {
                    this.$router.push({path: '/report/testReport/detail/' + reportId});
                })
                .catch(action => {
                    // 用户选择关闭，不做任何操作
                });
            });
            this.runVisible = false;
        },
        
        /**
         * 编辑通知配置事件
         * @param {Object} row - 计划行数据
         * @param {number} row.id - 计划ID
         */
        editNotice(row){
            let url = '/autotest/plan/notice/'+row.id;
            this.$get(url, response => {
                let data = response.data;
                if(data !== null){
                    // 如果已有通知配置，则加载现有配置
                    this.noticeForm.id = data.id;
                    this.noticeForm.planId = data.planId;
                    this.noticeForm.notificationId = data.notificationId;
                    this.noticeForm.condition = data.condition;
                }else{
                    // 如果没有通知配置，则初始化默认配置
                    this.noticeForm.planId = row.id;
                    this.noticeForm.condition = 'A';
                }
                this.noticeVisible = true;
            });
        },
        
        /**
         * 关闭通知配置弹框
         */
        closeNotice(){
            this.noticeVisible = false;
        },
        
        /**
         * 提交通知配置
         * @param {Object} noticeForm - 通知配置表单数据
         */
        submitNotice(noticeForm){
            let url = '/autotest/plan/save/notice';
            this.$post(url, noticeForm, response =>{
                this.$message.success("保存成功");
                this.noticeVisible = false;
            });
        },
        
        /**
         * 删除计划事件
         * @param {Object} row - 计划行数据
         * @param {number} row.id - 计划ID
         */
        deletePlan(row){
            this.$confirm('确定要删除计划吗?', '删除提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            })
            .then(() => {
                let url = '/autotest/plan/delete';
                this.$post(url, {id: row.id}, response => {
                    this.$message.success("删除成功");
                    this.getPlanData(this.searchForm);
                });
            })
            .catch(() => {
                this.$message.success("取消成功");
            })
        },
    }
}
</script>

<style scoped>
/* 计划名称样式 - 确保文本不会溢出并保持左对齐 */
.plan-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    width: 100%;
    text-align: left;
}
</style>