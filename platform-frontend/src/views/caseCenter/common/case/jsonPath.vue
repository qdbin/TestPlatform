/**
* 响应断言
*/ 
<template>
    <div>
        <el-row :gutter="10">
            <el-col :span="12">
                <div class="req-json-editor">
                    <json-editor-vue style="height:478px;" v-model="jsonData" :mainMenuBar="false" mode="text" />
                </div>
            </el-col>
            <el-col :span="12">
                <div class="tree-data">
                    <json-tree :data="treeData" @addContent="addContent($event)"/>
                </div>
            </el-col>
        </el-row>
    </div>
</template>
<script>
import JsonEditorVue from 'json-editor-vue'
import JsonTree from './jsonTree'
import {toJsonPath} from '@/utils/jsonPath'
export default {
    name: 'JsonPath',
    props:{
        apiId: String,
    },
    components: { JsonEditorVue, JsonTree },
    data() {
        return{
            jsonData:{},
            treeData:[],
        }
    },
    created() {
        this.getJson();
    },
    methods: {
        getJson(){
            let url = '/autotest/case/api/report/' + this.apiId;
            this.$get(url, response =>{
                this.jsonData = response.data;
                if(this.jsonData === null){
                    this.$message.warning('未获取到正确接口响应 请先执行接口请求');
                }else if (this.jsonData.length === 0){
                    this.$message.warning('解析接口响应数据失败 请确认是否为json');
                }else{
                    this.treeData.splice(0, this.treeData.length);
                    toJsonPath(this.treeData, this.jsonData, "$");
                }
            });
        },
        addContent(item){
            this.$emit('addContent', item);
        }
    },
    watch:{
        jsonData: {
            handler(newVal) {
                this.treeData.splice(0, this.treeData.length);
                toJsonPath(this.treeData, newVal, "$");
            },
            deep: true
        }
    }
}
</script>
<style scoped>
.req-json-editor{
    border: 1px solid rgb(219, 219, 219);
}
.req-json-editor >>> .jsoneditor-vue{
    height: 478px;
}
.req-json-editor >>> .ace-jsoneditor{
    height: 478px !important;
}
.req-json-editor >>> .jsoneditor-menu{
    display: none;
}
.req-json-editor >>> .jsoneditor{
    border: none;
}
.tree-data {
    height: 480px;
    border: 1px solid rgb(219, 219, 219);
    overflow: hidden;
    overflow-x: scroll;
    white-space: nowrap;
    box-sizing: border-box;
    padding: 15px 10px;
    overflow-y: scroll;
}       
</style>