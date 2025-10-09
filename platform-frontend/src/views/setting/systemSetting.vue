/**
 * 系统设置页面组件
 * 用途：统一管理域名标识、迭代版本、应用信息、通知配置与驱动配置等系统级设置。
 * 结构：左侧标签页切换不同设置模块；各子模块为独立子组件，支持权限控制显示操作入口。
 * 交互：进入页面初始化面包屑并请求当前用户在项目下的操作权限，用于控制子组件的操作按钮显隐。
 */
<template>
  <div>
    <!-- 左侧标签页：切换不同系统设置模块 -->
    <el-tabs v-model="activeName" tab-position="left">
      <!-- 域名标识设置：用于环境域名与业务标识管理 -->
      <el-tab-pane label="域名标识" name="domainSign">
        <domain-sign-setting :showOpt="showOpt" :activeName="activeName" />
      </el-tab-pane>
      <!-- 迭代版本设置：管理版本信息，供集合/计划等引用 -->
      <el-tab-pane label="迭代版本" name="version">
        <version-setting :showOpt="showOpt" :activeName="activeName" />
      </el-tab-pane>
      <!-- 应用信息设置：配置应用相关基础信息 -->
      <el-tab-pane label="应用信息" name="application">
        <application-setting :showOpt="showOpt" :activeName="activeName" />
      </el-tab-pane>
      <!-- 通知配置：执行结果通知通道与模板设置 -->
      <el-tab-pane label="通知配置" name="notification">
        <notification-setting :showOpt="showOpt" :activeName="activeName" />
      </el-tab-pane>
      <!-- 驱动配置：Web/App等驱动安装与接入配置 -->
      <el-tab-pane label="驱动配置" name="driver">
        <driver-setting :showOpt="showOpt" :activeName="activeName" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
// 子模块组件：分别承载不同系统设置
import VersionSetting from './common/versionSetting'
import DomainSignSetting from './common/domainSignSetting'
import ApplicationSetting from './common/applicationSetting'
import NotificationSetting from './common/notificationSetting'
import DriverSetting from './common/driverSetting'

export default {
  // 注册子组件
  components: {
    VersionSetting, DomainSignSetting, ApplicationSetting, NotificationSetting, DriverSetting
  },
  /**
   * 组件数据
   * @returns {Object} 包含当前激活标签与权限控制的状态
   */
  data() {
    return {
      activeName: null, // 当前激活的标签页名称
      showOpt: false // 是否展示操作入口（依据权限控制）
    }
  },
  /**
   * 生命周期：创建
   * 初始化面包屑并请求当前用户在项目下的系统设置操作权限
   */
  created() {
    this.$root.Bus.$emit('initBread', ["设置中心", "系统设置"]);
    this.getOptPerm();
  },
  methods: {
    /**
     * 获取系统设置操作权限
     * 依据用户与项目ID查询权限，更新操作入口显隐，并默认激活域名标识标签页
     */
    getOptPerm() {
      const url = "/autotest/setting/permission?userId=" + this.$store.state.userInfo.id + "&projectId=" + this.$store.state.projectId;
      this.$get(url, response => {
        this.showOpt = response.data;
        this.activeName = "domainSign"; // 默认进入域名标识设置
      });
    },
  }
}
</script>

<style scoped>
/* 系统设置页面样式（可根据需要补充） */
</style>
