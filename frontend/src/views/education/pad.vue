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
              <el-table-column label="评语" min-width="160" show-overflow-tooltip>
                <template #default="{ row }">
                  {{ extractTeacherReasonFromFeedback(row.feedback) || '-' }}
                </template>
              </el-table-column>
              <el-table-column label="批改图" width="86">
                <template #default="{ row }">
                  <el-button
                    v-if="extractReviewImageFromFeedback(row.feedback)"
                    link
                    type="primary"
                    @click="openReviewImage(extractReviewImageFromFeedback(row.feedback), 'teacher-list')"
                  >
                    查看
                  </el-button>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100">
                <template #default="{ row }">
                  <el-button link type="primary" @click="openHomeworkReview(row)">批改</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="考试评分" name="score">
          <el-card>
            <el-button @click="loadTeacherExamScores">刷新考试作答</el-button>
            <el-table :data="teacherExamScores" size="small" height="380" style="margin-top: 12px;">
              <el-table-column prop="exam_title" label="考试" />
              <el-table-column prop="class_name" label="班级" width="110" />
              <el-table-column prop="student_id" label="学生ID" width="90" />
              <el-table-column prop="student_name" label="学生" width="110" />
              <el-table-column prop="remark" label="作答" show-overflow-tooltip />
              <el-table-column prop="score" label="分数" width="80" />
              <el-table-column label="操作" width="100">
                <template #default="{ row }">
                  <el-button link type="primary" @click="openExamReview(row)">批改</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
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

        <el-tab-pane :label="`消息中心${chatContactCount > 0 ? `（${chatContactCount}）` : ''}`" name="message">
          <el-card>
            <template #header>
              <div class="chat-header-line">
                <span>班级私聊</span>
                <el-button link type="primary" @click="loadChatData">刷新</el-button>
              </div>
            </template>
            <div class="chat-layout">
              <aside class="chat-contact-pane">
                <div class="chat-mode-bar">
                  <el-segmented v-model="chatMode" :options="[{ label: '私聊', value: 'dm' }, { label: '群聊', value: 'group' }]" @change="handleChatModeChange" />
                </div>
                <el-input v-model="chatKeyword" placeholder="搜索姓名或群名" clearable class="chat-search-input" />
                <el-empty
                  v-if="chatMode === 'dm' ? filteredChatContacts.length === 0 : filteredChatGroups.length === 0"
                  :description="chatMode === 'dm' ? '暂无可联系对象' : '暂无群聊'"
                  :image-size="60"
                />
                <div
                  v-for="contact in (chatMode === 'dm' ? filteredChatContacts : filteredChatGroups)"
                  :key="chatMode === 'dm' ? `dm-${contact.user_id}` : `gp-${contact.groupId || contact.group_id}`"
                  :class="['chat-contact-item', {
                    active: chatMode === 'dm'
                      ? (activeChatTargetType === 'dm' && String(contact.user_id) === activeChatPeerId)
                      : (activeChatTargetType === 'group' && String(contact.groupId || contact.group_id) === activeChatGroupId)
                  }]"
                  @click="chatMode === 'dm' ? selectChatContact(contact) : selectChatGroup(contact)"
                >
                  <div class="chat-avatar">
                    {{ String(chatMode === 'dm' ? (contact.nick_name || '?') : (contact.groupName || contact.group_name || '群')).slice(0, 1) }}
                  </div>
                  <div class="chat-contact-text">
                    <strong>{{ chatMode === 'dm' ? (contact.nick_name || `用户${contact.user_id}`) : (contact.groupName || contact.group_name || '班级群') }}</strong>
                    <span v-if="chatMode === 'dm'">{{ contact.class_name || '' }} · {{ contact.role_key === 'teacher' ? '老师' : '学生' }}</span>
                    <span v-else>{{ contact.className || contact.class_name || '' }} · 群聊</span>
                  </div>
                </div>
              </aside>
              <section class="chat-main-pane">
                <div v-if="!activeChatTargetLabel" class="chat-empty">请选择左侧会话开始聊天</div>
                <template v-else>
                  <div class="chat-main-top">{{ activeChatTargetLabel }}</div>
                  <div ref="chatBodyRef" class="chat-message-list" v-loading="chatListLoading">
                    <el-empty v-if="chatMessages.length === 0 && !chatListLoading" description="暂无消息，发送第一条吧" :image-size="64" />
                    <div
                      v-for="item in chatMessages"
                      :key="item.message_id"
                      :class="['chat-message-row', { self: isSelfChatMessage(item) }]"
                    >
                      <div class="chat-bubble">
                        <strong v-if="activeChatTargetType === 'group'" class="chat-sender-name" @click="openPrivateFromGroup(item)">
                          {{ item.sender_name || `用户${item.sender_id}` }}
                        </strong>
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
        </el-tab-pane>
      </el-tabs>
    </template>

    <template v-if="isStudent">
      <el-tabs v-model="studentActiveTab" @tab-change="handleStudentTabChange">
        <el-tab-pane label="我的作业" name="homework">
          <el-card>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>我的作业</span>
              <el-button @click="loadStudentSubmissions">刷新</el-button>
            </div>
            <el-table :data="studentHomeworkMerged" size="small" height="420" style="margin-top: 12px;">
              <el-table-column prop="homeworkId" label="ID" width="70" />
              <el-table-column prop="title" label="标题" min-width="160" />
              <el-table-column prop="className" label="班级" width="110" />
              <el-table-column label="状态" width="96">
                <template #default="{ row }">
                  <el-tag v-if="row.statusLabel === '被打回'" type="danger" effect="light">被打回</el-tag>
                  <el-tag v-else-if="row.statusLabel === '已完成'" type="success" effect="light">已完成</el-tag>
                  <el-tag v-else type="info" effect="light">未完成</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="分数" width="86">
                <template #default="{ row }">
                  {{ row.score === null || row.score === undefined ? '--' : row.score }}
                </template>
              </el-table-column>
              <el-table-column prop="feedback" label="对错结果" min-width="180" show-overflow-tooltip />
              <el-table-column label="批改图" width="86">
                <template #default="{ row }">
                  <el-button
                    v-if="row.reviewImageUrl"
                    link
                    type="primary"
                    @click="openReviewImage(row.reviewImageUrl, 'student-list')"
                  >
                    查看
                  </el-button>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column label="附件" width="86">
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
                <template #default="{ row }">
                  <el-button
                    v-if="row.statusLabel !== '已完成'"
                    link
                    type="primary"
                    @click="openSubmit(row)"
                  >
                    提交
                  </el-button>
                  <span v-else>已提交</span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="我的考试成绩" name="exam">
          <el-card>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>我的考试（合并视图）</span>
              <el-button @click="refreshStudentExamMerged">刷新</el-button>
            </div>
            <el-table :data="studentExamMerged" size="small" height="560" style="margin-top: 12px;">
              <el-table-column prop="examId" label="ID" width="70" />
              <el-table-column prop="title" label="考试" min-width="180" />
              <el-table-column prop="className" label="班级" width="110" />
              <el-table-column prop="totalScore" label="总分" width="80" />
              <el-table-column label="我的分数" width="90">
                <template #default="{ row }">
                  {{ row.myScore === null || row.myScore === undefined ? '--' : row.myScore }}
                </template>
              </el-table-column>
              <el-table-column label="班级均分" width="90">
                <template #default>
                  {{ classScoreStats.avgText }}
                </template>
              </el-table-column>
              <el-table-column label="班级最高" width="90">
                <template #default>
                  {{ classScoreStats.maxText }}
                </template>
              </el-table-column>
              <el-table-column label="班级最低" width="90">
                <template #default>
                  {{ classScoreStats.minText }}
                </template>
              </el-table-column>
              <el-table-column prop="remark" label="批改结果" min-width="200" show-overflow-tooltip />
              <el-table-column label="状态" width="90">
                <template #default="{ row }">
                  <el-tag v-if="row.done" type="success" effect="light">已完成</el-tag>
                  <el-tag v-else type="info" effect="light">未完成</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100">
                <template #default="{ row }">
                  <el-button v-if="!row.done" link type="primary" @click="openExamSubmit(row)">作答</el-button>
                  <span v-else>已完成</span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
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

        <el-tab-pane :label="`消息中心${chatContactCount > 0 ? `（${chatContactCount}）` : ''}`" name="message">
          <el-card>
            <template #header>
              <div class="chat-header-line">
                <span>班级私聊</span>
                <el-button link type="primary" @click="loadChatData">刷新</el-button>
              </div>
            </template>
            <div class="chat-layout">
              <aside class="chat-contact-pane">
                <div class="chat-mode-bar">
                  <el-segmented v-model="chatMode" :options="[{ label: '私聊', value: 'dm' }, { label: '群聊', value: 'group' }]" @change="handleChatModeChange" />
                </div>
                <el-input v-model="chatKeyword" placeholder="搜索姓名或群名" clearable class="chat-search-input" />
                <el-empty
                  v-if="chatMode === 'dm' ? filteredChatContacts.length === 0 : filteredChatGroups.length === 0"
                  :description="chatMode === 'dm' ? '暂无可联系对象' : '暂无群聊'"
                  :image-size="60"
                />
                <div
                  v-for="contact in (chatMode === 'dm' ? filteredChatContacts : filteredChatGroups)"
                  :key="chatMode === 'dm' ? `dm-${contact.user_id}` : `gp-${contact.groupId || contact.group_id}`"
                  :class="['chat-contact-item', {
                    active: chatMode === 'dm'
                      ? (activeChatTargetType === 'dm' && String(contact.user_id) === activeChatPeerId)
                      : (activeChatTargetType === 'group' && String(contact.groupId || contact.group_id) === activeChatGroupId)
                  }]"
                  @click="chatMode === 'dm' ? selectChatContact(contact) : selectChatGroup(contact)"
                >
                  <div class="chat-avatar">
                    {{ String(chatMode === 'dm' ? (contact.nick_name || '?') : (contact.groupName || contact.group_name || '群')).slice(0, 1) }}
                  </div>
                  <div class="chat-contact-text">
                    <strong>{{ chatMode === 'dm' ? (contact.nick_name || `用户${contact.user_id}`) : (contact.groupName || contact.group_name || '班级群') }}</strong>
                    <span v-if="chatMode === 'dm'">{{ contact.class_name || '' }} · {{ contact.role_key === 'teacher' ? '老师' : '学生' }}</span>
                    <span v-else>{{ contact.className || contact.class_name || '' }} · 群聊</span>
                  </div>
                </div>
              </aside>
              <section class="chat-main-pane">
                <div v-if="!activeChatTargetLabel" class="chat-empty">请选择左侧会话开始聊天</div>
                <template v-else>
                  <div class="chat-main-top">{{ activeChatTargetLabel }}</div>
                  <div ref="chatBodyRef" class="chat-message-list" v-loading="chatListLoading">
                    <el-empty v-if="chatMessages.length === 0 && !chatListLoading" description="暂无消息，发送第一条吧" :image-size="64" />
                    <div
                      v-for="item in chatMessages"
                      :key="item.message_id"
                      :class="['chat-message-row', { self: isSelfChatMessage(item) }]"
                    >
                      <div class="chat-bubble">
                        <strong v-if="activeChatTargetType === 'group'" class="chat-sender-name" @click="openPrivateFromGroup(item)">
                          {{ item.sender_name || `用户${item.sender_id}` }}
                        </strong>
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
        </el-tab-pane>
      </el-tabs>
    </template>

    <el-dialog v-model="submitDialog" title="提交作业" width="520px">
      <el-form :model="submitForm" label-width="80px">
        <el-form-item label="作业ID"><el-input v-model="submitForm.homeworkId" disabled /></el-form-item>
        <el-form-item label="作答内容"><el-input v-model="submitForm.answerContent" type="textarea" :rows="5" /></el-form-item>
        <el-form-item label="作答图片">
          <FileUpload
            v-model="submitForm.answerImageUrl"
            :limit="1"
            :file-size="10"
            :file-type="answerImageTypes"
          />
        </el-form-item>
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
        <el-form-item label="作答图片">
          <FileUpload
            v-model="examSubmitForm.answerImageUrl"
            :limit="1"
            :file-size="10"
            :file-type="answerImageTypes"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="examSubmitDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitExam">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="reviewDialog" :title="reviewType === 'exam' ? '考试批改' : '作业批改'" width="980px">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form :model="reviewForm" label-width="92px">
            <el-form-item v-if="reviewType === 'homework'" label="提交ID"><el-input v-model="reviewForm.submissionId" disabled /></el-form-item>
            <el-form-item v-if="reviewType === 'exam'" label="成绩ID"><el-input v-model="reviewForm.scoreId" disabled /></el-form-item>
            <el-form-item v-if="reviewType === 'exam'" label="考试ID"><el-input v-model="reviewForm.examId" disabled /></el-form-item>
            <el-form-item label="学生"><el-input v-model="reviewForm.studentName" disabled /></el-form-item>
            <el-form-item label="题目">
              <el-input v-model="reviewForm.title" disabled />
            </el-form-item>
            <el-form-item label="学生作答">
              <el-input v-model="reviewForm.answerContent" type="textarea" :rows="6" />
            </el-form-item>
            <el-form-item label="作答图">
              <el-image
                v-if="reviewAnswerImageUrl"
                :src="reviewAnswerImageUrl"
                fit="contain"
                style="width: 100%; height: 160px; border: 1px solid #dbe2ea; border-radius: 8px;"
                :preview-src-list="[reviewAnswerImageUrl]"
              />
              <span v-else style="color: #94a3b8;">未检测到图片作答</span>
            </el-form-item>
            <el-form-item label="批注图片">
              <input type="file" accept="image/*" @change="handleReviewImageUpload" />
            </el-form-item>
          </el-form>
        </el-col>
        <el-col :span="12">
          <el-form :model="reviewForm" label-width="102px">
            <el-form-item label="示例答案">
              <el-input v-model="reviewForm.exampleAnswer" type="textarea" :rows="3" />
            </el-form-item>
            <el-form-item label="示例分数">
              <el-input-number v-model="reviewForm.exampleScore" :min="0" :max="reviewForm.maxScore || 100" />
            </el-form-item>
            <el-form-item label="示例评语">
              <el-input v-model="reviewForm.exampleFeedback" type="textarea" :rows="3" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" plain @click="handleAiSuggestReview">AI 批改建议</el-button>
              <el-button type="success" plain :loading="aiImageGrading" @click="handleAiImageGrade">AI图像批改</el-button>
            </el-form-item>
            <el-form-item label="人工分数">
              <el-input-number v-model="reviewForm.score" :min="0" :max="reviewForm.maxScore || 100" />
            </el-form-item>
            <el-form-item label="人工评语">
              <el-input v-model="reviewForm.feedback" type="textarea" :rows="3" />
            </el-form-item>
            <el-form-item label="批改结果图">
              <el-button size="small" @click="exportReviewCanvas">下载预览图</el-button>
              <span v-if="reviewForm.reviewImageUrl" style="margin-left: 8px; color: #64748b;">已绑定批改图</span>
            </el-form-item>
          </el-form>
        </el-col>
      </el-row>

      <div class="review-canvas-panel">
        <div class="review-toolbar">
          <el-radio-group v-model="reviewCanvasTool" size="small">
            <el-radio-button label="check">打勾</el-radio-button>
            <el-radio-button label="cross">打叉</el-radio-button>
            <el-radio-button label="text">文字</el-radio-button>
          </el-radio-group>
          <el-button size="small" @click="clearReviewCanvasMarks">清空批注</el-button>
          <el-button size="small" type="primary" plain @click="exportReviewCanvas">导出批注图</el-button>
        </div>
        <div class="review-canvas-wrap">
          <canvas ref="reviewCanvasRef" width="900" height="360" class="review-canvas" @click="onReviewCanvasClick" />
        </div>
      </div>

      <template #footer>
        <el-button @click="reviewDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitReview">提交批改</el-button>
      </template>
    </el-dialog>

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
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import useUserStore from '@/store/modules/user'
import { getToken } from '@/utils/auth'
import {
  createHomework,
  listTeacherHomework,
  listStudentHomework,
  submitHomework,
  uploadHomeworkAttachment,
  listTeacherHomeworkSubmissions,
  listStudentHomeworkSubmissions,
  scoreHomework as scoreHomeworkApi,
  createExam,
  listTeacherExam,
  listStudentExam as listStudentExamApi,
  submitExam,
  scoreExam,
  listStudentExamScore,
  listTeacherExamScore,
  listManagerScores,
  listStudentSelfScores,
  createTeacherTask,
  listTeacherTasks,
  listTeacherScores,
  aiSuggestReview
} from '@/api/education/pad'
import {
  listChatContacts,
  listChatMessages,
  sendChatMessage,
  listChatGroups,
  listGroupChatMessages,
  sendGroupChatMessage
} from '@/api/education/forum'
import { aiGradeSingle } from '@/api/education/aiGrading'

