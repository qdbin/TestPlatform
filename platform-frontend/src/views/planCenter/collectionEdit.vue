/**
 * 测试集合编辑组件
 * 功能：创建和编辑测试集合，管理集合中的测试用例，支持拖拽排序
 * 作者：自动化测试平台
 * 创建时间：2024
 */
<template>
  <div>
    <!-- 页面头部（包含标题、取消和保存按钮） -->
    <page-header title="编辑集合" :cancel="cancelAdd" :save="saveAdd"/>
    
    <!-- 集合编辑表单 -->
    <el-form ref="collectionForm" :rules="rules" :model="collectionForm" label-width="80px">
        <!-- 第一行：集合名称、迭代版本、执行设备 -->
        <el-row :gutter="40">
            <!-- 集合名称输入框 -->
            <el-col :span="10">
                <el-form-item size="small" label="集合名称" prop="name">
                    <el-input style="width: 100%" v-model="collectionForm.name" placeholder="请输入集合名称"/>
                </el-form-item>
            </el-col>
            <!-- 迭代版本选择框 -->
            <el-col :span="6">
                <el-form-item size="small" label="迭代版本" prop="versionId">
                    <el-select style="width: 100%" v-model="collectionForm.versionId" placeholder="请选择版本">
                        <el-option v-for="item in versionList" :key="item.id" :label="item.name" :value="item.id"/>
                    </el-select>
                </el-form-item>
            </el-col>
            <!-- 执行设备选择框（带提示信息） -->
            <el-col :span="8">
                <el-form-item size="small" label="执行设备" prop="deviceId">
                    <el-select style="width: 90%" v-model="collectionForm.deviceId" clearable placeholder="请选择执行设备">
                        <el-option v-for="item in deviceList" :key="item.id" :label="item.name" :value="item.id"/>
                    </el-select>
                    <el-tooltip style="width:5%" content="当前集合包含APP测试时 执行设备必选" placement="bottom">
                        <i class="el-icon-info"></i>
                    </el-tooltip>
                </el-form-item>
            </el-col>
        </el-row>
        
        <!-- 第二行：集合描述 -->
        <el-row :gutter="40">
            <el-col :span="16">
                <el-form-item size="small" label="集合描述" style="margin-bottom:0px">
                    <el-input style="width: 100%" :autosize="{ minRows: 4}" type="textarea" clearable placeholder="请输入集合描述" v-model="collectionForm.description" maxlength="200" show-word-limit/>
                </el-form-item>
            </el-col>
        </el-row>
        
        <!-- 集合用例列表（支持拖拽排序） -->
        <el-form-item style="margin-left:-80px;" prop="collectionCases"/>
        <el-table :data="collectionForm.collectionCases" row-key="id" class="sort-table" size="small">
            <!-- 拖拽排序列 -->
            <el-table-column label="" width="60px">
                <template>
                    <i class="iconfont icon-paixu"  @mousedown="rowDrop" style="font-size: 24px"/>
                </template>
            </el-table-column>
            <!-- 序号列 -->
            <el-table-column label="序号" prop="index" width="100px">
            </el-table-column>
            <!-- 用例名称列 -->
            <el-table-column label="用例名称" prop="caseName" min-width="180px">
            </el-table-column>
            <!-- 用例模块列 -->
            <el-table-column label="用例模块" prop="caseModule">
            </el-table-column>
            <!-- 用例类型列（APP类型显示系统信息） -->
            <el-table-column label="用例类型">
                <template slot-scope="scope">
                    <span v-if="scope.row.caseType==='APP'">{{scope.row.caseType}}({{scope.row.caseSystem}})</span>
                    <span v-else>{{scope.row.caseType}}</span>
                </template>
            </el-table-column>
            <!-- 操作列（删除按钮） -->
            <el-table-column label="操作" width="120px">
                <template slot-scope="scope">
                    <el-button size="mini" type="text" @click="deleteCollectionCase(scope.$index)">删除</el-button>
                </template>
            </el-table-column>
        </el-table>
        
        <!-- 新增用例按钮 -->
        <el-button size="small" icon="el-icon-plus" type="text" @click="selectCaseVisible=true">新增</el-button>  
    </el-form>
    
    <!-- 选择用例弹框 -->
    <el-dialog title="选择用例" :visible.sync="selectCaseVisible" width="800px" destroy-on-close>
        <select-case :selections="selections" :selectCaseVisible="selectCaseVisible"/>
        <div slot="footer" class="dialog-footer">
            <el-button size="small" @click="selectCaseVisible=false">取消</el-button>
            <el-button size="small" type="primary" @click="selectCaseSave">保存</el-button>
        </div>
    </el-dialog>
  </div>
</template>

<script>
// 导入所需组件和工具函数
import Sortable from 'sortablejs'  // 拖拽排序库
import PageHeader from '../common/components/pageheader'  // 页面头部组件
import SelectCase from './common/selectCase'  // 用例选择组件
import {getUUID} from '@/utils/util'  // UUID生成工具

