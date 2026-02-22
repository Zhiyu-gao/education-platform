<template>
  <div class="login-container">
    <!-- 装饰性背景元素 -->
    <div class="background-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>
    
    <div class="login-form-wrapper">
      <div class="login-logo">
        <div class="logo-container">
          <el-icon class="logo-icon"><DataAnalysis /></el-icon>
        </div>
        <h1 class="login-title">融合rag的智能教育平台</h1>
        <p class="login-subtitle">智能学习·知识融合·高效提升</p>
      </div>
      <el-form
        ref="loginRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        auto-complete="on"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            type="text"
            size="large"
            auto-complete="off"
            placeholder="请输入账号"
            :prefix-icon="User"
            class="login-input username-input"
            :validate-event="false"
          >
            <template #prepend>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            size="large"
            auto-complete="off"
            placeholder="请输入密码"
            :show-password="showPassword"
            class="login-input password-input"
            @keyup.enter="handleLogin"
            :validate-event="false"
          >
            <template #prepend>
              <el-icon><Lock /></el-icon>
            </template>
            <template #append>
              <el-icon @click="showPassword = !showPassword" class="password-toggle">
                <i v-if="showPassword">👁️</i>
                <i v-else>👁️‍🗨️</i>
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="code" v-if="captchaEnabled" class="code-form-item">
          <el-input
            v-model="loginForm.code"
            size="large"
            auto-complete="off"
            placeholder="请输入验证码"
            class="login-input code-input"
            @keyup.enter="handleLogin"
            :validate-event="false"
          >
            <template #prepend>
              <el-icon><Document /></el-icon>
            </template>
          </el-input>
          <div class="login-code">
            <img
              :src="codeUrl"
              @click="getCode"
              class="login-code-img"
              alt="验证码"
              title="点击刷新验证码"
            />
          </div>
        </el-form-item>
        <div class="login-options">
          <el-checkbox v-model="loginForm.rememberMe" class="remember-me">
            记住密码
          </el-checkbox>
          <div v-if="register" class="register-link">
            <router-link class="link-type" :to="'/register'">立即注册</router-link>
          </div>
        </div>
        <el-form-item>
          <el-button
            :loading="loading"
            size="large"
            type="primary"
            style="width: 100%"
            @click.prevent="handleLogin"
            class="login-button gradient-button"
          >
            <template #default>
              <el-icon class="button-icon"><Loading v-if="loading" /></el-icon>
              <span>登 录</span>
            </template>
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    <!-- 底部 -->
    <div class="login-footer">
      <span>Copyright © 2018-2025 ruoyi.vip All Rights Reserved.</span>
    </div>
  </div>
</template>

<script setup>
import { getCodeImg } from "@/api/login"
import Cookies from "js-cookie"
import { encrypt, decrypt } from "@/utils/jsencrypt"
import useUserStore from '@/store/modules/user'
import { User, Lock, Document, DataAnalysis, Loading } from '@element-plus/icons-vue'

// 页面标题已在模板中直接设置为固定值
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const { proxy } = getCurrentInstance()

const showPassword = ref(false)
const loginForm = ref({
  username: "admin",
  password: "admin123",
  rememberMe: false,
  code: "",
  uuid: ""
})

const loginRules = {
  username: [{ required: true, trigger: "blur", message: "请输入您的账号" }],
  password: [{ required: true, trigger: "blur", message: "请输入您的密码" }],
  code: [{ required: true, trigger: "change", message: "请输入验证码" }]
}

const codeUrl = ref("")
const loading = ref(false)
// 验证码开关
const captchaEnabled = ref(true)
// 注册开关
const register = ref(true)
const redirect = ref(undefined)

watch(route, (newRoute) => {
    redirect.value = newRoute.query && newRoute.query.redirect
}, { immediate: true })

function handleLogin() {
  proxy.$refs.loginRef.validate(valid => {
    if (valid) {
      loading.value = true
      // 勾选了需要记住密码设置在 cookie 中设置记住用户名和密码
      if (loginForm.value.rememberMe) {
        Cookies.set("username", loginForm.value.username, { expires: 30 })
        Cookies.set("password", encrypt(loginForm.value.password), { expires: 30 })
        Cookies.set("rememberMe", loginForm.value.rememberMe, { expires: 30 })
      } else {
        // 否则移除
        Cookies.remove("username")
        Cookies.remove("password")
        Cookies.remove("rememberMe")
      }
      // 调用action的登录方法
      userStore.login(loginForm.value).then(() => {
        const query = route.query
        const otherQueryParams = Object.keys(query).reduce((acc, cur) => {
          if (cur !== "redirect") {
            acc[cur] = query[cur]
          }
          return acc
        }, {})
        router.push({ path: redirect.value || "/", query: otherQueryParams })
      }).catch(() => {
        loading.value = false
        // 重新获取验证码
        if (captchaEnabled.value) {
          getCode()
        }
      })
    }
  })
}

function getCode() {
  getCodeImg().then(res => {
    console.log("验证码接口响应成功，响应头：", res.headers); // 打印响应头，确认 uuid 存在
    console.log("验证码接口响应体类型：", typeof res.data); // 确认响应体是 blob 类型
    captchaEnabled.value = res.captchaEnabled === undefined ? true : res.captchaEnabled
    if (captchaEnabled.value) {
      codeUrl.value = "data:image/gif;base64," + res.img
      loginForm.value.uuid = res.uuid
    }
  })
}