const router = useRouter()
const route = useRoute()
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
const teacherTaskForm = reactive({ teacherId: '', teacherName: '', title: '', content: '', dueTime: null })
const managerHomeworkForm = reactive({ title: '', className: '', content: '' })
const classOptions = Array.from({ length: 5 }, (_, g) => g + 1)
  .flatMap((grade) => Array.from({ length: 10 }, (_, c) => `G${grade}-C${c + 1}`))

const teacherHomework = ref([])
const teacherSubmissions = ref([])
const teacherExam = ref([])
const teacherExamScores = ref([])
const teacherTasks = ref([])
const teacherScores = ref([])

const studentHomework = ref([])
const studentSubmissions = ref([])
const studentExams = ref([])
const studentExamScores = ref([])
const studentPerfScores = ref([])
const classScoreStats = computed(() => {
  const values = (studentPerfScores.value || [])
    .map(row => Number(row.exam_score))
    .filter(num => Number.isFinite(num))
  if (!values.length) {
    return { avg: null, max: null, min: null, avgText: '--', maxText: '--', minText: '--' }
  }
  const sum = values.reduce((a, b) => a + b, 0)
  const avg = sum / values.length
  const max = Math.max(...values)
  const min = Math.min(...values)
  return {
    avg,
    max,
    min,
    avgText: avg.toFixed(1),
    maxText: max.toFixed(0),
    minText: min.toFixed(0)
  }
})
const studentExamMerged = computed(() => {
  const scoreMap = new Map()
  ;(studentExamScores.value || []).forEach((item) => {
    const key = Number(item.exam_id || item.examId)
    if (!Number.isFinite(key)) return
    scoreMap.set(key, item)
  })
  const merged = (studentExams.value || []).map((exam) => {
    const examId = Number(exam.examId || exam.exam_id)
    const scoreRow = scoreMap.get(examId)
    const myScoreRaw = scoreRow?.score
    const myScore = myScoreRaw === null || myScoreRaw === undefined ? null : Number(myScoreRaw)
    return {
      examId,
      title: exam.title || '',
      className: exam.className || exam.class_name || '',
      totalScore: exam.totalScore || exam.total_score || 100,
      myScore: Number.isFinite(myScore) ? myScore : null,
      remark: scoreRow?.remark || '--',
      done: Number.isFinite(myScore)
    }
  })
  return merged
})
const studentHomeworkMerged = computed(() => {
  const submissionMap = new Map()
  ;(studentSubmissions.value || []).forEach((item) => {
    const key = item.homework_id || item.homeworkId
    if (!key || submissionMap.has(key)) return
    submissionMap.set(key, item)
  })

  return (studentHomework.value || []).map((homework) => {
    const key = homework.homeworkId || homework.homework_id
    const submission = submissionMap.get(key)
    const rawFeedback = String(submission?.feedback || '')
    const feedback = extractStudentResultFromFeedback(rawFeedback) || (submission ? '已批改' : '')
    const reviewImageUrl = extractReviewImageFromFeedback(rawFeedback)
    const isRejected = /打回|退回|重做/.test(feedback)
    let statusLabel = '未完成'
    if (submission) {
      statusLabel = isRejected ? '被打回' : '已完成'
    }
    return {
      ...homework,
      score: submission?.score,
      feedback,
      reviewImageUrl,
      answer_content: submission?.answer_content || '',
      statusLabel
    }
  })
})

