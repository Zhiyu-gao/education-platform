<template>
  <div class="edu-auth-page">
    <div class="bg-glow bg-glow-left"></div>
    <div class="bg-glow bg-glow-right"></div>

    <el-card class="auth-card" shadow="never">
      <div class="auth-header">
        <h1>Pad 端登录</h1>
        <p>请选择身份后登录或注册，进入老师/学生工作台</p>
      </div>

      <el-radio-group v-model="roleType" class="role-switch" size="large">
        <el-radio-button label="teacher">老师端</el-radio-button>
        <el-radio-button label="student">学生端</el-radio-button>
      </el-radio-group>

      <el-tabs v-model="activeTab" stretch>
        <el-tab-pane label="登录" name="login">
          <el-form ref="loginRef" :model="loginForm" :rules="loginRules" label-position="top">
            <el-form-item label="账号" prop="username">
              <el-input v-model="loginForm.username" placeholder="请输入账号" clearable />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                show-password
                placeholder="请输入密码"
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="年级" prop="gradeNo">
                  <el-select v-model="loginForm.gradeNo" placeholder="请选择年级">
                    <el-option v-for="g in gradeOptions" :key="g" :label="`${g}年级`" :value="g" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="班级" prop="classNo">
                  <el-select v-model="loginForm.classNo" placeholder="请选择班级">
                    <el-option v-for="c in classOptions" :key="c" :label="`${c}班`" :value="c" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item>
              <el-button class="submit-btn" type="primary" :loading="loading" @click="handleLogin">登录</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-alert
            v-if="roleType === 'teacher'"
            type="warning"
            show-icon
            :closable="false"
            title="老师端注册后会自动绑定 teacher 角色。"
            class="role-tip"
          />
          <el-form ref="registerRef" :model="registerForm" :rules="registerRules" label-position="top">
            <el-form-item label="账号" prop="username">
              <el-input v-model="registerForm.username" placeholder="请输入账号" clearable />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                show-password
                placeholder="请输入密码"
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                show-password
                placeholder="请再次输入密码"
                @keyup.enter="handleRegister"
              />
            </el-form-item>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="年级" prop="gradeNo">
                  <el-select v-model="registerForm.gradeNo" placeholder="请选择年级">
                    <el-option v-for="g in gradeOptions" :key="g" :label="`${g}年级`" :value="g" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="班级" prop="classNo">
                  <el-select v-model="registerForm.classNo" placeholder="请选择班级">
                    <el-option v-for="c in classOptions" :key="c" :label="`${c}班`" :value="c" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item>
              <el-button class="submit-btn" type="success" :loading="loading" @click="handleRegister">注册</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <div class="extra-actions">
        <el-button link @click="goManagerLogin">返回管理端登录</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { loginEducationUser, registerEducationUser } from '@/api/education/auth'
import { getToken, setToken } from '@/utils/auth'
import useUserStore from '@/store/modules/user'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

const activeTab = ref('login')
const roleType = ref('teacher')
const loading = ref(false)
const redirect = ref('/education/pad')

const loginRef = ref()
const registerRef = ref()

const loginForm = reactive({
  username: '',
  password: '',
  gradeNo: 1,
  classNo: 1
})

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  roleKey: 'student',
  gradeNo: 1,
  classNo: 1
})
const gradeOptions = [1, 2, 3, 4, 5]
const classOptions = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
    return
  }
  if (registerForm.password !== value) {
    callback(new Error('两次密码不一致'))
    return
  }
  callback()
}

const loginRules = {
  username: [{ required: true, trigger: 'blur', message: '请输入账号' }],
  password: [{ required: true, trigger: 'blur', message: '请输入密码' }],
  gradeNo: [{ required: true, trigger: 'change', message: '请选择年级' }],
  classNo: [{ required: true, trigger: 'change', message: '请选择班级' }]
}

const registerRules = {
  username: [
    { required: true, trigger: 'blur', message: '请输入账号' },
    { min: 2, max: 20, trigger: 'blur', message: '账号长度需在 2-20 位之间' }
  ],
  password: [
    { required: true, trigger: 'blur', message: '请输入密码' },
    { min: 5, max: 20, trigger: 'blur', message: '密码长度需在 5-20 位之间' }
  ],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }]
  ,
  gradeNo: [{ required: true, trigger: 'change', message: '请选择年级' }],
  classNo: [{ required: true, trigger: 'change', message: '请选择班级' }]
}