function getCookie() {
  const username = Cookies.get("username")
  const password = Cookies.get("password")
  const rememberMe = Cookies.get("rememberMe")
  loginForm.value = {
    username: username === undefined ? loginForm.value.username : username,
    password: password === undefined ? loginForm.value.password : decrypt(password),
    rememberMe: rememberMe === undefined ? false : Boolean(rememberMe)
  }
}

getCode()
getCookie()
</script>

<style lang='scss' scoped>
.login-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background:
    radial-gradient(circle at 14% 10%, rgba(2, 132, 199, 0.16) 0, transparent 28%),
    radial-gradient(circle at 85% 90%, rgba(15, 118, 110, 0.16) 0, transparent 30%),
    linear-gradient(145deg, #f3f8fc 0%, #edf6f3 50%, #f8f6ef 100%);
  position: relative;
  overflow: hidden;
}

.background-shapes {
  position: absolute;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(2, 132, 199, 0.1);
  filter: blur(40px);
  animation: float 8s ease-in-out infinite;
}

.shape-1 {
  width: 300px;
  height: 300px;
  top: -50px;
  left: -50px;
  animation-delay: 0s;
}

.shape-2 {
  width: 400px;
  height: 400px;
  bottom: -100px;
  right: -100px;
  animation-delay: 2s;
  background: rgba(15, 118, 110, 0.14);
}

.shape-3 {
  width: 200px;
  height: 200px;
  top: 50%;
  left: 70%;
  transform: translate(-50%, -50%);
  animation-delay: 1s;
  background: rgba(245, 158, 11, 0.14);
}

.login-form-wrapper {
  background: rgba(255, 255, 255, 0.96);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(15px);
  width: 440px;
  padding: 40px;
  z-index: 1;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 6px;
    background: linear-gradient(90deg, #0f766e, #0284c7, #0f766e);
  }

  &:hover {
    box-shadow: 0 25px 80px rgba(0, 0, 0, 0.2);
    transform: translateY(-3px);
  }

  @media (max-width: 480px) {
    width: 92%;
    padding: 30px 25px;
  }
}

.login-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30px;
  flex-direction: column;
  position: relative;
}

.logo-container {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0f766e, #0284c7);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 15px;
  box-shadow: 0 10px 30px rgba(2, 132, 199, 0.3);
  animation: pulse 3s infinite;
  
  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: linear-gradient(135deg, #0f766e, #0284c7);
    transform: translate(-50%, -50%) scale(1.1);
    opacity: 0.6;
    z-index: -1;
  }
}

.logo-icon {
  font-size: 40px;
  color: white;
}

.login-title {
  font-size: 26px;
  font-weight: 700;
  color: #333;
  margin: 0 0 8px 0;
  text-align: center;
  background: linear-gradient(135deg, #0f766e, #0284c7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.login-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
  text-align: center;
  opacity: 0.8;
}

.login-form {
  width: 100%;
}

.login-input {
  border-radius: 10px;
  border: 2px solid #e1e5e9;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  height: 50px;
  font-size: 16px;
  background: white;
  
  .el-input__wrapper {
    box-shadow: none;
    border: none;
    background: transparent;
  }
  
  .el-input__inner {
    border: none;
    padding: 0 12px;
    font-size: 16px;
  }
  
  .el-input__prefix {
    left: 10px;
  }
  
  .el-input__suffix {
    right: 10px;
  }
  
  &.el-input-focus {
    border-color: #0284c7;
    box-shadow: 0 0 0 4px rgba(2, 132, 199, 0.15);
    transform: translateY(-1px);
  }
}

.password-toggle {
  cursor: pointer;
  color: #666;
  transition: color 0.3s;
  font-size: 18px;
  
  &:hover {
    color: #0284c7;
  }
}

.code-form-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.code-input {
  flex: 1;
  width: auto;
}

.login-code {
  flex-shrink: 0;
  width: 120px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-code-img {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  object-fit: cover;

  &:hover {
    transform: scale(1.02);
  }
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.remember-me {
  color: #666;
  font-size: 14px;
  .el-checkbox__label {
    padding-left: 6px;
  }
}

.register-link {
  font-size: 14px;
}

.link-type {
  color: #0284c7;
  text-decoration: none;
  transition: color 0.3s ease;

  &:hover {
    color: #0f766e;
    text-decoration: underline;
  }
}

.login-button {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  background: linear-gradient(135deg, #0f766e, #0284c7);
  border: none;
  border-radius: 8px;
  transition: all 0.3s ease;

  &:hover {
    background: linear-gradient(135deg, #0e9274, #0b79ab);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
  }

  &:active {
    transform: translateY(0);
  }
}

.login-footer {
  position: absolute;
  bottom: 20px;
  width: 100%;
  text-align: center;
  color: #4b6478;
  font-size: 12px;
  font-family: Arial;
  letter-spacing: 0.5px;
  z-index: 1;
}

// 动画效果
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// 添加平滑过渡
.el-form-item {
  margin-bottom: 20px;
}

.el-input__wrapper {
  border-radius: 8px !important;
}

.el-input-group__append,
.el-input-group__prepend {
  border-radius: 8px;
}
</style>
