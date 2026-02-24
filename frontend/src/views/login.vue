<template>
  <div class="login-page">
    <header class="top-nav">
      <div class="nav-inner">
        <div class="brand">
          <div class="brand-icon">教</div>
          <span>教育平台主控端</span>
        </div>

        <nav class="nav-links">
          <a href="#features">核心能力</a>
          <a href="#channels">端口分离</a>
          <a href="#ai">AI 服务</a>
          <a href="#security">权限安全</a>
        </nav>

        <div class="nav-actions" ref="navRef">
          <button class="btn ghost" @click.stop="showLoginPanel = !showLoginPanel">管理端登录</button>
          <button class="btn primary" @click="goPadAuth">Pad 端入口</button>

          <el-card v-show="showLoginPanel" shadow="always" class="nav-login-panel" @click.stop>
            <template #header>
              <div class="panel-title">主控制台账号登录</div>
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
        <div class="badge">主控端 / Pad 端 / Spring Boot / FastAPI</div>
        <h1>教育平台统一入口 <span>管理与教学分端协同</span></h1>
        <p>
          主控制台负责管理者全局业务；Pad 端面向老师与学生；Spring Boot 承载核心业务，FastAPI 专注 AI 能力。
        </p>
        <div class="hero-actions">
          <button class="btn primary" @click="showLoginPanel = true">进入管理端登录</button>
          <button class="btn ghost" @click="goPadAuth">进入 Pad 端</button>
        </div>
      </section>

      <section id="features" class="section">
        <h2>围绕当前技术栈与角色权限的核心能力</h2>
        <p class="section-subtitle">
          从主控端业务管理到 Pad 端教学协同，统一架构让管理、教学与 AI 能力高效联动。
        </p>
        <div class="feature-grid">
          <article class="feature-card">
            <div class="feature-icon lavender">📊</div>
            <h3>管理者全局视角</h3>
            <p>汇总查看班级成绩与教学数据，支撑学校级管理决策与任务统筹。</p>
          </article>
          <article class="feature-card">
            <div class="feature-icon mint">🧩</div>
            <h3>主控端 / Pad 端分离</h3>
            <p>管理者在主控端处理全局业务，老师与学生在 Pad 端完成教学闭环。</p>
          </article>
          <article class="feature-card">
            <div class="feature-icon lilac">👥</div>
            <h3>角色权限隔离</h3>
            <p>管理者、老师、学生按角色授权访问，页面能力和数据范围严格分开。</p>
          </article>
          <article class="feature-card">
            <div class="feature-icon sand">📝</div>
            <h3>作业考试编排</h3>
            <p>支持作业发布、考试安排、成绩回收与结果追踪，流程清晰可控。</p>
          </article>
          <article class="feature-card">
            <div class="feature-icon sky">🤖</div>
            <h3>AI 助手能力</h3>
            <p>通过 FastAPI 提供 RAG 问答与成绩预测能力，服务老师和学生的学习场景。</p>
          </article>
          <article class="feature-card">
            <div class="feature-icon rose">🛡️</div>
            <h3>服务边界清晰</h3>
            <p>Spring Boot 聚焦核心业务与鉴权，FastAPI 专注 AI 服务，降低耦合风险。</p>
          </article>
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

function goPadAuth() {
  router.push('/education/auth?redirect=/education/pad')
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
  --c-text: #1f2f46;
  --c-text-soft: #5f7491;
  --c-border: #d8e4f1;
  --c-surface: #ffffff;
  --c-accent: #1f7aff;
  --c-accent-2: #10a6a6;
  --c-accent-soft: #e7f3ff;
  min-height: 100vh;
  background: linear-gradient(180deg, #f1f7ff 0%, #f7fbff 100%);
  color: var(--c-text);
}

.top-nav {
  padding: 14px 18px;
}

.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
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
  background: linear-gradient(135deg, var(--c-accent), var(--c-accent-2));
  color: #fff;
  display: grid;
  place-items: center;
}

