/**
 * 公共组件  函数编辑
 */
<template>
  <div>
    <!-- 顶部页面头：根据是否新增/权限控制按钮显示 -->
    <page-header v-if="isAdd===true" title="新增函数" :cancel="cancelAdd" :save="saveAdd"/>
    <page-header v-else-if="functionForm.createUser!==currentUser" title="查看函数" :showSave="false" :cancel="cancelAdd"/>
    <page-header v-else title="编辑函数" :cancel="cancelAdd" :save="saveAdd"/>

    <!-- 函数基础信息与代码编辑表单 -->
    <el-form ref="functionForm" :rules="rules" :model="functionForm" label-width="80px">
		<!--基础信息-->
        <p class="tip">
            <span>基础信息</span>
            <el-tooltip content="函数名称限字母及下划线 且首字符不得为下划线" placement="bottom">
                <i class="el-icon-info"></i>
            </el-tooltip>
        </p>
        <el-row :gutter="10">
            <el-col :span="6">
                <el-form-item label="函数名称" prop="name">
                    <el-input size="small" :disabled="!isAdd" v-model="functionForm.name" placeholder="请输入函数名称 例name_str"/> <!-- 仅新增时可编辑名称 -->
                </el-form-item>
            </el-col>
            <el-col :span="7">
                <el-form-item label="调用方式" prop="expression">
                    <el-input size="small" v-model="functionForm.expression" :placeholder="place"/> <!-- 函数调用表达式占位提示 -->
                </el-form-item>
            </el-col>
            <el-col :span="11">
                <el-form-item label="函数说明" prop="description">
                    <el-input size="small" v-model="functionForm.description" placeholder="请输入函数说明"/> <!-- 简要说明函数用途 -->
                </el-form-item>
            </el-col>
        </el-row>

		<!--函数入参-->
        <p class="tip">函数入参</p> <!-- 定义参数名、类型与描述 -->
        <el-table :data="functionForm.param">
            <el-table-column label="入参名称" prop="paramName">
                <template slot-scope="scope">
                    <el-input size="small" style="width: 90%" placeholder="请输入入参名称" v-model="functionForm.param[scope.$index].paramName"/> <!-- 入参名称输入框 -->
                </template>
            </el-table-column>
            <el-table-column label="入参类型" prop="type">
                <template slot-scope="scope">
                    <el-select size="small" style="width: 90%" v-model="functionForm.param[scope.$index].type"> <!-- 选择入参类型 -->
                        <el-option v-for="item in types" :key="item" :label="item" :value="item"/>	<!--下列框绑定-->
                    </el-select>
                </template>
            </el-table-column>
            <el-table-column label="入参描述" prop="description">
                <template slot-scope="scope">
                    <el-input size="small" style="width: 90%" placeholder="请输入入参描述" v-model="functionForm.param[scope.$index].description"/> <!-- 入参含义说明 -->
                </template>
            </el-table-column>
            <el-table-column label="操作" width="100px">
                <template slot-scope="scope">
                    <el-button size="mini" type="text" @click="remove(scope.$index)">删除</el-button> <!-- 删除当前入参 -->
                </template>
            </el-table-column>
        </el-table>
        <el-button size="small" icon="el-icon-plus" type="text" @click="add">新增</el-button> <!-- 新增入参行 -->
        <el-button size="small" type="text" @click="deleteAll">删除全部</el-button> <!-- 清空入参定义 -->

		<!--函数代码-->
        <p class="tip">
            <span>函数代码</span>
            <el-tooltip content="代码内可直接使用定义的参数名 执行结果必须以sys_return(result)形式返回" placement="bottom">
                <i class="el-icon-info"></i>
            </el-tooltip>
        </p>
        <code-edit ref="editor" :data.sync='functionForm.code' :height='480' mode="python"/> <!-- Python 代码编辑器，双向绑定函数代码 -->
    </el-form>
  </div>
</template>

<script>
import PageHeader from '@/views/common/components/pageheader'
import CodeEdit from '@/views/common/business/codeEdit'
export default {
    components: { CodeEdit, PageHeader },
    data() {
        return{
          place: "格式如 {{@func(param)}}", // 调用方式占位提示
          types: ["String", "Int", "Float", "Boolean", "Bytes", "JSONObject", "JSONArray", "Other"], // 参数类型枚举
          functionForm: {
            id: "", // 函数ID
            name: "", // 函数名称
            from: "custom", // 来源：自定义
            param: [], // 入参定义列表
            code: "", // 函数代码
            expression: "", // 函数调用表达式
            description: "", // 函数说明
            createUser: "" // 创建人标识
          },
          rules: {
              name: [{ required: true, message: '函数名称不能为空', trigger: 'blur' }], // 名称必填
              expression: [{ required: true, message: '调用方式不能为空', trigger: 'blur' }], // 表达式必填
              description: [{ required: true, message: '函数说明不能为空', trigger: 'blur' }] // 说明必填
          },
          currentUser: "", // 当前用户ID
          isAdd: true, // 是否新增模式
        }
    },
    created(){
      this.$root.Bus.$emit('initBread', ["公共组件", "函数管理", "函数编辑"]);
      this.currentUser = this.$store.state.userInfo.id;
			// this.$route.params=id（push跳转传入的id）
      this.getDetail(this.$route.params);
    },
    methods: {
      // 获取详情：若存在ID则进入编辑模式并加载详情
      getDetail(param){
        if (param.functionId){
            this.isAdd = false;
            let url = '/autotest/function/detail/' + param.functionId;
            this.$get(url, response =>{
                let data = response.data;
                data.param = JSON.parse(data.param);
                this.functionForm = data;
            });
        }
      },
      // 取消返回函数列表页
      cancelAdd(){
          this.$router.push({path: '/common/funcManage'})
      },
      // 校验并保存函数，成功后跳转列表
      saveAdd(){
          this.$refs["functionForm"].validate(valid => {
              if (valid) {
                  let form = JSON.parse(JSON.stringify(this.functionForm));
                  form.projectId = this.$store.state.projectId;
                  form.param = JSON.stringify(form.param);
                  let url = '/autotest/function/save';
                  this.$post(url, form, response =>{
                      this.$message.success("保存成功");
                      this.$router.push({path: '/common/funcManage'});
                  });
              }else{
                  return false;
              }
          });
      },
      // 新增一个入参项
      add(){
          this.functionForm.param.push({paramName:"", type:"String", description: ""});
      },
      // 删除指定入参
      remove(index){
          this.functionForm.param.splice(index, 1);
      },
      // 清空全部入参
      deleteAll(){
          this.functionForm.param.splice(0, this.functionForm.param.length);
      },
    }

}
</script>

<style scoped>

</style>
