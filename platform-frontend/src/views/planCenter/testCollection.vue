/**
 * 测试集合管理组件 - 用于管理测试集合的增删改查、执行和报告查看
 */
<template>
  <div>
    <!-- 搜索筛选区域 -->
    <el-form :inline="true" :model="searchForm"> <!-- 行内表单：集合名称搜索与操作 -->
        <el-form-item label="">
            <el-input size="small" v-model="searchForm.condition" prefix-icon="el-icon-search" placeholder="请输入集合名称"/> <!-- 集合名称搜索输入框 -->
        </el-form-item>
        <el-form-item>
            <el-button size="small" type="primary" @click="search">搜索</el-button> <!-- 搜索按钮 -->
            <el-button size="small" @click="reset">重置</el-button> <!-- 重置搜索条件 -->
        </el-form-item>
        <el-form-item style="float: right">
            <el-button size="small" type="primary" icon="el-icon-plus" @click="addCollection">新增集合</el-button> <!-- 新增集合按钮 -->
        </el-form-item>
    </el-form>
    
    <!-- 测试集合列表表格 -->
    <el-table size="small" :data="collectionData" v-loading="loading" row-key="id" :expand-row-keys="expands" @expand-change="expandSelect"> <!-- 可展开表格，显示集合及其报告 -->
        <el-table-column type="expand" width="40px"> <!-- 展开列：显示集合下的报告列表 -->
            <template slot-scope="props">
                <div style="padding-left: 40px">
                    <!-- 报告列表子表格 -->
                    <el-table size="mini" :data="props.row.reportData"> <!-- 集合下的测试报告列表 -->
                        <el-table-column label="序号" prop="index" width="50px" align="center"/> <!-- 报告序号 -->
                        <el-table-column label="报告名称" prop="name" min-width="200px" :show-overflow-tooltip="true"/> <!-- 报告名称，超出省略 -->
                        <el-table-column label="报告状态" prop="format" width="100px"/> <!-- 报告执行状态 -->
                        <el-table-column label="执行进度" prop="runProgress" width="120px"> <!-- 执行进度条 -->
                            <template slot-scope="scope">
                                <el-progress :percentage="props.row.reportData[scope.$index].progress" :color="props.row.reportData[scope.$index].color"/> <!-- 进度条显示 -->
                            </template>
                        </el-table-column>
                        <el-table-column label="总用例数" prop="total" width="80px"/> <!-- 总用例数量 -->
                        <el-table-column label="成功数" prop="passCount" width="80px"/> <!-- 成功用例数量 -->
                        <el-table-column label="成功率" prop="passRate" width="80px"/> <!-- 用例成功率 -->
                        <el-table-column label="创建时间" prop="createTime" width="150px"/> <!-- 报告创建时间 -->
                        <el-table-column fixed="right" align="center"  label="操作" width="150px"> <!-- 报告操作列 -->
                            <template slot-scope="scope">
                                <el-button type="text" size="mini" @click="viewReport(scope.row)">查看</el-button> <!-- 查看报告详情 -->
                                <el-button type="text" size="mini" @click="deleteReport(props.row, scope.row)">删除</el-button> <!-- 删除报告 -->
                            </template>
                        </el-table-column>
                    </el-table>
                    <!-- 报告分页组件 -->
                    <Pagination style="float: right;" size="mini" v-bind:child-msg="props.row.pageparam" @callFather="reportCallFather($event, props.row)"/> <!-- 报告列表分页 -->
                </div>
            </template>
        </el-table-column>
        <el-table-column prop="index" label="序号" width="50px" align="center"/> <!-- 集合序号 -->
        <el-table-column prop="name" label="集合名称" min-width="160px" :show-overflow-tooltip="true"/> <!-- 集合名称，超出省略 -->
        <el-table-column prop="versionName" label="版本" :show-overflow-tooltip="true"/> <!-- 集合版本信息 -->
        <el-table-column prop="description" label="集合描述" min-width="180px" :show-overflow-tooltip="true"/> <!-- 集合描述信息 -->
        <el-table-column prop="username" label="创建人"/> <!-- 集合创建人 -->
        <el-table-column prop="updateTime" label="更新时间" width="150px"/> <!-- 集合更新时间 -->
        <el-table-column fixed="right" align="center" label="操作" width="150px"> <!-- 集合操作列 -->
            <template slot-scope="scope">
                <el-button type="text" size="mini" @click="runCollection(scope.row)">执行</el-button> <!-- 执行集合 -->
                <el-button type="text" size="mini" @click="editCollection(scope.row)">编辑</el-button> <!-- 编辑集合 -->
                <el-button type="text" size="mini" @click="deleteCollection(scope.row)">删除</el-button> <!-- 删除集合 -->
            </template>
        </el-table-column>
    </el-table>
    
    <!-- 集合列表分页组件 -->
    <Pagination v-bind:child-msg="pageparam" @callFather="collectionCallFather"/> <!-- 集合列表分页控制 -->
    
    <!-- 集合执行配置弹窗 -->
    <run-form :runForm="runForm" :runVisible="runVisible" :showEnvironment="showEnvironment" :showDevice="showDevice" 
        :deviceSystem="deviceSystem" @closeRun="closeRun" @run="run($event)"/> <!-- 集合执行时的引擎、环境、设备选择 -->
  </div>
