/**
 * 测试报告详情（展示报告状态、集合/用例/步骤层级数据）
 */
<template>
  <div>
    <!-- 报告基本信息头部 -->
    <div class="report-header">
        <!-- 报告名称 -->
        <div style="font-size: 20px">
            <span>{{report.name}}</span>
        </div>
        <!-- 执行状态和进度条 -->
        <div style="display: flex; margin-left: 20px;font-size:12px">
            <span style="margin-right: 10px">执行状态: {{report.format}}</span>
            <el-progress style="width:120px;" :percentage="report.progress" :color="report.color"/>
        </div>
    </div>
    
    <!-- 报告统计信息 -->
    <div class="report-base">
        <!-- 第一行：成功、失败、错误统计 -->
        <el-row :gutter="40" style="margin: 20px -20px">
            <el-col :span="3">
                <span>成功： <span class="lm-success">{{report.passCount}}</span></span>
            </el-col>
            <el-col :span="3">
                <span>失败： <span class="lm-fail">{{report.failCount}}</span></span>
            </el-col>
            <el-col :span="3">
                <span>错误： <span class="lm-error">{{report.errorCount}}</span></span>
            </el-col>
        </el-row>
        <!-- 第二行：时间信息 -->
        <el-row :gutter="40" style="margin: 20px -20px">
            <el-col :span="5">
                <span>开始时间： {{report.startTime}}</span>
            </el-col>
            <el-col :span="5">
                <span>结束时间： {{report.endTime}}</span>
            </el-col>
            <el-col :span="5">
                <span>执行时长： {{report.during}}</span>
            </el-col>
        </el-row>  
    </div>
    
    <!-- 测试集合结果列表（三层嵌套表格：集合 -> 用例 -> 步骤） -->
    <el-table size="small" :data="report.collectionList" stripe v-loading="loading">
        <!-- 集合展开列：显示该集合下的用例列表 -->
        <el-table-column type="expand" width="40px">
            <template slot-scope="collectionData">
                <div style="padding-left: 40px">
                <!-- 用例列表表格 -->
                <el-table size="mini" :data="collectionData.row.caseList" stripe>
                    <!-- 用例展开列：显示该用例下的步骤列表 -->
                    <el-table-column type="expand" width="40px">
                        <template slot-scope="caseData">
                            <div style="padding-left: 40px">
                            <!-- 步骤详情表格 -->
                            <el-table size="mini" :data="caseData.row.transList" stripe>
                                <!-- 步骤执行结果 -->
                                <el-table-column label="执行结果" prop="status" width="120px">
                                    <template slot-scope="scope">
                                        <span v-if="scope.row.status==='success'" class="lm-success"><i class="el-icon-success"/> 成功</span>
                                        <span v-if="scope.row.status==='fail'" class="lm-fail"><i class="el-icon-warning"/> 失败</span>
                                        <span v-if="scope.row.status==='error'" class="lm-error"><i class="el-icon-error"/> 错误</span>
                                    </template>
                                </el-table-column>
                                <!-- 根据用例类型显示不同的列名：API接口名称 或 WEB操作名称 -->
                                <el-table-column :label="caseData.row.caseType ==='API'?'接口名称':'操作名称'" prop="transName" min-width="150px"/>
                                <!-- 根据用例类型显示不同的内容：API接口地址 或 WEB操作元素 -->
                                <el-table-column :label="caseData.row.caseType ==='API'?'接口地址':'操作元素'" prop="content" min-width="200px"/>
                                <!-- 步骤描述 -->
                                <el-table-column label="步骤描述" prop="description" min-width="200px"/>
                                <!-- 执行日志查看 -->
                                <el-table-column label="执行日志" prop="execLog" width="120px">
                                    <template slot-scope="scope">
                                        <el-button size="small" type="text" @click="viewLog(scope.row.execLog)">查看日志</el-button>
                                    </template>
                                </el-table-column>
                                <!-- API用例显示响应时长 -->
                                <el-table-column label="响应时长" prop="during" v-if="caseData.row.caseType ==='API'" width="120px"/>
                                <!-- WEB/APP用例显示执行截图 -->
                                <el-table-column label="执行截图" prop="screenshotList" v-else width="120px">
                                    <template slot-scope="scope">
                                        <el-button v-if="scope.row.screenshotList.length !== 0" size="small" type="text" @click="scope.row.showViewer=true">查看</el-button>
                                        <el-image-viewer v-if="scope.row.showViewer" :on-close="()=>{scope.row.showViewer=false}" :url-list="scope.row.screenshotList"/>
                                    </template>
                                </el-table-column>
                            </el-table>
                            </div>
                        </template>
                    </el-table-column>
                    <!-- 用例执行结果 -->
                    <el-table-column label="执行结果" prop="status" width="120px">
                        <template slot-scope="scope">
                            <span v-if="scope.row.status==='success'" class="lm-success"><i class="el-icon-success"/> 成功</span>
                            <span v-if="scope.row.status==='fail'" class="lm-fail"><i class="el-icon-warning"/> 失败</span>
                            <span v-if="scope.row.status==='error'" class="lm-error"><i class="el-icon-error"/> 错误</span>
                            <span v-if="scope.row.status==='skip'" class="lm-info"><i class="el-icon-remove"/> 跳过</span>
                        </template>
                    </el-table-column>
                    <!-- 用例名称（可点击跳转到用例编辑页面） -->
                    <el-table-column label="用例名称" prop="caseName" min-width="150px">
                        <template slot-scope="scope">
                            <el-button type="text" size="mini" @click="viewCase(scope.row)">{{scope.row.caseName}}</el-button>
                        </template>
                    </el-table-column>
                    <!-- 用例描述 -->
                    <el-table-column label="用例描述" prop="caseDesc" min-width="200px"/>
                    <!-- 用例开始时间 -->
                    <el-table-column label="开始时间" prop="startTime" width="150px"/>
                    <!-- 用例结束时间 -->
                    <el-table-column label="结束时间" prop="endTime" width="150px"/>
                    <!-- 用例执行时长 -->
                    <el-table-column label="执行时长" prop="during" width="120px"/>
                </el-table>
                </div>
            </template>
        </el-table-column>
        <!-- 集合版本 -->
        <el-table-column prop="collectionVersion" label="集合版本" width="160"/>
        <!-- 集合名称 -->
        <el-table-column prop="collectionName" label="集合名称" min-width="200"/>
        <!-- 用例总数 -->
        <el-table-column prop="caseTotal" label="用例总数" width="120px"/>
        <!-- 成功用例数 -->
        <el-table-column prop="passCount" label="成功数" width="120px"/>
        <!-- 失败用例数 -->
        <el-table-column prop="failCount" label="失败数" width="120px"/>
        <!-- 错误用例数 -->
        <el-table-column prop="errorCount" label="错误数" width="120px"/>
    </el-table>
    
    <!-- 执行日志查看对话框 -->
    <el-dialog title="查看日志" :visible.sync="logVisable" width="600px" destroy-on-close @close="closeLog">
        <span v-html="log"/>
    </el-dialog>
  </div>
