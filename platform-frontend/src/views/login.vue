/**
 * 登录组件（登录与注册，支持记住密码与路由回跳）
 */
<template>
  <div class="login-wrap">
    <div class="welcome-title">
      <!-- 图片 -->
      <!-- <img class="logoimg" src="../assets/img/logo.png"> -->
      <span>A P I 自 动 化 测 试 平 台</span>
    </div>
    <!-- 登录表单：双向绑定loginForm并应用校验规则 -->
    <el-form label-position="left" :model="loginForm" :rules="rules" ref="loginForm" label-width="0px" class="demo-loginForm login-container">
      <h3 class="title">登录</h3>
      <el-form-item prop="account"> <!-- 账号输入：绑定loginForm.account -->
        <el-input type="text" id="username" v-model="loginForm.account" placeholder="账号/手机号"></el-input>
      </el-form-item>
      <el-form-item prop="password"> <!-- 密码输入：回车触发提交 -->
        <el-input type="password" id="password" v-model="loginForm.password" @keyup.enter.native="submitForm('loginForm')" placeholder="密码"></el-input>
      </el-form-item>
      <el-row style="margin-top: -10px">
        <el-col :span="8">
          <el-checkbox class="remember" v-model="rememberpwd">记住密码</el-checkbox>
        </el-col>
        <el-col :span="16">
          <el-button type="text" style="float:right" @click="registerVisible = true">立即注册</el-button>
        </el-col>
      </el-row>
      <el-form-item style="width:100%; margin-top:20px"> <!-- 提交按钮：显示加载态 -->
        <el-button type="primary" id="login" style="width:100%;" @click="submitForm('loginForm')" :loading="logining">登录</el-button>
      </el-form-item>
    </el-form>
    <!-- 注册弹窗：同步可见性并销毁关闭内容 -->
    <el-dialog title="注册用户" :visible.sync="registerVisible" width="450px" destroy-on-close>
      <el-form ref="registerForm" :rules="rules" :model="registerForm" label-width="80px">
          <el-form-item label="登录账号" prop="newAccount">
            <el-input size="small" style="width: 320px" v-model="registerForm.newAccount" placeholder="请输入登录账号"/>
          </el-form-item>
          <el-form-item label="手机号" prop="mobile">
            <el-input size="small" style="width: 320px" v-model="registerForm.mobile" placeholder="请输入手机号"/>
          </el-form-item>
          <el-form-item label="用户昵称" prop="username">
            <el-input size="small" style="width: 320px" v-model="registerForm.username" placeholder="请输入用户昵称"/>
          </el-form-item>
          <el-form-item label="邮箱地址" prop="email">
            <el-input size="small" style="width: 320px" v-model="registerForm.email" placeholder="请输入邮箱地址"/>
          </el-form-item>
          <el-form-item label="登录密码" prop="newPassword">
            <el-input size="small" type="password" style="width: 320px" v-model="registerForm.newPassword" placeholder="请输入6-16位密码"/>
          </el-form-item>
          <el-form-item label="确认密码" prop="repeatPassword">
            <el-input size="small" type="password" style="width: 320px" v-model="registerForm.repeatPassword" placeholder="请再次输入密码"/>
          </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
          <el-button size="small" style="margin-right:10px" type="primary" @click="registerUser">注册</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script type="text/ecmascript-6">
import { setCookie, getCookie, delCookie } from '../utils/util'