const managerExamScores = ref([])
const managerPerfScores = ref([])
const chatContacts = ref([])
const chatGroups = ref([])
const chatKeyword = ref('')
const chatMode = ref('dm')
const activeChatTargetType = ref('dm')
const activeChatPeerId = ref('')
const activeChatGroupId = ref('')
const chatMessages = ref([])
const chatInput = ref('')
const chatListLoading = ref(false)
const chatSending = ref(false)
const chatBodyRef = ref(null)
const chatContactCount = ref(0)
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
const submitForm = reactive({ homeworkId: '', answerContent: '', answerImageUrl: '' })
const reviewDialog = ref(false)
const reviewType = ref('homework')
const reviewForm = reactive({
  submissionId: '',
  scoreId: '',
  examId: '',
  studentId: '',
  studentName: '',
  title: '',
  answerContent: '',
  score: 0,
  maxScore: 100,
  feedback: '',
  reviewImageUrl: '',
  studentResultText: '',
  exampleAnswer: '',
  exampleScore: 85,
  exampleFeedback: ''
})
const reviewCanvasRef = ref(null)
const reviewCanvasTool = ref('check')
const reviewImageUrl = ref('')
let reviewCanvas = null
let reviewCanvasCtx = null
let reviewCanvasImage = null
const reviewCanvasMarks = ref([])
const examSubmitDialog = ref(false)
const examSubmitForm = reactive({ examId: '', examTitle: '', answerContent: '', answerImageUrl: '' })

