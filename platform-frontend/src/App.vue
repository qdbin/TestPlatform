<!--
  App 根组件（应用根容器与路由渲染入口）：提供全局样式环境与 <router-view> 占位渲染，作为单页应用的外层承载。
-->
<template>
  <!-- 应用根容器，承载所有页面 -->
  <div id="app"> 
    <!-- 路由占位：渲染当前匹配的子页面组件 -->
    <router-view />
  </div>
</template>

<script>
// 根组件定义：仅负责挂载与命名
export default {
  name: "App",
};
</script>

<style>
/* 页面与HTML根节点：填满视口并统一盒模型 */
html,
body {
  width: 100%; /* 占满宽度 */
  height: 100%; /* 占满高度 */
  box-sizing: border-box; /* 统一盒模型，包含边框与内边距 */
  padding: 0px; /* 去除默认内边距 */
  margin: 0px; /* 去除默认外边距 */
}
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif; /* 基础字体族 */
  font-size: 14px; /* 全局字体大小 */
  -webkit-font-smoothing: antialiased; /* WebKit 字体抗锯齿 */
  -moz-osx-font-smoothing: grayscale; /* macOS 字体抗锯齿 */
  color: #2c3e50; /* 全局文本颜色 */
  widows: 100%; /* 文本孤行控制（兼容旧属性） */
  height: 100%; /* 充满父容器高度 */
}
</style>
