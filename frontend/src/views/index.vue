<template>
  <div class="app-container home">
    <el-row :gutter="20">
      <el-col :sm="24" :lg="24" style="text-align: center; margin-bottom: 30px;">
        <h1>融合rag的智能教育平台</h1>
        <p>致力于提供智能化的教育解决方案，助力学生成长和教师教学</p>
      </el-col>
    </el-row>

    <!-- 首页架构总览 -->
    <el-row :gutter="20" style="margin-bottom: 30px;">
      <el-col :xs="24" :md="12">
        <el-card class="arch-card">
          <template #header>
            <div class="card-header">
              <i class="el-icon-share"></i>
              <span>技术架构图（主控端 / Pad端 / 后端 / AI）</span>
            </div>
          </template>
          <div class="arch-flow">
            <div class="arch-node strong">统一入口</div>
            <div class="arch-arrow">↓</div>
            <div class="arch-row">
              <div class="arch-node">主控端（管理界面）</div>
              <div class="arch-node">Pad端入口</div>
            </div>
            <div class="arch-arrow">↓</div>
            <div class="arch-row">
              <div class="arch-group">
                <h4>主控端角色</h4>
                <el-tag type="danger">总管理员</el-tag>
                <el-tag type="warning">学校管理员</el-tag>
                <el-tag>业务管理者</el-tag>
              </div>
              <div class="arch-group">
                <h4>Pad端角色</h4>
                <el-tag type="success">老师（education）</el-tag>
                <el-tag type="info">学生（education）</el-tag>
              </div>
            </div>
            <div class="arch-arrow">↓</div>
            <div class="arch-row">
              <div class="arch-group service">
                <h4>Spring Boot</h4>
                <p>用户/角色/权限鉴权、作业/考试/成绩/任务、数据隔离</p>
              </div>
              <div class="arch-group service">
                <h4>FastAPI</h4>
                <p>AI能力：RAG检索问答、成绩预测</p>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card class="arch-card">
          <template #header>
            <div class="card-header">
              <i class="el-icon-s-operation"></i>
              <span>权限层级图（部门到人员）</span>
            </div>
          </template>
          <div class="perm-flow">
            <div class="perm-level">
              <h4>总管理员（平台级）</h4>
              <p>查看所有学校所有班级成绩；跨学校统计与监管</p>
            </div>
            <div class="arch-arrow">↓</div>
            <div class="perm-level">
              <h4>学校管理员（校级）</h4>
              <p>查看本学校所有班级成绩；管理本学校任务与运营</p>
            </div>
            <div class="arch-arrow">↓</div>
            <div class="perm-level">
              <h4>老师（班级级）</h4>
              <p>布置作业/考试；仅查看自己班级学生成绩；可用AI助手</p>
            </div>
            <div class="arch-arrow">↓</div>
            <div class="perm-level">
              <h4>学生（个人级）</h4>
              <p>查看并提交自己的作业；仅查看自己的考试成绩；可用AI助手</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-bottom: 30px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <i class="el-icon-data-analysis"></i>
              <span>权限矩阵（角色 × 功能）</span>
            </div>
          </template>
          <el-table :data="permissionMatrix" border stripe>
            <el-table-column prop="feature" label="功能" min-width="220" />
            <el-table-column prop="superAdmin" label="总管理员" min-width="110" />
            <el-table-column prop="schoolAdmin" label="学校管理员" min-width="130" />
            <el-table-column prop="manager" label="业务管理者" min-width="120" />
            <el-table-column prop="teacher" label="老师（Pad）" min-width="120" />
            <el-table-column prop="student" label="学生（Pad）" min-width="120" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 主要功能模块 -->
    <el-row :gutter="20" style="margin-bottom: 30px;">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <i class="el-icon-user-solid"></i>
              <span>学生信息管理</span>
            </div>
          </template>
          <div class="card-body">
            <ul>
              <li>学生信息录入与管理</li>
              <li>学习数据统计与分析</li>
              <li>个人档案管理</li>
            </ul>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <i class="el-icon-monitor"></i>
              <span>大屏可视化</span>
            </div>
          </template>
          <div class="card-body">
            <ul>
              <li>学生可视化自己的成绩</li>
              <li>教师可视化班级成绩</li>
              <li>数据图表动态展示</li>
            </ul>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <i class="el-icon-robot"></i>
              <span>教育智能助手</span>
            </div>
          </template>
          <div class="card-body">
            <ul>
              <li>自动识别数学公式</li>
              <li>批改作文和作业</li>
              <li>自动生成练习题</li>
              <li>实时解答问题和心理疏导</li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-bottom: 30px;">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <i class="el-icon-data-analysis"></i>
              <span>教育情况预测</span>
            </div>
          </template>
          <div class="card-body">
            <ul>
              <li>输入相关信息，预测成绩</li>
              <li>预测学生毕业去向</li>
              <li>预警学生学习状态</li>
            </ul>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <i class="el-icon-folder-opened"></i>
              <span>资料圈</span>
            </div>
          </template>
          <div class="card-body">
            <ul>
              <li>学习资料分享</li>
              <li>评论与点赞</li>
              <li>资料收藏与粘贴</li>
            </ul>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <i class="el-icon-upload"></i>
              <span>上传自定义题目</span>
            </div>
          </template>
          <div class="card-body">
            <ul>
              <li>支持上传自定义题目pk</li>
              <li>题目导入与管理</li>
              <li>个性化练习设置</li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 技术栈 -->
    <el-row :gutter="20" style="margin-bottom: 30px;">
      <el-col :span="24">
        <el-card class="tech-stack">
          <template #header>
            <div class="card-header">
              <i class="el-icon-cpu"></i>
              <span>技术栈</span>
            </div>
          </template>
          <div class="card-body">
            <el-tag type="primary" v-for="tech in techStack" :key="tech" style="margin: 5px;">{{ tech }}</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 其他功能 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="other-functions">
          <template #header>
            <div class="card-header">
              <i class="el-icon-menu"></i>
              <span>其他功能</span>
            </div>
          </template>
          <div class="card-body">
            <div class="function-grid">
              <el-button type="default" plain v-for="func in otherFunctions" :key="func.key" @click="goToFunction(func.key)">
                {{ func.name }}
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="noteDialogVisible" title="笔记中心" width="900px">
      <el-row :gutter="16">
        <el-col :xs="24" :md="10">
          <el-card shadow="never" class="note-publish-card">
            <template #header>发布笔记</template>
            <el-form :model="noteForm" label-width="68px">
              <el-form-item label="标题">
                <el-input v-model="noteForm.title" placeholder="请输入笔记标题" maxlength="60" />
              </el-form-item>
              <el-form-item label="内容">
                <el-input v-model="noteForm.content" type="textarea" :rows="8" placeholder="请输入笔记内容" maxlength="2000" show-word-limit />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="noteSubmitting" @click="submitNote">发布笔记</el-button>
                <el-button link type="primary" @click="refreshNotes">刷新</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
        <el-col :xs="24" :md="14">
          <el-card shadow="never" class="note-list-card">
            <template #header>
              <div class="card-header">
                <span>笔记列表</span>
                <el-radio-group v-model="noteViewMode" size="small">
                  <el-radio-button label="all">全部笔记</el-radio-button>
                  <el-radio-button label="mine">我的笔记</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            <el-empty v-if="filteredNotes.length === 0" description="暂无笔记" />
            <div v-for="note in filteredNotes" :key="note.post_id" class="note-item">
              <div class="note-title">{{ parseNoteTitle(note.title) }}</div>
              <div class="note-meta">{{ note.author_name }} · {{ note.create_time }}</div>
              <div class="note-content">{{ note.content }}</div>
              <el-input
                v-model="noteReplyMap[note.post_id]"
                placeholder="回复这条笔记"
                size="small"
                @keyup.enter="replyNote(note.post_id)"
              />
              <div class="note-actions">
                <el-button link type="primary" size="small" @click="replyNote(note.post_id)">回复</el-button>
              </div>
              <div v-if="note.replies && note.replies.length" class="note-reply-list">
                <div v-for="reply in note.replies" :key="reply.reply_id" class="note-reply-item">
                  {{ reply.author_name }}：{{ reply.content }}
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-dialog>

    <el-dialog v-model="punchDialogVisible" title="打卡记录" width="560px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <span>今日日期：{{ todayText() }}</span>
        <el-button type="primary" @click="submitPunch">立即打卡</el-button>
      </div>
      <el-table :data="punchRecords" size="small" max-height="320">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="time" label="时间" width="120" />
        <el-table-column prop="userName" label="用户" />
      </el-table>
    </el-dialog>

    <el-dialog v-model="contactDialogVisible" title="联系我们" width="560px">
      <el-alert title="支持邮箱：edu-support@example.com；工作日 9:00-18:00" type="info" :closable="false" style="margin-bottom:12px;" />
      <el-form :model="contactForm" label-width="80px">
        <el-form-item label="联系人">
          <el-input v-model="contactForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="contactForm.phone" placeholder="请输入联系电话（可选）" />
        </el-form-item>
        <el-form-item label="咨询内容">
          <el-input v-model="contactForm.message" type="textarea" :rows="5" placeholder="请输入咨询内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="contactDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="contactSubmitting" @click="submitContact">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="feedbackDialogVisible" title="满意度调查" width="560px">
      <el-form :model="feedbackForm" label-width="90px">
        <el-form-item label="满意度">
          <el-rate v-model="feedbackForm.score" show-score score-template="{value} 分" />
        </el-form-item>
        <el-form-item label="反馈内容">
          <el-input v-model="feedbackForm.content" type="textarea" :rows="6" placeholder="请填写你的建议或意见" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="feedbackDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="feedbackSubmitting" @click="submitFeedback">提交反馈</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="Index">