</template>

<script>
// 导入时间格式化工具函数
import {timestampToTime} from '@/utils/util'

export default {
    // 注册图片查看器组件
    components: {
        'el-image-viewer': () => import('element-ui/packages/image/src/image-viewer')
    },
    
    /**
     * 组件数据
     * @returns {Object} 包含组件状态的数据对象
     */
    data() {
        return{
            loading: false,        // 加载状态
            report: {},           // 报告详细数据
            logVisable: false,    // 日志对话框显示状态
            log: ""              // 当前查看的日志内容
        }
    },
    
    /**
     * 组件创建时的生命周期钩子
     * 初始化面包屑导航并获取报告数据
     */
    created() {
        this.$root.Bus.$emit('initBread', ["测试追踪", "测试报告", "报告详情"]);
        this.getdata(this.$route.params);
    },
    
    methods: {
        /**
         * 获取报告详细数据
         * @param {Object} param - 路由参数，包含reportId
         */
        getdata(param) {
            let reportId = param.reportId;
            this.loading = true;
            let url = "/autotest/report/run/" + reportId;
            
            this.$get(url, response => {
                let report = response.data;
                
                // 格式化执行状态显示文本和颜色
                if(report.status === 'success'){
                    report.format = 'SUCCESS';
                    report.color = '#67C23A';
                }else if(report.status === 'fail'){
                    report.format = 'FAIL';
                    report.color = '#E6A23C';
                }else if(report.status === 'error'){
                    report.format = 'ERROR';
                    report.color = '#F56C6C';
                }else if(report.status === 'skip'){
                    report.format = 'SKIP';
                    report.color = '#535457';
                }else if(report.status === 'prepared'){
                    report.format = '等待执行';
                    report.color = '#409EFF';
                }else if(report.status === 'running'){
                    report.format = "RUNNING";
                    report.color = '#409EFF';
                }else if(report.status === 'discontinue'){
                    report.format = "已终止";
                    report.color = '#535457';
                }
                
                // 处理时间数据：如果没有开始或结束时间，使用当前时间
                if(!report.startTime){
                    report.startTime = Date.now();
                }
                if(!report.endTime){
                    report.endTime = Date.now();
                }
                
                // 计算执行时长并格式化时间显示
                report.during = (report.endTime - report.startTime)/1000 + 'S';
                report.startTime = timestampToTime(report.startTime);
                report.endTime = timestampToTime(report.endTime);
                
                // 处理集合列表中的用例数据
                for(let i=0;i<report.collectionList.length;i++){
                    let collection = report.collectionList[i];
                    for(let j=0;j<collection.caseList.length;j++){
                        let collectionCase = collection.caseList[j];
                        // 格式化用例的开始和结束时间
                        collectionCase.startTime = timestampToTime(collectionCase.startTime);
                        collectionCase.endTime = timestampToTime(collectionCase.endTime);
                        
                        // 对于非API用例，处理截图数据
                        if(collectionCase.caseType !== 'API'){
                            for(let k=0;k<collectionCase.transList.length;k++){
                                let trans = collectionCase.transList[k];
                                // 解析截图列表JSON数据
                                trans.screenshotList = JSON.parse(trans.screenshotList);
                                trans.showViewer = false; // 初始化图片查看器显示状态
                            }
                        }
                    }
                }
                
                this.report = report;
                this.loading = false;
            });
        },
        
        /**
         * 查看用例详情
         * 根据用例类型跳转到对应的用例编辑页面
         * @param {Object} row - 用例数据行
         */
        viewCase(row){
            if (row.caseType == "API"){
                // API用例：跳转到API用例编辑页面
                this.$router.push({path: '/caseCenter/caseManage/apiCase/edit/' + row.caseId});
            }else if (row.caseType == "WEB"){
                // WEB用例：跳转到WEB用例编辑页面
                this.$router.push({path: '/caseCenter/caseManage/webCase/edit/' + row.caseId});
            }else{
                // APP用例：先获取系统类型，再跳转到对应的APP用例编辑页面
                this.$get("/autotest/case/system/" + row.caseId, response =>{
                    let system = response.data;
                    this.$router.push({path: '/caseCenter/caseManage/appCase/'+ system +'/edit/' + row.caseId});
                });
            }
        },
        
        /**
         * 查看执行日志
         * 处理日志中的HTML标签，防止XSS攻击
         * @param {String} log - 原始日志内容
         */
        viewLog(log){
            // 处理请求体中的HTML标签
            let req = log.substring(log.indexOf("<span>请求体: ")+11, log.indexOf("</span><br>"));
            if(req){
                log = log.replace(req, req.replaceAll("<", "&lt;").replaceAll(">", "&gt;"));
            }
            
            // 处理响应体中的HTML标签
            let res = log.substring(log.indexOf("<br><b>响应体: ")+12, log.indexOf("</b><br><br>"));
            if(res){
                log = log.replace(res, res.replaceAll("<", "&lt;").replaceAll(">", "&gt;"));
            }
            
            this.log = log;
            this.logVisable = true;
        },
        
        /**
         * 关闭日志查看对话框
         * 清空日志内容并隐藏对话框
         */
        closeLog(){
            this.log = "";
            this.logVisable = false;
        }
    }
}
</script>

<style scoped>
/* 报告头部样式：包含标题和状态进度 */
.report-header{
    border-bottom: 1px solid rgb(219, 219, 219); /* 底部分隔线，浅灰 */
    height: 48px; /* 头部高度 */
    display: flex; /* 弹性布局，水平排列 */
    margin-bottom: 20px; /* 与下方内容间距 */
    align-items: center; /* 垂直居中对齐 */
    margin-top: -18px; /* 顶部微调，抵消页面间距 */
}

/* 报告基础信息区域样式：统计信息与时间块 */
.report-base{
    border-bottom: 1px solid rgb(219, 219, 219); /* 底部分隔线，浅灰 */
    margin-bottom: 10px; /* 与下方内容间距 */
    margin-top: 10px; /* 与上方内容间距 */
}
</style>