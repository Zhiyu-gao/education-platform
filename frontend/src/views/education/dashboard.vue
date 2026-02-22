<template>
  <div class="pad-fullscreen">
    <header class="top-layer">
      <div class="top-title">
        <h1>教育 Pad 端</h1>
        <p>{{ roleLabel }} · {{ userStore.nickName || userStore.name }}</p>
      </div>
      <div class="stat-grid">
        <div class="stat-card">
          <div class="stat-label">当前时间</div>
          <div class="stat-value">{{ currentTime }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">未完成任务</div>
          <div class="stat-value">{{ pendingTaskCount }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">未读消息</div>
          <div class="stat-value">{{ forumUnreadTotal }}</div>
        </div>
      </div>

      <div class="widget-grid">
        <div
          v-for="widget in quickWidgets"
          :key="widget.id"
          class="widget-item"
          @click="activeChannel = widget.channel"
        >
          <div class="widget-icon">{{ widget.icon }}</div>
          <div class="widget-text">
            <strong>{{ widget.title }}</strong>
            <span>{{ widget.subTitle }}</span>
          </div>
        </div>
      </div>
    </header>

    <main class="pad-content">
      <section v-show="activeChannel === 'publish'" class="channel-section">
        <el-row :gutter="16">
          <el-col :xl="10" :lg="10" :md="24" :sm="24" :xs="24">
            <el-card v-if="isTeacher || isManager" class="block-card" shadow="hover">
              <template #header>发布作业</template>
              <el-form :model="homeworkForm" label-width="72px">
                <el-form-item label="标题"><el-input v-model="homeworkForm.title" /></el-form-item>
                <el-form-item label="班级">
                  <el-select v-model="homeworkForm.className" placeholder="请选择班级" filterable>
                    <el-option v-for="item in classOptions" :key="item" :label="item" :value="item" />
                  </el-select>
                </el-form-item>
                <el-form-item label="内容"><el-input v-model="homeworkForm.content" type="textarea" :rows="4" /></el-form-item>
                <el-form-item><el-button type="primary" @click="handleCreateHomework">发布作业</el-button></el-form-item>
              </el-form>
            </el-card>

            <el-card v-if="isTeacher || isManager" class="block-card" shadow="hover">
              <template #header>发布考试</template>
              <el-form :model="examForm" label-width="72px">
                <el-form-item label="考试名"><el-input v-model="examForm.title" /></el-form-item>
                <el-form-item label="班级">
                  <el-select v-model="examForm.className" placeholder="请选择班级" filterable>
                    <el-option v-for="item in classOptions" :key="item" :label="item" :value="item" />
                  </el-select>
                </el-form-item>
                <el-form-item label="总分"><el-input-number v-model="examForm.totalScore" :min="1" :max="200" /></el-form-item>
                <el-form-item><el-button type="success" @click="handleCreateExam">发布考试</el-button></el-form-item>
              </el-form>
            </el-card>

            <el-card v-if="isTeacher || isManager" class="block-card" shadow="hover">
              <template #header>考试评分</template>
              <el-form :model="examScoreForm" label-width="78px">
                <el-form-item label="考试ID"><el-input v-model="examScoreForm.examId" /></el-form-item>
                <el-form-item label="学生ID"><el-input v-model="examScoreForm.studentId" /></el-form-item>
                <el-form-item label="学生名"><el-input v-model="examScoreForm.studentName" /></el-form-item>
                <el-form-item label="分数"><el-input-number v-model="examScoreForm.score" :min="0" :max="200" /></el-form-item>
                <el-form-item><el-button type="warning" @click="handleScoreExam">提交评分</el-button></el-form-item>
              </el-form>
            </el-card>

            <el-card v-if="isManager" class="block-card" shadow="hover">
              <template #header>管理者下发老师任务</template>
              <el-form :model="teacherTaskForm" label-width="78px">
                <el-form-item label="老师ID"><el-input v-model="teacherTaskForm.teacherId" /></el-form-item>
                <el-form-item label="标题"><el-input v-model="teacherTaskForm.title" /></el-form-item>
                <el-form-item label="内容"><el-input v-model="teacherTaskForm.content" type="textarea" :rows="3" /></el-form-item>
                <el-form-item><el-button type="danger" @click="handleCreateTeacherTask">发布任务</el-button></el-form-item>
              </el-form>
            </el-card>
          </el-col>

          <el-col :xl="14" :lg="14" :md="24" :sm="24" :xs="24">
            <el-card class="block-card" shadow="hover">
              <template #header>
                <div class="header-line">
                  <span>任务与数据列表</span>
                  <el-button link type="primary" @click="loadPublishData">刷新</el-button>
                </div>
              </template>

              <div v-if="isTeacher || isManager" class="table-zone">
                <h4>我发布的作业</h4>
                <el-table :data="teacherHomework" size="small" max-height="200">
                  <el-table-column prop="homeworkId" label="ID" width="68" />
                  <el-table-column prop="title" label="标题" />
                  <el-table-column prop="className" label="班级" width="130" />
                  <el-table-column prop="status" label="状态" width="100" />
                </el-table>
              </div>

              <div v-if="isTeacher || isManager" class="table-zone">
                <h4>我发布的考试</h4>
                <el-table :data="teacherExam" size="small" max-height="200">
                  <el-table-column prop="examId" label="ID" width="68" />
                  <el-table-column prop="title" label="考试" />
                  <el-table-column prop="className" label="班级" width="130" />
                  <el-table-column prop="totalScore" label="总分" width="90" />
                </el-table>
              </div>

              <div v-if="isStudent" class="table-zone">
                <h4>我的作业</h4>
                <el-table :data="studentHomework" size="small" max-height="200">
                  <el-table-column prop="homeworkId" label="ID" width="68" />
                  <el-table-column prop="title" label="标题" />
                  <el-table-column prop="className" label="班级" width="130" />
                  <el-table-column label="操作" width="96">
                    <template #default="scope">
                      <el-button link type="primary" @click="openSubmit(scope.row)">提交</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>

              <div v-if="isStudent" class="table-zone">
                <h4>我的考试</h4>
                <el-table :data="studentExam" size="small" max-height="200">
                  <el-table-column prop="examId" label="ID" width="68" />
                  <el-table-column prop="title" label="考试" />
                  <el-table-column prop="className" label="班级" width="130" />
                  <el-table-column prop="totalScore" label="总分" width="90" />
                </el-table>
              </div>

              <div v-if="isStudent" class="table-zone">
                <h4>我的作业提交记录</h4>
                <el-table :data="studentSubmissions" size="small" max-height="200">
                  <el-table-column prop="homework_title" label="作业" />
                  <el-table-column prop="score" label="分数" width="86" />
                  <el-table-column prop="feedback" label="反馈" show-overflow-tooltip />
                </el-table>
              </div>

              <div v-if="isTeacher" class="table-zone">
                <h4>学生作业提交（待批改）</h4>
                <el-table :data="teacherSubmissions" size="small" max-height="220">
                  <el-table-column prop="homework_title" label="作业" />
                  <el-table-column prop="student_name" label="学生" width="120" />
                  <el-table-column prop="answer_content" label="作答" show-overflow-tooltip />
                  <el-table-column prop="score" label="分数" width="80" />
                </el-table>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </section>

      <section v-show="activeChannel === 'visual'" class="channel-section">
        <el-card class="block-card" shadow="hover">
          <template #header>
            <div class="header-line">
              <span>学习与成绩可视化</span>
              <el-button link type="primary" @click="loadVisualData">刷新</el-button>
            </div>
          </template>

          <div class="kpi-grid">
            <div class="kpi-item">
              <div class="kpi-label">作业完成率</div>
              <div class="kpi-value">{{ visualStats.homeworkCompletion }}%</div>
              <el-progress :percentage="visualStats.homeworkCompletion" :stroke-width="10" />
            </div>
            <div class="kpi-item">
              <div class="kpi-label">考试均分</div>
              <div class="kpi-value">{{ visualStats.avgExamScore }}</div>
              <el-progress :percentage="Math.min(100, visualStats.avgExamScore)" status="success" :stroke-width="10" />
            </div>
            <div class="kpi-item">
              <div class="kpi-label">已评分作业数</div>
              <div class="kpi-value">{{ visualStats.scoredHomeworkCount }}</div>
              <el-progress :percentage="visualStats.scoredHomeworkRate" status="warning" :stroke-width="10" />
            </div>
            <div class="kpi-item">
              <div class="kpi-label">考试记录数</div>
              <div class="kpi-value">{{ visualStats.examRecordCount }}</div>
              <el-progress :percentage="visualStats.examRecordRate" :stroke-width="10" />
            </div>
          </div>

          <div class="table-zone">
            <h4>明细数据</h4>
            <el-table :data="visualRows" size="small" max-height="360">
              <el-table-column prop="name" label="名称" min-width="180" />
              <el-table-column prop="value" label="值" width="120" />
              <el-table-column prop="remark" label="说明" />
            </el-table>
          </div>
        </el-card>
      </section>

      <section v-show="activeChannel === 'ai'" class="channel-section">
        <el-row :gutter="16">
          <el-col :xl="12" :lg="12" :md="24" :sm="24" :xs="24">
            <el-card class="block-card" shadow="hover">
              <template #header>AI 智能助手（RAG）</template>
              <el-upload :auto-upload="false" :show-file-list="false" :on-change="handleRagFileChange" accept=".xlsx,.xls,.csv">
                <el-button type="primary" plain>选择知识库文件</el-button>
              </el-upload>
              <div class="upload-tip">当前文件：{{ ragUploadFileName || '未选择' }}</div>
              <el-button type="success" :loading="ragUploading" @click="handleUploadRagFile">上传知识库</el-button>

              <el-divider />
              <el-input v-model="ragQuestion" type="textarea" :rows="4" placeholder="请输入问题，例如：如何提高学生出勤率？" />
              <div class="action-line">
                <el-button type="primary" :loading="ragAsking" @click="handleAskRag">发送提问</el-button>
                <el-button link type="primary" @click="loadRagDatasets">刷新数据集</el-button>
              </div>
              <el-alert v-if="ragAnswer" title="AI回复" type="success" :closable="false" class="rag-answer">
                <template #default>{{ ragAnswer }}</template>
              </el-alert>

              <el-divider />
              <h4>数据集记录</h4>
              <el-table :data="ragDatasets" size="small" max-height="220">
                <el-table-column prop="dataset_id" label="ID" min-width="160" show-overflow-tooltip />
                <el-table-column prop="filename" label="文件名" />
                <el-table-column prop="created_at" label="时间" min-width="140" show-overflow-tooltip />
              </el-table>
            </el-card>
          </el-col>

          <el-col :xl="12" :lg="12" :md="24" :sm="24" :xs="24">
            <el-card class="block-card" shadow="hover">
              <template #header>AI 成绩预测</template>
              <el-upload :auto-upload="false" :show-file-list="false" :on-change="handleTrainFileChange" accept=".csv">
                <el-button type="primary" plain>选择训练CSV</el-button>
              </el-upload>
              <div class="upload-tip">当前文件：{{ trainFileName || '未选择' }}</div>
              <div class="action-line">
                <el-button type="success" :loading="trainingModel" @click="handleTrainModel">训练模型</el-button>
                <el-button link type="primary" @click="fetchModelInfo">获取模型信息</el-button>
              </div>
              <el-alert v-if="modelInfoText" :title="modelInfoText" type="info" :closable="false" />

              <el-divider />
              <el-form :model="predictForm.input_data" label-width="130px" class="predict-form">
                <el-form-item label="学习时长"><el-input-number v-model="predictForm.input_data.Hours_Studied" :min="0" :max="100" /></el-form-item>
                <el-form-item label="出勤率"><el-input-number v-model="predictForm.input_data.Attendance" :min="0" :max="100" /></el-form-item>
                <el-form-item label="历史分数"><el-input-number v-model="predictForm.input_data.Previous_Scores" :min="0" :max="100" /></el-form-item>
                <el-form-item label="睡眠时长"><el-input-number v-model="predictForm.input_data.Sleep_Hours" :min="0" :max="12" /></el-form-item>
                <el-form-item label="家教次数"><el-input-number v-model="predictForm.input_data.Tutoring_Sessions" :min="0" :max="30" /></el-form-item>
              </el-form>
              <div class="action-line">
                <el-button type="primary" :loading="predicting" @click="handlePredictScore">预测成绩</el-button>
              </div>
              <el-alert v-if="predictResultText" :title="predictResultText" :type="predictResultType" :closable="false" />
            </el-card>
          </el-col>
        </el-row>
      </section>

      <section v-show="activeChannel === 'forum'" class="channel-section">
        <el-row :gutter="16">
          <el-col :xl="10" :lg="10" :md="24" :sm="24" :xs="24">
            <el-card class="block-card" shadow="hover">
              <template #header>发布论坛消息</template>
              <el-form :model="forumForm" label-width="72px">
                <el-form-item label="标题"><el-input v-model="forumForm.title" /></el-form-item>
                <el-form-item label="内容"><el-input v-model="forumForm.content" type="textarea" :rows="6" /></el-form-item>
                <el-form-item><el-button type="primary" @click="publishForumPost">发布消息</el-button></el-form-item>
              </el-form>
            </el-card>
          </el-col>
          <el-col :xl="14" :lg="14" :md="24" :sm="24" :xs="24">
            <el-card class="block-card" shadow="hover">
              <template #header>
                <div class="header-line">
                  <span>论坛消息列表</span>
                  <el-button link type="primary" @click="loadForumPosts">刷新</el-button>
                </div>
              </template>
              <el-empty v-if="forumPosts.length === 0" description="暂无消息" />
              <div v-for="post in forumPosts" :key="post.post_id" class="forum-post">
                <div class="forum-top">
                  <strong>{{ post.title }}</strong>
                  <span>{{ post.author_name }}（{{ post.author_role }}） · {{ post.create_time }}</span>
                </div>
                <p>{{ post.content }}</p>
                <el-input
                  v-model="forumReplyMap[post.post_id]"
                  placeholder="回复这条消息"
                  size="small"
                  @keyup.enter="replyForumPost(post.post_id)"
                />
                <div class="reply-actions">
                  <el-button size="small" link type="primary" @click="replyForumPost(post.post_id)">回复</el-button>
                </div>
                <div v-if="post.replies && post.replies.length" class="reply-list">
                  <div v-for="reply in post.replies" :key="reply.reply_id" class="reply-item">
                    {{ reply.author_name }}：{{ reply.content }}
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </section>

      <section v-show="activeChannel === 'profile'" class="channel-section">
        <el-row :gutter="16">
          <el-col :xl="10" :lg="10" :md="24" :sm="24" :xs="24">
            <el-card class="block-card" shadow="hover">
              <template #header>个人资料</template>
              <el-form :model="profileForm" label-width="86px">
                <el-form-item label="账号"><el-input v-model="profileForm.userName" disabled /></el-form-item>
                <el-form-item label="昵称"><el-input v-model="profileForm.nickName" /></el-form-item>
                <el-form-item label="手机"><el-input v-model="profileForm.phonenumber" /></el-form-item>
                <el-form-item label="邮箱"><el-input v-model="profileForm.email" /></el-form-item>
                <el-form-item><el-button type="primary" @click="handleUpdateProfile">保存资料</el-button></el-form-item>
              </el-form>
            </el-card>
          </el-col>
          <el-col :xl="10" :lg="10" :md="24" :sm="24" :xs="24">
            <el-card class="block-card" shadow="hover">
              <template #header>修改密码</template>
              <el-form :model="pwdForm" label-width="86px">
                <el-form-item label="旧密码"><el-input v-model="pwdForm.oldPassword" type="password" show-password /></el-form-item>
                <el-form-item label="新密码"><el-input v-model="pwdForm.newPassword" type="password" show-password /></el-form-item>
                <el-form-item><el-button type="warning" @click="handleUpdatePassword">更新密码</el-button></el-form-item>
              </el-form>
            </el-card>
          </el-col>
          <el-col :xl="4" :lg="4" :md="24" :sm="24" :xs="24">
            <el-card class="block-card" shadow="hover">
              <template #header>会话</template>
              <el-button type="danger" plain style="width: 100%" @click="handleLogout">退出登录</el-button>
            </el-card>
          </el-col>
        </el-row>
      </section>
    </main>

    <nav class="bottom-nav">
      <button :class="['nav-btn', { active: activeChannel === 'publish' }]" @click="activeChannel = 'publish'">
        发布作业/考试
      </button>
      <button :class="['nav-btn', { active: activeChannel === 'visual' }]" @click="activeChannel = 'visual'">
        成绩可视化
      </button>
      <button :class="['nav-btn', { active: activeChannel === 'ai' }]" @click="activeChannel = 'ai'">
        AI助手/预测
      </button>
      <button :class="['nav-btn', { active: activeChannel === 'forum' }]" @click="activeChannel = 'forum'">
        论坛消息<span v-if="forumUnreadTotal > 0">（{{ forumUnreadTotal }}）</span>
      </button>
      <button :class="['nav-btn', { active: activeChannel === 'profile' }]" @click="activeChannel = 'profile'">
        个人信息
      </button>
    </nav>

    <el-dialog v-model="submitDialog" title="提交作业" width="520px">
      <el-form :model="submitForm" label-width="78px">
        <el-form-item label="作业ID"><el-input v-model="submitForm.homeworkId" disabled /></el-form-item>
        <el-form-item label="作答内容"><el-input v-model="submitForm.answerContent" type="textarea" :rows="6" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="submitDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitHomework">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import useUserStore from '@/store/modules/user'
import {
  createHomework,
  listTeacherHomework,
  listStudentHomework,
  submitHomework,
  listTeacherHomeworkSubmissions,
  listStudentHomeworkSubmissions,
  createExam,
  listTeacherExam,
  listStudentExam,
  scoreExam,
  listStudentExamScore,
  listManagerScores,
  listStudentSelfScores,
  createTeacherTask,
  listTeacherTasks,
  listTeacherScores
} from '@/api/education/pad'
import { uploadExcel, queryQuestion, getDatasets } from '@/api/education/rag'
import { trainPredictionModel, getModelInfo, predictScore } from '@/api/education/prediction'
import { getUserProfile, updateUserProfile, updateUserPwd } from '@/api/system/user'
import { listForumPosts, createForumPost, replyForumPost as replyForumPostApi, getForumNotice, markForumRead } from '@/api/education/forum'

const router = useRouter()
const userStore = useUserStore()

const activeChannel = ref('publish')

const roles = computed(() => (userStore.roles || []).map(r => String(r).toLowerCase()))
const isManager = computed(() => roles.value.includes('admin') || roles.value.includes('manager'))
const isTeacher = computed(() => roles.value.includes('teacher'))
const isStudent = computed(() => roles.value.includes('student') || roles.value.includes('role_default'))

const roleLabel = computed(() => {
  if (isManager.value) return '管理者'
  if (isTeacher.value) return '老师'
  return '学生'
})

const homeworkForm = reactive({ title: '', className: '', content: '' })
const examForm = reactive({ title: '', className: '', totalScore: 100 })
const classOptions = Array.from({ length: 5 }, (_, g) => g + 1)
  .flatMap((grade) => Array.from({ length: 10 }, (_, c) => `G${grade}-C${c + 1}`))
const examScoreForm = reactive({ examId: '', studentId: '', studentName: '', score: 0, remark: '' })
const teacherTaskForm = reactive({ teacherId: '', title: '', content: '' })

const teacherHomework = ref([])
const teacherExam = ref([])
const teacherSubmissions = ref([])
const teacherTasks = ref([])
const teacherScores = ref([])
const studentHomework = ref([])
const studentExam = ref([])
const studentSubmissions = ref([])
const studentExamScores = ref([])
const studentSelfScores = ref({ examScores: [], performanceScores: [] })
const managerScores = ref({ examScores: [], performanceScores: [] })

const submitDialog = ref(false)
const submitForm = reactive({ homeworkId: '', answerContent: '' })

const visualStats = reactive({
  homeworkCompletion: 0,
  avgExamScore: 0,
  scoredHomeworkCount: 0,
  scoredHomeworkRate: 0,
  examRecordCount: 0,
  examRecordRate: 0
})
const visualRows = ref([])

const ragUploadFile = ref(null)
const ragUploadFileName = ref('')
const ragUploading = ref(false)
const ragAsking = ref(false)
const ragQuestion = ref('')
const ragAnswer = ref('')
const ragDatasets = ref([])

const trainFile = ref(null)
const trainFileName = ref('')
const trainingModel = ref(false)
const predicting = ref(false)
const modelInfoText = ref('')
const predictResultText = ref('')
const predictResultType = ref('info')
const predictForm = reactive({
  input_data: {
    Hours_Studied: 30,
    Attendance: 90,
    Parental_Involvement: 'Medium',
    Access_to_Resources: 'Medium',
    Extracurricular_Activities: 'Yes',
    Sleep_Hours: 8,
    Previous_Scores: 75,
    Motivation_Level: 'Medium',
    Internet_Access: 'Yes',
    Tutoring_Sessions: 2,
    Family_Income: 'Medium',
    Teacher_Quality: 'High',
    School_Type: 'Public',
    Peer_Influence: 'Neutral',
    Physical_Activity: 5,
    Learning_Disabilities: 'No',
    Parental_Education_Level: "Bachelor's",
    Distance_from_Home: 'Medium',
    Gender: 'Female'
  }
})

const forumForm = reactive({ title: '', content: '' })
const forumPosts = ref([])
const forumReplyMap = reactive({})
const forumUnreadTotal = ref(0)
const currentTime = ref('')
let timeTimer = null

const profileForm = reactive({ userName: '', nickName: '', phonenumber: '', email: '' })
const pwdForm = reactive({ oldPassword: '', newPassword: '' })

const pendingTaskCount = computed(() => {
  if (isTeacher.value) {
    const todoTaskCount = (teacherTasks.value || []).filter(item => String(item.status || '').toUpperCase() !== 'DONE').length
    const unScoredCount = (teacherSubmissions.value || []).filter(item => item.score === null || item.score === undefined).length
    return todoTaskCount + unScoredCount
  }
  if (isStudent.value) {
    const allHomeworkIds = new Set((studentHomework.value || []).map(item => item.homeworkId))
    const submittedIds = new Set((studentSubmissions.value || []).map(item => item.homework_id))
    let notDone = 0
    allHomeworkIds.forEach(id => {
      if (!submittedIds.has(id)) notDone += 1
    })
    return notDone
  }
  return (teacherHomework.value || []).filter(item => String(item.status || '').toUpperCase() !== 'FINISHED').length
})

const quickWidgets = computed(() => {
  const cards = []
  if (isStudent.value && studentHomework.value.length > 0) {
    studentHomework.value.slice(0, 4).forEach((item, idx) => {
      cards.push({
        id: `s-hw-${idx}-${item.homeworkId}`,
        icon: '📘',
        title: `${item.title || '未命名'}（作业）`,
        subTitle: item.className || '学生任务',
        channel: 'publish'
      })
    })
  } else if (isTeacher.value && teacherTasks.value.length > 0) {
    teacherTasks.value.slice(0, 4).forEach((item, idx) => {
      cards.push({
        id: `t-task-${idx}-${item.taskId}`,
        icon: '🧾',
        title: `${item.title || '任务'}（教师任务）`,
        subTitle: item.status || '待处理',
        channel: 'publish'
      })
    })
  } else {
    cards.push(
      { id: 'default-1', icon: '📘', title: '英语（作业）', subTitle: '今日待完成', channel: 'publish' },
      { id: 'default-2', icon: '🧪', title: '数学（考试）', subTitle: '本周安排', channel: 'publish' },
      { id: 'default-3', icon: '📊', title: '成绩统计', subTitle: '学习可视化', channel: 'visual' },
      { id: 'default-4', icon: '🤖', title: 'AI学习助手', subTitle: '问答与预测', channel: 'ai' }
    )
  }
  return cards.slice(0, 8)
})

watch(activeChannel, async (val) => {
  if (val === 'publish') await loadPublishData()
  if (val === 'visual') await loadVisualData()
  if (val === 'ai') {
    await loadRagDatasets()
    await fetchModelInfo()
  }
  if (val === 'forum') {
    await loadForumPosts()
    await markForumReadState()
  }
  if (val === 'profile') await loadProfile()
})

function toNum(value) {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

function refreshTime() {
  currentTime.value = new Date().toLocaleString()
}

async function handleCreateHomework() {
  if (!homeworkForm.title) {
    ElMessage.warning('请填写作业标题')
    return
  }
  await createHomework(homeworkForm)
  ElMessage.success('作业发布成功')
  Object.assign(homeworkForm, { title: '', className: '', content: '' })
  await loadPublishData()
}

async function handleCreateExam() {
  if (!examForm.title) {
    ElMessage.warning('请填写考试名称')
    return
  }
  await createExam(examForm)
  ElMessage.success('考试发布成功')
  Object.assign(examForm, { title: '', className: '', totalScore: 100 })
  await loadPublishData()
}

async function handleScoreExam() {
  if (!examScoreForm.examId || !examScoreForm.studentId) {
    ElMessage.warning('请填写考试ID和学生ID')
    return
  }
  await scoreExam(examScoreForm)
  ElMessage.success('评分提交成功')
  Object.assign(examScoreForm, { examId: '', studentId: '', studentName: '', score: 0, remark: '' })
  await loadPublishData()
}

async function handleCreateTeacherTask() {
  if (!teacherTaskForm.teacherId || !teacherTaskForm.title) {
    ElMessage.warning('请填写老师ID和任务标题')
    return
  }
  await createTeacherTask(teacherTaskForm)
  ElMessage.success('老师任务发布成功')
  Object.assign(teacherTaskForm, { teacherId: '', title: '', content: '' })
}

function openSubmit(row) {
  submitForm.homeworkId = row.homeworkId
  submitForm.answerContent = ''
  submitDialog.value = true
}

async function handleSubmitHomework() {
  if (!submitForm.answerContent) {
    ElMessage.warning('请填写作答内容')
    return
  }
  await submitHomework(submitForm.homeworkId, { answerContent: submitForm.answerContent })
  ElMessage.success('提交成功')
  submitDialog.value = false
  await loadPublishData()
}

async function loadPublishData() {
  try {
    if (isTeacher.value || isManager.value) {
      const [homeworkRes, examRes] = await Promise.all([listTeacherHomework(), listTeacherExam()])
      teacherHomework.value = homeworkRes.data || []
      teacherExam.value = examRes.data || []
    }

    if (isTeacher.value) {
      const [subRes, taskRes, scoreRes] = await Promise.all([
        listTeacherHomeworkSubmissions(),
        listTeacherTasks(),
        listTeacherScores()
      ])
      teacherSubmissions.value = subRes.data || []
      teacherTasks.value = taskRes.data || []
      teacherScores.value = scoreRes.data || []
    }

    if (isStudent.value) {
      const [homeworkRes, subRes, examRes, examScoreRes, selfScoreRes] = await Promise.all([
        listStudentHomework(),
        listStudentHomeworkSubmissions(),
        listStudentExam(),
        listStudentExamScore(),
        listStudentSelfScores()
      ])
      studentHomework.value = homeworkRes.data || []
      studentSubmissions.value = subRes.data || []
      studentExam.value = examRes.data || []
      studentExamScores.value = examScoreRes.data || []
      studentSelfScores.value = selfScoreRes || { examScores: [], performanceScores: [] }
    }

    if (isManager.value) {
      managerScores.value = await listManagerScores()
    }
  } catch (error) {
    ElMessage.error('加载发布频道数据失败')
  }
}

async function loadVisualData() {
  try {
    let submissionList = []
    let examScores = []

    if (isTeacher.value) {
      const [subRes, scoreRes] = await Promise.all([listTeacherHomeworkSubmissions(), listTeacherScores()])
      submissionList = subRes.data || []
      examScores = scoreRes.data || []
    } else if (isStudent.value) {
      const [subRes, examScoreRes, selfRes] = await Promise.all([
        listStudentHomeworkSubmissions(),
        listStudentExamScore(),
        listStudentSelfScores()
      ])
      submissionList = subRes.data || []
      examScores = [...(examScoreRes.data || []), ...((selfRes.performanceScores || []))]
    } else if (isManager.value) {
      const all = await listManagerScores()
      submissionList = []
      examScores = [...(all.examScores || []), ...(all.performanceScores || [])]
    }

    const totalHomework = isStudent.value ? studentHomework.value.length : Math.max(teacherHomework.value.length, submissionList.length)
    const completionCount = submissionList.length
    const avgExam = examScores.length
      ? (examScores.reduce((sum, row) => sum + toNum(row.score || row.exam_score), 0) / examScores.length)
      : 0
    const scoredCount = submissionList.filter(row => row.score !== null && row.score !== undefined).length

    visualStats.homeworkCompletion = totalHomework ? Math.round((completionCount / totalHomework) * 100) : 0
    visualStats.avgExamScore = Number(avgExam.toFixed(1))
    visualStats.scoredHomeworkCount = scoredCount
    visualStats.scoredHomeworkRate = completionCount ? Math.round((scoredCount / completionCount) * 100) : 0
    visualStats.examRecordCount = examScores.length
    visualStats.examRecordRate = Math.min(100, examScores.length * 10)

    visualRows.value = [
      { name: '作业总量', value: totalHomework, remark: '当前视角可统计的作业总数' },
      { name: '已提交作业', value: completionCount, remark: '已完成提交的作业数量' },
      { name: '已评分作业', value: scoredCount, remark: '已给出分数的作业数量' },
      { name: '考试成绩记录', value: examScores.length, remark: '考试或成绩记录条数' },
      { name: '考试均分', value: visualStats.avgExamScore, remark: '按当前角色可见数据统计' }
    ]
  } catch (error) {
    ElMessage.error('加载可视化数据失败')
  }
}

function handleRagFileChange(file) {
  ragUploadFile.value = file
  ragUploadFileName.value = file.name || ''
}

async function handleUploadRagFile() {
  if (!ragUploadFile.value) {
    ElMessage.warning('请先选择知识库文件')
    return
  }
  ragUploading.value = true
  try {
    await uploadExcel(ragUploadFile.value)
    ElMessage.success('知识库上传成功')
    await loadRagDatasets()
  } catch (error) {
    ElMessage.error('知识库上传失败')
  } finally {
    ragUploading.value = false
  }
}

async function handleAskRag() {
  if (!ragQuestion.value) {
    ElMessage.warning('请输入提问内容')
    return
  }
  ragAsking.value = true
  ragAnswer.value = ''
  try {
    const res = await queryQuestion(ragQuestion.value)
    ragAnswer.value = res.answer || res.data || JSON.stringify(res)
  } catch (error) {
    ElMessage.error('提问失败，请检查 AI 服务')
  } finally {
    ragAsking.value = false
  }
}

async function loadRagDatasets() {
  try {
    const res = await getDatasets()
    ragDatasets.value = res.datasets || res.data || []
  } catch (error) {
    ragDatasets.value = []
  }
}

function handleTrainFileChange(file) {
  trainFile.value = file.raw
  trainFileName.value = file.name || ''
}

async function handleTrainModel() {
  if (!trainFile.value) {
    ElMessage.warning('请先选择训练CSV文件')
    return
  }
  trainingModel.value = true
  try {
    const formData = new FormData()
    formData.append('file', trainFile.value)
    const res = await trainPredictionModel(formData)
    const result = res.result || res
    if (result.status === 'success') {
      modelInfoText.value = `训练成功：MAE ${toNum(result.test_mae).toFixed(4)}，特征数 ${result.feature_count}`
      ElMessage.success('模型训练完成')
    } else {
      modelInfoText.value = result.message || '模型训练失败'
      ElMessage.error(modelInfoText.value)
    }
  } catch (error) {
    ElMessage.error('模型训练失败')
  } finally {
    trainingModel.value = false
  }
}

async function fetchModelInfo() {
  try {
    const res = await getModelInfo()
    if (res.status === 'success') {
      const fCount = (res.model_info && res.model_info.feature_count) || '--'
      modelInfoText.value = `模型已就绪，特征数：${fCount}`
    } else {
      modelInfoText.value = res.message || '模型信息不可用'
    }
  } catch (error) {
    modelInfoText.value = '获取模型信息失败'
  }
}

async function handlePredictScore() {
  predicting.value = true
  try {
    const res = await predictScore(predictForm)
    if (res.status === 'success') {
      predictResultType.value = 'success'
      predictResultText.value = `预测成绩：${toNum(res.predicted_score).toFixed(2)} 分`
    } else {
      predictResultType.value = 'error'
      predictResultText.value = res.message || '预测失败'
    }
  } catch (error) {
    predictResultType.value = 'error'
    predictResultText.value = '预测失败，请检查 AI 服务'
  } finally {
    predicting.value = false
  }
}

async function loadForumPosts() {
  try {
    const res = await listForumPosts()
    forumPosts.value = res.data || []
  } catch (error) {
    forumPosts.value = []
    ElMessage.error('加载论坛消息失败')
  }
}

async function loadForumNotice() {
  try {
    const res = await getForumNotice()
    forumUnreadTotal.value = res.unreadTotal || 0
  } catch (error) {
    forumUnreadTotal.value = 0
  }
}

async function markForumReadState() {
  try {
    await markForumRead()
    await loadForumNotice()
  } catch (error) {
    // ignore
  }
}

async function publishForumPost() {
  if (!forumForm.title || !forumForm.content) {
    ElMessage.warning('请填写标题和内容')
    return
  }
  const targetRole = isManager.value ? 'ALL' : (isTeacher.value ? 'STUDENT' : 'ALL')
  await createForumPost({
    title: forumForm.title,
    content: forumForm.content,
    targetRole
  })
  forumForm.title = ''
  forumForm.content = ''
  ElMessage.success('发布成功')
  await loadForumPosts()
  await loadForumNotice()
}

async function replyForumPost(postId) {
  const value = String(forumReplyMap[postId] || '').trim()
  if (!value) return
  await replyForumPostApi(postId, { content: value })
  forumReplyMap[postId] = ''
  ElMessage.success('回复成功')
  await loadForumPosts()
  await loadForumNotice()
}

async function loadProfile() {
  try {
    const res = await getUserProfile()
    const data = res.data || {}
    profileForm.userName = data.userName || ''
    profileForm.nickName = data.nickName || ''
    profileForm.phonenumber = data.phonenumber || ''
    profileForm.email = data.email || ''
  } catch (error) {
    ElMessage.error('加载个人信息失败')
  }
}

async function handleUpdateProfile() {
  await updateUserProfile({
    nickName: profileForm.nickName,
    phonenumber: profileForm.phonenumber,
    email: profileForm.email
  })
  ElMessage.success('个人信息已更新')
  await userStore.getInfo()
}

async function handleUpdatePassword() {
  if (!pwdForm.oldPassword || !pwdForm.newPassword) {
    ElMessage.warning('请填写完整密码')
    return
  }
  await updateUserPwd(pwdForm.oldPassword, pwdForm.newPassword)
  ElMessage.success('密码更新成功')
  Object.assign(pwdForm, { oldPassword: '', newPassword: '' })
}

async function handleLogout() {
  await userStore.logOut()
  router.push('/education/auth')
}

onMounted(async () => {
  refreshTime()
  timeTimer = setInterval(refreshTime, 1000)
  await loadForumPosts()
  await loadForumNotice()
  await loadPublishData()
  await loadVisualData()
  await loadProfile()
})

onBeforeUnmount(() => {
  if (timeTimer) {
    clearInterval(timeTimer)
    timeTimer = null
  }
})
</script>

<style scoped lang="scss">
.pad-fullscreen {
  min-height: 100vh;
  background: linear-gradient(145deg, #ecf7ff 0%, #f7f9fc 50%, #eef8f3 100%);
  color: #13334a;
}

.top-layer {
  position: sticky;
  top: 0;
  z-index: 20;
  backdrop-filter: blur(10px);
  background: rgba(250, 253, 255, 0.95);
  border-bottom: 1px solid #dceaf4;
  padding: 12px 14px;
}

.top-title h1 {
  margin: 0;
  font-size: 22px;
}

.top-title p {
  margin: 4px 0 12px;
  color: #4f6f86;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 10px;
}

.stat-card {
  background: #f2f9ff;
  border: 1px solid #d5e8f7;
  border-radius: 10px;
  padding: 10px 12px;
}

.stat-label {
  font-size: 12px;
  color: #5a768c;
}

.stat-value {
  margin-top: 2px;
  font-weight: 700;
  font-size: 18px;
  color: #17324d;
}

.widget-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.widget-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #ffffff;
  border: 1px solid #d9e8f4;
  border-radius: 10px;
  padding: 10px 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.widget-item:hover {
  transform: translateY(-1px);
  border-color: #8cb6d5;
  box-shadow: 0 6px 14px rgba(70, 117, 152, 0.14);
}

.widget-icon {
  font-size: 24px;
  line-height: 1;
}

.widget-text strong {
  display: block;
  color: #17324d;
  font-size: 14px;
}

.widget-text span {
  display: block;
  margin-top: 2px;
  color: #5f7f97;
  font-size: 12px;
}

.pad-content {
  padding: 16px;
  padding-bottom: 88px;
}

.block-card {
  margin-bottom: 14px;
  border-radius: 12px;
}

.header-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-zone {
  margin-top: 10px;
}

.table-zone h4 {
  margin: 0 0 8px;
  color: #1f4f72;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.kpi-item {
  background: #f7fbff;
  border: 1px solid #d8e8f3;
  border-radius: 10px;
  padding: 12px;
}

.kpi-label {
  color: #58788f;
  font-size: 13px;
}

.kpi-value {
  font-size: 24px;
  font-weight: 700;
  margin: 4px 0 10px;
}

.upload-tip {
  margin: 8px 0;
  color: #5c778b;
  font-size: 13px;
}

.action-line {
  margin: 10px 0;
  display: flex;
  gap: 10px;
  align-items: center;
}

.rag-answer {
  margin-top: 10px;
  white-space: pre-wrap;
}

.forum-post {
  border: 1px solid #dbe7f3;
  border-radius: 10px;
  padding: 10px;
  margin-bottom: 10px;
  background: #f9fcff;
}

.forum-top {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 6px;
}

.forum-top span {
  color: #6b8599;
  font-size: 12px;
}

.reply-actions {
  margin: 4px 0;
}

.reply-list {
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px dashed #d7e5f1;
}

.reply-item {
  color: #3b5f79;
  font-size: 13px;
  margin-bottom: 4px;
}

.predict-form :deep(.el-form-item) {
  margin-bottom: 10px;
}

.bottom-nav {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 30;
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
  padding: 10px 10px max(10px, env(safe-area-inset-bottom));
  border-top: 1px solid #d7e7f3;
  background: rgba(245, 251, 255, 0.98);
  backdrop-filter: blur(8px);
}

.nav-btn {
  border: 1px solid #bfd8ea;
  border-radius: 10px;
  background: #fff;
  color: #355b77;
  font-size: 13px;
  padding: 8px 6px;
  line-height: 1.2;
  cursor: pointer;
}

.nav-btn.active {
  background: #2f89c8;
  color: #fff;
  border-color: #2f89c8;
}

@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .widget-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .top-layer {
    padding: 8px 10px;
  }

  .top-title h1 {
    font-size: 20px;
  }

  .stat-grid {
    grid-template-columns: 1fr;
  }

  .pad-content {
    padding: 10px;
    padding-bottom: 100px;
  }

  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .widget-grid {
    grid-template-columns: 1fr;
  }

  .bottom-nav {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
