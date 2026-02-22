<template>
  <div class="pad-page">
    <el-card class="pad-header">
      <div class="pad-header-main">
        <div>
          <h2>Pad 端工作台</h2>
          <p>按角色展示任务：管理者（全量管理）、老师（布置作业/考试）、学生（完成作业/查看成绩）</p>
        </div>
        <div class="pad-header-actions">
          <el-button @click="openProfileDialog">个人信息</el-button>
          <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
        </div>
      </div>
    </el-card>

    <template v-if="isManager">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-card>
            <template #header>管理者创建老师任务</template>
            <el-form :model="teacherTaskForm" label-width="90px">
              <el-form-item label="老师ID"><el-input v-model="teacherTaskForm.teacherId" /></el-form-item>
              <el-form-item label="任务标题"><el-input v-model="teacherTaskForm.title" /></el-form-item>
              <el-form-item label="任务内容"><el-input v-model="teacherTaskForm.content" type="textarea" /></el-form-item>
              <el-form-item><el-button type="primary" @click="handleCreateTeacherTask">发布任务</el-button></el-form-item>
            </el-form>
            <el-divider />
            <h4>管理者创建学生作业</h4>
            <el-form :model="managerHomeworkForm" label-width="90px">
              <el-form-item label="作业标题"><el-input v-model="managerHomeworkForm.title" /></el-form-item>
              <el-form-item label="班级">
                <el-select v-model="managerHomeworkForm.className" placeholder="请选择班级" filterable>
                  <el-option v-for="item in classOptions" :key="item" :label="item" :value="item" />
                </el-select>
              </el-form-item>
              <el-form-item label="作业内容"><el-input v-model="managerHomeworkForm.content" type="textarea" /></el-form-item>
              <el-form-item><el-button type="success" @click="handleManagerCreateHomework">发布学生作业</el-button></el-form-item>
            </el-form>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>管理者查看所有班级/考试成绩</template>
            <el-button type="primary" @click="loadManagerScores">刷新</el-button>
            <el-divider />
            <h4>考试成绩</h4>
            <el-table :data="managerExamScores" size="small" height="220">
              <el-table-column prop="exam_title" label="考试" />
              <el-table-column prop="class_name" label="班级" />
              <el-table-column prop="student_id" label="学生ID" width="90" />
              <el-table-column prop="score" label="分数" width="80" />
            </el-table>
            <h4 style="margin-top: 12px;">学生总成绩表</h4>
            <el-table :data="managerPerfScores" size="small" height="220">
              <el-table-column prop="student_id" label="学生ID" width="90" />
              <el-table-column prop="exam_score" label="成绩" width="80" />
              <el-table-column prop="school_type" label="学校类型" />
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </template>

    <template v-if="isTeacher">
      <el-tabs v-model="teacherActiveTab" @tab-change="handleTeacherTabChange">
        <el-tab-pane label="发布任务" name="publish">
          <el-row :gutter="16">
            <el-col :span="10">
              <el-card>
                <el-form label-width="80px">
                  <el-form-item label="发布类型">
                    <el-select v-model="publishType" @change="loadTeacherPublishData">
                      <el-option label="发布作业" value="homework" />
                      <el-option label="发布考试" value="exam" />
                    </el-select>
                  </el-form-item>

                  <template v-if="publishType === 'homework'">
                    <el-form-item label="标题"><el-input v-model="homeworkForm.title" /></el-form-item>
                    <el-form-item label="班级">
                      <el-select v-model="homeworkForm.className" placeholder="请选择班级" filterable>
                        <el-option v-for="item in classOptions" :key="item" :label="item" :value="item" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="形式">
                      <el-select v-model="homeworkForm.publishMode">
                        <el-option label="纯文本" value="text" />
                        <el-option label="Word" value="word" />
                        <el-option label="PDF" value="pdf" />
                      </el-select>
                    </el-form-item>
                    <el-form-item v-if="homeworkForm.publishMode === 'text'" label="内容">
                      <el-input v-model="homeworkForm.content" type="textarea" />
                    </el-form-item>
                    <el-form-item v-else label="附件">
                      <FileUpload
                        v-model="homeworkForm.fileUrl"
                        :limit="1"
                        :file-size="20"
                        :file-type="homeworkUploadTypes"
                      />
                    </el-form-item>
                    <el-form-item><el-button type="primary" @click="handleCreateHomework">发布作业</el-button></el-form-item>
                  </template>

                  <template v-else>
                    <el-form-item label="考试名"><el-input v-model="examForm.title" /></el-form-item>
                    <el-form-item label="班级">
                      <el-select v-model="examForm.className" placeholder="请选择班级" filterable>
                        <el-option v-for="item in classOptions" :key="item" :label="item" :value="item" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="总分"><el-input-number v-model="examForm.totalScore" :min="1" :max="200" /></el-form-item>
                    <el-form-item><el-button type="primary" @click="handleCreateExam">发布考试</el-button></el-form-item>
                  </template>
                </el-form>
              </el-card>
            </el-col>
            <el-col :span="14">
              <el-card>
                <el-table v-if="publishType === 'homework'" :data="teacherHomework" size="small" height="320">
                  <el-table-column prop="homeworkId" label="ID" width="70" />
                  <el-table-column prop="title" label="标题" />
                  <el-table-column prop="className" label="班级" />
                  <el-table-column label="附件" width="96">
                    <template #default="{ row }">
                      <el-button
                        v-if="hasHomeworkAttachment(row.content)"
                        link
                        type="primary"
                        @click="openHomeworkAttachment(row.content)"
                      >
                        查看
                      </el-button>
                      <span v-else>-</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="status" label="状态" width="100" />
                </el-table>
                <el-table v-else :data="teacherExam" size="small" height="320">
                  <el-table-column prop="examId" label="ID" width="70" />
                  <el-table-column prop="title" label="考试名" />
                  <el-table-column prop="className" label="班级" />
                  <el-table-column prop="totalScore" label="总分" width="80" />
                </el-table>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <el-tab-pane label="批改作业" name="review">
          <el-card>
            <el-button @click="loadTeacherHomeworkSubmissions">刷新提交</el-button>
            <el-table :data="teacherSubmissions" size="small" height="380" style="margin-top: 12px;">
              <el-table-column prop="homework_title" label="作业" />
              <el-table-column prop="student_id" label="学生ID" width="90" />
              <el-table-column prop="student_name" label="学生" width="120" />
              <el-table-column prop="answer_content" label="作答" show-overflow-tooltip />
              <el-table-column prop="score" label="分数" width="80" />
              <el-table-column label="操作" width="100">
                <template #default="{ row }">
                  <el-button link type="primary" @click="openHomeworkReview(row)">批改</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="考试评分" name="score">
          <el-row :gutter="16">
            <el-col :span="10">
              <el-card>
                <el-form :model="examScoreForm" label-width="80px">
                  <el-form-item label="考试ID"><el-input v-model="examScoreForm.examId" /></el-form-item>
                  <el-form-item label="学生ID"><el-input v-model="examScoreForm.studentId" /></el-form-item>
                  <el-form-item label="学生名"><el-input v-model="examScoreForm.studentName" /></el-form-item>
                  <el-form-item label="分数"><el-input-number v-model="examScoreForm.score" :min="0" :max="200" /></el-form-item>
                  <el-form-item><el-button type="success" @click="handleScoreExam">提交评分</el-button></el-form-item>
                </el-form>
              </el-card>
            </el-col>
            <el-col :span="14">
              <el-card>
                <el-table :data="teacherExam" size="small" height="360">
                  <el-table-column prop="examId" label="ID" width="70" />
                  <el-table-column prop="title" label="考试名" />
                  <el-table-column prop="className" label="班级" />
                  <el-table-column prop="totalScore" label="总分" width="80" />
                </el-table>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <el-tab-pane label="我的管理任务" name="task">
          <el-card>
            <el-table :data="teacherTasks" size="small" height="380">
              <el-table-column prop="taskId" label="ID" width="70" />
              <el-table-column prop="title" label="标题" />
              <el-table-column prop="content" label="内容" show-overflow-tooltip />
              <el-table-column prop="status" label="状态" width="100" />
            </el-table>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="查看学生成绩" name="studentScore">
          <el-card>
            <el-button @click="loadTeacherScores">刷新成绩</el-button>
            <el-table :data="teacherScores" size="small" height="380" style="margin-top: 12px;">
              <el-table-column prop="student_id" label="学生ID" width="90" />
              <el-table-column prop="exam_score" label="总成绩" width="90" />
              <el-table-column prop="gender" label="性别" width="90" />
              <el-table-column prop="school_type" label="学校类型" />
            </el-table>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="数据可视化" name="visual">
          <div class="visual-grid">
            <el-card class="chart-card">
              <template #header>
                <div class="chart-header">
                  <span>考试发布趋势</span>
                  <el-button link type="primary" @click="refreshTeacherVisual">刷新</el-button>
                </div>
              </template>
              <div ref="teacherExamTrendRef" class="chart-box"></div>
            </el-card>

            <el-card class="chart-card">
              <template #header>作业批改分布</template>
              <div ref="teacherHomeworkDistRef" class="chart-box"></div>
            </el-card>

            <el-card class="chart-card">
              <template #header>教师任务状态占比</template>
              <div ref="teacherTaskPieRef" class="chart-box"></div>
            </el-card>

            <el-card class="chart-card">
              <template #header>教学指标雷达</template>
              <div ref="teacherRadarRef" class="chart-box"></div>
            </el-card>
          </div>
        </el-tab-pane>

        <el-tab-pane :label="`消息中心${messageUnreadTotal > 0 ? `（${messageUnreadTotal}）` : ''}`" name="message">
          <el-row :gutter="16">
            <el-col :span="10">
              <el-card>
                <template #header>老师给学生发消息</template>
                <el-form :model="messageForm" label-width="72px">
                  <el-form-item label="标题"><el-input v-model="messageForm.title" /></el-form-item>
                  <el-form-item label="内容"><el-input v-model="messageForm.content" type="textarea" :rows="6" /></el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="sendMessageToStudent">发送消息</el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-col>
            <el-col :span="14">
              <el-card>
                <template #header>
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span>消息列表</span>
                    <el-button link type="primary" @click="refreshMessages">刷新</el-button>
                  </div>
                </template>
                <el-empty v-if="messagePosts.length === 0" description="暂无消息" />
                <div v-for="post in messagePosts" :key="post.post_id" class="message-post">
                  <div class="message-top">
                    <strong>{{ post.title }}</strong>
                    <span>{{ post.author_name }}（{{ post.author_role }}） · {{ post.create_time }}</span>
                  </div>
                  <p>{{ post.content }}</p>
                  <el-input
                    v-model="messageReplyMap[post.post_id]"
                    placeholder="回复消息"
                    size="small"
                    @keyup.enter="replyMessage(post.post_id)"
                  />
                  <div class="reply-actions">
                    <el-button size="small" link type="primary" @click="replyMessage(post.post_id)">回复</el-button>
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
        </el-tab-pane>
      </el-tabs>
    </template>

    <template v-if="isStudent">
      <el-tabs v-model="studentActiveTab" @tab-change="handleStudentTabChange">
        <el-tab-pane label="我的作业" name="homework">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-card>
                <el-button @click="loadStudentHomework">刷新作业</el-button>
                <el-table :data="studentHomework" size="small" height="360" style="margin-top: 12px;">
                  <el-table-column prop="homeworkId" label="ID" width="70" />
                  <el-table-column prop="title" label="标题" />
                  <el-table-column prop="className" label="班级" />
                  <el-table-column label="附件" width="96">
                    <template #default="{ row }">
                      <el-button
                        v-if="hasHomeworkAttachment(row.content)"
                        link
                        type="primary"
                        @click="openHomeworkAttachment(row.content)"
                      >
                        查看
                      </el-button>
                      <span v-else>-</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="120">
                    <template #default="scope">
                      <el-button link type="primary" @click="openSubmit(scope.row)">提交</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <el-button @click="loadStudentSubmissions">刷新我的提交</el-button>
                <el-table :data="studentSubmissions" size="small" height="360" style="margin-top: 12px;">
                  <el-table-column prop="homework_title" label="作业" />
                  <el-table-column prop="score" label="分数" width="80" />
                  <el-table-column prop="feedback" label="反馈" show-overflow-tooltip />
                </el-table>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <el-tab-pane label="我的考试成绩" name="exam">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-card>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span>可参加考试</span>
                  <el-button @click="loadStudentExamList">刷新考试</el-button>
                </div>
                <el-table :data="studentExams" size="small" height="360" style="margin-top: 12px;">
                  <el-table-column prop="examId" label="ID" width="70" />
                  <el-table-column prop="title" label="考试" />
                  <el-table-column prop="className" label="班级" width="110" />
                  <el-table-column label="操作" width="100">
                    <template #default="{ row }">
                      <el-button link type="primary" @click="openExamSubmit(row)">作答</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span>考试评分结果</span>
                  <el-button @click="loadStudentExamScore">刷新分数</el-button>
                </div>
                <el-table :data="studentExamScores" size="small" height="170" style="margin-top: 12px;">
                  <el-table-column prop="exam_title" label="考试" />
                  <el-table-column prop="score" label="分数" width="80" />
                  <el-table-column prop="remark" label="评语/作答" show-overflow-tooltip />
                </el-table>
                <el-divider />
                <el-button @click="loadStudentSelfScores">刷新总成绩</el-button>
                <el-table :data="studentPerfScores" size="small" height="360" style="margin-top: 12px;">
                  <el-table-column prop="student_id" label="学生ID" width="90" />
                  <el-table-column prop="exam_score" label="总成绩" width="90" />
                  <el-table-column prop="school_type" label="学校类型" />
                </el-table>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <el-tab-pane label="数据可视化" name="visual">
          <div class="visual-grid">
            <el-card class="chart-card">
              <template #header>
                <div class="chart-header">
                  <span>我的考试趋势</span>
                  <el-button link type="primary" @click="refreshStudentVisual">刷新</el-button>
                </div>
              </template>
              <div ref="studentExamTrendRef" class="chart-box"></div>
            </el-card>

            <el-card class="chart-card">
              <template #header>作业得分分布</template>
              <div ref="studentHomeworkBarRef" class="chart-box"></div>
            </el-card>

            <el-card class="chart-card">
              <template #header>作业完成率</template>
              <div ref="studentCompletionGaugeRef" class="chart-box"></div>
            </el-card>

            <el-card class="chart-card">
              <template #header>学习画像雷达</template>
              <div ref="studentRadarRef" class="chart-box"></div>
            </el-card>
          </div>
        </el-tab-pane>

        <el-tab-pane :label="`消息中心${messageUnreadTotal > 0 ? `（${messageUnreadTotal}）` : ''}`" name="message">
          <el-card>
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>老师消息</span>
                <el-button link type="primary" @click="refreshMessages">刷新</el-button>
              </div>
            </template>
            <el-empty v-if="messagePosts.length === 0" description="暂无消息" />
            <div v-for="post in messagePosts" :key="post.post_id" class="message-post">
              <div class="message-top">
                <strong>{{ post.title }}</strong>
                <span>{{ post.author_name }}（{{ post.author_role }}） · {{ post.create_time }}</span>
              </div>
              <p>{{ post.content }}</p>
              <el-input
                v-model="messageReplyMap[post.post_id]"
                placeholder="回复老师消息"
                size="small"
                @keyup.enter="replyMessage(post.post_id)"
              />
              <div class="reply-actions">
                <el-button size="small" link type="primary" @click="replyMessage(post.post_id)">回复</el-button>
              </div>
              <div v-if="post.replies && post.replies.length" class="reply-list">
                <div v-for="reply in post.replies" :key="reply.reply_id" class="reply-item">
                  {{ reply.author_name }}：{{ reply.content }}
                </div>
              </div>
            </div>
          </el-card>
        </el-tab-pane>
      </el-tabs>

      <el-dialog v-model="submitDialog" title="提交作业" width="520px">
        <el-form :model="submitForm" label-width="80px">
          <el-form-item label="作业ID"><el-input v-model="submitForm.homeworkId" disabled /></el-form-item>
          <el-form-item label="作答内容"><el-input v-model="submitForm.answerContent" type="textarea" :rows="5" /></el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="submitDialog = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitHomework">提交</el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="examSubmitDialog" title="提交考试作答" width="560px">
        <el-form :model="examSubmitForm" label-width="80px">
          <el-form-item label="考试ID"><el-input v-model="examSubmitForm.examId" disabled /></el-form-item>
          <el-form-item label="考试名"><el-input v-model="examSubmitForm.examTitle" disabled /></el-form-item>
          <el-form-item label="作答内容"><el-input v-model="examSubmitForm.answerContent" type="textarea" :rows="6" /></el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="examSubmitDialog = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitExam">提交</el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="homeworkReviewDialog" title="批改作业" width="520px">
        <el-form :model="homeworkReviewForm" label-width="90px">
          <el-form-item label="提交ID"><el-input v-model="homeworkReviewForm.submissionId" disabled /></el-form-item>
          <el-form-item label="学生"><el-input v-model="homeworkReviewForm.studentName" disabled /></el-form-item>
          <el-form-item label="分数"><el-input-number v-model="homeworkReviewForm.score" :min="0" :max="100" /></el-form-item>
          <el-form-item label="评语"><el-input v-model="homeworkReviewForm.feedback" type="textarea" :rows="4" /></el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="homeworkReviewDialog = false">取消</el-button>
          <el-button type="primary" @click="handleScoreHomework">提交批改</el-button>
        </template>
      </el-dialog>
    </template>

    <div class="bottom-actions" v-if="isTeacher || isStudent">
      <el-button type="primary" plain @click="goTo('/education/rag')">AI 智能问答（RAG）</el-button>
      <el-button type="success" plain @click="goTo('/education/prediction')">AI 成绩预测</el-button>
    </div>

    <el-dialog v-model="profileDialogVisible" title="个人信息" width="520px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="账号">{{ profileInfo.userName }}</el-descriptions-item>
        <el-descriptions-item label="昵称">{{ profileInfo.nickName }}</el-descriptions-item>
        <el-descriptions-item label="角色">{{ profileInfo.roles }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button type="primary" @click="profileDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import useUserStore from '@/store/modules/user'
import {
  createHomework,
  listTeacherHomework,
  listStudentHomework,
  submitHomework,
  listTeacherHomeworkSubmissions,
  listStudentHomeworkSubmissions,
  scoreHomework as scoreHomeworkApi,
  createExam,
  listTeacherExam,
  listStudentExam as listStudentExamApi,
  submitExam,
  scoreExam,
  listStudentExamScore,
  listManagerScores,
  listStudentSelfScores,
  createTeacherTask,
  listTeacherTasks,
  listTeacherScores
} from '@/api/education/pad'
import {
  listForumPosts,
  createForumPost,
  replyForumPost as replyForumPostApi,
  getForumNotice,
  markForumRead
} from '@/api/education/forum'

const router = useRouter()
const userStore = useUserStore()

const roles = computed(() => (userStore.roles || []).map(r => String(r).toLowerCase()))
const isManager = computed(() => roles.value.includes('admin') || roles.value.includes('manager'))
const isTeacher = computed(() => roles.value.includes('teacher'))
const isStudent = computed(() => roles.value.includes('student') || roles.value.includes('role_default'))
const teacherActiveTab = ref('publish')
const studentActiveTab = ref('homework')
const publishType = ref('homework')

const homeworkForm = reactive({ title: '', className: '', content: '', publishMode: 'text', fileUrl: '' })
const examForm = reactive({ title: '', className: '', totalScore: 100 })
const examScoreForm = reactive({ examId: '', studentId: '', studentName: '', score: 0, remark: '' })
const teacherTaskForm = reactive({ teacherId: '', teacherName: '', title: '', content: '', dueTime: null })
const managerHomeworkForm = reactive({ title: '', className: '', content: '' })
const classOptions = Array.from({ length: 5 }, (_, g) => g + 1)
  .flatMap((grade) => Array.from({ length: 10 }, (_, c) => `G${grade}-C${c + 1}`))

const teacherHomework = ref([])
const teacherSubmissions = ref([])
const teacherExam = ref([])
const teacherTasks = ref([])
const teacherScores = ref([])

const studentHomework = ref([])
const studentSubmissions = ref([])
const studentExams = ref([])
const studentExamScores = ref([])
const studentPerfScores = ref([])

const managerExamScores = ref([])
const managerPerfScores = ref([])
const messageForm = reactive({ title: '', content: '' })
const messagePosts = ref([])
const messageReplyMap = reactive({})
const messageUnreadTotal = ref(0)
const profileDialogVisible = ref(false)
const profileInfo = reactive({
  userName: '',
  nickName: '',
  roles: ''
})
const teacherExamTrendRef = ref(null)
const teacherHomeworkDistRef = ref(null)
const teacherTaskPieRef = ref(null)
const teacherRadarRef = ref(null)
const studentExamTrendRef = ref(null)
const studentHomeworkBarRef = ref(null)
const studentCompletionGaugeRef = ref(null)
const studentRadarRef = ref(null)
let teacherExamTrendChart = null
let teacherHomeworkDistChart = null
let teacherTaskPieChart = null
let teacherRadarChart = null
let studentExamTrendChart = null
let studentHomeworkBarChart = null
let studentCompletionGaugeChart = null
let studentRadarChart = null

const submitDialog = ref(false)
const submitForm = reactive({ homeworkId: '', answerContent: '' })
const homeworkReviewDialog = ref(false)
const homeworkReviewForm = reactive({ submissionId: '', studentName: '', score: 0, feedback: '' })
const examSubmitDialog = ref(false)
const examSubmitForm = reactive({ examId: '', examTitle: '', answerContent: '' })

const goTo = (path) => router.push(path)
const baseApi = import.meta.env.VITE_APP_BASE_API
const homeworkUploadTypes = computed(() => {
  if (homeworkForm.publishMode === 'word') return ['doc', 'docx']
  if (homeworkForm.publishMode === 'pdf') return ['pdf']
  return ['txt']
})

function buildHomeworkContent() {
  if (homeworkForm.publishMode === 'text') {
    return String(homeworkForm.content || '').trim()
  }
  const fileUrl = String(homeworkForm.fileUrl || '').split(',')[0]
  if (!fileUrl) return ''
  const modeLabel = homeworkForm.publishMode === 'word' ? 'WORD' : 'PDF'
  return `[${modeLabel}附件] ${fileUrl}`
}

function parseHomeworkAttachment(content) {
  const value = String(content || '').trim()
  const match = value.match(/^\[(WORD|PDF)附件\]\s+(.+)$/i)
  if (!match) return null
  return { type: String(match[1]).toUpperCase(), url: match[2] }
}

function hasHomeworkAttachment(content) {
  return !!parseHomeworkAttachment(content)
}

function openHomeworkAttachment(content) {
  const attachment = parseHomeworkAttachment(content)
  if (!attachment) {
    ElMessage.warning('该作业没有附件')
    return
  }
  const url = attachment.url.startsWith('http') ? attachment.url : `${baseApi}${attachment.url}`
  window.open(url, '_blank')
}

function loadTeacherPublishData() {
  if (publishType.value === 'exam') {
    loadTeacherExam()
    return
  }
  loadTeacherHomework()
}

async function handleCreateHomework() {
  const title = String(homeworkForm.title || '').trim()
  const className = String(homeworkForm.className || '').trim()
  const content = buildHomeworkContent()
  if (!title || !className) {
    ElMessage.warning('请填写标题和班级')
    return
  }
  if (!content) {
    ElMessage.warning(homeworkForm.publishMode === 'text' ? '请填写作业内容' : '请先上传作业附件')
    return
  }
  await createHomework({ title, className, content })
  ElMessage.success('作业已发布')
  Object.assign(homeworkForm, { title: '', className: '', content: '', publishMode: 'text', fileUrl: '' })
  loadTeacherHomework()
}

async function loadTeacherHomework() {
  const res = await listTeacherHomework()
  teacherHomework.value = res.data || []
}

async function loadStudentHomework() {
  const res = await listStudentHomework()
  studentHomework.value = res.data || []
}

async function loadTeacherHomeworkSubmissions() {
  const res = await listTeacherHomeworkSubmissions()
  teacherSubmissions.value = res.data || []
}

function openHomeworkReview(row) {
  homeworkReviewForm.submissionId = row.submission_id
  homeworkReviewForm.studentName = row.student_name || ''
  homeworkReviewForm.score = Number(row.score ?? 0)
  homeworkReviewForm.feedback = row.feedback || ''
  homeworkReviewDialog.value = true
}

async function handleScoreHomework() {
  if (!homeworkReviewForm.submissionId) {
    ElMessage.warning('提交记录不能为空')
    return
  }
  await scoreHomeworkApi({
    submissionId: homeworkReviewForm.submissionId,
    score: homeworkReviewForm.score,
    feedback: homeworkReviewForm.feedback
  })
  ElMessage.success('作业批改成功')
  homeworkReviewDialog.value = false
  await loadTeacherHomeworkSubmissions()
}

async function loadStudentSubmissions() {
  const res = await listStudentHomeworkSubmissions()
  studentSubmissions.value = res.data || []
}

function openSubmit(row) {
  submitForm.homeworkId = row.homeworkId
  submitForm.answerContent = ''
  submitDialog.value = true
}

async function handleSubmitHomework() {
  await submitHomework(submitForm.homeworkId, { answerContent: submitForm.answerContent })
  ElMessage.success('作业提交成功')
  submitDialog.value = false
  loadStudentSubmissions()
}

async function handleCreateExam() {
  await createExam(examForm)
  ElMessage.success('考试已发布')
  Object.assign(examForm, { title: '', className: '', totalScore: 100 })
  loadTeacherExam()
}

async function loadTeacherExam() {
  const res = await listTeacherExam()
  teacherExam.value = res.data || []
}

async function handleScoreExam() {
  await scoreExam(examScoreForm)
  ElMessage.success('评分成功')
  Object.assign(examScoreForm, { examId: '', studentId: '', studentName: '', score: 0, remark: '' })
}

async function loadStudentExamScore() {
  const res = await listStudentExamScore()
  studentExamScores.value = res.data || []
}

async function loadStudentExamList() {
  const res = await listStudentExamApi()
  studentExams.value = res.data || []
}

function openExamSubmit(row) {
  examSubmitForm.examId = row.examId
  examSubmitForm.examTitle = row.title
  examSubmitForm.answerContent = ''
  examSubmitDialog.value = true
}

async function handleSubmitExam() {
  const answerContent = String(examSubmitForm.answerContent || '').trim()
  if (!examSubmitForm.examId || !answerContent) {
    ElMessage.warning('请填写作答内容')
    return
  }
  await submitExam(examSubmitForm.examId, { answerContent })
  ElMessage.success('考试作答已提交')
  examSubmitDialog.value = false
  await loadStudentExamScore()
}

async function loadStudentSelfScores() {
  const res = await listStudentSelfScores()
  studentPerfScores.value = res.performanceScores || []
}

async function loadManagerScores() {
  const res = await listManagerScores()
  managerExamScores.value = res.examScores || []
  managerPerfScores.value = res.performanceScores || []
}

async function handleCreateTeacherTask() {
  await createTeacherTask(teacherTaskForm)
  ElMessage.success('老师任务已发布')
  Object.assign(teacherTaskForm, { teacherId: '', teacherName: '', title: '', content: '', dueTime: null })
}

async function handleManagerCreateHomework() {
  await createHomework(managerHomeworkForm)
  ElMessage.success('学生作业已发布')
  Object.assign(managerHomeworkForm, { title: '', className: '', content: '' })
}

async function loadTeacherTasks() {
  const res = await listTeacherTasks()
  teacherTasks.value = res.data || []
}

async function loadTeacherScores() {
  const res = await listTeacherScores()
  teacherScores.value = res.data || []
}

function safeNum(v) {
  const n = Number(v)
  return Number.isFinite(n) ? n : 0
}

function ensureChart(instance, el) {
  if (!el) return null
  if (!instance) return echarts.init(el)
  return instance
}

function renderTeacherCharts() {
  teacherExamTrendChart = ensureChart(teacherExamTrendChart, teacherExamTrendRef.value)
  teacherHomeworkDistChart = ensureChart(teacherHomeworkDistChart, teacherHomeworkDistRef.value)
  teacherTaskPieChart = ensureChart(teacherTaskPieChart, teacherTaskPieRef.value)
  teacherRadarChart = ensureChart(teacherRadarChart, teacherRadarRef.value)
  if (!teacherExamTrendChart || !teacherHomeworkDistChart || !teacherTaskPieChart || !teacherRadarChart) return

  const examNames = (teacherExam.value || []).map((row, idx) => row.title || `考试${idx + 1}`)
  const examTotals = (teacherExam.value || []).map(row => safeNum(row.totalScore))

  const scoreBins = { '0-59': 0, '60-79': 0, '80-89': 0, '90+': 0 }
  ;(teacherSubmissions.value || []).forEach(row => {
    const s = safeNum(row.score)
    if (s >= 90) scoreBins['90+'] += 1
    else if (s >= 80) scoreBins['80-89'] += 1
    else if (s >= 60) scoreBins['60-79'] += 1
    else scoreBins['0-59'] += 1
  })

  const taskStatusMap = {}
  ;(teacherTasks.value || []).forEach(row => {
    const key = String(row.status || 'UNKNOWN').toUpperCase()
    taskStatusMap[key] = (taskStatusMap[key] || 0) + 1
  })
  const taskPieData = Object.keys(taskStatusMap).map(k => ({ name: k, value: taskStatusMap[k] }))

  const avgScore = (() => {
    if (!teacherScores.value.length) return 0
    const total = teacherScores.value.reduce((sum, row) => sum + safeNum(row.exam_score), 0)
    return total / teacherScores.value.length
  })()
  const doneTaskRate = teacherTasks.value.length
    ? Math.round((teacherTasks.value.filter(t => String(t.status || '').toUpperCase() === 'DONE').length / teacherTasks.value.length) * 100)
    : 0
  const gradedRate = teacherSubmissions.value.length
    ? Math.round((teacherSubmissions.value.filter(s => s.score !== null && s.score !== undefined).length / teacherSubmissions.value.length) * 100)
    : 0

  teacherExamTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: examNames.length ? examNames : ['暂无数据'] },
    yAxis: { type: 'value' },
    series: [{ type: 'line', smooth: true, data: examTotals.length ? examTotals : [0], areaStyle: {} }]
  })

  teacherHomeworkDistChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: Object.keys(scoreBins) },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', barWidth: 26, data: Object.values(scoreBins) }]
  })

  teacherTaskPieChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: taskPieData.length ? taskPieData : [{ name: '暂无', value: 1 }]
    }]
  })

  teacherRadarChart.setOption({
    radar: {
      indicator: [
        { name: '均分', max: 100 },
        { name: '已批改率', max: 100 },
        { name: '任务完成率', max: 100 },
        { name: '考试数量', max: 100 },
        { name: '作业提交量', max: 100 }
      ]
    },
    series: [{
      type: 'radar',
      data: [{
        value: [
          Number(avgScore.toFixed(1)),
          gradedRate,
          doneTaskRate,
          Math.min(100, teacherExam.value.length * 10),
          Math.min(100, teacherSubmissions.value.length * 5)
        ]
      }]
    }]
  })
}

