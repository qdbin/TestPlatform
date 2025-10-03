<!-- 
 公共组件：边栏、导航栏（通过父子路由实现）
-->
/**
 * Index布局组件（左侧导航 + 顶部导航 + 子路由内容）
 */
<template>
  <!-- 布局结构：左侧导航 + 顶部导航 + 子页面内容 -->
  <el-container class="index-con"> <!-- 页面外层容器 -->
    <el-aside :class="showclass">  <!-- 左侧导航栏：由事件总线控制展开/收起 -->
      <leftnav></leftnav>
    </el-aside>
    <el-container class="main-con"> <!-- 主区域容器：包含顶部与内容 -->
      <el-header class="index-header">  <!-- 顶部导航栏：承载面包屑与工具 -->
        <navcon :breadList="breadList" ></navcon> <!-- 面包屑：依据全局事件更新 -->
      </el-header>
      <el-main class="index-main">  <!-- 主要内容区域：子路由渲染位置 -->
        <router-view></router-view>  <!-- 子页面渲染入口 -->
      </el-main>
    </el-container>
  </el-container>
  
</template>
<script>
// 导入组件
import navcon from './common/components/navcon.vue'
import leftnav from './common/components/leftnav.vue'
export default {
  name: 'index', // 页面名称：Index布局组件
  data() {
    return {
      showclass: 'aside',  // 控制侧边栏展开/收起
      breadList:[]  // 面包屑导航数据
    }
  },
  // 注册组件
  components: {
    navcon,
    leftnav
  },
  methods: {},
  // 页面创建后：监听全局事件总线
  created() {
    // 监听侧边栏切换事件（展开/收起侧栏）
    this.$root.Bus.$on('toggle', value => {
      if (value) {
        this.showclass = 'asideshow'
      } else {
        setTimeout(() => {
          this.showclass = 'aside'
        }, 300)
      }
    });
    // 监听面包屑更新事件（刷新导航层级）
    this.$root.Bus.$on('initBread', breadList=>{
      this.breadList = breadList  // 更新面包屑数据
    });
  },
  // 创建前：恢复用户相关信息到Vuex
  beforeCreate() {
    // 关键步骤：从localStorage恢复用户数据到Vuex
    this.$store.commit('set_token', localStorage.getItem('token'));
    this.$store.commit('set_userInfo', JSON.parse(localStorage.getItem('userInfo')));
    this.$store.commit('set_project', JSON.parse(localStorage.getItem('userInfo')).lastProject);
    this.$store.commit('set_permission', JSON.parse(localStorage.getItem('userInfo')).permissions);
  }
}
</script>
<style >
/* 布局样式定义：容器、侧栏、头部、主内容 */
/* 页面容器：占满窗口并统一盒模型 */
.index-con {
  height: 100%; /* 全高 */
  width: 100%; /* 全宽 */
  box-sizing: border-box; /* 统一盒模型 */
}
/* 侧边栏：收起状态样式 */
.aside {
  width: 48px !important; /* 收起宽度 */
  height: 100%; /* 全高 */
  background-color: #334157; /* 背景色 */
  margin: 0px; /* 去除外边距 */
}
/* 侧边栏：展开状态样式 */
.asideshow {
  width: 200px !important; /* 展开宽度 */
  height: 100%; /* 全高 */
  background-color: #334157; /* 背景色一致 */
  margin: 0px; /* 去除外边距 */
}
/* 顶部导航区域：限制高度 */
.index-header{
  max-height: 40px; /* 最大高度 */
}
/* 主内容卡片：填满并去边框 */
.main-card{
  min-height: 100%; /* 最小高度铺满 */
  border: none; /* 去边框 */
}
</style>