</template>

<script>
import Pagination from '../common/components/pagination'
import {timestampToTime} from '@/utils/util'
import RunForm from '@/views/common/business/runForm'

export default {
    // 注册组件
    components: {
        Pagination, RunForm
    },
    data() {
        return{
            expands: [], // 默认展开的行ID数组
            loading:false, // 表格加载状态
            searchForm: { // 搜索表单参数
                page: 1, // 当前页码
                limit: 10, // 每页条数
                condition: "" // 搜索条件
            },
            collectionData: [], // 集合列表数据
            pageparam: { // 分页配置参数
                currentPage: 1,
                pageSize: 10,
                total: 0
            },
            runVisible: false, // 执行配置弹窗显示状态
            showEnvironment: false, // 是否显示环境选择
            showDevice: false, // 是否显示设备选择
            deviceSystem: null, // 设备操作系统类型
            runForm: { // 执行配置表单
                engineId: "", // 引擎ID
                environmentId: null, // 环境ID
                deviceId: null // 设备ID
            },
            runRow: null // 当前执行的集合行数据
        }
    },
    created() {
        // 生命周期：初始化面包屑导航并加载集合数据
        this.$root.Bus.$emit('initBread', ["计划中心", "测试集合"])
        this.getCollectionData(this.searchForm)
    },
    methods: {
        // 获取集合列表数据并处理分页与时间格式
        getCollectionData(searchParam) {
            this.loading = true
            let url = '/autotest/collection/list/' + searchParam.page + '/' + searchParam.limit;
            let param = {
                condition: searchParam.condition,
                projectId: this.$store.state.projectId
            };
            this.$post(url, param, response => {
                let data = response.data;
                for(let i =0; i<data.list.length; i++){
                    data.list[i].updateTime= timestampToTime(data.list[i].updateTime); // 时间格式化
                    data.list[i].reportData = []; // 初始化报告数据
                    data.list[i].pageparam = { // 初始化报告分页参数
                        currentPage: 1,
                        pageSize: 10,
                        total: 0
                    };
                    data.list[i].index = (searchParam.page-1) * searchParam.limit + i+1; // 计算序号
                }
                this.collectionData = data.list;
                this.loading = false;
                // 更新分页信息
                this.pageparam.currentPage = this.searchForm.page;
                this.pageparam.pageSize = this.searchForm.limit;
                this.pageparam.total = data.total;
            });
        },
        
        // 获取指定集合的报告数据
        getReportData(row){
            let url = '/autotest/report/list/' + row.pageparam.currentPage + '/' + row.pageparam.pageSize;
            let param = {
                projectId: this.$store.state.projectId,
                collectionId: row.id
            };
            this.$post(url, param, response => {
                let data = response.data;
                for(let i =0; i<data.list.length; i++){
                    data.list[i].createTime = timestampToTime(data.list[i].createTime); // 时间格式化
                    let status = data.list[i].status
                    // 根据报告状态设置显示格式和颜色
                    if(status === 'success'){
                        data.list[i].format = 'SUCCESS';
                        data.list[i].color = '#67C23A';
                    }else if(status === 'fail'){
                        data.list[i].format = 'FAIL';
                        data.list[i].color = '#E6A23C';
                    }else if(status === 'error'){
                        data.list[i].format = 'ERROR';
                        data.list[i].color = '#F56C6C';
                    }else if(status === 'skip'){
                        data.list[i].format = 'SKIP';
                        data.list[i].color = '#535457';
                    }else if(status === 'prepared'){
                        data.list[i].format = '等待执行';
                        data.list[i].color = '#409EFF';
                    }else if(status === 'running'){
                        data.list[i].format = "RUNNING";
                        data.list[i].color = '#409EFF';
                    }else if(status === 'discontinue'){
                        data.list[i].format = "已终止";
                        data.list[i].color = '#535457';
                    }
                    data.list[i].index = (row.pageparam.currentPage-1) * row.pageparam.pageSize + i+1; // 计算序号
                }
                row.reportData = data.list;
                row.pageparam.total = data.total;
            });
        },
        
        // 表格展开/收起事件处理
        expandSelect(row, expandedRows) {
            if(expandedRows.indexOf(row) === -1){  // 关闭行
                this.expands.splice(this.expands.indexOf(row.id), 1);
            } else{ // 打开行
                if(this.expands.indexOf(row.id) === -1){
                    this.expands.push(row.id);
                    this.getReportData(row); // 加载报告数据
                }
            }
        },
        
        // 集合列表分页回调：更新搜索参数并重新加载数据
        collectionCallFather(parm) {
            this.searchForm.page = parm.currentPage;
            this.searchForm.limit = parm.pageSize;
            this.getCollectionData(this.searchForm);
        },
        
        // 报告列表分页回调：更新报告分页参数并重新加载报告数据
        reportCallFather(param, row){
            row.pageparam.currentPage = param.currentPage;
            row.pageparam.pageSize = param.pageSize;
            this.getReportData(row);
        },
        
        // 搜索按钮：根据条件刷新集合列表
        search() {
            this.getCollectionData(this.searchForm);
        },
        
        // 重置按钮：清空条件并重新加载
        reset() {
            this.searchForm.condition = "";
            this.getCollectionData(this.searchForm);
        },
        
        // 新增集合：跳转到集合新增页面
        addCollection(){
            this.$router.push({path: '/planManage/testCollection/add'})
        },
        
        // 执行集合：检查集合类型并配置执行参数
        runCollection(row){
            let url = "/autotest/collection/types/" + row.id;
            this.$get(url, response =>{
                this.showEnvironment = response.data.needEnvironment; // 是否需要环境配置
                this.showDevice = response.data.hasAndroid || response.data.hasApple; // 是否需要设备配置
                if(response.data.hasAndroid){
                    this.deviceSystem = "android";
                }
                if(response.data.hasApple){
                    this.deviceSystem = "apple";
                }
                this.runRow = row;
                // 初始化执行表单
                this.runForm.engineId = 'system';
                this.runForm.environmentId = null;
                this.runForm.deviceId = null;
                this.runForm.sourceType = "collection";
                this.runForm.sourceId = row.id;
                this.runForm.sourceName = row.name;
                this.runForm.taskType = "run";
                this.runForm.projectId = this.$store.state.projectId;
                this.runVisible = true;
            });
        },
        
        // 关闭执行配置弹窗
        closeRun(){
            this.runVisible = false;
        },
        
        // 提交执行任务并刷新报告列表
        run(runForm){
            let url = '/autotest/run';
            this.$post(url, runForm, response =>{
                this.$message.success("执行成功 执行结果请查看报告");
                this.expands.push(this.runRow.id); // 自动展开当前集合的报告
                this.getReportData(this.runRow); // 刷新报告数据
            });
            this.runVisible = false;
        },
        
        // 编辑集合：跳转到集合编辑页面
        editCollection(row){
            this.$router.push({path: '/planManage/testCollection/edit/' + row.id})
        },
        
        // 查看报告：跳转到报告详情页面
        viewReport(row){
            this.$router.push({path: '/report/testReport/detail/' + row.id});
        },
        
        // 删除报告：确认后删除并刷新报告列表
        deleteReport(cRow, rRow){
            this.$confirm('确定要删除报告吗?', '删除提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            })
            .then(() => {
                let url = '/autotest/report/delete';
                this.$post(url, {id: rRow.id}, response => {
                    this.$message.success("删除成功");
                    this.getReportData(cRow); // 刷新报告列表
                });
            })
            .catch(() => {
                this.$message.success("取消成功");
            })
        },
        
        // 删除集合：确认后删除并刷新集合列表
        deleteCollection(row){
            this.$confirm('确定要删除集合吗?', '删除提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            })
            .then(() => {
                let url = '/autotest/collection/delete';
                this.$post(url, {id: row.id}, response => {
                    this.$message.success("删除成功");
                    this.getCollectionData(this.searchForm); // 刷新集合列表
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
/* 测试集合管理页面样式 */
</style>
