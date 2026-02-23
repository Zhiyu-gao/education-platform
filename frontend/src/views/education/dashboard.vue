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
          <div class="stat-label">聊天对象</div>
          <div class="stat-value">{{ chatContactCount }}</div>
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

            <el-card v-if="isTeacher" class="block-card" shadow="hover">
              <template #header>AI批改设置</template>
              <el-upload :auto-upload="false" :show-file-list="false" :on-change="handleAiReferenceChange" accept=".png,.jpg,.jpeg,.webp">
                <el-button type="primary" plain size="small">上传批改样卷</el-button>
              </el-upload>
              <div class="upload-tip">样卷：{{ aiReferenceFileName || '未上传' }}</div>
              <el-form label-width="86px">
                <el-form-item label="满分"><el-input-number v-model="aiMaxScore" :min="1" :max="200" /></el-form-item>
                <el-form-item label="批改标准"><el-input v-model="aiRubric" type="textarea" :rows="3" placeholder="如：步骤完整、结果正确、单位规范" /></el-form-item>
              </el-form>
              <el-button type="success" size="small" :loading="aiReferenceUploading" @click="handleUploadAiReference">保存样卷</el-button>
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
                <el-table :data="studentHomeworkMerged" size="small" max-height="260">
                  <el-table-column prop="homeworkId" label="ID" width="68" />
                  <el-table-column prop="title" label="标题" min-width="150" />
                  <el-table-column prop="className" label="班级" width="130" />
                  <el-table-column label="状态" width="96">
                    <template #default="scope">
                      <el-tag v-if="scope.row.statusLabel === '被打回'" type="danger" effect="light">被打回</el-tag>
                      <el-tag v-else-if="scope.row.statusLabel === '已完成'" type="success" effect="light">已完成</el-tag>
                      <el-tag v-else type="info" effect="light">未完成</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="分数" width="86">
                    <template #default="scope">
                      {{ scope.row.score === null || scope.row.score === undefined ? '--' : scope.row.score }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="feedback" label="反馈" show-overflow-tooltip />
                  <el-table-column label="附件" width="86">
                    <template #default="scope">
                      <el-button link type="primary" @click="previewSubmissionAttachments(scope.row)">查看</el-button>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="96">
                    <template #default="scope">
                      <el-button
                        v-if="scope.row.statusLabel !== '已完成'"
                        link
                        type="primary"
                        @click="openSubmit(scope.row)"
                      >
                        提交
                      </el-button>
                      <span v-else>已提交</span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>

              <div v-if="isStudent" class="table-zone">
                <h4>我的考试成绩</h4>
                <el-table :data="studentExamMerged" size="small" max-height="220">
                  <el-table-column prop="examId" label="ID" width="68" />
                  <el-table-column prop="title" label="考试" />
                  <el-table-column label="状态" width="96">
                    <template #default="scope">
                      <el-tag :type="scope.row.statusLabel === '已完成' ? 'success' : 'info'" effect="light">
                        {{ scope.row.statusLabel }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="我的成绩" width="96">
                    <template #default="scope">
                      {{ scope.row.myScore === null || scope.row.myScore === undefined ? '--' : scope.row.myScore }}
                    </template>
                  </el-table-column>
                  <el-table-column label="我的排位" width="96">
                    <template #default="scope">
                      {{ scope.row.rankLabel }}
                    </template>
                  </el-table-column>
                </el-table>
              </div>

              <div v-if="isTeacher" class="table-zone">
                <h4>学生作业提交（待批改）</h4>
                <div class="action-line">
                  <el-button type="warning" plain size="small" :loading="aiBatchGrading" @click="handleAiBatchGradeHomework">一键AI批改未批改</el-button>
                </div>
                <el-table :data="teacherSubmissions" size="small" max-height="220">
                  <el-table-column prop="homework_title" label="作业" />
                  <el-table-column prop="student_name" label="学生" width="120" />
                  <el-table-column prop="answer_content" label="作答" show-overflow-tooltip />
                  <el-table-column label="附件" width="86">
                    <template #default="scope">
                      <el-button link type="primary" @click="previewSubmissionAttachments(scope.row)">查看</el-button>
                    </template>
                  </el-table-column>
                  <el-table-column label="批改状态" width="98">
                    <template #default="scope">
                      <el-tag :type="scope.row.score === null || scope.row.score === undefined ? 'warning' : 'success'" effect="light">
                        {{ scope.row.score === null || scope.row.score === undefined ? '待批改' : '已批改' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="score" label="分数" width="80" />
                  <el-table-column prop="feedback" label="反馈" show-overflow-tooltip />
                  <el-table-column label="操作" width="96">
                    <template #default="scope">
                      <el-button link type="primary" @click="openHomeworkScore(scope.row)">手动</el-button>
                      <el-button link type="success" @click="openAiSingleGrade(scope.row)">AI</el-button>
                    </template>
                  </el-table-column>
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
        <el-card class="block-card chat-card" shadow="hover">
          <template #header>
            <div class="header-line">
              <span>消息中心</span>
              <el-button link type="primary" @click="loadChatData">刷新</el-button>
            </div>
          </template>
          <div class="chat-layout">
            <aside class="chat-contact-pane">
              <el-empty v-if="chatContacts.length === 0" description="暂无可联系对象" :image-size="64" />
              <div
                v-for="contact in chatContacts"
                :key="contact.user_id"
                :class="['chat-contact-item', { active: String(contact.user_id) === activeChatPeerId }]"
                @click="selectChatContact(contact)"
              >
                <div class="chat-avatar">{{ String(contact.nick_name || '?').slice(0, 1) }}</div>
                <div class="chat-contact-text">
                  <strong>{{ contact.nick_name || `用户${contact.user_id}` }}</strong>
                  <span>{{ contact.class_name || '' }} · {{ contact.role_key === 'teacher' ? '老师' : '学生' }}</span>
                </div>
              </div>
            </aside>

            <section class="chat-main-pane">
              <div v-if="!activeChatPeerId" class="chat-empty">
                请选择左侧联系人开始聊天
              </div>
              <template v-else>
                <div ref="chatBodyRef" class="chat-message-list" v-loading="chatListLoading">
                  <el-empty v-if="chatMessages.length === 0 && !chatListLoading" description="暂无消息，发送第一条吧" :image-size="68" />
                  <div
                    v-for="item in chatMessages"
                    :key="item.message_id"
                    :class="['chat-message-row', { self: isSelfMessage(item) }]"
                  >
                    <div class="chat-bubble">
                      <p>{{ item.content }}</p>
                      <span>{{ item.create_time }}</span>
                    </div>
                  </div>
                </div>
                <div class="chat-editor">
                  <el-input
                    v-model="chatInput"
                    type="textarea"
                    :rows="2"
                    resize="none"
                    placeholder="输入消息，回车发送"
                    @keyup.enter.exact.prevent="sendChat"
                  />
                  <el-button type="primary" :loading="chatSending" @click="sendChat">发送</el-button>
                </div>
              </template>
            </section>
          </div>
        </el-card>
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
        消息中心<span v-if="chatContactCount > 0">（{{ chatContactCount }}）</span>
      </button>
      <button :class="['nav-btn', { active: activeChannel === 'profile' }]" @click="activeChannel = 'profile'">
        个人信息
      </button>
    </nav>

    <el-dialog v-model="submitDialog" title="提交作业" width="520px">
      <el-form :model="submitForm" label-width="78px">
        <el-form-item label="作业ID"><el-input v-model="submitForm.homeworkId" disabled /></el-form-item>
        <el-form-item label="作答内容"><el-input v-model="submitForm.answerContent" type="textarea" :rows="6" /></el-form-item>
        <el-form-item label="图片附件">
          <el-upload
            :auto-upload="false"
            list-type="picture-card"
            accept=".png,.jpg,.jpeg,.webp"
            multiple
            :limit="6"
            :on-change="handleHomeworkImageChange"
            :on-remove="handleHomeworkImageRemove"
            :on-exceed="handleHomeworkImageExceed"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="submitDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitHomework">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="homeworkScoreDialog" title="作业批改" width="520px">
      <el-form :model="homeworkScoreForm" label-width="86px">
        <el-form-item label="提交ID"><el-input v-model="homeworkScoreForm.submissionId" disabled /></el-form-item>
        <el-form-item label="学生"><el-input v-model="homeworkScoreForm.studentName" disabled /></el-form-item>
        <el-form-item label="分数"><el-input-number v-model="homeworkScoreForm.score" :min="0" :max="100" /></el-form-item>
        <el-form-item label="反馈"><el-input v-model="homeworkScoreForm.feedback" type="textarea" :rows="4" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="homeworkScoreDialog = false">取消</el-button>
        <el-button type="primary" @click="handleScoreHomework">提交批改</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="aiSingleDialog" title="AI批改单份试卷" width="560px">
      <el-form label-width="94px">
        <el-form-item label="提交ID">
          <el-input :model-value="(aiSingleTarget && (aiSingleTarget.submission_id || aiSingleTarget.submissionId)) || ''" disabled />
        </el-form-item>
        <el-form-item label="学生">
          <el-input :model-value="(aiSingleTarget && (aiSingleTarget.student_name || aiSingleTarget.studentName)) || ''" disabled />
        </el-form-item>
        <el-form-item label="学生试卷">
          <el-upload :auto-upload="false" :show-file-list="false" :on-change="handleAiSingleStudentFileChange" accept=".png,.jpg,.jpeg,.webp">
            <el-button type="primary" plain size="small">上传学生试卷图</el-button>
          </el-upload>
          <span class="selected-files">{{ aiSingleStudentFileName || '未选择（将退化为文本AI批改）' }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="aiSingleDialog = false">取消</el-button>
        <el-button type="success" :loading="aiSingleGrading" @click="handleAiSingleGrade">AI批改并写入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import useUserStore from '@/store/modules/user'
import {
  createHomework,
  listTeacherHomework,
  listStudentHomework,
  submitHomework,
  uploadHomeworkAttachment,
  listTeacherHomeworkSubmissions,
  listStudentHomeworkSubmissions,
  scoreHomework,
  createExam,
  listTeacherExam,
  listStudentExam,
  scoreExam,
  listStudentExamScore,
  listManagerScores,
  listStudentSelfScores,
  createTeacherTask,
  listTeacherTasks,
  listTeacherScores,
  aiSuggestReview
} from '@/api/education/pad'
import { uploadExcel, queryQuestion, getDatasets } from '@/api/education/rag'
import { uploadAiReference, aiGradeSingle } from '@/api/education/aiGrading'
import { trainPredictionModel, getModelInfo, predictScore } from '@/api/education/prediction'
import { getUserProfile, updateUserProfile, updateUserPwd } from '@/api/system/user'
import { listChatContacts, listChatMessages, sendChatMessage } from '@/api/education/forum'

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
const submitImageFiles = ref([])
const homeworkScoreDialog = ref(false)
const homeworkScoreForm = reactive({ submissionId: '', studentName: '', score: 0, feedback: '' })
const aiReferenceFile = ref(null)
const aiReferenceFileName = ref('')
const aiReferenceId = ref('')
const aiRubric = ref('')
const aiMaxScore = ref(100)
const aiReferenceUploading = ref(false)
const aiSingleDialog = ref(false)
const aiSingleTarget = ref(null)
const aiSingleStudentFile = ref(null)
const aiSingleStudentFileName = ref('')
const aiSingleGrading = ref(false)
const aiBatchGrading = ref(false)

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

const chatContacts = ref([])
const activeChatPeerId = ref('')
const chatMessages = ref([])
const chatInput = ref('')
const chatListLoading = ref(false)
const chatSending = ref(false)
const chatBodyRef = ref(null)
const chatContactCount = ref(0)
const currentTime = ref('')
let timeTimer = null
let chatPollTimer = null

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

const studentHomeworkMerged = computed(() => {
  const submissionMap = new Map()
  ;(studentSubmissions.value || []).forEach((item) => {
    const key = item.homeworkId || item.homework_id
    if (!key) return
    if (!submissionMap.has(key)) {
      submissionMap.set(key, item)
    }
  })

  return (studentHomework.value || []).map((hw) => {
    const key = hw.homeworkId || hw.homework_id
    const submission = submissionMap.get(key)
    const feedback = submission?.feedback || ''
    const isRejected = /打回|退回|重做/.test(String(feedback))
    let statusLabel = '未完成'
    if (submission) {
      statusLabel = isRejected ? '被打回' : '已完成'
    }
    return {
      ...hw,
      answer_content: submission?.answer_content || submission?.answerContent || '',
      score: submission?.score,
      feedback,
      statusLabel
    }
  })
})

const studentExamMerged = computed(() => {
  const scoreMap = new Map()
  ;(studentExamScores.value || []).forEach((row) => {
    const key = row.examId || row.exam_id
    if (!key) return
    scoreMap.set(key, row)
  })

  const selfData = studentSelfScores.value?.data || studentSelfScores.value || {}
  const perfRows = selfData.performanceScores || []
  const sortedPerf = [...perfRows].sort((a, b) => toNum(b.exam_score) - toNum(a.exam_score))
  const myId = toNum(userStore.id)
  let myRank = -1
  sortedPerf.forEach((item, idx) => {
    const sid = toNum(item.student_id || item.studentId)
    if (sid === myId && myRank === -1) {
      myRank = idx + 1
    }
  })
  const rankLabel = myRank > 0 ? `${myRank}/${sortedPerf.length || myRank}` : '--'

  return (studentExam.value || []).map((exam) => {
    const key = exam.examId || exam.exam_id
    const scoreRow = scoreMap.get(key)
    const myScore = scoreRow?.score
    return {
      ...exam,
      myScore,
      rankLabel,
      statusLabel: myScore === null || myScore === undefined ? '未完成' : '已完成'
    }
  })
})

watch(activeChannel, async (val) => {
  if (val === 'publish') await loadPublishData()
  if (val === 'visual') await loadVisualData()
  if (val === 'ai') {
    await loadRagDatasets()
    await fetchModelInfo()
  }
  if (val === 'forum') {
    await loadChatData()
  }
  if (val === 'profile') await loadProfile()
})

function toNum(value) {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

function extractUrls(text) {
  const raw = String(text || '')
  const matches = raw.match(/https?:\/\/[^\s]+/g) || []
  return Array.from(new Set(matches))
}

function previewSubmissionAttachments(row) {
  const urls = extractUrls(row?.answer_content || row?.answerContent)
  if (!urls.length) {
    ElMessage.info('该提交暂无图片附件')
    return
  }
  urls.forEach((url) => window.open(url, '_blank'))
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
  submitImageFiles.value = []
  submitDialog.value = true
}

async function handleSubmitHomework() {
  if (!submitForm.answerContent && submitImageFiles.value.length === 0) {
    ElMessage.warning('请填写作答内容或上传图片')
    return
  }
  const uploadedUrls = []
  try {
    for (const file of submitImageFiles.value) {
      const uploadRes = await uploadHomeworkAttachment(file)
      if (uploadRes?.url) {
        uploadedUrls.push(uploadRes.url)
      }
    }
  } catch (error) {
    ElMessage.error(error?.message || '图片上传失败，请重试')
    return
  }

  let answerContent = submitForm.answerContent || ''
  if (uploadedUrls.length > 0) {
    const attachments = uploadedUrls.join('\n')
    answerContent = answerContent
      ? `${answerContent}\n\n【图片附件】\n${attachments}`
      : `【图片附件】\n${attachments}`
  }

  await submitHomework(submitForm.homeworkId, { answerContent })
  ElMessage.success('提交成功')
  submitDialog.value = false
  submitImageFiles.value = []
  await loadPublishData()
}

function handleHomeworkImageChange(file, fileList) {
  const maxSize = 10 * 1024 * 1024
  const valid = []
  ;(fileList || []).forEach((item) => {
    const f = item.raw || item
    if (!f) return
    if (f.size > maxSize) {
      ElMessage.warning(`图片 ${item.name || f.name || ''} 超过10MB，已忽略`)
      return
    }
    valid.push(f)
  })
  submitImageFiles.value = valid
}

function handleHomeworkImageRemove(file, fileList) {
  submitImageFiles.value = (fileList || []).map(item => item.raw || item).filter(Boolean)
}

function handleHomeworkImageExceed() {
  ElMessage.warning('最多上传6张图片')
}

function openHomeworkScore(row) {
  homeworkScoreForm.submissionId = row.submissionId || row.submission_id || ''
  homeworkScoreForm.studentName = row.studentName || row.student_name || ''
  homeworkScoreForm.score = row.score === null || row.score === undefined ? 0 : toNum(row.score)
  homeworkScoreForm.feedback = row.feedback || ''
  homeworkScoreDialog.value = true
}

async function handleScoreHomework() {
  if (!homeworkScoreForm.submissionId) {
    ElMessage.warning('缺少提交记录ID')
    return
  }
  await scoreHomework({
    submissionId: homeworkScoreForm.submissionId,
    score: homeworkScoreForm.score,
    feedback: homeworkScoreForm.feedback
  })
  ElMessage.success('作业批改已保存')
  homeworkScoreDialog.value = false
  Object.assign(homeworkScoreForm, { submissionId: '', studentName: '', score: 0, feedback: '' })
  await loadPublishData()
}

function handleAiReferenceChange(file) {
  aiReferenceFile.value = file
  aiReferenceFileName.value = file?.name || ''
}

async function handleUploadAiReference() {
  if (!aiReferenceFile.value) {
    ElMessage.warning('请先上传批改样卷图片')
    return
  }
  aiReferenceUploading.value = true
  try {
    const res = await uploadAiReference(aiReferenceFile.value)
    aiReferenceId.value = res.referenceId || ''
    ElMessage.success('AI样卷已保存')
  } catch (error) {
    ElMessage.error('样卷上传失败')
  } finally {
    aiReferenceUploading.value = false
  }
}

function openAiSingleGrade(row) {
  aiSingleTarget.value = row
  aiSingleStudentFile.value = null
  aiSingleStudentFileName.value = ''
  aiSingleDialog.value = true
}

function handleAiSingleStudentFileChange(file) {
  aiSingleStudentFile.value = file
  aiSingleStudentFileName.value = file?.name || ''
}

async function handleAiSingleGrade() {
  const row = aiSingleTarget.value
  if (!row) {
    ElMessage.warning('缺少待批改记录')
    return
  }
  const submissionId = row.submissionId || row.submission_id
  if (!submissionId) {
    ElMessage.warning('缺少提交ID')
    return
  }

  aiSingleGrading.value = true
  try {
    let score = 0
    let feedback = ''
    let annotatedImage = ''
    if (aiSingleStudentFile.value) {
      const res = await aiGradeSingle({
        file: aiSingleStudentFile.value,
        referenceId: aiReferenceId.value,
        rubric: aiRubric.value,
        maxScore: aiMaxScore.value
      })
      score = toNum(res.score)
      feedback = String(res.feedback || '')
      annotatedImage = res.annotatedImageUrl || ''
    } else {
      const suggest = await aiSuggestReview({
        targetAnswer: row.answer_content || '',
        exampleAnswer: aiRubric.value || '',
        exampleFeedback: '按标准完成度给分，指出主要失分点',
        exampleScore: Math.min(90, aiMaxScore.value),
        maxScore: aiMaxScore.value
      })
      score = toNum(suggest.suggestedScore)
      feedback = String(suggest.suggestedFeedback || '')
    }

    const feedbackWithImage = annotatedImage
      ? `${feedback}\n[标注图](${annotatedImage})`
      : feedback
    await scoreHomework({
      submissionId,
      score: Math.max(0, Math.min(100, Math.round(score))),
      feedback: feedbackWithImage
    })
    ElMessage.success('AI批改完成并已写入')
    aiSingleDialog.value = false
    await loadPublishData()
  } catch (error) {
    ElMessage.error('AI批改失败')
  } finally {
    aiSingleGrading.value = false
  }
}

async function handleAiBatchGradeHomework() {
  const ungraded = (teacherSubmissions.value || []).filter(item => item.score === null || item.score === undefined)
  if (!ungraded.length) {
    ElMessage.info('当前没有待批改作业')
    return
  }
  aiBatchGrading.value = true
  try {
    for (const row of ungraded) {
      const suggest = await aiSuggestReview({
        targetAnswer: row.answer_content || '',
        exampleAnswer: aiRubric.value || '',
        exampleFeedback: '按标准完成度给分，指出主要失分点',
        exampleScore: Math.min(90, aiMaxScore.value),
        maxScore: aiMaxScore.value
      })
      await scoreHomework({
        submissionId: row.submissionId || row.submission_id,
        score: Math.max(0, Math.min(100, Math.round(toNum(suggest.suggestedScore)))),
        feedback: `[AI一键批改] ${String(suggest.suggestedFeedback || '')}`
      })
    }
    ElMessage.success(`AI已完成 ${ungraded.length} 份作业批改`)
    await loadPublishData()
  } catch (error) {
    ElMessage.error('一键AI批改失败')
  } finally {
    aiBatchGrading.value = false
  }
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

function normalizeUserId(value) {
  return String(value === null || value === undefined ? '' : value)
}

function isSelfMessage(item) {
  return toNum(item.sender_id || item.senderId) === toNum(userStore.id)
}

function scrollChatToBottom() {
  nextTick(() => {
    if (!chatBodyRef.value) return
    chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
  })
}

async function loadChatData() {
  if (!(isTeacher.value || isStudent.value)) {
    chatContacts.value = []
    activeChatPeerId.value = ''
    chatMessages.value = []
    chatContactCount.value = 0
    return
  }
  try {
    chatListLoading.value = true
    const res = await listChatContacts()
    chatContacts.value = res.data || []
    chatContactCount.value = chatContacts.value.length
    const exists = chatContacts.value.some(item => normalizeUserId(item.user_id) === activeChatPeerId.value)
    if (!exists) {
      activeChatPeerId.value = chatContacts.value.length ? normalizeUserId(chatContacts.value[0].user_id) : ''
    }
    await loadChatMessageList()
  } catch (error) {
    chatContacts.value = []
    activeChatPeerId.value = ''
    chatMessages.value = []
    chatContactCount.value = 0
    ElMessage.error('加载联系人失败')
  } finally {
    chatListLoading.value = false
  }
}

async function selectChatContact(contact) {
  const peerId = normalizeUserId(contact && contact.user_id)
  if (!peerId || peerId === activeChatPeerId.value) return
  activeChatPeerId.value = peerId
  await loadChatMessageList()
}

async function loadChatMessageList() {
  if (!activeChatPeerId.value) {
    chatMessages.value = []
    return
  }
  chatListLoading.value = true
  try {
    const res = await listChatMessages(activeChatPeerId.value)
    chatMessages.value = res.data || []
    scrollChatToBottom()
  } catch (error) {
    chatMessages.value = []
    ElMessage.error('加载消息失败')
  } finally {
    chatListLoading.value = false
  }
}

async function sendChat() {
  const content = String(chatInput.value || '').trim()
  if (!activeChatPeerId.value) {
    ElMessage.warning('请先选择联系人')
    return
  }
  if (!content) {
    ElMessage.warning('请输入消息内容')
    return
  }
  chatSending.value = true
  try {
    await sendChatMessage({
      peerUserId: toNum(activeChatPeerId.value),
      content
    })
    chatInput.value = ''
    await loadChatMessageList()
  } catch (error) {
    ElMessage.error(error?.message || '发送消息失败')
  } finally {
    chatSending.value = false
  }
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
  chatPollTimer = setInterval(async () => {
    if (activeChannel.value === 'forum' && activeChatPeerId.value) {
      await loadChatMessageList()
    }
  }, 5000)
  await loadChatData()
  await loadPublishData()
  await loadVisualData()
  await loadProfile()
})

onBeforeUnmount(() => {
  if (timeTimer) {
    clearInterval(timeTimer)
    timeTimer = null
  }
  if (chatPollTimer) {
    clearInterval(chatPollTimer)
    chatPollTimer = null
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

.chat-card {
  margin-bottom: 0;
}

.chat-layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 14px;
  min-height: 520px;
}

.chat-contact-pane {
  border: 1px solid #d7e7f3;
  border-radius: 12px;
  padding: 10px;
  overflow-y: auto;
  max-height: 620px;
  background: #f9fcff;
}

.chat-contact-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 8px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chat-contact-item:hover {
  background: #eff7ff;
}

.chat-contact-item.active {
  background: #e5f3ff;
  border: 1px solid #add1ef;
}

.chat-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  color: #255877;
  background: linear-gradient(145deg, #e4f2ff 0%, #d3ebff 100%);
}

.chat-contact-text strong {
  display: block;
  color: #17324d;
  font-size: 14px;
}

.chat-contact-text span {
  display: block;
  margin-top: 2px;
  color: #62839a;
  font-size: 12px;
}

.chat-main-pane {
  border: 1px solid #d7e7f3;
  border-radius: 12px;
  background: #f6fbff;
  display: flex;
  flex-direction: column;
  min-height: 520px;
}

.chat-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #648399;
}

.chat-message-list {
  flex: 1;
  overflow-y: auto;
  padding: 14px;
}

.chat-message-row {
  display: flex;
  margin-bottom: 10px;
}

.chat-message-row.self {
  justify-content: flex-end;
}

.chat-bubble {
  max-width: 72%;
  background: #ffffff;
  border: 1px solid #dbe8f4;
  border-radius: 12px;
  padding: 8px 10px;
}

.chat-message-row.self .chat-bubble {
  background: #dff0ff;
  border-color: #b7d9f5;
}

.chat-bubble p {
  margin: 0;
  white-space: pre-wrap;
  color: #1c3d56;
  line-height: 1.45;
}

.chat-bubble span {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #6d8aa0;
}

.chat-editor {
  border-top: 1px solid #d7e7f3;
  padding: 10px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 86px;
  gap: 10px;
  align-items: end;
  background: #ffffff;
  border-radius: 0 0 12px 12px;
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

  .chat-layout {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .chat-contact-pane {
    max-height: 220px;
  }

  .chat-main-pane {
    min-height: 420px;
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
