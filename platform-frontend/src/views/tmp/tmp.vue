<template>
  <div class="tmp-container">
    <!-- 页面标题 -->
    <div class="tmp-header">
      <h2>组件测试容器</h2>
      <p>将任意组件内容复制到下方进行测试</p>
    </div>

    <!-- 组件展示区域 -->
    <div class="component-showcase">
      <!-- 这里是你要粘贴组件内容的地方 -->
      <div class="placeholder-box">
        <el-empty description="请将组件内容粘贴到这里进行测试">
          <template #description>
            <div>
              <p>📋 组件测试容器已准备就绪</p>
              <p style="font-size: 12px; color: #909399; margin-top: 10px;">
                从其他组件复制 template、script、style 内容到对应区域
              </p>
            </div>
          </template>
        </el-empty>
      </div>
    </div>

    <!-- 快速导航按钮 -->
    <div class="quick-nav">
      <el-button type="primary" @click="goToTmpHtml" size="small">
        <i class="el-icon-link"></i> 跳转到路由测试页面
      </el-button>
      <el-button @click="clearComponent" size="small" type="warning">
        <i class="el-icon-delete"></i> 清空当前内容
      </el-button>
      <el-button @click="showHelp" size="small" type="info">
        <i class="el-icon-question"></i> 使用帮助
      </el-button>
    </div>

    <!-- 使用说明弹窗 -->
    <el-dialog title="使用说明" :visible.sync="helpVisible" width="600px">
      <div class="help-content">
        <h4>🎯 如何使用这个测试容器</h4>
        <el-divider></el-divider>
        
        <h5>📋 方法一：直接复制粘贴</h5>
        <ol>
          <li>打开项目中任意 .vue 文件</li>
          <li>复制 &lt;template&gt; 标签内的内容</li>
          <li>回到本页面，找到 "component-showcase" div</li>
          <li>替换 placeholder-box 内容为你复制的组件内容</li>
        </ol>

        <h5>🔄 方法二：完整组件替换</h5>
        <ol>
          <li>复制整个 .vue 文件的内容</li>
          <li>粘贴到本文件的对应区域</li>
          <li>确保 template、script、style 结构完整</li>
        </ol>

        <h5>⚡ 快速测试技巧</h5>
        <ul>
          <li>使用路由测试页面可以快速验证组件跳转</li>
          <li>组件内容会自动应用项目的全局样式</li>
          <li>可以使用项目中的所有 UI 组件和工具函数</li>
        </ul>
      </div>
    </el-dialog>
  </div>
</template>

<script>
/**
 * 组件测试容器
 * 用于快速测试和学习项目中的各个组件
 * 使用方法：
 * 1. 从其他组件复制内容到对应区域
 * 2. 保存文件即可看到效果
 * 3. 使用路由测试页面验证跳转功能
 */
export default {
  name: 'TmpTest',
  data() {
    return {
      helpVisible: false  // 控制帮助弹窗显示
    }
  },
  methods: {
    /**
     * 跳转到路由测试页面
     */
    goToTmpHtml() {
      // 使用路由名称跳转
      this.$router.push('/tmp-route');
    },

    /**
     * 清空当前组件内容
     */
    clearComponent() {
      this.$confirm('确定要清空当前组件内容吗？此操作不可恢复。', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$message.success('组件内容已清空，可以开始新的测试');
      }).catch(() => {
        this.$message.info('已取消清空操作');
      });
    },

    /**
     * 显示使用帮助
     */
    showHelp() {
      this.helpVisible = true;
    }
  }
}
</script>

<style lang="scss" scoped>
.tmp-container {
  padding: 20px;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.tmp-header {
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

.component-showcase {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  min-height: 400px;
}

.placeholder-box {
  border: 2px dashed #dcdfe6;
  border-radius: 6px;
  padding: 40px;
  text-align: center;
  background-color: #fafafa;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quick-nav {
  text-align: center;
  margin-top: 20px;
  
  .el-button {
    margin: 0 10px;
  }
}

.help-content {
  h4 {
    color: #303133;
    margin-bottom: 20px;
    text-align: center;
  }
  
  h5 {
    color: #409eff;
    margin: 15px 0 10px 0;
  }
  
  ol, ul {
    margin-left: 20px;
    line-height: 1.8;
  }
  
  li {
    margin-bottom: 5px;
  }
}

/* 组件内容样式区域 - 你可以在这里添加全局样式 */
.component-content {
  /* 这里是你要粘贴的组件样式 */
}
</style>