const goTo = (path) => router.push(path)
const baseApi = import.meta.env.VITE_APP_BASE_API
const aiBaseApi = String(import.meta.env.VITE_AI_BASE_API || 'http://127.0.0.1:8000').trim().replace(/\/$/, '')
const homeworkUploadTypes = computed(() => {
  if (homeworkForm.publishMode === 'word') return ['doc', 'docx']
  if (homeworkForm.publishMode === 'pdf') return ['pdf']
  return ['txt']
})
const answerImageTypes = ['png', 'jpg', 'jpeg', 'bmp', 'gif']
const reviewAnswerImageUrl = computed(() => {
  const reviewedUrl = resolveFileUrl(reviewForm.reviewImageUrl)
  if (reviewedUrl) return reviewedUrl
  return extractImageUrl(reviewForm.answerContent)
})
const REVIEW_IMAGE_MARKER = '[REVIEW_IMAGE]'
const TEACHER_REASON_START = '[TEACHER_REASON]'
const TEACHER_REASON_END = '[/TEACHER_REASON]'
const STUDENT_RESULT_START = '[STUDENT_RESULT]'
const STUDENT_RESULT_END = '[/STUDENT_RESULT]'
const aiImageGrading = ref(false)

const filteredChatContacts = computed(() => {
  const keyword = String(chatKeyword.value || '').trim().toLowerCase()
  if (!keyword) return chatContacts.value
  return (chatContacts.value || []).filter((item) => {
    const name = String(item?.nick_name || item?.user_name || item?.user_id || '').toLowerCase()
    return name.includes(keyword)
  })
})

const filteredChatGroups = computed(() => {
  const keyword = String(chatKeyword.value || '').trim().toLowerCase()
  if (!keyword) return chatGroups.value
  return (chatGroups.value || []).filter((item) => {
    const name = String(item?.groupName || item?.group_name || item?.groupId || '').toLowerCase()
    return name.includes(keyword)
  })
})

const activeChatTargetLabel = computed(() => {
  if (activeChatTargetType.value === 'group') {
    const target = (chatGroups.value || []).find((g) => String(g.groupId || g.group_id) === activeChatGroupId.value)
    return target ? String(target.groupName || target.group_name || '班级群聊') : ''
  }
  const peer = (chatContacts.value || []).find((item) => normalizeUserId(item.user_id) === activeChatPeerId.value)
  return peer ? String(peer.nick_name || `用户${peer.user_id}`) : ''
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
  const url = resolveFileUrl(attachment.url)
  window.open(url, '_blank')
}

function resolveFileUrl(url) {
  const value = String(url || '').trim()
  if (!value) return ''
  if (value.startsWith('http')) return value
  if (value.startsWith('//')) return `${window.location.protocol}${value}`
  // 已经包含网关前缀时，不再重复拼接，避免出现 /dev-api/dev-api/...
  if (/^\/(dev-api|prod-api|stage-api)\b/.test(value)) return value
  // AI 批改图由 AI 服务静态目录 /files 提供
  if (/^\/?files\//.test(value)) {
    const normalizedAiPath = value.startsWith('/') ? value : `/${value}`
    return aiBaseApi ? `${aiBaseApi}${normalizedAiPath}` : normalizedAiPath
  }
  const normalizedBase = String(baseApi || '').trim().replace(/\/$/, '')
  const normalizedPath = value.startsWith('/') ? value : `/${value}`
  if (normalizedBase && normalizedPath.startsWith(`${normalizedBase}/`)) {
    return normalizedPath
  }
  return `${normalizedBase}${normalizedPath}`
}

function openReviewImage(rawUrl, scene = 'unknown') {
  const resolved = resolveFileUrl(rawUrl)
  console.info('[Pad][ReviewImage] open', {
    scene,
    rawUrl: String(rawUrl || ''),
    resolvedUrl: resolved
  })
  if (!resolved) {
    ElMessage.warning('批改图地址为空')
    return
  }
  window.open(resolved, '_blank')
}

function extractImageUrl(text) {
  const value = String(text || '')
  const markdownMatch = value.match(/!\[[^\]]*]\(([^)\s]+)\)/i)
  if (markdownMatch && markdownMatch[1]) {
    return resolveFileUrl(markdownMatch[1])
  }
  const plainMatch = value.match(/((https?:\/\/|\/)[^\s]+?\.(png|jpg|jpeg|gif|webp))/i)
  if (plainMatch && plainMatch[1]) {
    return resolveFileUrl(plainMatch[1])
  }
  return ''
}

function extractReviewImageFromFeedback(feedback) {
  const value = String(feedback || '')
  const reviewMarker = value.match(/\[(REVIEW_IMAGE|标注图)\]\(([^)\s]+)\)/i)
  if (reviewMarker?.[2]) return reviewMarker[2]
  const markdownImage = value.match(/!\[[^\]]*]\(([^)\s]+)\)/i)
  if (markdownImage?.[1]) return markdownImage[1]
  const filePath = value.match(/((https?:\/\/|\/)files\/[^\s)\]]+)/i)
  if (filePath?.[1]) return filePath[1]
  return ''
}

