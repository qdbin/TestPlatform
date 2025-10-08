/**
 * 系统管理  角色管理
 */
<template>
  <div>
    <!-- 搜索筛选 -->
    <el-form :inline="true" :model="searchForm">
        <el-form-item label="">
            <el-input size="small" v-model="searchForm.condition" prefix-icon="el-icon-search" placeholder="请输入角色名"/>
        </el-form-item>
        <el-form-item>
            <el-button size="small" type="primary" @click="search">搜索</el-button>
            <el-button size="small" @click="reset">重置</el-button>
        </el-form-item>
    </el-form>
    <!--列表-->
    <el-table size="small" :data="roleData" v-loading="loading">
        <el-table-column prop="index" label="序号" width="50px" align="center"/>
        <el-table-column prop="name" label="角色名" min-width="150px"/>
        <el-table-column prop="projectName" label="所属项目" min-width="200px"/>
        <el-table-column prop="createTime" label="创建时间" width="150px"/>
        <el-table-column fixed="right" align="operation" label="操作" width="100px">
            <template slot-scope="scope">
                <el-button type="text" size="mini" @click="viewUser(scope.row.id)">查看用户</el-button>
            </template>
        </el-table-column>
    </el-table>
    <!-- 分页组件 -->
    <Pagination v-bind:child-msg="pageparam" @callFather="callFather"/>
    <!-- 新增用户界面 -->
    <el-dialog title="查看用户" :visible.sync="viewUserVisible" width="800px" destroy-on-close>
        <el-form :inline="true" :model="searchUserForm">
            <el-form-item label="">
                <el-input size="small" v-model="searchUserForm.condition" prefix-icon="el-icon-search" placeholder="用户名、账号"/>
            </el-form-item>
            <el-form-item>
                <el-button size="small" type="primary" @click="searchUser">搜索</el-button>
                <el-button size="small" @click="resetUser">重置</el-button>
            </el-form-item>
        </el-form>
        <el-table size="small" :data="userData" v-loading="userLoading">
            <el-table-column prop="index" label="序号" width="50px" align="center"/>
            <el-table-column prop="username" label="用户名"/>
            <el-table-column prop="account" label="用户账号"/>
            <el-table-column prop="createTime" label="创建时间" width="150px"/>
            <el-table-column fixed="right" align="operation" label="操作" width="80px">
                <template slot-scope="scope">
                    <el-button type="text" size="mini" @click="deleteUser(scope.row)">删除用户</el-button>
                </template>
            </el-table-column>
        </el-table>
        <!-- 分页组件 -->
        <Pagination v-bind:child-msg="userPageparam" @callFather="userCallFather"/>
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
    // 页面状态、搜索/分页参数、弹窗与分页配置
    data() {
        return{
            loading:false,
            userLoading: false,
            viewUserVisible: false,
            searchForm: {
                page: 1,
                limit: 10,
                condition: ""
            },
            searchUserForm: {
                page: 1,
                limit: 10,
                condition: "",
                roleId: ""
            },
            userData: [],
            roleData: [],
            pageparam: {
                currentPage: 1,
                pageSize: 10,
                total: 0
            },
            userPageparam: {
                currentPage: 1,
                pageSize: 10,
                total: 0
            }
        }
    },
    // 初始化：设置面包屑并拉取角色列表
    created() {
        this.$root.Bus.$emit('initBread', ["系统管理", "角色管理"]); // 更新面包屑导航
        this.getRole(this.searchForm); // 拉取角色列表
    },
    // 业务方法
    methods: {
        // 拉取角色列表并进行分页赋值
        getRole(searchParam) {
            this.loading = true
            let url = '/autotest/role/list/' + searchParam.page + '/' + searchParam.limit;
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
                this.roleData = data.list;
                this.loading = false;
                // 分页赋值
                this.pageparam.currentPage = this.searchForm.page;
                this.pageparam.pageSize = this.searchForm.limit;
                this.pageparam.total = data.total;
            });
        },
        // 拉取角色下的用户列表
        getUser(searchParam) {
          this.userLoading = true;
          let url = "/autotest/role/user/list/" + searchParam.page + '/' + searchParam.limit;
          let param = {
            condition: searchParam.condition,
            roleId: searchParam.roleId
          }
          this.$post(url, param, response => {
                let data = response.data;
                for(let i =0; i<data.list.length; i++){
                    data.list[i].createTime= timestampToTime(data.list[i].createTime); // 时间格式化
                    data.list[i].index = (searchParam.page-1) * searchParam.limit + i+1; // 计算序号
                }
                this.userData = data.list;
                this.userLoading = false;
                // 分页赋值
                this.userPageparam.currentPage = this.searchUserForm.page;
                this.userPageparam.pageSize = this.searchUserForm.limit;
                this.userPageparam.total = data.total;
            });
        },
        // 打开“查看用户”弹窗并拉取用户
        viewUser(roleId){
          this.searchUserForm.roleId =roleId;
          this.viewUserVisible = true;
          this.getUser(this.searchUserForm);
        },
        // 角色分页回传
        callFather(parm) {
            this.searchForm.page = parm.currentPage;
            this.searchForm.limit = parm.pageSize;
            this.getRole(this.searchForm);
        },
        // 弹窗内用户分页回传
        userCallFather(parm) {
            this.searchUserForm.page = parm.currentPage;
            this.searchUserForm.limit = parm.pageSize;
            this.getUser(this.searchUserForm);
        },
        // 搜索角色
        search() {
            this.getRole(this.searchForm);
        },
        // 搜索角色下用户
        searchUser() {
            this.getUser(this.searchUserForm);
        },
        // 重置角色搜索条件
        reset() {
            this.searchForm.condition = "";
            this.getRole(this.searchForm);
        },
        // 重置弹窗内用户搜索条件
        resetUser() {
            this.searchUserForm.condition = "";
            this.getRole(this.searchUserForm);
        },
        // 删除用户角色权限（二次确认）
        deleteUser(row){
            this.$confirm('确定要删除该用户的角色权限吗?', '删除提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            })
            .then(() => {
                let url = '/autotest/role/user/delete';
                let param = {
                  roleId: this.searchUserForm.roleId,
                  userId: row.id
                }
                this.$post(url, param, response => {
                    this.$message.success("删除成功"); // 操作成功提示
                    this.getUser(this.searchUserForm); // 刷新用户列表
                });
            })
            .catch(() => {
                this.$message.success("取消成功"); // 取消提示
            })
        },
    }
}
</script>

<style scoped>
/* 页面样式作用域：当前为空，后续按需补充 */
</style>