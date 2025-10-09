/**
 * 网络请求封装：统一处理token、错误提示、文件上传下载
 */

import {message} from '@/utils/message';
import axios from 'axios';
import store from '@/vuex/store';

axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8080'; // 接口根地址
axios.defaults.timeout = 30000; // 超时时间(ms)

// 上传配置：设置multipart表单与token
function getUploadConfig(token, url, formData) {
  return {
    method: 'POST', // 提交方式
    url: url, // 上传地址
    data: formData, // 表单数据
    headers: {
      'Content-Type': 'multipart/form-data', // 表单类型
      'token': token // 身份令牌
    }
  };
}

// 通用请求头：附加token
function getTokenConfig(token) {
  return {
    headers: {
      'token': token // 身份令牌
    }
  };
}

// 退出登录：清空状态并跳转登录页
function logout(store, router){
  store.commit('del_userInfo');
  store.commit('del_token');
  if(router.currentRoute.path !== '/login'){
    router.push({ path: '/login', query:{ redirect: router.currentRoute.fullPath } }); // 记录来源路径
  }
}

// 响应统一处理（token刷新、回调、异常提示）
function then(success, response, result) {
  // 数据为空，直接执行回调
  if (!response.data) {
    success(response);
  } else if (response.data.status === 0) {
    // 执行回调
    success(response.data);
    // 如果token变化，则更新token
    if(response.headers.token !== store.state.token){
      localStorage.setItem('token', response.headers.token);
      store.commit('set_token', response.headers.token);  // 刷新token
    }
  } else if(response.data.status >= 2020 && response.data.status < 2050){
    // 登录过期 或未登录 重新登录
    if (response.data.message) {
      message.warning(response.data.message);
    }
    return false;
  }else if(response.data.status == 1000){
    // 未知错误提示具体报错信息
    if (response.data.data) {
      message.warning(response.data.data);
    }
  }else {
    window.console.warn(response.data);
    if (response.data.message) {
      message.warning(response.data.message);
    }
  }
  result.loading = false;
  return true;
}

// 异常处理：输出错误并做统一提示
function exception(error, result) {
  result.loading = false;
  window.console.error(error);
  if (error.status && error.statusText) {
    message.error({message: error.status+error.statusText, showClose: true}); // 展示状态码
  }else{
    message.error(error.message);
  }
}

// 登录请求：不带token的post
export function login(url, data, success) {
  let result = {loading: true};
  axios.post(url, data).then(response => {
    success(response);
  }).catch(error => {
    exception(error, result);
  });
  result.loading = false;
  return result;
}

// GET请求：自动附带token
export function get(url, success) {
  let result = {loading: true};
  let config = getTokenConfig(this.$store.state.token);
  if (!success) {
    return axios.get(url, config);
  } else {
    axios.get(url, config).then(response => {
      let res = then(success, response, result);
      if(res == false){
        logout(this.$store, this.$router);
      }
    }).catch(error => {
      exception(error, result, url);
    });
    return result;
  }
}

// POST请求：自动附带token
export function post(url, data, success) {
  let result = {loading: true};
  let config = getTokenConfig(this.$store.state.token);
  // 如果无自定回调则直接post
  if (!success) {
    return axios.post(url, data, config);
  } else {
    // 执行post
    axios.post(url, data, config).then(response => {
      // 响应统一处理（token刷新、回调、异常提示）
      let res = then(success, response, result);
      // 若token过期，则需要重新登录
      if(res == false){
        logout(this.$store, this.$router);
      }
    }).catch(error => {
      exception(error, result, url);
    });
    return result;
  }
}

// 通用请求：axios.request透传配置
export function request(axiosRequestConfig, success) {
  let result = {loading: true};
  if (!success) {
    return axios.request(axiosRequestConfig);
  } else {
    axios.request(axiosRequestConfig).then(response => {
      let res = then(success, response, result);
      if(res == false){
        logout(this.$store, this.$router);
      }
    }).catch(error => {
      exception(error, result);
    });
    return result;
  }
}

// 文件下载：以blob响应并触发a标签保存
export function fileDownload(url) {
  let config = getTokenConfig(this.$store.state.token);
  config["responseType"] = 'blob';
  axios.get(url, config)
    .then(response => {
      let fileName = window.decodeURI(response.headers['content-disposition'].split('=')[1]);
      let link = document.createElement("a");
      link.href = window.URL.createObjectURL(new Blob([response.data], {type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=utf-8"})); // 文件类型
      link.download = fileName; // 文件名
      link.click();
    });
}

// 文件上传：支持单文件、多文件与额外参数（将param和file整理为一个FormData）
export function fileUpload(url, file, files, param, success) {
  let formData = new FormData();
  if (file) {
    formData.append("file", file); // 单文件
  }
  if (files) {
    files.forEach(f => {
      formData.append("files", f); // 多文件
    });
  }
  for (var key in param) {
    formData.append(key, param[key]); // 追加参数
  }
  // 整理上传配置：整理headers,data
  let axiosRequestConfig = getUploadConfig(this.$store.state.token, url, formData);
  return request(axiosRequestConfig, success);
}

export default {
  install(Vue) {

    if (!axios) {
      window.console.error('You have to install axios');
      return;
    }

    // axios.defaults.withCredentials = true;

    Vue.prototype.$login = login; // 登录

    Vue.prototype.$get = get; // GET

    Vue.prototype.$post = post; // POST

    Vue.prototype.$request = request; // 通用请求

    Vue.prototype.$fileDownload = fileDownload; // 文件下载

    Vue.prototype.$fileUpload = fileUpload; // 文件上传

    return axios;
  }
};
