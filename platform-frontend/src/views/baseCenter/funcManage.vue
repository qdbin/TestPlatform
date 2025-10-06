/**
 * 公共组件  函数管理
 */
<template>
  <div>
    <!-- 搜索筛选 -->
    <el-form :inline="true" :model="searchForm">
        <el-form-item label="">
            <el-input size="small" v-model="searchForm.condition" prefix-icon="el-icon-search" placeholder="请输入函数名称"/>
        </el-form-item>
        <el-form-item>
            <el-button size="small" type="primary" @click="search">搜索</el-button>
            <el-button size="small" @click="reset">重置</el-button>
        </el-form-item>
        <el-form-item style="float: right">
            <el-button size="small" type="primary" icon="el-icon-plus" @click="addFunction">新增函数</el-button>
        </el-form-item>
    </el-form>

    <!-- 函数数据表格 -->
    <el-table size="small" :data="functionData" v-loading="loading">
        <el-table-column prop="index" label="序号" align="center" width="50px"/>
        <el-table-column prop="name" label="函数名称" min-width="120px" :show-overflow-tooltip="true"/>
        <el-table-column prop="from" label="函数类型">
            <template slot-scope="scope">
                <span v-if="scope.row.from==='system'">系统内置函数</span>
                <span v-if="scope.row.from==='custom'">用户定义函数</span>
            </template>
        </el-table-column>
        <el-table-column prop="expression" label="调用方式" min-width="200px" :show-overflow-tooltip="true"/>
        <el-table-column prop="description" label="函数说明" min-width="200px" :show-overflow-tooltip="true"/>
        <el-table-column prop="username" label="创建人"/>
        <el-table-column prop="updateTime" label="更新时间" width="150px"/>
        <el-table-column fixed="right" align="operation" label="操作" width="100px">
            <template slot-scope="scope">
                <el-button type="text" size="mini" @click="viewFunction(scope.row)">查看</el-button>
                <el-button type="text" size="mini" v-if="scope.row.createUser ===currentUser" @click="deleteFunction(scope.row)">删除</el-button>
            </template>
        </el-table-column>
    </el-table>
    <!-- 分页组件 -->
    <Pagination v-bind:child-msg="pageparam" @callFather="callFather"></Pagination>
  </div>
</template>

<script>
import Pagination from '../common/components/pagination'    // 分页组件
import {timestampToTime} from '@/utils/util'    // 时间戳转换工具
export default {
    components: {
        Pagination
    },
    data() {
        return {
            loading: false, // 表格加载状态

            // 搜索表单数据
            searchForm: {
                condition: "", // 搜索条件（函数名称）
                page: 1, // 当前页码
                limit: 10 // 每页条数
            },

            functionData: [], // 函数列表数据

            // 分页配置参数
            pageparam: {
                currentPage: 1, // 当前页码
                pageSize: 10, // 每页大小
                total: 0 // 总记录数
            },

            currentUser: "", // 当前用户名
        }
    },
    created() {
        this.$root.Bus.$emit('initBread', ["公共组件", "函数管理"]); // 设置面包屑导航
        this.currentUser = this.$store.state.userInfo.id;
        this.getdata(this.searchForm); // 加载函数列表数据
    },
    methods: {
        // 获取列表数据方法
        getdata(searchParam) {
            // 获取报告
            this.loading = true;    // 开启加载状态
            let url = '/autotest/function/list/' + searchParam.page + '/' + searchParam.limit;// 函数列表API地址
            let param = {
                projectId: this.$store.state.projectId,
                condition: searchParam.condition
            };
            this.$post(url, param, response => {
                let data = response.data;
                // 处理列表数据：添加序号和格式化时间
                for(let i =0; i<data.list.length; i++){
                    data.list[i].updateTime = timestampToTime(data.list[i].updateTime);
                    data.list[i].index = (searchParam.page-1) * searchParam.limit + i+1;
                }
                this.functionData = data.list; // 设置函数列表数据
                this.loading = false; // 关闭加载状态
                // 更新分页信息
                this.pageparam.currentPage = this.searchForm.page;
                this.pageparam.pageSize = this.searchForm.limit;
                this.pageparam.total = data.total;
            });
        },
        // 分页回调处理函数
        callFather(param) {
            this.searchForm.page = param.currentPage;
            this.searchForm.limit = param.pageSize;
            this.getdata(this.searchForm);
        },
        // 搜索按钮
        search() {
            this.getdata(this.searchForm);
        },
        // 重置按钮
        reset() {
            this.searchForm.condition = "";
            this.getdata(this.searchForm);
        },
        // 新增函数
        addFunction(){
            this.$router.push({path: '/common/funcManage/add'});
        },
        // 查看函数
        viewFunction(row){
            this.$router.push({path: '/common/funcManage/edit/' + row.id});
        },
        // 删除函数
        deleteFunction(row){
            this.$confirm('函数删除后相关用例无法执行 确定要删除函数吗?', '删除提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            })
            .then(() => {
                let url = '/autotest/function/delete';
                this.$post(url, {id: row.id}, response => {
                    this.$message.success("删除成功");
                    this.getdata(this.searchForm);
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

</style>
