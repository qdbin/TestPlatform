/**
 * 接口管理组件 - 模块树与接口列表，支持检索、导入、增删改与自动生成用例
 */
<template>
  <div>
    <!-- 搜索筛选区域 -->
    <el-form :inline="true" :model="searchForm"> <!-- 行内表单：接口搜索与操作 -->
        <el-form-item label="">
            <el-input size="small" v-model="searchForm.condition" prefix-icon="el-icon-search" placeholder="请输入接口NO、名称、地址"/> <!-- 多条件搜索输入框 -->
        </el-form-item>
        <el-form-item>
            <el-button size="small" type="primary" @click="search">搜索</el-button> <!-- 搜索按钮 -->
            <el-button size="small" @click="reset">重置</el-button> <!-- 重置搜索条件 -->
        </el-form-item>
        <el-form-item style="float: right">
            <el-button size="small" type="primary" icon="el-icon-plus" @click="addApi">新增接口</el-button> <!-- 新增接口按钮 -->
        </el-form-item>
          <el-form-item style="float: right">
          <el-button size="small" type="success" icon="el-icon-plus" @click="importApi">导入接口</el-button> <!-- 批量导入接口按钮 -->
        </el-form-item>
    </el-form>

    <!-- 接口模块树 -->
    <el-col :span="4" class="left-tree"> <!-- 左侧模块树区域 -->
        <module-tree title="接口模块" :treeData="treeData" :currentModule="searchForm.moduleId" @clickModule="clickModule($event)" @appendModule="appendModule($event)"
            @removeModule="removeModule(arguments)" @dragNode="dragNode(arguments)"/> <!-- 模块树组件：支持增删改拖拽 -->
    </el-col>

    <!-- 接口列表表格 -->
    <el-col :span="20" class="right-table"> <!-- 右侧接口列表区域 -->
        <el-table size="small" :data="apiListData" v-loading="loading" element-loading-text="拼命加载中"> <!-- 接口数据表格 -->
            <el-table-column prop="num" label="NO" width="60px"/> <!-- 接口编号 -->
            <el-table-column prop="name" label="接口名称" min-width="180" :show-overflow-tooltip="true"/> <!-- 接口名称，超出省略 -->
            <el-table-column prop="path" label="接口地址" min-width="150" :show-overflow-tooltip="true"/> <!-- 接口路径 -->
            <el-table-column prop="moduleName" label="所属模块" :show-overflow-tooltip="true"/> <!-- 所属模块名称 -->
            <el-table-column prop="username" label="创建人"/> <!-- 创建人 -->
            <el-table-column prop="updateTime" label="更新时间" width="150"/> <!-- 更新时间 -->
            <el-table-column fixed="right" align="operation" label="操作" width="150"> <!-- 操作列 -->
                <template slot-scope="scope">
                    <el-button type="text" size="mini" @click="editApi(scope.row)">编辑</el-button> <!-- 编辑接口 -->
                    <el-button type="text" size="mini" @click="deleteApi(scope.row)">删除</el-button> <!-- 删除接口 -->
                    <el-button type="text" size="mini" @click="generateCase(scope.row)">生成用例</el-button> <!-- 自动生成用例 -->
                </template>
            </el-table-column>
        </el-table>
        <!-- 分页组件 -->
        <Pagination v-bind:child-msg="pageParam" @callFather="callFather"></Pagination> <!-- 分页控制 -->
    </el-col>

    <!-- 添加模块弹窗 -->
    <module-append :title="title" :show.sync="moduleVisible" :moduleForm="moduleForm" @closeDialog="closeDialog" @submitModule="submitModule($event)"/> <!-- 模块添加弹窗 -->

    <!-- 上传文件弹窗 -->
    <el-dialog title="上传文件" :visible.sync="uploadFileVisible" width="600px" destroy-on-close> <!-- 文件导入弹窗 -->
      <el-form label-width="120px" style="padding-right: 30px;" :model="uploadFileForm" :rules="rules" ref="uploadFileForm">
        <el-form-item label="文件来源" prop="sourceType">
          <el-radio-group v-model="uploadFileForm.sourceType"> <!-- 文件来源选择 -->
            <el-radio label="postman">postman</el-radio> <!-- Postman导出文件 -->
            <el-radio label="swagger">swagger3</el-radio> <!-- Swagger3文档 -->
          </el-radio-group>
        </el-form-item>
        <el-form-item label="选择模块" prop="moduleId">
          <select-tree style="width:90%" placeholder="请选择导入后的模块" :selectedValue="uploadFileForm.moduleId"
                       :selectedLabel="uploadFileForm.moduleName" :treeData="treeData" @selectModule="selectModule($event)"/> <!-- 模块选择树 -->
        </el-form-item>
        <el-form-item label="选择文件" prop="fileList">
          <el-upload class="upload-demo" :file-list="uploadFileForm.fileList" :before-upload="beforeUpload" :http-request="uploadFile"
                     :on-remove="removeFile" :on-exceed="handleExceed" drag action :limit="1" ref="upload"> <!-- 文件上传组件 -->
            <i class="el-icon-upload"></i>
            <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
            <div class="el-upload__tip" slot="tip">只能上传单个文件，且不超过50M</div> <!-- 上传限制提示 -->
          </el-upload>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button size="small" @click="uploadFileVisible=false">取消</el-button> <!-- 取消上传 -->
        <el-button size="small" type="primary" @click="submitFileForm('uploadFileForm', uploadFileForm)">上传</el-button> <!-- 确认上传 -->
      </div>
    </el-dialog>

    <!-- 自动生成用例配置抽屉 -->
    <el-drawer :visible.sync="editRuleVisible" direction="rtl" :with-header="false" destroy-on-close size="920px"> <!-- 用例生成规则配置 -->
        <div class="api-drawer-header">
            <span style="float: left; font-size: 16px;">生成规则配置</span> <!-- 抽屉标题 -->
            <el-button size="small" type="primary" style="float: right;" @click="submitRuleForm(paramRuleForm)">确定</el-button> <!-- 确认生成 -->
        </div>
        <div class="api-drawer-body">
            <autocase :paramRuleForm="paramRuleForm"/> <!-- 自动用例配置组件 -->
        </div>
    </el-drawer>
  </div>