function renderStudentCharts() {
  studentExamTrendChart = ensureChart(studentExamTrendChart, studentExamTrendRef.value)
  studentHomeworkBarChart = ensureChart(studentHomeworkBarChart, studentHomeworkBarRef.value)
  studentCompletionGaugeChart = ensureChart(studentCompletionGaugeChart, studentCompletionGaugeRef.value)
  studentRadarChart = ensureChart(studentRadarChart, studentRadarRef.value)
  if (!studentExamTrendChart || !studentHomeworkBarChart || !studentCompletionGaugeChart || !studentRadarChart) return

  const examNames = (studentExamScores.value || []).map((row, idx) => row.exam_title || `考试${idx + 1}`)
  const examScores = (studentExamScores.value || []).map(row => safeNum(row.score))
  const hwNames = (studentSubmissions.value || []).map((row, idx) => row.homework_title || `作业${idx + 1}`)
  const hwScores = (studentSubmissions.value || []).map(row => safeNum(row.score))

  const completionRate = studentHomework.value.length
    ? Math.round((studentSubmissions.value.length / studentHomework.value.length) * 100)
    : 0
  const avgExam = examScores.length ? examScores.reduce((a, b) => a + b, 0) / examScores.length : 0
  const avgHomework = hwScores.length ? hwScores.reduce((a, b) => a + b, 0) / hwScores.length : 0
  const perfAvg = studentPerfScores.value.length
    ? studentPerfScores.value.reduce((sum, row) => sum + safeNum(row.exam_score), 0) / studentPerfScores.value.length
    : 0

  studentExamTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: examNames.length ? examNames : ['暂无数据'] },
    yAxis: { type: 'value', max: 100 },
    series: [{ type: 'line', smooth: true, data: examScores.length ? examScores : [0], areaStyle: {} }]
  })

  studentHomeworkBarChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: hwNames.length ? hwNames : ['暂无数据'] },
    yAxis: { type: 'value', max: 100 },
    series: [{ type: 'bar', data: hwScores.length ? hwScores : [0] }]
  })

  studentCompletionGaugeChart.setOption({
    series: [{
      type: 'gauge',
      min: 0,
      max: 100,
      detail: { formatter: '{value}%' },
      data: [{ value: completionRate, name: '完成率' }]
    }]
  })

  studentRadarChart.setOption({
    radar: {
      indicator: [
        { name: '考试均分', max: 100 },
        { name: '作业均分', max: 100 },
        { name: '完成率', max: 100 },
        { name: '综合成绩', max: 100 },
        { name: '活跃度', max: 100 }
      ]
    },
    series: [{
      type: 'radar',
      data: [{
        value: [
          Number(avgExam.toFixed(1)),
          Number(avgHomework.toFixed(1)),
          completionRate,
          Number(perfAvg.toFixed(1)),
          Math.min(100, (studentSubmissions.value.length + studentExamScores.value.length) * 8)
        ]
      }]
    }]
  })
}

