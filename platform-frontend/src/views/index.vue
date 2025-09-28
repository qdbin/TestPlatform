<!-- 
 公共组件：边栏、导航栏（通过父子路由实现）
-->
<template>
  <el-container class="index-con">
    <el-aside :class="showclass">  <!-- 左侧导航栏 -->
      <leftnav></leftnav>
    </el-aside>
    <el-container class="main-con">
      <el-header class="index-header">  <!-- 顶部导航栏 -->
        <navcon :breadList="breadList" ></navcon>
      </el-header>
      <el-main class="index-main">  <!-- 主要内容区域 -->
        <router-view></router-view>  <!-- 显示子路由页面 -->
      </el-main>
    </el-container>
  </el-container>
</template>
<script>
// 导入组件
import navcon from './common/components/navcon.vue'
import leftnav from './common/components/leftnav.vue'
export default {
  name: 'index',
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
  created() {
    // 监听侧边栏切换事件
    this.$root.Bus.$on('toggle', value => {
      if (value) {
        this.showclass = 'asideshow'
      } else {
        setTimeout(() => {
          this.showclass = 'aside'
        }, 300)
      }
    });
    // 监听面包屑更新事件
    this.$root.Bus.$on('initBread', breadList=>{
      this.breadList = breadList  // 更新面包屑数据
    });
  },
  beforeCreate() {
    // 从localStorage恢复用户数据到Vuex
    this.$store.commit('set_token', localStorage.getItem('token'));
    this.$store.commit('set_userInfo', JSON.parse(localStorage.getItem('userInfo')));
    this.$store.commit('set_project', JSON.parse(localStorage.getItem('userInfo')).lastProject);
    this.$store.commit('set_permission', JSON.parse(localStorage.getItem('userInfo')).permissions);
  }
}
</script>
<style >
.index-con {
  height: 100%;
  width: 100%;
  box-sizing: border-box;
}
.aside {
  width: 48px !important;
  height: 100%;
  background-color: #334157;
  margin: 0px;
}
.asideshow {
  width: 200px !important;
  height: 100%;
  background-color: #334157;
  margin: 0px;
}
.index-header{
  max-height: 40px;
}
.main-card{
  min-height: 100%;
  border: none;
}
</style>
