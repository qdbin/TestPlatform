/**
 * 应用入口文件（注册UI与插件、创建根实例、配置路由拦截）
 */
import Vue from 'vue';
// 引入element UI
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
// 注册ElementUI组件库到Vue实例
Vue.use(ElementUI);
import editor from 'vue2-ace-editor'
// 引入App
import App from './App';
// 引入路由
import router from './router';
// 引入状态管理
import store from './vuex/store';
// 引入icon
import './assets/icon/iconfont.css';
// 引入全局样式
import '../static/css/index.css';
// 引入axios
import ajax from './utils/ajax';
import axios from 'axios';
// 注册自定义ajax插件：挂载统一请求方法
Vue.use(ajax);
Vue.prototype.$axios = axios; // 暴露原始axios以便特殊场景使用

Vue.config.productionTip = false; // 关闭生产环境提示

// 过滤器：注册utils中导出的函数为全局过滤器
import * as custom from './utils/util'
Object.keys(custom).forEach(key => {
    Vue.filter(key, custom[key])
})

/* eslint-disable no-new */
// 创建并挂载根实例
new Vue({
    router, // 路由实例
    store, // 使用Vuex状态管理
    render: h => h(App), // 渲染根组件
    data: {
        // 空的实例放到根组件下，所有的子组件都能调用
        Bus: new Vue()  // 事件总线：跨组件通信
    }
}).$mount('#app')

// 路由拦截器：鉴权与权限校验
// 路由前置守卫：登录态与权限校验
router.beforeEach((to, from, next) => {
    if (to.matched.length != 0) {
        if (to.meta.requireAuth) { // 需要登录权限
            if (store.state.token !== null) { // 已登录（通过state判断）
                // 关键步骤：按路由meta校验具体权限
                if (to.meta.requirePerm) {
                    if(store.state.permissions.includes(to.meta.requirePerm)){
                        next(); // 权限通过，放行
                    }else{
                        next({
                            path: '/home/dashboard' // 无权限，回到主页
                        });
                    }
                }else{
                    next(); // 无特定权限要求，直接放行
                }
            } else {
                next({
                    path: '/login',
                    query: { redirect: to.fullPath } // 记录来源，登录成功后回跳
                });
            }
        } else {
            next(); // 不需要登录权限，直接放行
        }
    } else {
        next({
            path: '/login',
            query: { redirect: to.fullPath } // 未匹配到路由时回到登录
        })
    }
})