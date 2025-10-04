/**
 * 文件管理组件 - 用于管理测试项目中的文件资源
 * 功能：文件上传、列表展示、搜索筛选、删除管理等
 */
<template>
  <div>
    <!-- 搜索筛选区域 -->
    <el-form :inline="true" :model="searchForm"> <!-- 行内表单：文件搜索与操作 -->
        <el-form-item label="">
            <el-input size="small" v-model="searchForm.condition" prefix-icon="el-icon-search" placeholder="请输入文件UUID/名称"></el-input> <!-- 绑定搜索条件，支持UUID或名称 -->
        </el-form-item>
        <el-form-item>
            <el-button size="small" type="primary" @click="search">搜索</el-button> <!-- 触发搜索 -->
            <el-button size="small" @click="reset">重置</el-button> <!-- 清空条件并刷新 -->
        </el-form-item>
        <el-form-item style="float: right">
            <el-button size="small" type="primary" icon="el-icon-plus" @click="addFile">上传文件</el-button> <!-- 打开上传弹窗 -->
        </el-form-item>
    </el-form>
    
    <!-- 文件列表表格 -->
    <el-table size="small" :data="fileData" v-loading="loading"> <!-- 文件数据表格，支持加载状态 -->
        <el-table-column prop="id" label="UUID" width="250px"/> <!-- 文件唯一标识 -->
        <el-table-column prop="name" label="文件名称" min-width="200px" :show-overflow-tooltip="true"/> <!-- 名称，超出省略提示 -->
        <el-table-column prop="description" label="文件描述" min-width="240px" :show-overflow-tooltip="true"/> <!-- 描述信息 -->
        <el-table-column prop="username" label="创建人"/> <!-- 创建人 -->
        <el-table-column prop="createTime" label="上传时间" width="150px"/> <!-- 上传时间 -->
        <el-table-column fixed="right" align="operation" label="操作" width="100px"> <!-- 操作列 -->
            <template slot-scope="scope">
                <el-button type="text" v-if="scope.row.createUser===currentUser" size="mini" @click="deleteFile(scope.row)">删除</el-button> <!-- 仅创建者可删除 -->
            </template>
        </el-table-column>
    </el-table>
    
    <!-- 分页组件 -->
    <Pagination v-bind:child-msg="pageparam" @callFather="callFather"/> <!-- 分页控制组件 -->
    
    <!-- 上传文件弹窗 -->
    <el-dialog title="上传文件" :visible.sync="uploadFileVisible" width="600px" destroy-on-close> <!-- 文件上传对话框 -->
        <el-form label-width="120px" style="padding-right: 30px;" :model="uploadFileForm" :rules="rules" ref="uploadFileForm"> <!-- 上传表单 -->
            <el-form-item label="文件名称" prop="name">
                <el-input size="small" style="width: 90%" v-model="uploadFileForm.name" placeholder="请输入文件名称"/> <!-- 文件名称输入 -->
            </el-form-item>
            <el-form-item label="文件描述" prop="description">
                <el-input size="small" style="width: 90%" v-model="uploadFileForm.description" :autosize="{ minRows: 3}"
                maxlength="200" show-word-limit type="textarea" clearable placeholder="请输入文件描述"/> <!-- 文件描述输入 -->
            </el-form-item>
            <el-form-item label="选择文件" prop="fileList">
                <!-- 文件上传组件 -->
                <el-upload class="upload-demo" :file-list="uploadFileForm.fileList" :before-upload="beforeUpload" :http-request="uploadFile"
                        :on-remove="removeFile" :on-exceed="handleExceed" drag action :limit="1" ref="upload"> <!-- 拖拽上传，限制单文件 -->
                    <i class="el-icon-upload"></i> <!-- 上传图标 -->
                    <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div> <!-- 上传提示文本 -->
                    <div class="el-upload__tip" slot="tip">只能上传单个文件，且不超过50M</div> <!-- 上传限制说明 -->
                </el-upload>
            </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
            <el-button size="small" @click="uploadFileVisible=false">取消</el-button> <!-- 取消上传 -->
            <el-button size="small" type="primary" @click="submitFileForm('uploadFileForm', uploadFileForm)">上传</el-button> <!-- 确认上传 -->
        </div>
    </el-dialog>
  </div>
</template>

<script>
// 导入所需组件和工具函数
import Pagination from '../common/components/pagination' // 分页组件
import {timestampToTime} from '@/utils/util' // 时间戳转换工具

