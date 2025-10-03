/**
 * Vuex 状态管理（存储用户信息、令牌、项目与权限）
 */
import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);
// 登录验证与权限状态容器
export default new Vuex.Store({
    state: {
        userInfo: null, // 当前用户信息
        token: null, // 登录令牌
        projectId: null, // 当前项目ID
        permissions: [] // 权限标识集合
    },
    mutations: {
        // 设置用户信息
        set_userInfo(state, user) {
            state.userInfo = user; // 设置用户信息
        },
        // 清空用户信息
        del_userInfo(state) {
            state.userInfo = null; // 清空用户信息
            localStorage.removeItem("userInfo"); // 清除本地缓存
        },
        // 设置令牌
        set_token(state, token) {
            state.token = token; // 设置令牌
        },
        // 清空令牌
        del_token(state) {
            state.token = null; // 清空令牌
            localStorage.removeItem('token'); // 清除本地缓存
        },
        // 设置当前项目ID
        set_project(state, projectId){
            state.projectId = projectId; // 设置当前项目
        },
        // 设置权限集合
        set_permission(state, permissions){
            state.permissions = permissions; // 设置权限集合
        }
    }
})