/**
 * 用例管理组件 - 用于管理测试用例的增删改查、模块分类和执行调试
 */
<template>
  <div>
    <!-- 搜索筛选区域 -->
    <el-form :inline="true" :model="searchForm"> <!-- 行内表单：用例搜索与操作 -->
        <el-form-item label="">
            <el-input size="small" v-model="searchForm.condition" prefix-icon="el-icon-search" placeholder="请输入用例NO、名称"/> <!-- 用例名称搜索输入框 -->
        </el-form-item>
        <el-form-item label="">
            <el-select size="small" clearable style="width:120px" v-model="searchForm.caseType" placeholder="用例类型"> <!-- 用例类型筛选 -->
                <el-option v-for="item in caseTypes" :key="item" :label="item" :value="item"/>
            </el-select>
        </el-form-item>
        <el-form-item label="" v-if="searchForm.caseType==='APP'">
            <el-select size="small" clearable style="width:120px" v-model="searchForm.system" placeholder="操作系统"> <!-- APP用例操作系统筛选 -->
                <el-option v-for="item in systems" :key="item" :label="item" :value="item"/>
            </el-select>
        </el-form-item>
        <el-form-item>
            <el-button size="small" type="primary" @click="search">搜索</el-button> <!-- 搜索按钮 -->
            <el-button size="small" @click="reset">重置</el-button> <!-- 重置搜索条件 -->
        </el-form-item>
        <el-form-item style="float: right">
            <el-button size="small" type="primary" icon="el-icon-plus" @click="addCase">新增用例</el-button> <!-- 新增用例按钮 -->
        </el-form-item>
    </el-form>
    
    <!-- 用例模块树 -->
    <el-col :span="4" class="left-tree"> <!-- 左侧模块树区域 -->
        <module-tree title="用例模块" :treeData="treeData" :currentModule="searchForm.moduleId" @clickModule="clickModule($event)" @appendModule="appendModule($event)"
             @removeModule="removeModule(arguments)" @dragNode="dragNode(arguments)"/> <!-- 模块树组件：支持增删改拖拽 -->
    </el-col>
    
    <!-- 用例列表表格 -->
    <el-col :span="20" class="right-table"> <!-- 右侧用例列表区域 -->
        <el-table size="small" :data="caseListData" v-loading="loading" element-loading-text="拼命加载中"> <!-- 用例数据表格 -->
            <el-table-column prop="num" label="NO" width="60px"/> <!-- 用例编号 -->
            <el-table-column prop="name" label="用例名称" min-width="200px" :show-overflow-tooltip="true"> <!-- 用例名称，可点击编辑 -->
                <template slot-scope="scope">
                    <el-button type="text" class="case-name" @click="editCase(scope.row)">
                        <a>{{scope.row.name}}</a>
                    </el-button>
                </template>
            </el-table-column>
            <el-table-column prop="level" label="用例等级"/> <!-- 用例等级 -->
            <el-table-column prop="type" label="用例类型"> <!-- 用例类型，APP类型显示操作系统 -->
                <template slot-scope="scope">
                    <span v-if="scope.row.type==='APP'">{{scope.row.type}}({{scope.row.system}})</span>
                    <span v-else>{{scope.row.type}}</span>
                </template>
            </el-table-column>
            <el-table-column prop="moduleName" label="所属模块" :show-overflow-tooltip="true"/> <!-- 所属模块名称 -->
            <el-table-column prop="username" label="创建人"/> <!-- 创建人 -->
            <el-table-column prop="updateTime" label="更新时间"  width="150px"/> <!-- 更新时间 -->
            <el-table-column fixed="right" align="operation" label="操作" width="150px"> <!-- 操作列 -->
                <template slot-scope="scope">
                    <el-button type="text" size="mini" @click="runCase(scope.row)">执行</el-button> <!-- 执行用例 -->
                    <el-button type="text" size="mini" @click="copyCase(scope.row)">复用</el-button> <!-- 复用用例 -->
                    <el-button type="text" size="mini" @click="deleteCase(scope.row)">删除</el-button> <!-- 删除用例 -->
                </template>
            </el-table-column>
        </el-table>
        <!-- 分页组件 -->
        <Pagination v-bind:child-msg="pageParam" @callFather="callFather"/> <!-- 分页控制 -->
    </el-col>
    
    <!-- 添加模块弹窗 -->
    <module-append title="添加用例模块" :show.sync="moduleVisible" :moduleForm="moduleForm" @closeDialog="closeDialog" @submitModule="submitModule($event)"/> <!-- 模块添加弹窗 -->
    
    <!-- 添加用例弹窗 -->
    <el-dialog title="选择用例类型" :visible.sync="caseVisible" width="500px" destroy-on-close> <!-- 用例类型选择弹窗 -->
        <el-radio-group style="margin-left:15px;" v-model="newCaseType"> <!-- 用例类型选择 -->
            <el-radio :label="'API'">API</el-radio> <!-- API用例 -->
            <el-radio :label="'WEB'">WEB</el-radio> <!-- WEB用例 -->
            <el-radio :label="'ANDROID'">APP(android)</el-radio> <!-- Android APP用例 -->
            <el-radio :label="'APPLE'">APP(apple)</el-radio> <!-- iOS APP用例 -->
        </el-radio-group>
        <div slot="footer" class="dialog-footer">
            <el-button size="small" type="primary" @click="submitCase">确定</el-button> <!-- 确认创建用例 -->
        </div>
    </el-dialog>
    
    <!-- 用例执行选择引擎和环境 -->
    <run-form :runForm="runForm" :runVisible="runVisible" :showEnvironment="showEnvironment" :deviceSystem="deviceSystem"
         :showDevice="showDevice" @closeRun="closeRun" @run="run($event)"/> <!-- 用例执行配置弹窗 -->
    
    <!-- 用例执行结果展示 -->
    <run-result :taskId="taskId" :caseType="caseType" :resultVisable="resultVisable" @closeResult="closeResult"/> <!-- 用例执行结果弹窗 -->
  </div>