.nav-links {
  display: flex;
  gap: 26px;
}

.nav-links a {
  color: var(--c-text-soft);
  text-decoration: none;
}

.nav-actions {
  position: relative;
  display: flex;
  gap: 10px;
}

.btn {
  border: 1px solid var(--c-border);
  background: #f6fafd;
  color: var(--c-text);
  border-radius: 12px;
  padding: 10px 18px;
  font-weight: 600;
  cursor: pointer;
}

.btn.primary {
  color: #fff;
  background: linear-gradient(135deg, var(--c-accent), var(--c-accent-2));
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
  margin-bottom: 18px;
}

.code-item :deep(.el-form-item__content) {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: nowrap;
}

.code-item :deep(.el-input) {
  flex: 1;
  min-width: 0;
}

.code-img {
  width: 108px;
  height: 40px;
  border-radius: 8px;
  cursor: pointer;
  flex: 0 0 108px;
}

.row-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 4px 0 8px;
}

.register-link {
  color: var(--c-accent);
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
  display: flex;
  flex-direction: column;
  align-items: center;
}

.badge {
  display: inline-block;
  padding: 8px 14px;
  border-radius: 999px;
  background: var(--c-accent-soft);
  color: var(--c-accent);
  font-weight: 600;
  font-size: 12px;
}

.hero h1 {
  font-size: clamp(40px, 5vw, 72px);
  line-height: 1.1;
  margin: 20px 0 14px;
  white-space: nowrap;
  display: inline-block;
  text-align: center;
}

.hero h1 span {
  color: var(--c-accent);
}

.hero p {
  margin: 0;
  max-width: none;
  color: var(--c-text-soft);
  font-size: 20px;
  white-space: nowrap;
  display: inline-block;
  text-align: center;
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
  margin-bottom: 16px;
}

.section-subtitle {
  margin: 0 auto 30px;
  max-width: 760px;
  text-align: center;
  color: var(--c-text-soft);
  font-size: 18px;
  line-height: 1.7;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.feature-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 22px;
  min-height: 220px;
  padding: 34px 30px 30px;
  box-sizing: border-box;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  border-color: #c2d8ee;
  box-shadow: 0 14px 30px rgba(34, 60, 110, 0.08);
}

.feature-icon {
  width: 74px;
  height: 74px;
  border-radius: 20px;
  display: grid;
  place-items: center;
  font-size: 30px;
  margin-bottom: 22px;
}

.feature-card h3 {
  margin: 0;
  color: var(--c-text);
  font-size: 22px;
}

.feature-card p {
  margin: 14px 0 0;
  color: var(--c-text-soft);
  font-size: 18px;
  line-height: 1.6;
}

.lavender { background: #e8f1ff; }
.mint { background: #e6f8f5; }
.lilac { background: #edf3ff; }
.sand { background: #f2f4ff; }
.sky { background: #e8f6ff; }
.rose { background: #e9f8ff; }

@media (max-width: 1280px) {
  .feature-card {
    min-height: 240px;
    padding: 28px 24px;
  }

  .feature-card h3 {
    font-size: 20px;
  }

  .feature-card p {
    font-size: 17px;
  }
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

  .section-subtitle {
    font-size: 16px;
  }
}

@media (max-width: 640px) {
  .hero {
    margin-top: 44px;
  }

  .hero h1 {
    white-space: normal;
  }

  .hero p {
    white-space: normal;
  }

  .hero-actions {
    flex-direction: column;
  }

  .feature-grid {
    grid-template-columns: 1fr;
  }

  .feature-card {
    min-height: auto;
    padding: 24px 20px;
    border-radius: 18px;
  }

  .feature-icon {
    width: 64px;
    height: 64px;
    font-size: 26px;
    margin-bottom: 16px;
  }

  .feature-card h3 {
    font-size: 20px;
  }

  .feature-card p {
    font-size: 16px;
  }
}
</style>