export default {
    // 注册子组件
    components:{PageHeader, SelectCase},
    
    /**
     * 组件数据定义
     * @returns {Object} 组件的响应式数据对象
     */
    data() {
        return{
            selections: [],  // 选中的用例列表
            selectCaseVisible: false,  // 用例选择弹框显示状态
            
            // 集合表单数据
            collectionForm: {
                id: "",                 // 集合ID
                name: "",               // 集合名称
                deviceId: null,         // 执行设备ID
                versionId: "",          // 版本ID
                description: "",        // 集合描述
                collectionCases: []     // 集合包含的用例列表
            },
            
            versionList: [],  // 版本列表
            deviceList: [],   // 设备列表
            
            // 表单验证规则
            rules: {
                name: [{ required: true, message: '集合名称不能为空', trigger: 'blur' }],
                versionId: [{ required: true, message: '版本不能为空', trigger: 'blur' }],
                collectionCases: [{ required: true, message: '请至少选择一条测试用例', trigger: 'blur' }],
            }
        }
    },
    
    /**
     * 组件创建时的生命周期钩子
     * 初始化面包屑导航并获取相关数据
     */
    created() {
        this.$root.Bus.$emit('initBread', ["计划中心", "测试集合", "集合编辑"]);
        this.getDetail(this.$route.params);
        this.getVersion();
        this.getDevice();
    },
    
    methods: {
        /**
         * 获取设备列表
         * 用于执行设备选择框的数据源
         */
        getDevice(){
            let url = "/autotest/device/list";
            this.$post(url, {projectId: this.$store.state.projectId}, response => {
                this.deviceList = response.data;
            });
        },
        
        /**
         * 行拖拽功能实现
         * 使用Sortable.js实现表格行的拖拽排序
         */
        rowDrop () {
            // 找到要拖拽元素的父容器
            const tbody = document.querySelector('.sort-table tbody');
            const _this = this;
            Sortable.create(tbody, {
                // 指定父元素下可被拖拽的子元素
                draggable: ".el-table__row",
                onEnd ({ newIndex, oldIndex }) {
                    // 移动数组中的元素位置
                    const currRow = _this.collectionForm.collectionCases.splice(oldIndex, 1)[0];
                    _this.collectionForm.collectionCases.splice(newIndex, 0, currRow);
                    // 重新排序序号
                    _this.sortCollectiionCase();
                }
            });
        },
        
        /**
         * 重新排序集合用例
         * 更新用例列表中每个用例的序号
         */
        sortCollectiionCase(){
            for(let i=0; i<this.collectionForm.collectionCases.length; i++){
                this.collectionForm.collectionCases[i].index = i+1;
            }
        },
        
        /**
         * 保存用例选择
         * 将选中的用例添加到集合中
         */
        selectCaseSave(){
            for(let i=0;i<this.selections.length;i++){
                let collectionCase = {
                    id: getUUID(),  // 生成唯一ID
                    index: this.collectionForm.collectionCases.length+1,  // 设置序号
                    caseId: this.selections[i].id,
                    caseName: this.selections[i].name,
                    caseModule: this.selections[i].moduleName,
                    caseType: this.selections[i].type,
                    caseSystem: this.selections[i].system,
                }
                this.collectionForm.collectionCases.push(collectionCase);
            }
            // 清空选择列表并关闭弹框
            this.selections.splice(0, this.selections.length);
            this.selectCaseVisible = false;
        },
        
        /**
         * 删除集合用例
         * @param {number} index - 要删除的用例在列表中的索引
         */
        deleteCollectionCase(index){
            this.collectionForm.collectionCases.splice(index, 1);
            // 重新排序剩余用例的序号
            for(let i=0; i<this.collectionForm.collectionCases.length; i++){
                this.collectionForm.collectionCases[i].index = i+1;
            }
        },
        
        /**
         * 获取版本列表
         * 用于版本选择框的数据源
         */
        getVersion(){
            let url = "/autotest/version/list/" + this.$store.state.projectId;
            this.$get(url, response => {
                this.versionList = response.data;
            });
        },
        
        /**
         * 获取集合详情
         * @param {Object} param - 路由参数
         * @param {string} param.collectionId - 集合ID（编辑模式时存在）
         */
        getDetail(param){
            if (param.collectionId){
                let url = "/autotest/collection/detail/" + param.collectionId;
                this.$get(url, response => {
                    this.collectionForm = response.data;
                });
            }
        },
        
        /**
         * 取消编辑
         * 返回到测试集合列表页面
         */
        cancelAdd(){
            this.$router.push({path: '/planManage/testCollection'})
        },
        
        /**
         * 保存集合
         * 验证表单并提交集合数据
         */
        saveAdd(){
            this.$refs["collectionForm"].validate(valid => {
                if (valid) {
                    // 设置项目ID并重新排序用例
                    this.collectionForm.projectId = this.$store.state.projectId;
                    for(let i=0; i<this.collectionForm.collectionCases.length; i++){
                        this.collectionForm.collectionCases[i].index = i+1;
                    }
                    
                    // 提交保存请求
                    let url = '/autotest/collection/save';
                    this.$post(url, this.collectionForm, response =>{
                        this.$message.success("保存成功");
                        this.$router.push({path: '/planManage/testCollection'});
                    });
                }else{
                    return false;
                }
            });
        },
    }
}
</script>

<style scoped>
/* 组件样式（当前为空，可根据需要添加自定义样式） */
</style>
