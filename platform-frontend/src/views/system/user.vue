/**
 * 系统管理  用户管理
 */
<template>
  <div>
    <!-- 搜索筛选 -->
    <el-form :inline="true" :model="searchForm">
        <el-form-item label="">
            <el-input size="small" v-model="searchForm.condition" prefix-icon="el-icon-search" placeholder="请输入用户名"/>
        </el-form-item>
        <el-form-item>
            <el-button size="small" type="primary" @click="search">搜索</el-button>
            <el-button size="small" @click="reset">重置</el-button>
        </el-form-item>
        <el-form-item style="float: right">
            <el-button size="small" type="primary" icon="el-icon-plus" @click="addUser">新增用户</el-button>
        </el-form-item>
    </el-form>
    <!--列表-->
    <el-table size="small" :data="userData" v-loading="loading">
        <el-table-column prop="index" label="序号" width="50px" align="center"/>
        <el-table-column prop="username" label="用户名" min-width="100px" :show-overflow-tooltip="true"/>
        <el-table-column prop="account" label="登录账号" :show-overflow-tooltip="true"/>
        <el-table-column prop="email" label="邮箱" min-width="200px" :show-overflow-tooltip="true"/>
        <el-table-column prop="createTime" label="注册时间" width="150px"/>
        <el-table-column fixed="right" align="operation" label="操作" width="100px">
            <template slot-scope="scope">
                <el-button type="text" size="mini" @click="editUser(scope.row)">编辑</el-button>
                <el-button type="text" size="mini" @click="deleteUser(scope.row)">删除</el-button>
            </template>
        </el-table-column>
    </el-table>
    <!-- 分页组件 -->
    <Pagination v-bind:child-msg="pageparam" @callFather="callFather"/>
    <!-- 新增用户界面 -->
    <el-dialog :title="title" :visible.sync="userVisible" width="600px" destroy-on-close>
        <el-form label-width="120px" style="padding-right: 30px;" :model="userForm" label-position="top" :rules="rules" ref="userForm">
            <el-form-item label="项目名称" prop="projectName">
                <el-input size="small" disabled style="width: 100%" v-model="userForm.projectName"/>
            </el-form-item>
            <el-form-item label="选择用户" prop="userIds">
                <el-select size="small" style="width: 100%" v-model="userForm.userIds" :disabled="userForm.isEdit" multiple filterable placeholder="输入登录账号查找" 
                remote reserve-keyword :remote-method="searchUser" :loading="uLoading">
                  <el-option v-for="item in userList" :key="item.id" :label="item.username" :value="item.id"/>
                </el-select>
            </el-form-item>
            <el-form-item label="选择角色" prop="roleIds">
                <el-select size="small" style="width: 100%" v-model="userForm.roleIds" multiple filterable placeholder="请选择项目角色">
                    <el-option v-for="item in roleList" :key="item.id" :label="item.name" :value="item.id"/>
                </el-select>
            </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
            <el-button size="small" @click="userVisible=false">取消</el-button>
            <el-button size="small" type="primary" @click="submitUserForm('userForm', userForm)">确定</el-button>
        </div>
    </el-dialog>
  </div>
</template>