function stripReviewImageFromFeedback(feedback) {
  return String(feedback || '')
    .replace(/\n?\[(REVIEW_IMAGE|标注图)\]\(([^)\s]+)\)\s*/ig, '')
    .replace(/\n?!\[[^\]]*]\(([^)\s]+)\)\s*/ig, '')
    .trim()
}

function extractBlock(text, startTag, endTag) {
  const value = String(text || '')
  const start = value.indexOf(startTag)
  if (start < 0) return ''
  const from = start + startTag.length
  const end = value.indexOf(endTag, from)
  if (end < 0) return value.slice(from).trim()
  return value.slice(from, end).trim()
}

function stripBlock(text, startTag, endTag) {
  const value = String(text || '')
  const start = value.indexOf(startTag)
  if (start < 0) return value
  const end = value.indexOf(endTag, start + startTag.length)
  if (end < 0) return value.slice(0, start).trim()
  return `${value.slice(0, start)}${value.slice(end + endTag.length)}`.trim()
}

function extractTeacherReasonFromFeedback(feedback) {
  const reason = extractBlock(feedback, TEACHER_REASON_START, TEACHER_REASON_END)
  if (reason) return reason
  const plain = stripReviewImageFromFeedback(feedback)
  return stripBlock(stripBlock(plain, STUDENT_RESULT_START, STUDENT_RESULT_END), TEACHER_REASON_START, TEACHER_REASON_END)
}

function extractStudentResultFromFeedback(feedback) {
  return extractBlock(feedback, STUDENT_RESULT_START, STUDENT_RESULT_END)
}

function mergeTeacherStudentFeedback(teacherReason, studentResult) {
  const reason = String(teacherReason || '').trim()
  const student = String(studentResult || '').trim()
  const parts = []
  if (reason) parts.push(`${TEACHER_REASON_START}${reason}${TEACHER_REASON_END}`)
  if (student) parts.push(`${STUDENT_RESULT_START}${student}${STUDENT_RESULT_END}`)
  return parts.join('\n')
}

function mergeFeedbackWithReviewImage(feedback, reviewImageUrl) {
  const plain = String(feedback || '').trim()
  if (!reviewImageUrl) return plain
  return `${plain}${plain ? '\n' : ''}${REVIEW_IMAGE_MARKER}(${reviewImageUrl})`
}

function dataUrlToFile(dataUrl, fileName) {
  const parts = String(dataUrl || '').split(',')
  if (parts.length < 2) return null
  const mimeMatch = parts[0].match(/:(.*?);/)
  const mime = mimeMatch?.[1] || 'image/png'
  const byteString = window.atob(parts[1])
  const byteNumbers = new Array(byteString.length)
  for (let i = 0; i < byteString.length; i += 1) {
    byteNumbers[i] = byteString.charCodeAt(i)
  }
  const byteArray = new Uint8Array(byteNumbers)
  return new File([byteArray], fileName, { type: mime })
}

async function uploadReviewCanvasImage() {
  if (!reviewCanvas) return ''
  const dataUrl = reviewCanvas.toDataURL('image/png')
  const file = dataUrlToFile(dataUrl, `review-${Date.now()}.png`)
  if (!file) return ''
  const res = await uploadHomeworkAttachment(file)
  return String(res?.fileName || res?.url || '').trim()
}

async function fetchImageAsFile(imageUrl) {
  const url = resolveFileUrl(imageUrl)
  if (!url) return null
  const token = getToken()
  const headers = token ? { Authorization: `Bearer ${token}` } : {}
  const resp = await fetch(url, { headers })
  if (!resp.ok) throw new Error(`读取作答图片失败: ${resp.status}`)
  const contentType = String(resp.headers.get('content-type') || '').toLowerCase()
  if (!contentType.startsWith('image/')) {
    throw new Error(`读取到的内容不是图片：${contentType || 'unknown'}`)
  }
  const blob = await resp.blob()
  if (!blob || blob.size <= 0) {
    throw new Error('读取到空图片内容')
  }
  const ext = blob.type?.includes('png') ? 'png' : 'jpg'
  return new File([blob], `student-answer-${Date.now()}.${ext}`, { type: blob.type || 'image/jpeg' })
}

async function handleAiImageGrade() {
  const imageUrl = reviewAnswerImageUrl.value
  if (!imageUrl) {
    ElMessage.warning('未检测到学生作答图片，无法进行图像AI批改')
    return
  }
  aiImageGrading.value = true
  try {
    const studentFile = await fetchImageAsFile(imageUrl)
    if (!studentFile) {
      ElMessage.warning('作答图片读取失败')
      return
    }
    const res = await aiGradeSingle({
      file: studentFile,
      rubric: reviewForm.exampleFeedback || reviewForm.exampleAnswer || '',
      maxScore: reviewForm.maxScore || 100
    })
    const teacherFeedback = String(res?.teacherFeedback || res?.feedback || '').trim()
    const studentFeedback = String(res?.studentFeedback || '').trim()
    reviewForm.feedback = teacherFeedback
    reviewForm.studentResultText = studentFeedback
    reviewForm.score = Number(res?.score ?? reviewForm.score)
    reviewForm.reviewImageUrl = String(res?.annotatedImageUrl || '').trim()
    if (reviewForm.reviewImageUrl) {
      reviewImageUrl.value = resolveFileUrl(reviewForm.reviewImageUrl)
      loadReviewCanvasImage(reviewImageUrl.value)
    }
    ElMessage.success('AI图像批改完成，已生成对错标注和错因')
  } catch (error) {
    ElMessage.error(error?.message || 'AI图像批改失败')
  } finally {
    aiImageGrading.value = false
  }
}

async function handleAiSuggestReview() {
  const targetAnswer = String(reviewForm.answerContent || '').trim()
  if (!targetAnswer) {
    ElMessage.warning('请先填写学生作答内容')
    return
  }
  const res = await aiSuggestReview({
    exampleAnswer: reviewForm.exampleAnswer,
    exampleScore: reviewForm.exampleScore,
    exampleFeedback: reviewForm.exampleFeedback,
    targetAnswer,
    maxScore: reviewForm.maxScore || 100
  })
  reviewForm.score = Number(res.suggestedScore ?? reviewForm.score)
  reviewForm.feedback = res.suggestedFeedback || reviewForm.feedback
  ElMessage.success(`已生成 AI 建议，相似度 ${Number(res.similarity || 0).toFixed(2)}`)
}

