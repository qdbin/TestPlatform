/**
 * 公共参数管理组件：按“系统参数组/自定义参数”分类集中管理参数。
 * 提供检索、组内展开分页、增删改、类型化编辑（文本/JSON/键值对）能力，
 * 系统参数以分组展开查看，自定义参数以平铺列表查看，保持交互一致性。
 */
<template>
  <div>
    <!-- 搜索筛选区域 -->
    <el-form :inline="true" :model="searchForm">
      <el-form-item label="">
        <el-input size="small" v-model="searchForm.condition" prefix-icon="el-icon-search" placeholder="请输入参数名称"/> <!-- 绑定搜索条件，搜索参数名称 -->
      </el-form-item>
      <el-form-item>
        <el-button size="small" type="primary" @click="search">搜索</el-button> <!-- 触发搜索 -->
        <el-button size="small" @click="reset">重置</el-button> <!-- 重置搜索条件 -->
      </el-form-item>
      <el-form-item style="float: right" v-if="activeName==='custom'">
          <el-button size="small" type="primary" icon="el-icon-plus" @click="addCustomParam">新增自定义参数</el-button> <!-- 仅自定义参数页显示新增入口 -->
      </el-form-item>
    </el-form>

    <!-- 参数分类标签页（系统参数&&自定义参数） -->
    <el-tabs v-model="activeName" style="magin-left: -10px"> <!-- 标签页切换，绑定当前页签 -->
      <!-- 系统参数标签页 -->
      <el-tab-pane label="系统参数" name="system">
        <el-table size="small" v-loading="systemClassLoading" :data="systemClassList" @expand-change="expandSelect" row-key="index" :expand-row-keys="expands"> <!-- 使用行索引作为唯一键并控制默认展开行 -->
					<!-- 可扩展字段--插槽--详细参数表格 -->
					<el-table-column type="expand" width="40px">
            <template slot-scope="props">
              <div style="padding-left: 40px">
                <el-table size="mini" :data="props.row.systemParamList">
                  <el-table-column label="序号" prop="index" width="50px" align="center"/> <!-- 列：序号 -->
                  <el-table-column label="参数名" prop="name"/> <!-- 列：参数名称 -->
                  <el-table-column label="参数值" prop="paramData" min-width="150px" :show-overflow-tooltip="true"/> <!-- 列：参数值，超出省略提示 -->
                  <el-table-column label="参数描述" prop="description" min-width="150px" :show-overflow-tooltip="true"/> <!-- 列：参数描述 -->
                  <el-table-column label="创建人" prop="username"/> <!-- 列：创建人 -->
                  <el-table-column label="更新时间" prop="updateTime" width="150px"/> <!-- 列：更新时间 -->
                  <el-table-column fixed="right" align="operation" label="操作" width="100px"> <!-- 操作列 -->
										<!-- 内置插槽--操作 -->
                    <template slot-scope="scope">
                      <el-button type="text" size="mini" @click="editParam(scope.row)">编辑</el-button> <!-- 编辑系统参数 -->
                      <el-button type="text" size="mini" @click="deleteParam(props.$index, scope.row)">删除</el-button> <!-- 删除该参数 -->
                    </template>
                  </el-table-column>
                </el-table>
              </div>
              <!-- 系统参数分页组件 -->
              <Pagination style="float: right;" size="mini" v-bind:child-msg="props.row.pageparam" @callFather="systemParamCallFather($event, props.$index)"/> <!-- 系统参数分页控制 -->
            </template>
          </el-table-column>
					<!--常规表字段-->
          <el-table-column label="序号" prop="index" width="50px" align="center"/> <!-- 组序号 -->
          <el-table-column label="系统参数名" prop="name"/> <!-- 参数组名称 -->
          <el-table-column label="系统参数描述" prop="description"/> <!-- 参数组描述 -->
          <el-table-column fixed="right" align="operation" label="操作" width="100px"> <!-- 组级操作列 -->
            <template slot-scope="scope">
              <el-button type="text" size="mini" @click="addSystemParam(scope.row)">新增系统参数</el-button> <!-- 新建系统参数 -->
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 自定义参数标签页：平铺展示参数 -->
      <el-tab-pane label="自定义参数" name="custom">
        <el-table size="small" :data="customParamList" v-loading="customParamLoading"> <!-- 平铺列表展示自定义参数 -->
          <el-table-column label="序号" prop="index" width="50px" align="center"/> <!-- 自定义参数序号 -->
            <el-table-column label="参数名" prop="name"/> <!-- 参数名称 -->
            <el-table-column label="参数类型" prop="dataType"/> <!-- 值类型 -->
            <el-table-column label="参数值" prop="paramData" min-width="150px" :show-overflow-tooltip="true"/> <!-- 参数值，超出省略提示 -->
            <el-table-column label="参数描述" prop="description" min-width="150px" :show-overflow-tooltip="true"/> <!-- 描述 -->
            <el-table-column label="创建人" prop="username"/> <!-- 创建人 -->
            <el-table-column label="更新时间" prop="updateTime" width="150px"/> <!-- 更新时间 -->
            <el-table-column fixed="right" align="operation" label="操作" width="100px"> <!-- 操作列 -->
              <template slot-scope="scope">
                <el-button type="text" size="mini" @click="editParam(scope.row)">编辑</el-button> <!-- 编辑自定义参数 -->
                <el-button type="text" size="mini" @click="deleteParam(scope.$index, scope.row)">删除</el-button> <!-- 删除该参数 -->
              </template>
            </el-table-column>
          </el-table>
        <!-- 自定义参数分页组件 -->
        <Pagination size="small" v-bind:child-msg="customPageparam" @callFather="customParamCallFather"/> <!-- 自定义参数分页控制 -->
      </el-tab-pane>
    </el-tabs>

    <!-- 参数编辑弹窗 -->
    <el-dialog :title="title" :visible.sync="editParamVisible" width="800px" destroy-on-close>
      <el-form label-width="120px" style="padding-right: 30px;" :model="editParamForm" :rules="rules" ref="editParamForm">
				<!-- 参数名 -->
				<el-form-item label="参数名" prop="name">
					<el-input size="small" style="width: 90%" v-model="editParamForm.name" placeholder="请输入参数名"/> <!-- 参数名称输入 -->
				</el-form-item>
				<!-- 自定义参数类型选择 -->
				<el-form-item v-if="activeName !=='system'" label="参数类型" prop="dataType"> <!-- 仅自定义参数显示类型选择 -->
					<el-select size="small" style="width: 90%" v-model="editParamForm.dataType" placeholder="请选择参数类型" @change="changeDataType"> <!-- 参数类型下拉选择 -->
						<el-option v-for="item in dataTypes" :key="item" :label="item" :value="item"/> <!-- 数据类型选项 -->
					</el-select>
				</el-form-item>
				<!-- 系统参数值编辑区域 -->
				<el-form-item label="参数值" prop="paramData">
					<!-- 系统参数键值对编辑器 -->
					<div v-if="activeName === 'system'" style="width:90%">
						<!-- coin【+】 -->
						<div v-if="systemParams.length === 0" style="font-size: 24px; margin-top:8px; display: flex;"> <!-- 空参数时显示添加按钮 -->
							<i class="el-icon-circle-plus lm-success" @click="addSysParam(0)"></i> <!-- 添加第一个参数 -->
						</div>
						<!-- key:value -->
						<el-row v-for="(item, index) in systemParams" :key="index"> <!-- 系统参数键值对列表 -->
							<el-col :span="9">
								<el-input size="small" style="width:95%" v-model="item.name" placeholder="参数名称"/> : <!-- 参数键输入 -->
							</el-col>
							<el-col :span="13">
								<el-input size="small" style="width:95%;" v-model="item.value" placeholder="参数值"/> <!-- 参数值输入 -->
							</el-col>
							<!-- coin【+】/【-】 -->
							<el-col :span="2">
								<div style="font-size: 24px; margin-top:8px; display: flex;"> <!-- 操作按钮组 -->
									<i class="el-icon-circle-plus lm-success" @click="addSysParam(index)"></i> <!-- 添加参数 -->
									<i class="el-icon-remove lm-error" @click="deleteSysParam(index)"></i> <!-- 删除参数 -->
								</div>
							</el-col>
						</el-row>
					</div>

					<!-- JSON类型参数编辑器 -->
					<div class="req-json-editor" v-else-if="editParamForm.dataType==='JSONObject' || editParamForm.dataType==='JSONArray'" >
						<json-editor-vue style="height:200px; width: 90%" v-model="jsonData" :mainMenuBar="false" mode="text" /> <!-- JSON可视化编辑器 -->
					</div>
					<!-- 普通文本参数编辑器 -->
					<el-input v-else size="small" style="width: 90%" v-model="editParamForm.paramData" :autosize="{ minRows: 6}" type="textarea" clearable placeholder="请输入参数值"/>
				</el-form-item>

				<!--参数描述-->
				<el-form-item label="参数描述" prop="description">
					<el-input size="small" style="width: 90%" :autosize="{ minRows: 4}" type="textarea" clearable placeholder="请输入参数描述" v-model="editParamForm.description" maxlength="200" show-word-limit/> <!-- 参数描述输入 -->
				</el-form-item>
      </el-form>

			<!--取消 || 保存-->
      <div slot="footer" class="dialog-footer">
          <el-button size="small" @click="editParamVisible=false">取消</el-button>
          <el-button size="small" type="primary" @click="saveParam('editParamForm', editParamForm)">保存</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