watch(
  () => route.query,
  (query) => {
    if (query && query.redirect) {
      redirect.value = String(query.redirect)
    }
    if (query && query.tab) {
      const tab = String(query.tab)
      activeTab.value = tab === 'register' ? 'register' : 'login'
    }
  },
  { immediate: true }
)

function normalizeRoles(roles = []) {
  return roles.map(role => String(role || '').toLowerCase())
}

function hasRoleByType(roles = []) {
  const roleKeys = normalizeRoles(roles)
  if (roleType.value === 'teacher') {
    return roleKeys.includes('teacher')
  }
  return roleKeys.includes('student') || roleKeys.includes('role_default')
}

async function handleLogin() {
  if (!loginRef.value) return
  const valid = await loginRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    if (getToken()) {
      await userStore.logOut()
    }

    const res = await loginEducationUser({
      username: loginForm.username,
      password: loginForm.password,
      gradeNo: loginForm.gradeNo,
      classNo: loginForm.classNo
    })
    setToken(res.token)
    userStore.token = res.token
    const info = await userStore.getInfo()

    if (!hasRoleByType(info.roles || [])) {
      await userStore.logOut()
      ElMessage.error(`当前账号不是${roleType.value === 'teacher' ? '老师' : '学生'}角色，请更换账号`)
      return
    }

    ElMessage.success('登录成功')
    const to = redirect.value && redirect.value.startsWith('/education') ? redirect.value : '/education/pad'
    router.push(to)
  } catch (error) {
    // 错误提示由全局 request 拦截器处理
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (!registerRef.value) return
  const valid = await registerRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await registerEducationUser({
      username: registerForm.username,
      password: registerForm.password,
      roleKey: roleType.value,
      gradeNo: registerForm.gradeNo,
      classNo: registerForm.classNo
    })

    await ElMessageBox.alert(
      `${roleType.value === 'teacher' ? '老师' : '学生'}账号注册成功，请登录后进入 Pad 端。`,
      '注册成功',
      { type: 'success' }
    )

    activeTab.value = 'login'
    loginForm.username = registerForm.username
    loginForm.password = ''
    registerForm.password = ''
    registerForm.confirmPassword = ''
  } catch (error) {
    // 错误提示由全局 request 拦截器处理
  } finally {
    loading.value = false
  }
}

function goManagerLogin() {
  router.push('/login')
}
</script>

<style scoped lang="scss">
.edu-auth-page {
  min-height: 100vh;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at 15% 20%, rgba(2, 132, 199, 0.18), transparent 40%),
    radial-gradient(circle at 80% 10%, rgba(15, 118, 110, 0.16), transparent 35%),
    linear-gradient(140deg, #f4fbff 0%, #edf7f7 42%, #f7f9ee 100%);
  overflow: hidden;
}

.bg-glow {
  position: absolute;
  width: 420px;
  height: 420px;
  border-radius: 50%;
  filter: blur(48px);
  opacity: 0.45;
}

.bg-glow-left {
  left: -140px;
  bottom: -180px;
  background: #0284c7;
}

.bg-glow-right {
  right: -140px;
  top: -180px;
  background: #0f766e;
}

.auth-card {
  width: 500px;
  max-width: calc(100vw - 32px);
  border-radius: 16px;
  border: 1px solid rgba(44, 62, 80, 0.08);
  position: relative;
  z-index: 2;
}

.auth-header {
  margin-bottom: 16px;

  h1 {
    margin: 0;
    font-size: 28px;
    color: #17324d;
  }

  p {
    margin: 8px 0 0;
    color: #4e6a84;
  }
}

.role-switch {
  margin-bottom: 18px;
}

.role-tip {
  margin-bottom: 12px;
}

.submit-btn {
  width: 100%;
}

.extra-actions {
  margin-top: 6px;
  text-align: center;
}

@media (max-width: 640px) {
  .auth-card {
    width: calc(100vw - 20px);
    border-radius: 12px;
  }

  .auth-header h1 {
    font-size: 24px;
  }

}
</style>
