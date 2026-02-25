<template>
  <div class="tmp-route-container">
    <!-- 页面标题 -->
    <div class="route-header">
      <h2>路由测试页面</h2>
      <p>测试不同组件的路由跳转功能</p>
    </div>

    <!-- 路由视图容器 -->
    <div class="route-view-container">
      <router-view></router-view>
    </div>

    <!-- 路由导航按钮区域 -->
    <div class="route-nav-area">
      <h3>🧭 路由导航测试</h3>
      <div class="nav-buttons">
        <el-button 
          type="primary" 
          @click="navigateTo('login')" 
          size="small"
          icon="el-icon-user">
          登录页面
        </el-button>
        
        <el-button 
          type="success" 
          @click="navigateTo('home')" 
          size="small"
          icon="el-icon-house">
          主页
        </el-button>
        
        <el-button 
          type="info" 
          @click="navigateTo('tmp')" 
          size="small"
          icon="el-icon-monitor">
          组件测试页面
        </el-button>
        
        <el-button 
          type="warning" 
          @click="showComponentSelector" 
          size="small"
          icon="el-icon-copy-document">
          快速组件测试
        </el-button>
      </div>
    </div>

    <!-- 组件选择器弹窗 -->
    <el-dialog 
      title="选择要测试的组件" 
      :visible.sync="componentSelectorVisible" 
      width="800px"
      top="5vh">
      
      <div class="component-grid">
        <!-- 基础中心组件 -->
        <div class="component-category">
          <h4>📁 基础中心</h4>
          <div class="component-list">
            <el-button 
              v-for="item in baseComponents" 
              :key="item.path"
              @click="testComponent(item)"
              size="mini"
              :type="item.type">
              {{ item.name }}
            </el-button>
          </div>
        </div>

        <!-- 环境中心组件 -->
        <div class="component-category">
          <h4>🌍 环境中心</h4>
          <div class="component-list">
            <el-button 
              v-for="item in envComponents" 
              :key="item.path"
              @click="testComponent(item)"
              size="mini"
              :type="item.type">
              {{ item.name }}
            </el-button>
          </div>
        </div>

        <!-- 用例中心组件 -->
        <div class="component-category">
          <h4>📋 用例中心</h4>
          <div class="component-list">
            <el-button 
              v-for="item in caseComponents" 
              :key="item.path"
              @click="testComponent(item)"
              size="mini"
              :type="item.type">
              {{ item.name }}
            </el-button>
          </div>
        </div>

        <!-- 计划中心组件 -->
        <div class="component-category">
          <h4>📅 计划中心</h4>
          <div class="component-list">
            <el-button 
              v-for="item in planComponents" 
              :key="item.path"
              @click="testComponent(item)"
              size="mini"
              :type="item.type">
              {{ item.name }}
            </el-button>
          </div>
        </div>
      </div>
      
      <div slot="footer" class="dialog-footer">
        <el-button @click="componentSelectorVisible = false" size="small">关闭</el-button>
      </div>
    </el-dialog>

    <!-- 使用说明 -->
    <div class="usage-tips">
      <el-alert
        title="💡 使用提示"
        type="info"
        :closable="false"
        description="点击上方按钮可以测试不同的路由跳转，或使用组件选择器快速测试项目中的各个组件功能">
      </el-alert>
    </div>
  </div>
</template>

<script>
/**
 * 路由测试页面
 * 用于测试项目中的路由跳转和组件展示
 */
export default {
  name: 'TmpRouteTest',
  data() {
    return {
      componentSelectorVisible: false,
      // 组件分类数据
      baseComponents: [
        { name: '文件管理', path: '/common/fileManage', type: 'primary' },
        { name: '公共参数', path: '/common/commonParam', type: 'primary' },
        { name: '函数管理', path: '/common/funcManage', type: 'primary' },
        { name: '操作管理', path: '/common/operationManage', type: 'primary' }
      ],
      envComponents: [
        { name: '环境管理', path: '/envCenter/envManage', type: 'success' },
        { name: '引擎管理', path: '/envCenter/engineManage', type: 'success' },
        { name: '设备管理', path: '/envCenter/deviceManage', type: 'success' }
      ],
      caseComponents: [
        { name: '接口管理', path: '/caseCenter/interfaceManage', type: 'warning' },
        { name: '元素管理', path: '/caseCenter/elementManage', type: 'warning' },
        { name: '控件管理', path: '/caseCenter/controlManage', type: 'warning' },
        { name: '用例管理', path: '/caseCenter/caseManage', type: 'warning' }
      ],
      planComponents: [
        { name: '测试集合', path: '/planCenter/testCollection', type: 'info' },
        { name: '测试计划', path: '/planCenter/testPlan', type: 'info' }
      ]
    }
  },
  methods: {
    /**
     * 路由跳转
     * @param {string} target - 目标页面
     */
    navigateTo(target) {
      switch(target) {
        case 'login':
          this.$router.push('/login');
          break;
        case 'home':
          this.$router.push('/home/dashboard');
          break;
        case 'tmp':
          this.$router.push('/tmp');
          break;
        default:
          this.$message.warning('未知的路由目标');
      }
    },

    /**
     * 显示组件选择器
     */
    showComponentSelector() {
      this.componentSelectorVisible = true;
    },

    /**
     * 测试组件路由
     * @param {Object} component - 组件信息
     */
    testComponent(component) {
      this.$message.success(`正在跳转到：${component.name}`);
      this.componentSelectorVisible = false;
      
      // 延迟跳转，让用户看到提示消息
      setTimeout(() => {
        this.$router.push(component.path);
      }, 500);
    }
  }
}
</script>

<style lang="scss" scoped>
.tmp-route-container {
  padding: 20px;
  min-height: 100vh;
  background-color: #f0f2f5;
}

.route-header {
  text-align: center;
  margin-bottom: 30px;
  
  h2 {
    color: #303133;
    margin-bottom: 10px;
    font-size: 24px;
  }
  
  p {
    color: #909399;
    font-size: 14px;
  }
}

.route-view-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  min-height: 200px;
  border: 2px dashed #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &::before {
    content: "🎯 路由视图区域 - 跳转的组件将在这里显示";
    color: #c0c4cc;
    font-size: 16px;
  }
}

.route-nav-area {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  
  h3 {
    color: #303133;
    margin-bottom: 15px;
    text-align: center;
  }
}

.nav-buttons {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 10px;
  
  .el-button {
    margin: 0;
  }
}

.component-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  max-height: 400px;
  overflow-y: auto;
}

.component-category {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 15px;
  
  h4 {
    color: #303133;
    margin-bottom: 12px;
    font-size: 14px;
    text-align: center;
    border-bottom: 1px solid #e4e7ed;
    padding-bottom: 8px;
  }
}

.component-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  
  .el-button {
    width: 100%;
    justify-content: flex-start;
  }
}

.usage-tips {
  margin-top: 20px;
}
</style>