</template>

<script>
import Pagination from '../common/components/pagination'
import ModuleTree from './common/module/moduleTree'
import ModuleAppend from './common/module/moduleAppend'
import {timestampToTime} from '@/utils/util'
import RunForm from '@/views/common/business/runForm'
import RunResult from './common/case/runResult'

export default {
    // 注册组件
    components: {
        Pagination, ModuleTree, ModuleAppend, RunForm, RunResult
    },
    data() {
        return{
            loading:false, // 表格加载状态
            moduleVisible: false, // 模块编辑弹窗显示状态
            caseVisible: false, // 用例类型选择弹窗显示状态
            moduleForm: { // 模块表单数据
                name: "", // 模块名称
                parentId: "", // 父模块ID
                parentName: "", // 父模块名称
                data: "", // 模块数据
            },
            newCaseType:"API", // 新建用例类型
            caseTypes:["API", "WEB", "APP"], // 用例类型选项
            systems: ["android", "apple"], // 操作系统选项
            searchForm: { // 搜索表单参数
                page: 1, // 当前页码
                limit: 10, // 每页条数
                condition: "", // 搜索条件
                caseType: "", // 用例类型筛选
                moduleId: "", // 模块筛选ID
                system: "" // 操作系统筛选
            },
            caseListData: [], // 用例列表数据
            pageParam: { // 分页配置参数
                currentPage: 1,
                pageSize: 10,
                total: 0
            },
            treeData: [], // 模块树数据
            runVisible: false, // 执行配置弹窗显示状态
            showEnvironment: false, // 是否显示环境选择
            showDevice: false, // 是否显示设备选择
            deviceSystem: null, // 设备操作系统
            runForm: { // 执行配置表单
                engineId: "", // 引擎ID
                environmentId: null, // 环境ID
                deviceId: null // 设备ID
            },
            resultVisable: false, // 执行结果弹窗显示状态
            taskId: "", // 执行任务ID
            caseType: "" // 当前执行用例类型
        }
    },
    created() {
        // 生命周期：初始化面包屑导航并加载数据
        this.$root.Bus.$emit('initBread', ["用例中心", "用例管理"])
        this.getTree()
        this.getdata(this.searchForm)
    },
    methods: {
        // 点击模块树节点，筛选对应模块的用例
        clickModule(data){
            this.searchForm.moduleId = data.id;
            this.getdata(this.searchForm);
        },
        
        // 添加模块：设置父模块信息并打开弹窗
        appendModule(data) {
            if (data){
                this.moduleForm.parentId = data.id;
                this.moduleForm.parentName = data.label;
                this.moduleForm.data = data;
            }else{
                this.moduleForm.parentId = 0;
                this.moduleForm.parentName = "根节点";
                this.moduleForm.data = "";
            }
            this.moduleVisible = true;
        },
        
        // 删除模块：检查子模块后执行删除
        removeModule(args) {
            let node = args[0];
            let data = args[1];
            if(data.children.length != 0){
                this.$message.warning("当前模块有子模块, 无法删除");
                return;
            }
            let url = '/autotest/module/delete';
            this.$post(url, data, response =>{
                const parent = node.parent;
                const children = parent.data.children || parent.data;
                const index = children.findIndex(d => d.id === data.id);
                children.splice(index, 1); // 从树中移除节点
                this.$message.success("模块删除成功")
            });
        },
        
        // 拖拽模块：更新模块的父级关系
        dragNode(args){
            let dragNode = args[0];
            let newParent = args[1];
            let url = '/autotest/module/save';
            let moduleForm = dragNode.data;
            moduleForm.parentId = newParent;
            this.$post(url, moduleForm, response =>{
                this.$message.success("更改成功")
            });
        },
        
        // 关闭模块编辑弹窗
        closeDialog(){
            this.moduleVisible = false;
        },
        
        // 提交模块保存：新增或编辑模块
        submitModule(moduleForm) {
            moduleForm.projectId = this.$store.state.projectId;
            moduleForm.moduleType = 'case_module';
            let url = '/autotest/module/save';
            this.$post(url, moduleForm, response =>{
                const newChild = response.data;
                // 根据父模块ID添加到对应位置
                if (moduleForm.parentId === 0){
                    this.treeData.push(newChild);
                }else{
                    if (!this.moduleForm.data.children){
                        this.$set(this.moduleForm.data, 'children', []);
                    }
                    this.moduleForm.data.children.push(newChild);
                }
                this.moduleVisible = false;
                this.moduleForm.name = "";
            });
        },
        
        // 获取模块树数据
        getTree(){
            let url = '/autotest/module/list/case/' + this.$store.state.projectId;
            this.$get(url, response =>{
                response.data.unshift({id: "0", name:"默认模块", label: "默认模块"}); // 添加默认模块
                this.treeData = response.data;
            });
        },
        
        // 获取用例列表数据
        getdata(searchParam) {
            this.loading = true;
            let url = '/autotest/case/list/' + searchParam.page + '/' + searchParam.limit;
            let param = {
                condition: searchParam.condition,
                caseType: searchParam.caseType,
                moduleId: searchParam.moduleId,
                projectId: this.$store.state.projectId,
                system: searchParam.system
            };
            this.$post(url, param, response => {
                let data = response.data;
                // 处理列表数据：设置默认模块名称和格式化时间
                for(let i=0;i<data.list.length;i++){
                    if(data.list[i].moduleId==='0'){
                        data.list[i].moduleName='默认模块';
                    }
                    data.list[i].updateTime = timestampToTime(data.list[i].updateTime);
                }
                this.caseListData = data.list;
                this.loading = false
                // 分页赋值
                this.pageParam.currentPage = this.searchForm.page;
                this.pageParam.pageSize = this.searchForm.limit;
                this.pageParam.total = data.total;
            });
        },
        
        // 分页插件事件回调
        callFather(parm) {
            this.searchForm.page = parm.currentPage
            this.searchForm.limit = parm.pageSize
            this.getdata(this.searchForm)
        },
        
        // 搜索按钮：根据条件刷新列表
        search() {
            this.getdata(this.searchForm)
        },
        
        // 重置按钮：清空条件并重新加载
        reset() {
            this.searchForm.condition = "";
            this.searchForm.caseType = "";
            this.searchForm.moduleId = "";
            this.searchForm.system = "";
            this.getdata(this.searchForm);
        },
        
        // 新增用例：打开用例类型选择弹窗
        addCase(){
            this.newCaseType = "API";
            this.caseVisible = true;
        },
        
        // 提交用例保存：根据类型跳转到对应编辑页面
        submitCase() {
            if (this.newCaseType == "API"){
                this.$router.push({path: '/caseCenter/caseManage/apiCase/add'});
            }else if (this.newCaseType == "WEB"){
                this.$router.push({path: '/caseCenter/caseManage/webCase/add'});
            }else if (this.newCaseType == "ANDROID"){ 
                this.$router.push({path: '/caseCenter/caseManage/appCase/android/add'});
            }else if (this.newCaseType == "APPLE"){
                this.$router.push({path: '/caseCenter/caseManage/appCase/apple/add'});
            }
        },
        
        // 编辑用例：根据用例类型跳转到对应编辑页面
        editCase(row){
            if (row.type === "API"){
                this.$router.push({path: '/caseCenter/caseManage/apiCase/edit/' + row.id});
            }else if (row.type === "WEB"){
                this.$router.push({path: '/caseCenter/caseManage/webCase/edit/' + row.id});
            }else{
                if(row.system === "android"){
                    this.$router.push({path: '/caseCenter/caseManage/appCase/android/edit/' + row.id});
                }else if (row.system === "apple"){
                    this.$router.push({path: '/caseCenter/caseManage/appCase/apple/edit/' + row.id});
                }
            }
        },
        
        // 复用用例：根据用例类型跳转到对应复制页面
        copyCase(row){
            if (row.type === "API"){
                this.$router.push({path: '/caseCenter/caseManage/apiCase/copy/' + row.id});
            }else if (row.type === "WEB"){
                this.$router.push({path: '/caseCenter/caseManage/webCase/copy/' + row.id});
            }else{
                if(row.system === "android"){
                    this.$router.push({path: '/caseCenter/caseManage/appCase/android/copy/' + row.id});
                }else if (row.system === "apple"){
                    this.$router.push({path: '/caseCenter/caseManage/appCase/apple/copy/' + row.id});
                }
            }
        },
        
        // 执行用例：配置执行环境和设备
        runCase(row){
            // 用例调试
            this.runForm.engineId = 'system';
            this.runForm.environmentId = null;
            this.runForm.deviceId = null;
            let environmentIds = JSON.parse(row.environmentIds);
            
            this.runForm.sourceType = "case";
            this.runForm.sourceId = row.id;
            this.runForm.sourceName = row.name;
            this.runForm.taskType = "debug";
            this.runForm.projectId = this.$store.state.projectId;
            this.caseType = row.type;
            
            // 根据用例类型配置执行环境
            if(this.caseType === 'API' || this.caseType === 'WEB'){
                if(environmentIds.length > 0){
                    this.runForm.environmentId = environmentIds[0];
                }
                this.showEnvironment = true; // 显示环境选择
                this.showDevice = false;
                this.deviceSystem = null;
            }else{
                this.showEnvironment = false;
                this.showDevice = true; // 显示设备选择
                this.deviceSystem = row.system;
            }
            this.runVisible = true;
        },
        
        // 关闭执行配置弹窗
        closeRun(){
            this.runVisible = false;
        },
        
        // 执行用例：提交执行请求
        run(runForm){
            let url = '/autotest/run';
            this.$post(url, runForm, response =>{
                this.taskId = response.data.id;
                this.resultVisable = true; // 显示执行结果
            });
            this.runVisible = false;
        },
        
        // 关闭执行结果弹窗
        closeResult(){
            this.resultVisable = false;
        },
        
        // 删除用例：确认后执行删除操作
        deleteCase(row){
            this.$confirm('确定要删除用例吗?', '删除提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            })
            .then(() => {
                let url = '/autotest/case/delete';
                this.$post(url, {id: row.id}, response => {
                    this.$message.success("删除成功");
                    this.getdata(this.searchForm); // 刷新列表
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
/* 左侧模块树样式 */
.left-tree {
    padding-right: 5px; /* 右侧内边距 */
    border-right:1px solid rgb(219, 219, 219); /* 右边框分割线 */
}

/* 右侧表格样式 */
.right-table {
    padding-left: 5px; /* 左侧内边距 */
}

/* 用例名称链接样式 */
.case-name {
    overflow: hidden; /* 隐藏溢出内容 */
    text-overflow: ellipsis; /* 文本溢出省略号 */
    white-space: nowrap; /* 不换行 */
    width: 100%; /* 全宽 */
    text-align: left; /* 左对齐 */
}
</style>