import { computed, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import useUserStore from '@/store/modules/user'
import { createForumPost, listForumPosts, replyForumPost } from '@/api/education/forum'

const techStack = ['tensorflow', 'vue3', 'elementplus', 'fastapi', 'langchain', 'LLM', 'RAG', 'nginx', 'docker']
const router = useRouter()
const userStore = useUserStore()
const NOTE_TITLE_PREFIX = '[NOTE]'
const permissionMatrix = [
  { feature: '查看所有学校成绩', superAdmin: '✅', schoolAdmin: '❌', manager: '❌', teacher: '❌', student: '❌' },
  { feature: '查看本学校所有班级成绩', superAdmin: '✅', schoolAdmin: '✅', manager: '✅（按授权）', teacher: '❌', student: '❌' },
  { feature: '查看本班学生成绩', superAdmin: '❌', schoolAdmin: '✅（汇总视角）', manager: '✅（按授权）', teacher: '✅（仅自己班）', student: '❌' },
  { feature: '查看个人成绩', superAdmin: '❌', schoolAdmin: '❌', manager: '❌', teacher: '❌', student: '✅（仅本人）' },
  { feature: '创建学生作业任务', superAdmin: '✅', schoolAdmin: '✅', manager: '✅', teacher: '✅（本班）', student: '❌' },
  { feature: '创建老师任务', superAdmin: '✅', schoolAdmin: '✅', manager: '✅', teacher: '❌', student: '❌' },
  { feature: '布置考试', superAdmin: '✅（策略）', schoolAdmin: '✅（校级）', manager: '✅（按授权）', teacher: '✅（本班）', student: '❌' },
  { feature: 'Pad端登录/注册后进入业务', superAdmin: '可进入（协同）', schoolAdmin: '可进入（协同）', manager: '可进入（协同）', teacher: '✅', student: '✅' },
  { feature: 'AI助手（RAG/成绩预测）', superAdmin: '可选', schoolAdmin: '可选', manager: '可选', teacher: '✅', student: '✅' }
]

const otherFunctions = [
  { key: 'orgManage', name: '组织管理' },
  { key: 'userManage', name: '人员管理' },
  { key: 'classManage', name: '班级管理' },
  { key: 'pad', name: 'Pad端入口' },
  { key: 'login', name: '登录' },
  { key: 'register', name: '注册' },
  { key: 'punch', name: '打卡记录' },
  { key: 'searchNote', name: '搜索笔记' },
  { key: 'myNote', name: '我的笔记' },
  { key: 'questionRecord', name: '错题记录' },
  { key: 'myScore', name: '我的成绩' },
  { key: 'contactUs', name: '联系我们' },
  { key: 'feedback', name: '满意度调查' },
  { key: 'logout', name: '退出登录' }
]

const noteDialogVisible = ref(false)
const noteSubmitting = ref(false)
const noteViewMode = ref('all')
const notePosts = ref([])
const noteForm = reactive({ title: '', content: '' })
const noteReplyMap = reactive({})
const punchDialogVisible = ref(false)
const contactDialogVisible = ref(false)
const feedbackDialogVisible = ref(false)
const contactSubmitting = ref(false)
const feedbackSubmitting = ref(false)
const contactForm = reactive({
  name: '',
  phone: '',
  message: ''
})
const feedbackForm = reactive({
  score: 5,
  content: ''
})
const punchRecords = ref([])
const filteredNotes = computed(() => {
  const mineId = Number(userStore.id || 0)
  const list = (notePosts.value || []).filter(item => isNotePost(item.title))
  if (noteViewMode.value === 'mine') {
    return list.filter(item => Number(item.author_id) === mineId)
  }
  return list
})

function isNotePost(title) {
  const value = String(title || '')
  return value.startsWith(NOTE_TITLE_PREFIX) || value.startsWith('NOTE:')
}

function parseNoteTitle(title) {
  const value = String(title || '')
  if (value.startsWith(NOTE_TITLE_PREFIX)) return value.replace(/^\[NOTE\]\s*/, '')
  if (value.startsWith('NOTE:')) return value.replace(/^NOTE:\s*/, '')
  return value
}

function getPunchStorageKey() {
  const uid = Number(userStore.id || 0)
  return `edu_punch_records_${uid || 'guest'}`
}

function loadPunchRecords() {
  try {
    const raw = localStorage.getItem(getPunchStorageKey())
    const list = raw ? JSON.parse(raw) : []
    punchRecords.value = Array.isArray(list) ? list : []
  } catch (error) {
    punchRecords.value = []
  }
}

function savePunchRecords() {
  localStorage.setItem(getPunchStorageKey(), JSON.stringify(punchRecords.value || []))
}

function todayText() {
  return new Date().toISOString().slice(0, 10)
}

async function openPunchDialog() {
  loadPunchRecords()
  punchDialogVisible.value = true
}

async function submitPunch() {
  const today = todayText()
  const exists = (punchRecords.value || []).some(item => item.date === today)
  if (exists) {
    ElMessage.info('今天已打卡')
    return
  }
  const record = {
    date: today,
    time: new Date().toLocaleTimeString(),
    userName: userStore.name || userStore.nickName || '当前用户'
  }
  punchRecords.value = [record, ...(punchRecords.value || [])]
  savePunchRecords()
  try {
    await createForumPost({
      title: '[PUNCH] 每日打卡',
      content: `${record.userName} 于 ${record.date} ${record.time} 完成打卡`,
      targetRole: 'ALL'
    })
  } catch (error) {
    // 打卡主流程不受论坛消息失败影响
  }
  ElMessage.success('打卡成功')
}

async function submitContact() {
  const name = String(contactForm.name || '').trim()
  const phone = String(contactForm.phone || '').trim()
  const message = String(contactForm.message || '').trim()
  if (!name || !message) {
    ElMessage.warning('请填写联系人和咨询内容')
    return
  }
  contactSubmitting.value = true
  try {
    await createForumPost({
      title: '[CONTACT] 联系我们',
      content: `联系人：${name}\n电话：${phone || '-'}\n内容：${message}`,
      targetRole: 'ALL'
    })
    contactForm.name = ''
    contactForm.phone = ''
    contactForm.message = ''
    contactDialogVisible.value = false
    ElMessage.success('咨询已提交，我们会尽快联系你')
  } catch (error) {
    ElMessage.error('提交失败，请稍后再试')
  } finally {
    contactSubmitting.value = false
  }
}

async function submitFeedback() {
  const score = Number(feedbackForm.score || 0)
  const content = String(feedbackForm.content || '').trim()
  if (!content) {
    ElMessage.warning('请填写反馈内容')
    return
  }
  feedbackSubmitting.value = true
  try {
    await createForumPost({
      title: '[SURVEY] 满意度调查',
      content: `满意度：${score}/5\n反馈：${content}`,
      targetRole: 'ALL'
    })
    feedbackForm.score = 5
    feedbackForm.content = ''
    feedbackDialogVisible.value = false
    ElMessage.success('感谢反馈，已提交')
  } catch (error) {
    ElMessage.error('提交失败，请稍后重试')
  } finally {
    feedbackSubmitting.value = false
  }
}

async function refreshNotes() {
  try {
    const res = await listForumPosts()
    notePosts.value = res.data || []
  } catch (error) {
    notePosts.value = []
    ElMessage.error('加载笔记失败')
  }
}

async function openNoteCenter(mode = 'all') {
  noteViewMode.value = mode === 'mine' ? 'mine' : 'all'
  noteDialogVisible.value = true
  await refreshNotes()
}

async function submitNote() {
  const title = String(noteForm.title || '').trim()
  const content = String(noteForm.content || '').trim()
  if (!title || !content) {
    ElMessage.warning('请填写完整的标题和内容')
    return
  }
  noteSubmitting.value = true
  try {
    await createForumPost({
      title: `${NOTE_TITLE_PREFIX} ${title}`,
      content,
      targetRole: 'ALL'
    })
    noteForm.title = ''
    noteForm.content = ''
    ElMessage.success('笔记发布成功')
    await refreshNotes()
  } catch (error) {
    ElMessage.error('笔记发布失败')
  } finally {
    noteSubmitting.value = false
  }
}

async function replyNote(postId) {
  const content = String(noteReplyMap[postId] || '').trim()
  if (!content) return
  try {
    await replyForumPost(postId, { content })
    noteReplyMap[postId] = ''
    ElMessage.success('回复成功')
    await refreshNotes()
  } catch (error) {
    ElMessage.error('回复失败')
  }
}

const functionActionMap = {
  orgManage: () => router.push('/system/dept'),
  userManage: () => router.push('/system/user'),
  classManage: () => router.push('/system/dept'),
  pad: () => router.push('/education/auth?redirect=/education/pad'),
  login: () => router.push('/education/auth?redirect=/education/pad&tab=login'),
  register: () => router.push('/education/auth?redirect=/education/pad&tab=register'),
  searchNote: () => openNoteCenter('all'),
  myNote: () => openNoteCenter('mine'),
  questionRecord: () => router.push('/education/auth?redirect=' + encodeURIComponent('/education/pad?studentTab=homework')),
  myScore: () => router.push('/education/auth?redirect=' + encodeURIComponent('/education/pad?studentTab=exam')),
  punch: () => openPunchDialog(),
  contactUs: () => { contactDialogVisible.value = true },
  feedback: () => { feedbackDialogVisible.value = true },
  logout: async () => {
    try {
      await ElMessageBox.confirm('确认退出当前账号吗？', '提示', { type: 'warning' })
    } catch (error) {
      return
    }
    await userStore.logOut()
    router.push('/login')
  }
}

async function goToFunction(key) {
  const action = functionActionMap[key]
  if (!action) {
    ElMessage(`功能开发中：${otherFunctions.find(f => f.key === key)?.name || key}`)
    return
  }
  try {
    await action()
  } catch (error) {
    const msg = String(error || '')
    if (msg.includes('cancel') || msg.includes('close')) return
    ElMessage.error('操作失败，请稍后重试')
  }
}
</script>

<style scoped lang="scss">
.home {
  padding: 24px;
  font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  color: #334155;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid rgba(15, 23, 42, 0.06);
  
  h1 {
    font-size: 36px;
    margin-bottom: 10px;
    color: #0b3b51;
  }
  
  h2 {
    font-size: 24px;
    margin-bottom: 15px;
    color: #163f57;
  }
  
  .feature-card {
    height: 100%;
    transition: all 0.3s ease;
    
    &:hover {
      box-shadow: 0 10px 24px rgba(15, 23, 42, 0.1);
      transform: translateY(-4px);
    }
    
    .card-header {
      display: flex;
      align-items: center;
      font-size: 18px;
      font-weight: 500;
      color: #0f172a;
      
      i {
        margin-right: 8px;
        color: #0284c7;
      }
    }
    
    .card-body {
      padding: 15px 0;
      
      ul {
        list-style: none;
        padding: 0;
        margin: 0;
        
        li {
          padding: 8px 0;
          padding-left: 20px;
          position: relative;
          
          &::before {
            content: "•";
            color: #0f766e;
            position: absolute;
            left: 0;
            font-size: 18px;
          }
        }
      }
    }
  }

  .arch-card {
    height: 100%;
  }

  .arch-flow {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .arch-row {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
  }

  .arch-node {
    background: #f8fafc;
    border: 1px solid #dbeafe;
    border-radius: 8px;
    padding: 10px 12px;
    text-align: center;
    font-weight: 600;
    color: #1e293b;
  }

  .arch-node.strong {
    background: #e0f2fe;
    border-color: #7dd3fc;
  }

  .arch-arrow {
    text-align: center;
    color: #0f766e;
    font-size: 18px;
    line-height: 1;
  }

  .arch-group {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 10px 12px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;

    h4 {
      margin: 0 0 6px 0;
      width: 100%;
      color: #0f172a;
      font-size: 14px;
    }
  }

  .arch-group.service {
    p {
      margin: 0;
      font-size: 13px;
      color: #475569;
      line-height: 1.5;
    }
  }

  .perm-flow {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .perm-level {
    background: #f8fafc;
    border-left: 4px solid #0ea5e9;
    border-radius: 8px;
    padding: 10px 12px;

    h4 {
      margin: 0 0 6px 0;
      color: #0f172a;
      font-size: 14px;
    }

    p {
      margin: 0;
      color: #475569;
      font-size: 13px;
      line-height: 1.5;
    }
  }

  .tech-stack {
    .card-body {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
    }
  }
  
  .other-functions {
    .function-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
      gap: 10px;
    }
  }

  .note-publish-card,
  .note-list-card {
    min-height: 560px;
  }

  .note-item {
    border: 1px solid #dceaf6;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 10px;
    background: #f9fcff;
  }

  .note-title {
    font-size: 15px;
    font-weight: 700;
    color: #0f172a;
  }

  .note-meta {
    margin-top: 4px;
    margin-bottom: 8px;
    font-size: 12px;
    color: #64748b;
  }

  .note-content {
    color: #334155;
    white-space: pre-wrap;
    line-height: 1.6;
    margin-bottom: 8px;
  }

  .note-actions {
    margin-top: 4px;
  }

  .note-reply-list {
    margin-top: 6px;
    border-top: 1px dashed #dbe7f4;
    padding-top: 6px;
  }

  .note-reply-item {
    font-size: 13px;
    color: #3b4f63;
    margin-bottom: 4px;
  }

  @media (max-width: 768px) {
    .arch-row {
      grid-template-columns: 1fr;
    }
  }
}
</style>
