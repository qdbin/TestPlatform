/**
 * 测试报告管理组件 - 用于查看和管理测试执行报告
 * 功能：报告列表展示、搜索筛选、查看详情、删除报告等
 * 作者：自动化测试平台
 * 创建时间：2024
 */
<template>
  <div>
    <!-- 搜索筛选区域 -->
    <el-form :inline="true" :model="searchForm"> <!-- 行内表单：报告名称搜索与操作 -->
        <el-form-item label="">
            <el-input size="small" v-model="searchForm.condition" prefix-icon="el-icon-search" placeholder="请输入报告名称"/> <!-- 报告名称搜索输入框 -->
        </el-form-item>
        <el-form-item>
            <el-button size="small" type="primary" @click="search">搜索</el-button> <!-- 搜索按钮 -->
            <el-button size="small" @click="reset">重置</el-button> <!-- 重置搜索条件 -->
        </el-form-item>
    </el-form>
    
    <!-- 测试报告列表表格 -->
    <el-table size="small" :data="reportData" v-loading="loading"> <!-- 报告数据表格，支持加载状态 -->
        <el-table-column prop="index" label="序号" align="center" width="50px"/> <!-- 报告序号列 -->
        <el-table-column prop="name" label="报告名称" min-width="160px"/> <!-- 报告名称列，最小宽度160px -->
        <el-table-column prop="format" label="报告状态" width="100px"/> <!-- 报告执行状态列 -->
        <el-table-column prop="runProgress" label="执行进度" width="120px"> <!-- 执行进度列 -->
            <template slot-scope="scope">
                <el-progress :percentage="scope.row.progress" :color="scope.row.color"/> <!-- 进度条显示，颜色根据状态变化 -->
            </template>
        </el-table-column>
        <el-table-column prop="total" label="总用例数" width="80px"/> <!-- 总用例数量列 -->
        <el-table-column prop="passCount" label="成功数" width="80px"/> <!-- 成功用例数量列 -->
        <el-table-column prop="passRate" label="成功率" width="80px"/> <!-- 用例成功率列 -->
        <el-table-column prop="username" label="执行人" width="100px"/> <!-- 报告执行人列 -->
        <el-table-column prop="createTime" label="创建时间" width="150px"/> <!-- 报告创建时间列 -->
        <el-table-column fixed="right" align="operation" label="操作" width="100px"> <!-- 操作列，固定在右侧 -->
            <template slot-scope="scope">
                <el-button type="text" size="mini" @click="viewReport(scope.row)">查看</el-button> <!-- 查看报告详情按钮 -->
                <el-button type="text" size="mini" @click="deleteReport(scope.row)">删除</el-button> <!-- 删除报告按钮 -->
            </template>
        </el-table-column>
    </el-table>
    
    <!-- 分页组件 -->
    <Pagination v-bind:child-msg="pageparam" @callFather="callFather"></Pagination> <!-- 分页控件，支持页码和每页数量调整 -->
  </div>
</template>

<script>
// 导入所需组件和工具函数
import Pagination from '../common/components/pagination'  // 分页组件
import {timestampToTime} from '@/utils/util'  // 时间戳转换工具

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
            loading: false,  // 表格加载状态
            
            // 搜索表单数据
            searchForm: {
                page: 1,        // 当前页码
                limit: 10,      // 每页显示数量
                condition: ""   // 搜索条件（报告名称）
            },
            
            reportData: [],  // 测试报告列表数据
            
            // 分页参数
            pageparam: {
                currentPage: 1,  // 当前页码
                pageSize: 10,    // 每页大小
                total: 0         // 总记录数
            },
        }
    },
    
    /**
     * 组件创建时的生命周期钩子
     * 初始化面包屑导航并获取报告数据
     */
    created() {
        this.$root.Bus.$emit('initBread', ["测试追踪", "测试报告"]);
        this.getdata(this.searchForm)
    },
    
    methods: {
        /**
         * 获取测试报告列表数据并处理状态格式化
         * @param {Object} searchParam - 搜索参数对象
         * @param {number} searchParam.page - 页码
         * @param {number} searchParam.limit - 每页数量
         * @param {string} searchParam.condition - 搜索条件
         */
        getdata(searchParam) {
            this.loading = true;
            let url = '/autotest/report/list/' + searchParam.page + '/' + searchParam.limit;
            let param = {
                projectId: this.$store.state.projectId,
                condition: searchParam.condition
            };
            this.$post(url, param, response => {
                let data = response.data;
                // 处理报告数据：时间格式化、状态格式化、序号计算
                for(let i =0; i<data.list.length; i++){
                    data.list[i].createTime = timestampToTime(data.list[i].createTime); // 时间格式化
                    let status = data.list[i].status
                    // 根据报告状态设置显示格式和颜色
                    if(status === 'success'){
                        data.list[i].format = 'SUCCESS';
                        data.list[i].color = '#67C23A';  // 绿色：成功
                    }else if(status === 'fail'){
                        data.list[i].format = 'FAIL';
                        data.list[i].color = '#E6A23C';  // 橙色：失败
                    }else if(status === 'error'){
                        data.list[i].format = 'ERROR';
                        data.list[i].color = '#F56C6C';  // 红色：错误
                    }else if(status === 'skip'){
                        data.list[i].format = 'SKIP';
                        data.list[i].color = '#535457';  // 灰色：跳过
                    }else if(status === 'prepared'){
                        data.list[i].format = '等待执行';
                        data.list[i].color = '#409EFF';  // 蓝色：等待执行
                    }else if(status === 'running'){
                        data.list[i].format = "RUNNING";
                        data.list[i].color = '#409EFF';  // 蓝色：执行中
                    }else if(status === 'discontinue'){
                        data.list[i].format = "已终止";
                        data.list[i].color = '#535457';  // 灰色：已终止
                    }
                    data.list[i].index = (searchParam.page-1) * searchParam.limit + i+1; // 计算序号
                }
                this.reportData = data.list;
                this.loading = false;
                // 更新分页信息
                this.pageparam.currentPage = this.searchForm.page;
                this.pageparam.pageSize = this.searchForm.limit;
                this.pageparam.total = data.total;
            });
        },
        
        /**
         * 分页组件回调函数：处理页码和每页数量变化
         * @param {Object} param - 分页参数
         * @param {number} param.currentPage - 当前页码
         * @param {number} param.pageSize - 每页数量
         */
        callFather(param) {
            this.searchForm.page = param.currentPage;
            this.searchForm.limit = param.pageSize;
            this.getdata(this.searchForm);
        },
        
        /**
         * 搜索按钮：根据搜索条件刷新报告列表
         */
        search() {
            this.getdata(this.searchForm);
        },
        
        /**
         * 重置按钮：清空搜索条件并重新加载报告列表
         */
        reset() {
            this.searchForm.condition = "";
            this.getdata(this.searchForm);
        },
        
        /**
         * 查看报告详情：跳转到报告详情页面
         * @param {Object} row - 报告行数据
         * @param {string} row.id - 报告ID
         */
        viewReport(row){
            this.$router.push({path: '/report/testReport/detail/' + row.id});
        },
        
        /**
         * 删除报告：确认后删除指定报告并刷新列表
         * @param {Object} row - 报告行数据
         * @param {string} row.id - 报告ID
         */
        deleteReport(row){
            this.$confirm('确定要删除报告吗?', '删除提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            })
            .then(() => {
                let url = '/autotest/report/delete';
                this.$post(url, {id: row.id}, response => {
                    this.$message.success("删除成功");
                    this.getdata(this.searchForm); // 刷新报告列表
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
/* 测试报告管理页面样式 */
</style>