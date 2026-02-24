<template>
  <div class="login-page">
    <header class="top-nav">
      <div class="nav-inner">
        <div class="brand">
          <div class="brand-icon">P</div>
          <span>PAD HelpDesk</span>
        </div>

        <nav class="nav-links">
          <a href="#features">Features</a>
          <a href="#channels">Channels</a>
          <a href="#ai">AI Assistant</a>
          <a href="#pricing">Pricing</a>
        </nav>

        <div class="nav-actions" ref="navRef">
          <button class="btn ghost" @click.stop="showLoginPanel = !showLoginPanel">Sign In</button>
          <button class="btn primary">Start Free</button>

          <el-card v-show="showLoginPanel" shadow="always" class="nav-login-panel" @click.stop>
            <template #header>
              <div class="panel-title">账号登录</div>
            </template>

            <el-form ref="loginRef" :model="loginForm" :rules="loginRules" class="login-form" auto-complete="on">
              <el-form-item prop="username">
                <el-input v-model="loginForm.username" placeholder="请输入账号" :prefix-icon="User" />
              </el-form-item>
              <el-form-item prop="password">
                <el-input
                  v-model="loginForm.password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="请输入密码"
                  :prefix-icon="Lock"
                  @keyup.enter="handleLogin"
                />
              </el-form-item>
              <el-form-item prop="code" v-if="captchaEnabled" class="code-item">
                <el-input v-model="loginForm.code" placeholder="验证码" :prefix-icon="Document" @keyup.enter="handleLogin" />
                <img :src="codeUrl" class="code-img" alt="验证码" @click="getCode" />
              </el-form-item>

              <div class="row-between">
                <el-checkbox v-model="loginForm.rememberMe">记住密码</el-checkbox>
                <router-link v-if="register" to="/register" class="register-link">立即注册</router-link>
              </div>

              <el-button type="primary" :loading="loading" class="submit-btn" @click.prevent="handleLogin">登 录</el-button>
            </el-form>
          </el-card>
        </div>
      </div>
    </header>

    <main>
      <section class="hero">
        <div class="badge">Rated #1 in Customer Satisfaction</div>
        <h1>Delight Your Customers<br /><span>With Every Interaction</span></h1>
        <p>
          统一会话、智能分配、自动化处理，让老师和学生在 Pad 端获得更顺滑的服务体验。
        </p>
        <div class="hero-actions">
          <button class="btn primary">Start 14-Day Free Trial</button>
          <button class="btn ghost">Watch Demo</button>
        </div>
      </section>

      <section id="features" class="section">
        <h2>Everything You Need for Great Support</h2>
        <div class="feature-grid">
          <div class="feature-card">Unified Inbox</div>
          <div class="feature-card">Smart Automation</div>
          <div class="feature-card">Team Collaboration</div>
          <div class="feature-card">Real-time Analytics</div>
          <div class="feature-card">Knowledge Base</div>
          <div class="feature-card">Enterprise Security</div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { getCodeImg } from '@/api/login'
import Cookies from 'js-cookie'
import { encrypt, decrypt } from '@/utils/jsencrypt'
import useUserStore from '@/store/modules/user'
import { User, Lock, Document } from '@element-plus/icons-vue'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const { proxy } = getCurrentInstance()

const navRef = ref(null)
const showLoginPanel = ref(false)
const showPassword = ref(false)

const loginForm = ref({
  username: 'admin',
  password: 'admin123',
  rememberMe: false,
  code: '',
  uuid: ''
})

const loginRules = {
  username: [{ required: true, trigger: 'blur', message: '请输入账号' }],
  password: [{ required: true, trigger: 'blur', message: '请输入密码' }],
  code: [{ required: true, trigger: 'change', message: '请输入验证码' }]
}

const codeUrl = ref('')
const loading = ref(false)
const captchaEnabled = ref(true)
const register = ref(true)
const redirect = ref(undefined)

watch(
  route,
  (newRoute) => {
    redirect.value = newRoute.query && newRoute.query.redirect
  },
  { immediate: true }
)

const onDocClick = (e) => {
  if (!showLoginPanel.value) return
  if (!navRef.value) return
  if (!navRef.value.contains(e.target)) showLoginPanel.value = false
}