async function refreshTeacherVisual() {
  await Promise.all([loadTeacherHomeworkSubmissions(), loadTeacherExam(), loadTeacherTasks(), loadTeacherScores()])
  await nextTick()
  renderTeacherCharts()
}

async function refreshStudentVisual() {
  await Promise.all([loadStudentHomework(), loadStudentSubmissions(), loadStudentExamScore(), loadStudentSelfScores()])
  await nextTick()
  renderStudentCharts()
}

async function handleTeacherTabChange(name) {
  if (name === 'visual') {
    await refreshTeacherVisual()
  }
}

async function handleStudentTabChange(name) {
  if (name === 'exam') {
    await loadStudentExamList()
    await loadStudentExamScore()
  }
  if (name === 'visual') {
    await refreshStudentVisual()
  }
}

async function loadMessagePosts() {
  const res = await listForumPosts()
  messagePosts.value = res.data || []
}

async function loadMessageNotice() {
  try {
    const res = await getForumNotice()
    messageUnreadTotal.value = res.unreadTotal || 0
  } catch (error) {
    messageUnreadTotal.value = 0
  }
}

async function markMessageReadState() {
  try {
    await markForumRead()
    await loadMessageNotice()
  } catch (error) {
    // ignore
  }
}

async function sendMessageToStudent() {
  if (!messageForm.title || !messageForm.content) {
    ElMessage.warning('请填写标题和内容')
    return
  }
  await createForumPost({
    title: messageForm.title,
    content: messageForm.content,
    targetRole: 'STUDENT'
  })
  messageForm.title = ''
  messageForm.content = ''
  ElMessage.success('消息已发送给学生')
  await loadMessagePosts()
  await loadMessageNotice()
}