export default {
    // 注册子组件
    components: {
        Pagination
    },
    
    /**
     * 组件数据定义
     * @returns {Object} 组件的响应式数据对象
     */
    data() {
        return{
            loading: false, // 列表加载状态
            uploadFileVisible: false, // 上传弹窗显隐状态
            
            // 搜索表单数据
            searchForm: {
                page: 1, // 当前页码
                limit: 10, // 每页显示数量
                condition: "" // 搜索条件（文件名或UUID）
            },
            
            fileData: [], // 文件列表数据
            
            // 分页参数配置
            pageparam: {
                currentPage: 1, // 当前页码
                pageSize: 10, // 每页大小
                total: 0 // 总记录数
            },
            
            // 上传文件表单数据
            uploadFileForm: {}, 
            
            // 表单验证规则
            rules: {
                name: [{ required: true, message: '文件名称不能为空', trigger: 'blur' }], // 名称必填校验
                fileList: [{ required: true, message: '文件不能为空', trigger: 'blur' }] // 文件必选校验
            },
            
            currentUser: "" // 当前登录用户ID
        }
    },
    
    /**
     * 组件创建时的生命周期钩子
     * 初始化面包屑导航、获取当前用户信息并加载文件列表
     */
    created() {
        this.$root.Bus.$emit('initBread', ["公共组件", "文件管理"]); // 设置面包屑导航
        this.currentUser = this.$store.state.userInfo.id; // 获取当前用户ID
        this.getdata(this.searchForm); // 加载文件列表数据
    },
    
    methods: {
        /**
         * 获取文件列表数据并处理分页与时间格式
         * @param {Object} searchParam - 搜索参数对象，包含页码、条数、搜索条件
         */
        getdata(searchParam) {
            this.loading = true // 开启加载状态
            let url = '/autotest/file/list/' + searchParam.page + '/' + searchParam.limit; // 构建API路径
            let param = {
                condition: searchParam.condition, // 搜索条件
                projectId: this.$store.state.projectId // 当前项目ID
            };
            // 执行查询，并对查询后的response数据进行预处理（时间戳转换，更新文件数据，更新分页参数）
            this.$post(url, param, response => {
                let data = response.data;
                // 处理时间格式转换
                for(let i = 0; i < data.list.length; i++){
                    // 时间戳转换为可读格式
                    data.list[i].createTime = timestampToTime(data.list[i].createTime); 
                }
                this.fileData = data.list; // 设置文件列表数据
                this.loading = false; // 关闭加载状态
                
                // 更新分页参数
                this.pageparam.currentPage = this.searchForm.page;
                this.pageparam.pageSize = this.searchForm.limit;
                this.pageparam.total = data.total;
            });
        },

        /**
         * 分页组件回调事件处理
         * @param {Object} parm - 分页参数对象，包含当前页和每页大小
         */
        callFather(parm) {
            this.searchForm.page = parm.currentPage; // 更新当前页码
            this.searchForm.limit = parm.pageSize; // 更新每页条数
            this.getdata(this.searchForm); // 重新获取数据
        },

        /**
         * 搜索按钮点击事件
         * 根据搜索条件重新获取文件列表
         */
        search() {
            this.getdata(this.searchForm);
        },

        /**
         * 重置按钮点击事件
         * 清空搜索条件并重新加载数据
         */
        reset() {
            this.searchForm.condition = ""; // 清空搜索条件
            this.getdata(this.searchForm); // 重新获取数据
        },

        /**
         * 新增文件按钮点击事件
         * 初始化上传表单并打开上传弹窗
         */
        addFile(){
            this.uploadFileForm = {
                name: "", // 文件名称
                description: "", // 文件描述
                fileList: [] // 文件列表
            };
            this.uploadFileVisible = true; // 显示上传弹窗
        },
        
        /**
         * 提交上传表单
         * @param {String} confirm - 表单引用名称
         * @param {Object} form - 表单数据对象
         */
        submitFileForm(confirm, form){
            this.$refs[confirm].validate(valid => {
              if (valid) {
                    let url = '/autotest/file/upload'; // 上传API地址
                    let data = {
                        name: form.name, // 文件名称
                        description: form.description, // 文件描述
                        projectId: this.$store.state.projectId // 项目ID
                    };
                    let file = form.fileList[0]; // 获取上传文件（只获得第一个，每次上传一个）
                    this.$fileUpload(url, file, null, data, response =>{
                        this.$message.success("上传成功"); // 成功提示
                        this.uploadFileVisible = false; // 关闭弹窗
                        this.getdata(this.searchForm); // 刷新列表
                    });
                }else{
                    return false; // 验证失败
                }
            });
        },

        /**
         * 删除文件操作
         * @param {Object} row - 文件行数据对象
         */
        deleteFile(row){
            this.$confirm('确定要删除文件吗? 文件删除可能会导致相关用例无法执行!', '删除提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            })
            .then(() => {
                let url = '/autotest/file/delete'; // 删除API地址
                this.$post(url, {id: row.id}, response => {
                    this.$message.success("删除成功"); // 成功提示
                    this.getdata(this.searchForm); // 刷新列表
                });
            })
            .catch(() => {
                this.$message.success("取消成功"); // 取消提示
            })
        },

        /**
         * 文件上传前的校验处理
         * @param {File} file - 待上传的文件对象
         * @returns {Boolean} 是否允许上传
         */
        beforeUpload(file) {
            if (file.size > 50 * 1024 * 1024) { // 检查文件大小限制（50MB）
                this.$message.warning('文件大小超过50M 无法上传');
                return false;
            }
            return true;
        },
        
        /**
         * 文件数量超出限制处理
         */
        handleExceed() {
            this.$message.warning('一次最多只能上传一个文件');
        },
        
        /**
         * 文件选择后的处理
         * @param {Object} option - 上传选项对象，包含文件信息
         */
        uploadFile(option) {
            this.uploadFileForm.fileList.push(option.file); // 添加文件到表单
            this.uploadFileForm.name = option.file.name; // 自动填充文件名
            this.$refs.uploadFileForm.validateField('fileList'); // 触发文件字段验证
        },
        
        /**
         * 移除已选择的文件
         */
        removeFile() {
            this.uploadFileForm.fileList = []; // 清空文件列表
        }
    }
}
</script>

<style scoped>
/* 文件管理组件样式 */
</style>