onMounted(() => {
  document.addEventListener('click', onDocClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', onDocClick)
})

function handleLogin() {
  proxy.$refs.loginRef.validate((valid) => {
    if (!valid) return
    loading.value = true

    if (loginForm.value.rememberMe) {
      Cookies.set('username', loginForm.value.username, { expires: 30 })
      Cookies.set('password', encrypt(loginForm.value.password), { expires: 30 })
      Cookies.set('rememberMe', loginForm.value.rememberMe, { expires: 30 })
    } else {
      Cookies.remove('username')
      Cookies.remove('password')
      Cookies.remove('rememberMe')
    }

    userStore
      .login(loginForm.value)
      .then(() => {
        const query = route.query
        const otherQueryParams = Object.keys(query).reduce((acc, cur) => {
          if (cur !== 'redirect') acc[cur] = query[cur]
          return acc
        }, {})
        showLoginPanel.value = false
        router.push({ path: redirect.value || '/', query: otherQueryParams })
      })
      .catch(() => {
        loading.value = false
        if (captchaEnabled.value) getCode()
      })
  })
}

function getCode() {
  getCodeImg().then((res) => {
    captchaEnabled.value = res.captchaEnabled === undefined ? true : res.captchaEnabled
    if (captchaEnabled.value) {
      codeUrl.value = 'data:image/gif;base64,' + res.img
      loginForm.value.uuid = res.uuid
    }
  })
}

function getCookie() {
  const username = Cookies.get('username')
  const password = Cookies.get('password')
  const rememberMe = Cookies.get('rememberMe')
  loginForm.value = {
    username: username === undefined ? loginForm.value.username : username,
    password: password === undefined ? loginForm.value.password : decrypt(password),
    rememberMe: rememberMe === undefined ? false : Boolean(rememberMe),
    code: '',
    uuid: ''
  }
}

getCode()
getCookie()
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f5f6ff 0%, #f9fbff 100%);
  color: #1f2a44;
}

.top-nav {
  padding: 14px 18px;
}

.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  background: #fff;
  border: 1px solid #e5eaf3;
  border-radius: 16px;
  padding: 14px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
}

.brand-icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6f6dff, #5a66f8);
  color: #fff;
  display: grid;
  place-items: center;
}

.nav-links {
  display: flex;
  gap: 26px;
}

.nav-links a {
  color: #6a7694;
  text-decoration: none;
}

.nav-actions {
  position: relative;
  display: flex;
  gap: 10px;
}

.btn {
  border: 1px solid #dbe2ef;
  background: #f7f9fc;
  color: #1f2a44;
  border-radius: 12px;
  padding: 10px 18px;
  font-weight: 600;
  cursor: pointer;
}

.btn.primary {
  color: #fff;
  background: linear-gradient(135deg, #6f6dff, #5a66f8);
  border-color: transparent;
}

.nav-login-panel {
  position: absolute;
  right: 0;
  top: calc(100% + 10px);
  width: min(380px, 92vw);
  border-radius: 14px;
  z-index: 20;
}

.panel-title {
  font-weight: 700;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.code-item {
  display: grid;
  grid-template-columns: 1fr 108px;
  gap: 10px;
}

.code-img {
  width: 100%;
  height: 40px;
  border-radius: 8px;
  cursor: pointer;
}

.row-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 4px 0 8px;
}

.register-link {
  color: #5a66f8;
  text-decoration: none;
}

.submit-btn {
  width: 100%;
}

.hero {
  max-width: 900px;
  margin: 80px auto 40px;
  text-align: center;
  padding: 0 16px;
}

.badge {
  display: inline-block;
  padding: 8px 14px;
  border-radius: 999px;
  background: #ebeaff;
  color: #5a66f8;
  font-weight: 600;
  font-size: 12px;
}

.hero h1 {
  font-size: clamp(40px, 5vw, 72px);
  line-height: 1.1;
  margin: 20px 0 14px;
}

.hero h1 span {
  color: #5a66f8;
}

.hero p {
  margin: 0 auto;
  max-width: 700px;
  color: #6d7a95;
  font-size: 20px;
}

.hero-actions {
  margin-top: 28px;
  display: flex;
  justify-content: center;
  gap: 12px;
}

.section {
  max-width: 1200px;
  margin: 100px auto 0;
  padding: 0 16px 80px;
}

.section h2 {
  text-align: center;
  font-size: clamp(30px, 3.4vw, 52px);
  margin-bottom: 28px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.feature-card {
  background: #fff;
  border: 1px solid #e3e8f2;
  border-radius: 14px;
  min-height: 120px;
  display: grid;
  place-items: center;
  color: #42506e;
  font-weight: 600;
}

@media (max-width: 960px) {
  .nav-links {
    display: none;
  }

  .feature-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .hero p {
    font-size: 18px;
  }
}

@media (max-width: 640px) {
  .hero {
    margin-top: 44px;
  }

  .hero-actions {
    flex-direction: column;
  }

  .feature-grid {
    grid-template-columns: 1fr;
  }
}
</style>