<script>
import Pagination from '../common/components/pagination'
import {timestampToTime} from '@/utils/util'
export default {
    // 注册子组件
    components: {
        Pagination
    },
    // 页面状态、搜索/分页参数、当前项目、弹窗表单及校验
    data() {
        return{
            title: "新增项目用户",
            uLoading: false,
            loading:false,
            userVisible: false,
            searchForm: {
                page: 1,
                limit: 10,
                condition: ""
            },
            userList:[],
            roleList: [],
            userData: [],
            pageparam: {
                currentPage: 1,
                pageSize: 10,
                total: 0
            },
            currentProject: {
              projectId: "",
              projectName: ""
            },
            userForm: {
              isEdit: false
            },
            rules: {
                projectName: [{ required: true, message: '项目名称不能为空', trigger: 'blur' }],
                userIds: [{ required: true, message: '用户不能为空', trigger: 'blur' }],
                roleIds: [{ required: true, message: '角色不能为空', trigger: 'blur' }],
            }
        }
    },
    // 初始化：设置面包屑，拉取列表、角色与项目信息
    created() {
        this.$root.Bus.$emit('initBread', ["系统管理", "用户管理"]); // 更新面包屑导航
        this.getdata(this.searchForm); // 拉取用户列表
        this.getRoles(); // 拉取当前项目角色
        this.getProject(); // 拉取当前项目信息
    },
    // 业务方法
    methods: {
        // 获取用户列表并进行分页赋值
        getdata(searchParam) {
            this.loading = true
            let url = '/autotest/project/user/list/' + searchParam.page + '/' + searchParam.limit;
            let param = {
                condition: searchParam.condition,
                projectId: this.$store.state.projectId
            };
            this.$post(url, param, response => {
                let data = response.data;
                for(let i =0; i<data.list.length; i++){
                    data.list[i].createTime= timestampToTime(data.list[i].createTime); // 时间格式化
                    data.list[i].index = (searchParam.page-1) * searchParam.limit + i+1; // 计算序号
                }
                this.userData = data.list;
                this.loading = false;
                // 分页赋值
                this.pageparam.currentPage = this.searchForm.page;
                this.pageparam.pageSize = this.searchForm.limit;
                this.pageparam.total = data.total;
            });
        },
        // 获取当前项目角色
        getRoles() {
          let url = "/autotest/project/role/list?projectId=" + this.$store.state.projectId;
          this.$get(url, response => {
            this.roleList = response.data;
          });
        },
        // 获取当前项目信息
        getProject(){
          let url = "/autotest/project/info?projectId=" + this.$store.state.projectId;
           this.$get(url, response => {
            this.currentProject.projectId = response.data.id;
            this.currentProject.projectName = response.data.name;
          });
        },
        // 接收分页组件回传并刷新列表
        callFather(parm) {
            this.searchForm.page = parm.currentPage;
            this.searchForm.limit = parm.pageSize;
            this.getdata(this.searchForm);
        },
        // 搜索按钮，按条件查询
        search() {
            this.getdata(this.searchForm);
        },
        // 重置搜索条件并刷新
        reset() {
            this.searchForm.condition = "";
            this.getdata(this.searchForm);
        },
        // 打开“新增项目用户”弹窗并重置表单
        addUser(){
            this.title = "新增项目用户";
            this.userList = [];
            this.userForm = {
              isEdit: false,
              projectId: this.currentProject.projectId,
              projectName: this.currentProject.projectName
            };
            this.userVisible = true;
        },
        submitUserForm(confirm, form){
            this.$refs[confirm].validate(valid => {
                if (valid) {
                    let url = '/autotest/project/user/save';
                    this.$post(url, form, response =>{ // 表单校验通过后提交保存
                        this.$message.success("保存成功"); // 成功提示
                        this.userVisible = false; // 关闭弹窗
                        this.getdata(this.searchForm); // 刷新列表
                    });
                }else{
                    return false;
                }
            });
        },
        // 远程搜索用户（按账号）
        searchUser(query){
          this.uLoading = true;
          let url = '/autotest/user/query?account=' + query;
          this.$get(url, response => {
            this.uLoading = false;
            this.userList = response.data;
          });
        },
        // 删除项目下用户（二次确认）
        deleteUser(row){
            this.$confirm('确定要删除该项目下的用户吗?', '删除提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            })
            .then(() => {
                let url = '/autotest/project/user/delete';
                let param = {
                  projectId: this.$store.state.projectId,
                  userId: row.id
                }
                this.$post(url, param, response => {
                    this.$message.success("删除成功"); // 操作成功提示
                    this.getdata(this.searchForm); // 刷新列表
                });
            })
            .catch(() => {
                this.$message.success("取消成功"); // 取消提示
            })
        },
        // 打开“编辑项目用户”，预填用户与角色信息
        editUser(row){
          this.title = "编辑项目用户";
          this.userList = [
            {id: row.id, username: row.username}
          ];
          this.userForm = {
            isEdit: true,
            projectId: this.currentProject.projectId,
            projectName: this.currentProject.projectName,
            userIds: [row.id],
            roleIds: [],
          };
          let url = "/autotest/user/role/list?projectId=" + this.currentProject.projectId + "&userId=" + row.id;
          this.$get(url, response =>{
            this.userForm.roleIds = response.data;
          });
          this.userVisible = true;
        },
    }
}
</script>

<style scoped>
/* 页面样式作用域：当前为空，后续按需补充 */
</style>