function initReviewCanvas() {
  reviewCanvas = reviewCanvasRef.value
  if (!reviewCanvas) return
  reviewCanvasCtx = reviewCanvas.getContext('2d')
  drawReviewCanvas()
}

function drawReviewCanvas() {
  if (!reviewCanvas || !reviewCanvasCtx) return
  reviewCanvasCtx.clearRect(0, 0, reviewCanvas.width, reviewCanvas.height)
  reviewCanvasCtx.fillStyle = '#f8fafc'
  reviewCanvasCtx.fillRect(0, 0, reviewCanvas.width, reviewCanvas.height)
  if (reviewCanvasImage) {
    reviewCanvasCtx.drawImage(reviewCanvasImage, 0, 0, reviewCanvas.width, reviewCanvas.height)
  } else {
    reviewCanvasCtx.fillStyle = '#64748b'
    reviewCanvasCtx.font = '16px sans-serif'
    reviewCanvasCtx.fillText('未加载作答图片，可上传图片后进行勾叉批注。', 24, 36)
  }
  for (const mark of reviewCanvasMarks.value) {
    drawReviewMark(mark)
  }
}

function drawReviewMark(mark) {
  if (!reviewCanvasCtx) return
  const { x, y, type, text } = mark
  reviewCanvasCtx.lineWidth = 3
  if (type === 'check') {
    reviewCanvasCtx.strokeStyle = '#16a34a'
    reviewCanvasCtx.beginPath()
    reviewCanvasCtx.moveTo(x - 10, y)
    reviewCanvasCtx.lineTo(x - 2, y + 10)
    reviewCanvasCtx.lineTo(x + 14, y - 10)
    reviewCanvasCtx.stroke()
    return
  }
  if (type === 'cross') {
    reviewCanvasCtx.strokeStyle = '#dc2626'
    reviewCanvasCtx.beginPath()
    reviewCanvasCtx.moveTo(x - 10, y - 10)
    reviewCanvasCtx.lineTo(x + 10, y + 10)
    reviewCanvasCtx.moveTo(x + 10, y - 10)
    reviewCanvasCtx.lineTo(x - 10, y + 10)
    reviewCanvasCtx.stroke()
    return
  }
  reviewCanvasCtx.fillStyle = '#0f172a'
  reviewCanvasCtx.font = '16px sans-serif'
  reviewCanvasCtx.fillText(text || '批注', x, y)
}

function onReviewCanvasClick(event) {
  if (!reviewCanvas) return
  const rect = reviewCanvas.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  if (reviewCanvasTool.value === 'text') {
    const text = window.prompt('输入批注文字')
    if (!text) return
    reviewCanvasMarks.value.push({ type: 'text', x, y, text })
  } else {
    reviewCanvasMarks.value.push({ type: reviewCanvasTool.value, x, y })
  }
  drawReviewCanvas()
}

function clearReviewCanvasMarks() {
  reviewCanvasMarks.value = []
  drawReviewCanvas()
}

function exportReviewCanvas() {
  if (!reviewCanvas) return
  const link = document.createElement('a')
  link.download = `review-${Date.now()}.png`
  link.href = reviewCanvas.toDataURL('image/png')
  link.click()
}

function loadReviewCanvasImage(url) {
  if (!url) return
  const image = new Image()
  image.crossOrigin = 'anonymous'
  image.onload = () => {
    reviewCanvasImage = image
    drawReviewCanvas()
  }
  image.onerror = () => {
    reviewCanvasImage = null
    drawReviewCanvas()
  }
  image.src = url
}

function handleReviewImageUpload(event) {
  const file = event?.target?.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    reviewImageUrl.value = String(reader.result || '')
    loadReviewCanvasImage(reviewImageUrl.value)
  }
  reader.readAsDataURL(file)
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
  reviewType.value = 'homework'
  reviewForm.submissionId = row.submission_id
  reviewForm.scoreId = ''
  reviewForm.examId = ''
  reviewForm.studentId = row.student_id
  reviewForm.studentName = row.student_name || ''
  reviewForm.title = row.homework_title || ''
  reviewForm.answerContent = row.answer_content || ''
  reviewForm.score = Number(row.score ?? 0)
  reviewForm.maxScore = 100
  reviewForm.feedback = extractTeacherReasonFromFeedback(row.feedback || '')
  reviewForm.studentResultText = extractStudentResultFromFeedback(row.feedback || '')
  reviewForm.reviewImageUrl = extractReviewImageFromFeedback(row.feedback || '')
  reviewForm.exampleAnswer = row.answer_content || ''
  reviewForm.exampleScore = Number(row.score ?? 85)
  reviewForm.exampleFeedback = extractTeacherReasonFromFeedback(row.feedback || '')
  openReviewDialogWithAnswer()
}

async function loadStudentSubmissions() {
  const res = await listStudentHomeworkSubmissions()
  studentSubmissions.value = res.data || []
}

function openSubmit(row) {
  submitForm.homeworkId = row.homeworkId
  submitForm.answerContent = ''
  submitForm.answerImageUrl = ''
  submitDialog.value = true
}

function buildAnswerContentWithImage(textValue, imageValue) {
  const text = String(textValue || '').trim()
  const imageUrl = String(imageValue || '').split(',')[0]
  if (!imageUrl) return text
  if (!text) return `![作答图片](${imageUrl})`
  return `${text}\n![作答图片](${imageUrl})`
}