async function replyMessage(postId) {
  const value = String(messageReplyMap[postId] || '').trim()
  if (!value) return
  await replyForumPostApi(postId, { content: value })
  messageReplyMap[postId] = ''
  ElMessage.success('回复成功')
  await loadMessagePosts()
  await loadMessageNotice()
}

async function refreshMessages() {
  await loadMessagePosts()
  await markMessageReadState()
}

function openProfileDialog() {
  profileInfo.userName = userStore.name || ''
  profileInfo.nickName = userStore.nickName || ''
  profileInfo.roles = (roles.value || []).join(', ')
  profileDialogVisible.value = true
}

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确认退出登录吗？', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch (error) {
    return
  }
  await userStore.logOut()
  router.push('/education/auth?redirect=/education/pad')
}

onMounted(() => {
  if (isTeacher.value) {
    loadTeacherHomework()
    loadTeacherHomeworkSubmissions()
    loadTeacherExam()
    loadTeacherTasks()
    loadTeacherScores()
    loadMessagePosts()
    loadMessageNotice()
  }
  if (isStudent.value) {
    loadStudentHomework()
    loadStudentSubmissions()
    loadStudentExamList()
    loadStudentExamScore()
    loadStudentSelfScores()
    loadMessagePosts()
    loadMessageNotice()
    markMessageReadState()
  }
  if (isManager.value) {
    loadManagerScores()
  }
  window.addEventListener('resize', handleChartResize)
})