</template>

<script>
import Pagination from '../common/components/pagination'
import ModuleTree from './common/module/moduleTree'
import ModuleAppend from './common/module/moduleAppend'
import {timestampToTime} from '@/utils/util'
import SelectTree from "../common/business/selectTree";
import Autocase from "./common/case/autocase"

export default {
    // 注册组件
    components: {
        Pagination, ModuleTree, ModuleAppend, SelectTree, Autocase
    },
    data() {
        return{
            uploadFileVisible: false, // 文件上传弹窗显示状态
            uploadFileForm : { // 文件上传表单数据
              sourceType: "postman", // 文件来源类型
              fileList: [], // 上传文件列表
              moduleId:"", // 导入目标模块ID
              moduleName:"" // 导入目标模块名称
            },
            rules:{ // 表单验证规则
              sourceType:[{ required: true, message: '文件来源不能为空', trigger: 'blur' }],
              fileList: [{ required: true, message: '文件不能为空', trigger: 'blur' }],
              moduleId: [{ required: true, message: '导入模块不能为空', trigger: 'blur' }]
            },
            loading:false, // 表格加载状态
            moduleVisible: false, // 模块编辑弹窗显示状态
            moduleForm: { // 模块表单数据
                name: "", // 模块名称
                parentId: "", // 父模块ID
                parentName: "", // 父模块名称
                data: "", // 模块数据
            },
            title: '添加接口模块', // 弹窗标题
            searchForm: { // 搜索表单参数
                page: 1, // 当前页码
                limit: 10, // 每页条数
                condition: "", // 搜索条件
                moduleId: "", // 模块筛选ID
            },
            moduleList:[] , // 存放当前项目中所有module的列表
            apiListData: [], // 接口列表数据
            pageParam: { // 分页配置参数
                currentPage: 1,
                pageSize: 10,
                total: 0
            },
            treeData: [], // 存放所有module的数据: /autotest/module/list/api/的响应结果
            editRuleVisible: false, // 用例生成规则弹窗显示状态
            paramRuleForm: { // 用例生成规则表单
                apiId: null, // 接口ID
                header: [], // 请求头参数规则
                body: [], // 请求体参数规则
                query: [], // 查询参数规则
                rest: [], // 路径参数规则
                positiveAssertion: [], // 正向断言规则
                oppositeAssertion: [] // 逆向断言规则
            }
        }
    },
    created() {
        // 生命周期：初始化面包屑导航并加载数据
        this.$root.Bus.$emit('initBread', ["用例中心", "接口管理"])
        this.getTree()
        this.getdata(this.searchForm)
    },
    methods: {
      // 上传前文件格式和大小验证
      beforeUpload(file) {
        if (file.size > 50 * 1024 * 1024) {
          this.$message.warning('文件大小超过50M 无法上传');
          return false;
        }
        return true;
      },

      // 文件上传处理
      uploadFile(option) {
        this.uploadFileForm.fileList.push(option.file);
        this.uploadFileForm.name = option.file.name;
        this.$refs.uploadFileForm.validateField('fileList'); // 触发文件字段验证
      },

      // 移除上传文件
      removeFile() {
        this.uploadFileForm.fileList = [];
      },

      // 文件数量超限处理
      handleExceed() {
        this.$message.warning('一次最多只能上传一个文件');
      },

      // 选择导入模块
      selectModule(data){
        this.uploadFileForm.moduleId = data.id;
        this.uploadFileForm.moduleName = data.label;
      },

      // 提交文件上传表单
      submitFileForm(confirm, form){
        this.$refs[confirm].validate(valid => {
          if (valid) {
              let url = '/autotest/import/api';
              let data = {
                projectId: this.$store.state.projectId,
                moduleId: form.moduleId,
                sourceType: form.sourceType
              };
              let file = form.fileList[0];
              // 执行文件上传并刷新列表
              this.$fileUpload(url, file, null, data, response =>{
                  this.$message.success("上传成功");
                  this.uploadFileVisible = false;
                  this.getdata(this.searchForm);
              });
          }else{
              return false;
          }
        });
      },

        // 点击模块树节点，筛选对应模块的接口
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
            moduleForm.moduleType = 'api_module';
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
          let url = '/autotest/module/list/api/' + this.$store.state.projectId;
            this.$get(url, response =>{
                response.data.unshift({id: "0", name:"默认模块", label: "默认模块"}); // 添加默认模块
                this.treeData = response.data;
            });
        },

        // 获取接口列表数据
        getdata(searchParam) {
            this.loading = true;
            let url = '/autotest/api/list/' + searchParam.page + '/' + searchParam.limit;
            let param = {
                condition: searchParam.condition,
                moduleId: searchParam.moduleId,
                projectId: this.$store.state.projectId
            };
            this.$post(url, param, response => {
                let data = response.data;
                // 处理列表数据：若所属模块id为0，则赋值模块名字段
                for(let i=0;i<data.list.length;i++){
                    if(data.list[i].moduleId==='0'){
                        data.list[i].moduleName='默认模块';
                    }
										// 格式化时间
                    data.list[i].updateTime = timestampToTime(data.list[i].updateTime);
                }
                this.apiListData = data.list;
                this.loading = false
                // 分页赋值
                this.pageParam.currentPage = this.searchForm.page;
                this.pageParam.pageSize = this.searchForm.limit;
                this.pageParam.total = data.total;
            });
        },

        // 分页插件事件回调
        callFather(param) {
            this.searchForm.page = param.currentPage
            this.searchForm.limit = param.pageSize
            this.getdata(this.searchForm)
        },

        // 搜索按钮：根据条件刷新列表
        search() {
            this.getdata(this.searchForm)
        },

        // 重置按钮：清空条件并重新加载
        reset() {
            this.searchForm.condition = "";
            this.searchForm.moduleId = "";
            this.getdata(this.searchForm);
        },

        // 导入接口：打开文件上传弹窗
        importApi(){
          this.uploadFileVisible = true;
        },

        // 新增接口：跳转到接口编辑页面
        addApi(){
            this.$router.push({path: '/caseCenter/interfaceManage/add'})
        },

        // 编辑接口：跳转到接口编辑页面
        editApi(row){
            this.$router.push({path: '/caseCenter/interfaceManage/edit/' + row.id})
        },

        // 删除接口：确认后执行删除操作
        deleteApi(row){
            this.$confirm('确定要删除接口吗?', '删除提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            })
            .then(() => {
                let url = '/autotest/api/delete';
                this.$post(url, {id: row.id}, response => {
                    this.$message.success("删除成功");
                    this.getdata(this.searchForm); // 刷新列表
                });
            })
            .catch(() => {
                this.$message.success("取消成功");
            })
        },

        // 自动生成用例：初始化规则表单并打开配置抽屉
        generateCase(row){
          this.paramRuleForm.apiId = row.id;
          this.paramRuleForm.header = [];
          this.paramRuleForm.body = [];
          this.paramRuleForm.query = [];
          this.paramRuleForm.rest = [];
          this.paramRuleForm.positiveAssertion = [];
          this.paramRuleForm.oppositeAssertion = [];
          this.editRuleVisible = true;
        },

        // 提交自动用例生成规则
        submitRuleForm(form){
          if(form.positiveAssertion.length === 0 | form.oppositeAssertion.length === 0){
            this.$message.warning("请至少维护一条正向断言以及逆向断言");
            return;
          }
          let url = '/autotest/case/auto/generate';
          this.$post(url, form, response => {
              this.$message.success("生成成功 前往用例管理页查看");
              this.editRuleVisible = false;
          });
        }
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

/* 抽屉头部样式 */
.api-drawer-header{
    border-bottom: 1px solid rgb(219, 219, 219); /* 底部边框 */
    height: 42px; /* 固定高度 */
    display: flex; /* 弹性布局 */
    justify-content: space-between; /* 两端对齐 */
    align-items: center; /* 垂直居中 */
    padding: 0px 20px; /* 左右内边距 */
}

/* 抽屉内容样式 */
.api-drawer-body{
    padding: 10px 20px; /* 内边距 */
}
</style>