async function handleSubmitHomework() {
  const answerContent = buildAnswerContentWithImage(submitForm.answerContent, submitForm.answerImageUrl)
  console.info('[Pad][Homework] submit-start', {
    homeworkId: submitForm.homeworkId,
    answerTextLength: String(submitForm.answerContent || '').length,
    answerImageUrl: submitForm.answerImageUrl,
    payloadLength: String(answerContent || '').length
  })
  if (!answerContent) {
    ElMessage.warning('请填写作答内容或上传作答图片')
    return
  }
  try {
    const res = await submitHomework(submitForm.homeworkId, { answerContent })
    console.info('[Pad][Homework] submit-success', {
      homeworkId: submitForm.homeworkId,
      response: res
    })
    ElMessage.success('作业提交成功')
    submitDialog.value = false
    loadStudentSubmissions()
  } catch (error) {
    console.error('[Pad][Homework] submit-failed', {
      homeworkId: submitForm.homeworkId,
      answerImageUrl: submitForm.answerImageUrl,
      error
    })
    ElMessage.error(error?.message || '作业提交失败，请稍后重试')
  }
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

async function loadTeacherExamScores() {
  const res = await listTeacherExamScore()
  teacherExamScores.value = res.data || []
}

function openExamReview(row) {
  reviewType.value = 'exam'
  reviewForm.submissionId = ''
  reviewForm.scoreId = row.score_id
  reviewForm.examId = row.exam_id
  reviewForm.studentId = row.student_id
  reviewForm.studentName = row.student_name || ''
  reviewForm.title = row.exam_title || ''
  reviewForm.answerContent = row.remark || ''
  reviewForm.maxScore = Number(row.total_score || 100)
  reviewForm.score = Number(row.score ?? 0)
  reviewForm.feedback = ''
  reviewForm.studentResultText = ''
  reviewForm.reviewImageUrl = ''
  reviewForm.exampleAnswer = row.remark || ''
  reviewForm.exampleScore = Number(row.score ?? Math.min(85, reviewForm.maxScore))
  reviewForm.exampleFeedback = ''
  openReviewDialogWithAnswer()
}

function openReviewDialogWithAnswer() {
  reviewDialog.value = true
  reviewCanvasMarks.value = []
  reviewImageUrl.value = ''
  reviewCanvasImage = null
  const reviewedImageUrl = resolveFileUrl(reviewForm.reviewImageUrl)
  const answerImageUrl = extractImageUrl(reviewForm.answerContent)
  const maybeImageUrl = reviewedImageUrl || answerImageUrl
  console.info('[Pad][Review] open-dialog', {
    type: reviewType.value,
    submissionId: reviewForm.submissionId,
    scoreId: reviewForm.scoreId,
    storedReviewImage: reviewForm.reviewImageUrl,
    reviewedImageUrl,
    answerImageUrl,
    baseCanvasImage: maybeImageUrl
  })
  nextTick(() => {
    initReviewCanvas()
    if (maybeImageUrl) {
      loadReviewCanvasImage(maybeImageUrl)
    } else {
      drawReviewCanvas()
    }
  })
}

async function handleSubmitReview() {
  if (reviewType.value === 'homework') {
    if (!reviewForm.submissionId) {
      ElMessage.warning('提交记录不能为空')
      return
    }
    const hasCanvasDrawMarks = reviewCanvasMarks.value.length > 0
    const hasLocalCanvasImage = String(reviewImageUrl.value || '').startsWith('data:image/')
    let uploadedReviewImageUrl = String(reviewForm.reviewImageUrl || '').trim()
    if ((hasCanvasDrawMarks || hasLocalCanvasImage) && reviewCanvas) {
      uploadedReviewImageUrl = await uploadReviewCanvasImage()
    }
    const roleSeparatedFeedback = mergeTeacherStudentFeedback(reviewForm.feedback, reviewForm.studentResultText)
    const mergedFeedback = mergeFeedbackWithReviewImage(roleSeparatedFeedback, uploadedReviewImageUrl)
    console.info('[Pad][Review] submit-homework', {
      submissionId: reviewForm.submissionId,
      score: reviewForm.score,
      hasCanvasDrawMarks,
      hasLocalCanvasImage,
      uploadedReviewImageUrl,
      mergedFeedbackLength: String(mergedFeedback || '').length
    })
    await scoreHomeworkApi({
      submissionId: reviewForm.submissionId,
      score: reviewForm.score,
      feedback: mergedFeedback
    })
    ElMessage.success('作业批改成功')
    reviewDialog.value = false
    await loadTeacherHomeworkSubmissions()
    await loadChatData()
    return
  }
  if (!reviewForm.examId || !reviewForm.studentId) {
    ElMessage.warning('考试作答记录不完整')
    return
  }
  const remark = reviewForm.feedback
    ? `作答：${reviewForm.answerContent}\n评语：${reviewForm.feedback}`
    : reviewForm.answerContent
  await scoreExam({
    examId: reviewForm.examId,
    studentId: reviewForm.studentId,
    studentName: reviewForm.studentName,
    score: reviewForm.score,
    remark
  })
  ElMessage.success('考试批改成功')
  reviewDialog.value = false
  await loadTeacherExamScores()
}

async function loadStudentExamScore() {
  const res = await listStudentExamScore()
  studentExamScores.value = res.data || []
}

async function loadStudentExamList() {
  const res = await listStudentExamApi()
  studentExams.value = res.data || []
}

async function refreshStudentExamMerged() {
  await Promise.all([loadStudentExamList(), loadStudentExamScore(), loadStudentSelfScores()])
}

function openExamSubmit(row) {
  examSubmitForm.examId = row.examId
  examSubmitForm.examTitle = row.title
  examSubmitForm.answerContent = ''
  examSubmitForm.answerImageUrl = ''
  examSubmitDialog.value = true
}

async function handleSubmitExam() {
  const answerContent = buildAnswerContentWithImage(examSubmitForm.answerContent, examSubmitForm.answerImageUrl)
  if (!examSubmitForm.examId || !answerContent) {
    ElMessage.warning('请填写作答内容或上传作答图片')
    return
  }
  await submitExam(examSubmitForm.examId, { answerContent })
  ElMessage.success('考试作答已提交')
  examSubmitDialog.value = false
  await refreshStudentExamMerged()
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
  if (name === 'score') {
    await loadTeacherExamScores()
  }
  if (name === 'visual') {
    await refreshTeacherVisual()
  }
  if (name === 'message') {
    await loadChatData()
  }
}

async function handleStudentTabChange(name) {
  if (name === 'exam') {
    await refreshStudentExamMerged()
  }
  if (name === 'visual') {
    await refreshStudentVisual()
  }
  if (name === 'message') {
    await loadChatData()
  }
}

function applyTabFromQuery() {
  const studentTab = String(route.query.studentTab || '').trim()
  if (isStudent.value && ['homework', 'exam', 'visual', 'message'].includes(studentTab)) {
    studentActiveTab.value = studentTab
  }
  const teacherTab = String(route.query.teacherTab || '').trim()
  if (isTeacher.value && ['publish', 'review', 'score', 'task', 'studentScore', 'visual', 'message'].includes(teacherTab)) {
    teacherActiveTab.value = teacherTab
  }
}

function normalizeUserId(value) {
  return String(value === null || value === undefined ? '' : value)
}

function isSelfChatMessage(item) {
  return Number(item?.sender_id || item?.senderId || 0) === Number(userStore.id || 0)
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
    chatGroups.value = []
    activeChatPeerId.value = ''
    activeChatGroupId.value = ''
    chatMessages.value = []
    chatContactCount.value = 0
    activeChatTargetType.value = 'dm'
    return
  }
  try {
    chatListLoading.value = true
    const [contactRes, groupRes] = await Promise.all([listChatContacts(), listChatGroups()])
    chatContacts.value = contactRes.data || []
    chatGroups.value = groupRes.data || []
    chatContactCount.value = chatContacts.value.length
    const dmExists = chatContacts.value.some(item => normalizeUserId(item.user_id) === activeChatPeerId.value)
    const gpExists = chatGroups.value.some(item => String(item.groupId || item.group_id) === activeChatGroupId.value)
    if (!dmExists) {
      activeChatPeerId.value = chatContacts.value.length ? normalizeUserId(chatContacts.value[0].user_id) : ''
    }
    if (!gpExists) {
      activeChatGroupId.value = chatGroups.value.length ? String(chatGroups.value[0].groupId || chatGroups.value[0].group_id) : ''
    }
    if (chatMode.value === 'group' && activeChatGroupId.value) {
      activeChatTargetType.value = 'group'
    } else if (activeChatPeerId.value) {
      activeChatTargetType.value = 'dm'
    } else if (activeChatGroupId.value) {
      activeChatTargetType.value = 'group'
    }
    await loadChatMessageList()
  } catch (error) {
    chatContacts.value = []
    chatGroups.value = []
    activeChatPeerId.value = ''
    activeChatGroupId.value = ''
    chatMessages.value = []
    chatContactCount.value = 0
    ElMessage.error('加载联系人失败')
  } finally {
    chatListLoading.value = false
  }
}