export default {
  name: 'login', // 组件名称：登录页
  // 表单与校验规则定义
  data() {
    var validateMobile = (rule, value, callback) => {
      if(value.length !== 11 || !(/^(((13[0-9]{1})|(14[0-9]{1})|(15[0-9]{1})|(16[0-9]{1})|(17[0-9]{1})|(18[0-9]{1})|(19[0-9]{1})|)+\d{8})$/.test(value))) {
        callback(new Error('手机号格式不正确'));
      }else{
        callback();
      }
    };
    var validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入密码'));
      } else {
        if (value.length < 6 || value.length > 16){
          callback(new Error('密码长度不符合规范'));
        }else if (this.registerForm.repeatPassword !== '') {
          this.$refs.registerForm.validateField('repeatPassword');
        }
        callback();
      }
    };
    var validatePass2 = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'));
      } else if (value.length < 6 || value.length > 16){
        callback(new Error('密码长度不符合规范'));
      } else if (value !== this.registerForm.newPassword) {
        callback(new Error('两次输入密码不一致!'));
      } else {
        callback();
      }
    };
    return {
      logining: false,
      rememberpwd: false,
      loginForm: {
        account: '',
        password: '',
      },
      registerVisible: false,
      registerForm: {},
      sendStatus: false,
      sendText: "获取验证码",
      countdown: 60,
      timer: null,
      // 表单校验规则：账号/密码/手机号/昵称/邮箱
      rules: {
        account: [{ required: true, message: '账号不能为空', trigger: 'blur' }],
        password: [{ required: true, message: '密码不能为空', trigger: 'blur' }],
        newPassword: [{ required: true, message: '密码不能为空', trigger: 'blur' },
                  { validator: validatePass, trigger: 'blur', required: true }],
        repeatPassword: [{ required: true, message: '确认密码不能为空', trigger: 'blur' },
                  { validator: validatePass2, trigger: 'blur', required: true }],
        mobile: [{ required: true, message: '手机号不能为空', trigger: 'blur' },
                  { validator: validateMobile, trigger: 'blur', required: true }],
        username: [{ required: true, message: '用户名不能为空', trigger: 'blur' }],
        email: [{ required: true, message: '邮箱地址不能为空', trigger: 'blur' }],
        newAccount: [{ required: true, message: '登录账号不能为空', trigger: 'blur' }]
      }
    }
  },
  // 初始化生命周期：尝试读取cookie以回填表单
  created() {
    // 初始化：从cookie读取账号与密码
    this.getuserpwd()
  },
  methods: {
    // 获得用户名和密码（从本地cookie中获得）
    getuserpwd() {
      if (getCookie('user') != '' && getCookie('pwd') != '') {
        this.loginForm.account = getCookie('user')
        this.loginForm.password = getCookie('pwd')
        this.rememberpwd = true
      }
    },

    // 注册用户：校验注册表单并提交
    registerUser(){
      // 关键步骤：校验通过后对密码进行Base64编码
      this.$refs["registerForm"].validate(valid => {
          if (valid) {
              let url = '/autotest/register';
              // 导入Base64，并encode密码（传输安全性基础处理）
              let Base64 = require('js-base64').Base64;
              this.registerForm.password = Base64.encode(this.registerForm.newPassword);
              this.registerForm.account = this.registerForm.newAccount;  
              this.$post(url, this.registerForm, response =>{
                if(response.data !== "注册成功"){
                  this.$message.warning(response.data);
                }else{
                  this.$message.success(response.data);
                  this.registerVisible = false;
                }
              });
          }else{
              return false;
          }
      })
    },

    // 提交登录：校验通过后编码密码并请求登录
    submitForm(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.logining = true;
          // 关键步骤：密码进行Base64编码后再提交
          let Base64 = require('js-base64').Base64;
          let loginForm = {
            account: this.loginForm.account,
            password: Base64.encode(this.loginForm.password)
          }; 
          this.$login("/autotest/login", loginForm, response => {
            if (response.data.status === 0) {
              if (this.rememberpwd) {
                //保存帐号密码到cookie，有效期7天
                setCookie('user', this.loginForm.account, 7);
                setCookie('pwd', this.loginForm.password, 7);
              } else {
                delCookie('user');
                delCookie('pwd');
              }
              // 缓存用户个人信息
              localStorage.setItem("userInfo", JSON.stringify(response.data.data));
              localStorage.setItem("token", response.headers.token);
              this.$store.commit('set_token', response.headers.token);
              this.$store.commit('set_userInfo', response.data.data);
              setTimeout(() => {
                this.logining = false;
                // 关键步骤：根据重定向参数决定跳转目标
                if(this.$router.currentRoute.query.redirect){
                  this.$router.push({ path: this.$router.currentRoute.query.redirect});
                }else{
                  this.$router.push({ path: '/home/dashboard'});
                }
              }, 1000)
            } else {
              this.$message.error(response.data.message + "  " + response.data.data);
              this.logining = false;
              return false;
            }
          })
        } 
      })
    },
  }
}
</script>

<style scoped>
/* 登录页外层容器：铺满窗口并控制背景展示 */
.login-wrap {
  box-sizing: border-box; /* 统一盒模型 */
  width: 100%; /* 充满宽度 */
  height: 100%; /* 充满高度 */
  padding-top: 10%; /* 顶部留白 */
  /* background-color: #112346; */
  background-repeat: no-repeat; /* 背景不重复 */
  background-position: center right; /* 背景定位 */
  background-size: 100%; /* 背景缩放 */
}
.welcome-title{
  font-family: initial; /* 字体族 */
  text-align: center; /* 居中 */
  font-size: 36px; /* 标题字号 */
  margin-bottom: 40px; /* 底部间距 */
}
.footer{
  position: fixed; /* 固定在底部 */
  font-size: 12px; /* 字号 */
  left: 0; /* 左侧对齐 */
  right: 0; /* 右侧对齐 */
  bottom: 0; /* 底部对齐 */
}
.login-container {
  border-radius: 10px; /* 圆角 */
  margin: 0px auto; /* 居中 */
  width: 350px; /* 宽度 */
  padding: 30px 35px 15px 35px; /* 内边距 */
  background: #fff; /* 背景白色 */
  border: 1px solid #eaeaea; /* 边框 */
  text-align: left; /* 左对齐 */
  box-shadow: 0 0 20px 2px rgba(0, 0, 0, 0.1); /* 阴影 */
}
.title {
  margin: 0px auto 40px auto; /* 上左右下间距 */
  text-align: center; /* 居中 */
  color: #505458; /* 颜色 */
}
.remember {
  margin: 11px 0px 0px 0px; /* 外边距 */
}
.logoimg{
  width: 40px; /* 宽度 */
  height: 40px; /* 高度 */
  margin-bottom: 4px; /* 底部间距 */
}
</style>