function handleChartResize() {
  ;[
    teacherExamTrendChart,
    teacherHomeworkDistChart,
    teacherTaskPieChart,
    teacherRadarChart,
    studentExamTrendChart,
    studentHomeworkBarChart,
    studentCompletionGaugeChart,
    studentRadarChart
  ].forEach(chart => chart && chart.resize())
}

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleChartResize)
  ;[
    teacherExamTrendChart,
    teacherHomeworkDistChart,
    teacherTaskPieChart,
    teacherRadarChart,
    studentExamTrendChart,
    studentHomeworkBarChart,
    studentCompletionGaugeChart,
    studentRadarChart
  ].forEach(chart => chart && chart.dispose())
})
</script>

<style scoped>
.pad-page { padding: 16px 16px 92px; }
.pad-header { margin-bottom: 16px; }
.pad-header-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.pad-header-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
.message-post {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 10px;
  background: #fff;
}
.message-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}
.message-top span {
  color: #909399;
  font-size: 12px;
}
.reply-actions {
  margin-top: 4px;
}
.reply-list {
  margin-top: 6px;
  padding: 6px 8px;
  border-left: 2px solid #e5e7eb;
  background: #f8fafc;
}
.reply-item {
  font-size: 13px;
  color: #4b5563;
  margin-bottom: 4px;
}
.visual-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
.chart-card {
  min-height: 320px;
}
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.chart-box {
  height: 250px;
}
.bottom-actions {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 30;
  display: flex;
  justify-content: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.94);
  border-top: 1px solid #e5e7eb;
  backdrop-filter: blur(8px);
}
@media (max-width: 992px) {
  .visual-grid {
    grid-template-columns: 1fr;
  }
}
</style>