function handleChatModeChange(mode) {
  if (mode === 'group') {
    activeChatTargetType.value = 'group'
    if (!activeChatGroupId.value && chatGroups.value.length) {
      activeChatGroupId.value = String(chatGroups.value[0].groupId || chatGroups.value[0].group_id)
    }
  } else {
    activeChatTargetType.value = 'dm'
    if (!activeChatPeerId.value && chatContacts.value.length) {
      activeChatPeerId.value = normalizeUserId(chatContacts.value[0].user_id)
    }
  }
  loadChatMessageList()
}

async function selectChatContact(contact) {
  const peerId = normalizeUserId(contact?.user_id)
  if (!peerId) return
  activeChatPeerId.value = peerId
  activeChatTargetType.value = 'dm'
  chatMode.value = 'dm'
  await loadChatMessageList()
}

async function selectChatGroup(group) {
  const groupId = String(group?.groupId || group?.group_id || '')
  if (!groupId) return
  activeChatGroupId.value = groupId
  activeChatTargetType.value = 'group'
  chatMode.value = 'group'
  await loadChatMessageList()
}

async function loadChatMessageList() {
  if (activeChatTargetType.value === 'group' && !activeChatGroupId.value) {
    chatMessages.value = []
    return
  }
  if (activeChatTargetType.value !== 'group' && !activeChatPeerId.value) {
    chatMessages.value = []
    return
  }
  chatListLoading.value = true
  try {
    const res = activeChatTargetType.value === 'group'
      ? await listGroupChatMessages(activeChatGroupId.value)
      : await listChatMessages(activeChatPeerId.value)
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
  if (!activeChatTargetLabel.value) {
    ElMessage.warning('请先选择会话')
    return
  }
  if (!content) {
    ElMessage.warning('请输入消息内容')
    return
  }
  chatSending.value = true
  try {
    if (activeChatTargetType.value === 'group') {
      await sendGroupChatMessage({
        groupId: activeChatGroupId.value,
        content
      })
    } else {
      await sendChatMessage({
        peerUserId: Number(activeChatPeerId.value),
        content
      })
    }
    chatInput.value = ''
    await loadChatMessageList()
  } catch (error) {
    ElMessage.error(error?.message || '发送消息失败')
  } finally {
    chatSending.value = false
  }
}

function openPrivateFromGroup(message) {
  const senderId = normalizeUserId(message?.sender_id || message?.senderId)
  if (!senderId || senderId === String(userStore.id || '')) return
  const target = (chatContacts.value || []).find((item) => normalizeUserId(item.user_id) === senderId)
  if (!target) return
  selectChatContact(target)
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
  applyTabFromQuery()
  if (isTeacher.value) {
    loadTeacherHomework()
    loadTeacherHomeworkSubmissions()
    loadTeacherExam()
    loadTeacherExamScores()
    loadTeacherTasks()
    loadTeacherScores()
    loadChatData()
  }
  if (isStudent.value) {
    loadStudentHomework()
    loadStudentSubmissions()
    refreshStudentExamMerged()
    loadChatData()
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
.chat-header-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.chat-layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 12px;
  min-height: 480px;
}
.chat-contact-pane {
  border: 1px solid #d7e7f3;
  border-radius: 10px;
  padding: 10px;
  overflow-y: auto;
  max-height: 560px;
  background: #f8fcff;
}
.chat-mode-bar {
  margin-bottom: 8px;
}
.chat-search-input {
  margin-bottom: 8px;
}
.chat-contact-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.chat-contact-item:hover {
  background: #edf7ff;
}
.chat-contact-item.active {
  background: #e3f1ff;
  border: 1px solid #b8d8f4;
}
.chat-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #265d7f;
  background: linear-gradient(145deg, #e6f4ff 0%, #d7ecff 100%);
}
.chat-contact-text strong {
  display: block;
  color: #1f3346;
  font-size: 14px;
}
.chat-contact-text span {
  display: block;
  margin-top: 2px;
  color: #6a879d;
  font-size: 12px;
}
.chat-main-pane {
  border: 1px solid #d7e7f3;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  background: #f6fbff;
}
.chat-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #69859b;
}
.chat-message-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  min-height: 300px;
}
.chat-main-top {
  padding: 10px 12px;
  border-bottom: 1px solid #d7e7f3;
  color: #35566e;
  font-weight: 600;
  background: #f9fcff;
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
  background: #fff;
  border: 1px solid #dbe8f4;
  border-radius: 12px;
  padding: 8px 10px;
}
.chat-message-row.self .chat-bubble {
  background: #dff0ff;
  border-color: #b9d9f5;
}
.chat-bubble p {
  margin: 0;
  white-space: pre-wrap;
  color: #243c52;
  line-height: 1.45;
}
.chat-sender-name {
  display: inline-block;
  margin-bottom: 4px;
  color: #1884d8;
  cursor: pointer;
}
.chat-bubble span {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #6b879d;
}
.chat-editor {
  border-top: 1px solid #d7e7f3;
  padding: 10px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 86px;
  gap: 10px;
  align-items: end;
  background: #fff;
  border-radius: 0 0 10px 10px;
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
.review-canvas-panel {
  margin-top: 8px;
  border: 1px solid #dbe2ea;
  border-radius: 10px;
  background: #ffffff;
}
.review-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-bottom: 1px solid #e5eaf3;
}
.review-canvas-wrap {
  padding: 12px;
}
.review-canvas {
  width: 100%;
  max-width: 100%;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  background: #f8fafc;
  cursor: crosshair;
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
  .chat-layout {
    grid-template-columns: 1fr;
  }
  .chat-contact-pane {
    max-height: 220px;
  }
}
</style>