// 导入所需组件和工具函数
import Pagination from '../common/components/pagination' // 分页组件
import JsonEditorVue from 'json-editor-vue' // JSON编辑器组件
import {timestampToTime} from '@/utils/util' // 时间戳转换工具

export default {
  // 注册子组件
  components: { Pagination, JsonEditorVue },

  data() {
    return{
      title: "新增参数", // 弹窗标题
      dataTypes:["String", "Int", "Float", "Boolean", "JSONObject", "JSONArray"], // 参数数据类型选项
      activeName: "system", // 当前选中标签页
      editParamVisible: false, // 参数编辑弹窗显隐状态
      editParamForm:{}, // 参数编辑表单数据
      systemClassLoading: false, // 系统参数组加载状态
      customParamLoading: false, // 自定义参数加载状态
      systemClassList:[], // 系统参数组列表
      customParamList:[], // 自定义参数列表
      expands: [], // 默认展开行索引数组
      customClassId:"", // 自定义参数组的ID

      // 搜索表单数据
      searchForm: {
        condition: "" // 搜索条件（参数名称）
      },

      // 自定义参数分页配置
      customPageparam: {
        currentPage: 1, // 当前页码
        pageSize: 10, // 每页大小
        total: 0 // 总记录数
      },

      jsonData: null, // JSON编辑器数据
      systemParams: [], // 系统参数键值对列表

      // 表单验证规则
      rules: {
          name: [{ required: true, message: '参数名称不能为空', trigger: 'blur' }], // 名称必填校验
          dataType: [{ required: true, message: '参数类型不能为空', trigger: 'blur' }], // 类型必选校验
          paramData: [{ required: true, message: '参数值格式错误或参数值不能为空', trigger: 'blur' }] // 参数值必填校验
      }
    }
  },

  created() {
    this.$root.Bus.$emit('initBread', ["公共组件", "公共参数"]); // 设置面包屑导航
    this.getSystemClassData(); // 加载系统参数组数据
  },

  methods: {
    /**
     * 区分system、custom参数组，并通过参数组_id获得对应的参数组data
     */
    getSystemClassData() {
      this.systemClassLoading = true; // 开启系统参数加载状态
      this.customParamLoading = true; // 开启自定义参数加载状态
      let url = '/autotest/commonParam/group/list/' + this.$store.state.projectId; // 构建API路径
      this.$get(url, response => {
        let data = response.data;
        this.systemClassLoading = false; // 关闭系统参数加载状态
        let systemIndex = 1; // 系统参数组序号计数器

        // 区分参数组--系统参数&自定义参数
        for(let i =0; i<data.length; i++){
					// 自定义参数组
          if(data[i].paramType === "custom"){
            this.customClassId = data[i].id; // 记录自定义参数组ID
						// get自定义参数数据
            this.getCustomParamData();
          }

					// 系统参数组
					else{
            data[i].index = systemIndex; // 设置序号
            systemIndex += 1;
            data[i].systemParamList = []; // 系统参数组数据list
            // 初始化分页参数
            data[i].pageparam = {
              currentPage: 1,
              pageSize: 10,
              total: 0
            };
            this.systemClassList.push(data[i]); // 添加到系统参数组list
          }
        }
      });
    },

    /**
     * 获取系统参数组下的参数数据并处理分页
		 * 通过参数组_id获取
     * @param {Number} index - 系统参数组在列表中的索引
     */
    getSystemParamData(index) {
      let systemClassId = this.systemClassList[index].id; // 获取参数组ID
      let currentPage = this.systemClassList[index].pageparam.currentPage; // 当前页码
      let pageSize = this.systemClassList[index].pageparam.pageSize; // 每页大小
      let url = '/autotest/commonParam/param/' + systemClassId + '/list/' + currentPage + '/' + pageSize; // 构建API路径
      let param = {
          condition: this.searchForm.condition // 搜索条件
      };
      this.$post(url, param, response => {
        let data = response.data;
        // 处理列表数据：添加序号和格式化时间
        for(let i=0; i<data.list.length; i++){
          data.list[i].index = (currentPage-1) * pageSize + i+1; // 计算序号
          data.list[i].updateTime = timestampToTime(data.list[i].updateTime); // 时间格式化
        }
        this.systemClassList[index].systemParamList = data.list; // 设置参数列表
        this.systemClassList[index].pageparam.total = data.total; // 更新总记录数
      });
    },

    /**
     * 获取自定义参数列表并处理分页
     * 加载当前项目的自定义参数数据
     */
    getCustomParamData() {
      this.customParamLoading = true; // 开启加载状态
      let url = '/autotest/commonParam/param/' + this.customClassId + '/list/' + this.customPageparam.currentPage + '/' + this.customPageparam.pageSize; // 构建API路径
      let param = {
          condition: this.searchForm.condition // 搜索条件
      };
      this.$post(url, param, response => {
        let data = response.data;
        // 处理列表数据：添加序号和格式化时间
        for(let i=0; i<data.list.length; i++){
					// 计算序号
          data.list[i].index = (this.customPageparam.currentPage -1) * this.customPageparam.pageSize + i+1;
					// 时间格式化
          data.list[i].updateTime = timestampToTime(data.list[i].updateTime);
        }
        this.customParamList = data.list; // 设置自定义参数列表
        this.customParamLoading = false; // 关闭加载状态
        this.customPageparam.total = data.total; // 更新总记录数
      });
    },

    /**
     * 展开行时加载对应系统参数
     * @param {Object} row - 展开的行数据
     * @param {Array} expandedRows - 当前展开的行数组
     */
    expandSelect(row, expandedRows) {
			// 有展开行时加载数据
      if(expandedRows.length != 0){
        this.getSystemParamData(row.index-1); // 加载对应参数组的参数数据
      }
    },

    /**
     * 搜索按钮点击事件
     * 根据当前标签页刷新对应的参数数据
     */
    search() {
			// 系统参数搜索
      if(this.activeName == "system"){
        // 展开所有分组并搜索
        for(let i=0;i<this.systemClassList.length;i++){
          this.systemClassList[i].pageparam.currentPage = 1; // 重置页码
          this.systemClassList[i].pageparam.pageSize = 10; // 重置页大小
          this.getSystemParamData(i); // 获取参数数据
          this.expands.push(i+1); // 添加到展开列表
        }
      }
			// 自定义参数搜索
			else{
        this.getCustomParamData(); // 直接搜索自定义参数
      }
    },

    /**
     * 重置按钮点击事件
     * 清空搜索条件并重新加载数据
     */
    reset() {
      this.searchForm.condition = ""; // 清空搜索条件
      if(this.activeName == "system"){ // 系统参数重置
        // 重新加载所有分组数据并收起展开
        for(let i=0;i<this.systemClassList.length;i++){
          this.getSystemParamData(i); // 重新获取数据
        }
        this.expands.splice(0, this.expands.length); // 清空展开列表
      }else{ // 自定义参数重置
        this.getCustomParamData(); // 重新加载自定义参数
      }
    },

    /**
     * 系统参数分页回调处理
     * @param {Object} param - 分页参数对象，包含当前页和每页大小
     * @param {Number} index - 参数组索引
     */
    systemParamCallFather(param, index){
      this.systemClassList[index].pageparam.currentPage = param.currentPage; // 更新当前页
      this.systemClassList[index].pageparam.pageSize = param.pageSize; // 更新页大小
      this.getSystemParamData(index); // 重新获取数据
    },

    /**
     * 自定义参数分页回调处理
     * @param {Object} param - 分页参数对象，包含当前页和每页大小
     */
    customParamCallFather(param){
      this.customPageparam.currentPage = param.currentPage; // 更新当前页
      this.customPageparam.pageSize = param.pageSize; // 更新页大小
      this.getCustomParamData(); // 重新获取数据
    },

    /**
     * 新增系统参数并打开编辑弹窗
     * @param {Object} row - 参数组行数据
     */
    addSystemParam(row){
      // 初始化系统参数表单
      this.editParamForm = {
        id: "", // 参数ID（新增时为空）
        name: "", // 参数名称
        dataType: "JSONObject", // 默认数据类型
        paramData: "{}", // 默认参数值
        description: "", // 参数描述
        groupId: row.id // 所属参数组ID
      };

      // 根据参数组类型预设默认值
      if(row.name === 'Proxy'){ // 代理参数组
        this.editParamForm.paramData = "{ \"url\":\"\", \"username\": \"\", \"password\": \"\" }"
      }else if(row.name === 'Header'){ // 请求头参数组
        this.editParamForm.paramData = "{ \"content-type\": \"application/json\" }"
      }

      this.systemParams = this.jsonToList(JSON.parse(this.editParamForm.paramData)); // 转换为键值对列表
      this.title = "新增系统参数"; // 设置弹窗标题
      this.editParamVisible = true; // 显示编辑弹窗
    },

    /**
     * 新增自定义参数并打开编辑弹窗
     */
    addCustomParam(){
      // 初始化自定义参数表单
      this.editParamForm = {
        id: "", // 参数ID（新增时为空）
        name: "", // 参数名称
        dataType: "String", // 默认数据类型
        paramData: "", // 参数值
        description: "", // 参数描述
        groupId: this.customClassId // 自定义参数组ID
      };
      this.title = "新增自定义参数"; // 设置弹窗标题
      this.editParamVisible = true; // 显示编辑弹窗
    },

    /**
     * 删除参数操作
     * @param {Number} index - 参数在列表中的索引
     * @param {Object} row - 参数行数据
     */
    deleteParam(index, row){
      this.$confirm('确定要删除参数吗?', '删除提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
      })
      .then(() => {
          let url = '/autotest/commonParam/param/delete'; // 删除API地址
          this.$post(url, {id: row.id}, response => {
            this.$message.success("删除成功"); // 成功提示
            // 根据当前标签页刷新对应数据
            if(this.activeName == "system"){
              this.getSystemParamData(index); // 刷新系统参数
            }else{
              this.getCustomParamData(); // 刷新自定义参数
            }
          });
      })
      .catch(() => {
          this.$message.success("取消成功"); // 取消提示
      })
    },

    /**
     * 编辑参数并预置编辑器数据
     * @param {Object} row - 参数行数据
     */
    editParam(row){
      // 复制参数数据到编辑表单
      this.editParamForm = {
        id: row.id, // 参数ID
        name: row.name, // 参数名称
        dataType: row.dataType, // 数据类型
        paramData: row.paramData, // 参数值
        description: row.description, // 参数描述
        groupId: row.groupId, // 参数组ID
        createUser: row.createUser, // 创建人
        createTime: row.createTime // 创建时间
      };

      // 根据参数类型初始化编辑器数据
      if(this.activeName === 'system'){ // 系统参数：转换为键值对列表
        this.systemParams = this.jsonToList(JSON.parse(this.editParamForm.paramData));
      }else if(row.dataType === 'JSONObject' || row.dataType === 'JSONArray'){ // JSON类型：解析为对象
        this.jsonData = JSON.parse(row.paramData);
      }

      this.title = "编辑参数"; // 设置弹窗标题
      this.editParamVisible = true; // 显示编辑弹窗
    },

    /**
     * 保存参数操作
     * @param {String} confirm - 表单引用名称
     * @param {Object} form - 表单数据对象
     */
    saveParam(confirm, form){
      // 系统参数需将键值对转回JSON字符串
      if (this.activeName === 'system'){
				// 更新编辑表单的参数的数据格式
        this.editParamForm.paramData = JSON.stringify(this.listToJson(this.systemParams)); // 转换为JSON字符串
      }

      this.$refs[confirm].validate(valid => {
        if (valid) {
          let url = '/autotest/commonParam/param/save'; // 保存API地址
          this.$post(url, form, response =>{
            this.$message.success("保存成功"); // 成功提示

            // 根据参数类型刷新对应列表数据
            if(this.activeName == "system"){ // 系统参数：查找对应参数组并刷新
              for(let i=0;i<this.systemClassList.length;i++){
                if(this.systemClassList[i].id == form.groupId){
                  this.getSystemParamData(i); // 刷新对应参数组数据
                  break;
                }
              }
            }else{ // 自定义参数：直接刷新
              this.getCustomParamData();
            }
            this.editParamVisible = false; // 关闭编辑弹窗
          });
        }else{
          return false; // 验证失败
        }
      });
    },

    /**
     * JSON编辑器内容变更同步到表单
     * @param {Object} value - JSON编辑器的值
     */
    onJsonChange(value){
      this.editParamForm.paramData = JSON.stringify(value); // 同步到表单数据
    },

    /**
     * 切换参数数据类型时初始化示例值
     * @param {String} value - 选择的数据类型
     */
    changeDataType(value){
      if(value === "JSONObject"){ // JSON对象类型
        this.editParamForm.paramData = "{}";
        this.jsonData = {};
      }else if(value === "JSONArray"){ // JSON数组类型
        this.editParamForm.paramData = "[]";
        this.jsonData = [];
      }else{ // 其他类型
        this.editParamForm.paramData = "";
      }
    },

    /**
     * 在列表中插入一条系统参数项
     * @param {Number} index - 插入位置索引
     */
    addSysParam(index){
			// 在指定位置插入新参数
			this.systemParams.splice(index+1, 0, {propName:"",propValue:""});
    },

    /**
     * 删除指定下标的系统参数项
     * @param {Number} index - 要删除的参数索引
     */
    deleteSysParam(index){
			this.systemParams.splice(index, 1); // 删除指定索引的参数
    },

    /**
     * 列表转JSON对象
     * @param {Array} list - 键值对列表
     * @returns {Object} 转换后的JSON对象
		 *
		 * example-list
		 * 	[{"name":"参数名","value":"参数值"},{},{}]
		 *
     */
    listToJson(list){
      let json = {};
      for(let i=0;i<list.length;i++){
        let item = list[i];
        json[item.name] = item.value; // 将键值对转换为JSON属性
      }
      return json;
    },

    /**
     * JSON对象转列表
     * @param {Object} json - JSON对象
     * @returns {Array} 转换后的键值对列表
     */
    jsonToList(json){
      let list = []
      for(let key in json){
        let item = {
          name: key, // 属性名作为键
          value: json[key] // 属性值作为值
        };
        list.push(item);
      }
      return list;
    }
  }
}
</script>

<style scoped>
/* JSON编辑器容器高度控制 */
.req-json-editor >>> .jsoneditor-vue{
    height: 200px; /* 统一设置容器高度 */
}
/* ACE编辑器高度控制 */
.req-json-editor >>> .ace-jsoneditor{
    height: 200px !important; /* 强制编辑区高度 */
}
/* 隐藏JSON编辑器菜单栏 */
.req-json-editor >>> .jsoneditor-menu{
    display: none; /* 去除顶部菜单 */
}
/* 编辑器边框样式 */
.req-json-editor >>> .jsoneditor{
    border: 1px solid rgb(219, 219, 219); /* 边框色与宽度 */
}
/* 修正滚动区域位置 */
.req-json-editor >>> .ace_scroller{
    left: 0px !important; /* 左边距修正 */
}
/* 隐藏行号区域 */
.req-json-editor >>> .ace_gutter{
    display: none; /* 不显示行号 */
}
</style>
