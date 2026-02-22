<template>
  <div class="rag-shell">
    <aside class="kb-sidebar">
      <div class="kb-header">
        <div>
          <h2>知识库</h2>
          <p>已上传文件</p>
        </div>
        <el-button text @click="refreshHistory" :loading="loadingHistory">刷新</el-button>
      </div>

      <el-scrollbar class="kb-list">
        <div v-if="historyDatasets.length === 0" class="kb-empty">
          <el-empty description="暂无数据集" :image-size="72" />
        </div>

        <div
          v-for="(dataset, index) in historyDatasets"
          :key="datasetKey(dataset, index)"
          class="kb-item"
        >
          <div class="kb-item-main">
            <div class="kb-name" :title="datasetName(dataset)">{{ datasetName(dataset) }}</div>
            <div class="kb-time">{{ formatTime(datasetTime(dataset)) }}</div>
          </div>
          <div class="kb-actions">
            <el-button text size="small" @click="viewDataset(dataset)">查看</el-button>
            <el-button text size="small" type="danger" @click="handleDeleteDataset(dataset)">删除</el-button>
          </div>
        </div>
      </el-scrollbar>
    </aside>

    <section class="chat-panel">
      <header class="chat-topbar">
        <div class="chat-title-wrap">
          <h1>AI 助手</h1>
          <span>RAG 问答</span>
        </div>

        <div class="upload-inline">
          <el-upload
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            accept=".xlsx,.xls,.txt"
            multiple
            :limit="5"
          >
            <el-button size="small" plain>选择文件</el-button>
          </el-upload>
          <span class="selected-files">{{ selectedFilesText }}</span>
          <el-button
            size="small"
            type="primary"
            :loading="uploadLoading"
            :disabled="!fileList.length || uploadLoading"
            @click="submitUpload"
          >
            上传
          </el-button>
        </div>
      </header>

      <main class="chat-stream" ref="chatContainer">
        <div v-if="messages.length === 0" class="chat-empty">
          <el-empty description="开始提问吧" :image-size="90" />
        </div>

        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['chat-row', message.type === 'user' ? 'is-user' : 'is-ai']"
        >
          <div class="chat-bubble">{{ message.content }}</div>
        </div>

        <div v-if="queryLoading" class="chat-row is-ai">
          <div class="chat-bubble loading-bubble">
            <el-skeleton :rows="2" animated />
          </div>
        </div>
      </main>

      <footer class="composer">
        <el-input
          v-model="question"
          type="textarea"
          :rows="3"
          resize="none"
          placeholder="输入问题，Enter 发送，Shift+Enter 换行"
          :disabled="queryLoading || uploadLoading"
          @keydown.enter.exact.prevent="submitQuery"
        />

        <div class="composer-actions">
          <span>可直接对话，也可基于上传知识库回答问题</span>
          <div class="composer-buttons">
            <el-button v-if="queryLoading" type="danger" plain @click="abortQuery">中止</el-button>
            <el-button
              type="primary"
              :loading="queryLoading"
              :disabled="!question.trim() || queryLoading || uploadLoading"
              @click="submitQuery"
            >
              发送
            </el-button>
          </div>
        </div>
      </footer>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { uploadExcel, queryQuestion, getDatasets, deleteDataset, getDatasetDetail } from '@/api/education/rag'

const historyDatasets = ref([])
const loadingHistory = ref(false)

const fileList = ref([])
const uploadLoading = ref(false)

const question = ref('')
const messages = ref([])
const queryLoading = ref(false)
const chatContainer = ref(null)
let queryAborted = false

const selectedFilesText = computed(() => {
  if (!fileList.value.length) return '未选择文件'
  if (fileList.value.length === 1) return fileList.value[0].name
  return `已选择 ${fileList.value.length} 个文件`
})

function datasetId(dataset = {}) {
  return dataset.id || dataset.dataset_id || ''
}

function datasetKey(dataset = {}, index = 0) {
  return datasetId(dataset) || `${datasetName(dataset)}-${index}`
}

function datasetName(dataset = {}) {
  return dataset.name || dataset.filename || dataset.dataset_id || '未命名数据集'
}

function datasetTime(dataset = {}) {
  return dataset.upload_time || dataset.created_at || ''
}

const handleFileChange = (file, uploadFiles) => {
  const validFiles = uploadFiles.filter((f) => {
    const name = (f.name || '').toLowerCase()
    return name.endsWith('.xlsx') || name.endsWith('.xls') || name.endsWith('.txt')
  })
  if (validFiles.length !== uploadFiles.length) {
    ElMessage.warning('仅支持 .xlsx / .xls / .txt 文件')
  }
  fileList.value = validFiles.slice(0, 5)
}

const handleExceed = () => {
  ElMessage.warning('最多上传 5 个文件')
}

const submitUpload = async () => {
  if (!fileList.value.length) {
    ElMessage.warning('请先选择文件')
    return
  }

  uploadLoading.value = true
  const successFiles = []
  const failedFiles = []

  try {
    for (const file of fileList.value) {
      try {
        await uploadExcel(file)
        successFiles.push(file.name)
      } catch (error) {
        failedFiles.push(file.name)
      }
    }

    if (successFiles.length) {
      ElMessage.success(`上传成功 ${successFiles.length} 个文件`)
      messages.value.push({
        type: 'ai',
        content: `已导入：${successFiles.join('、')}。现在可以基于这些内容提问。`
      })
      await getHistoryDatasets()
    }

    if (failedFiles.length) {
      ElMessage.warning(`上传失败：${failedFiles.join('、')}`)
      messages.value.push({
        type: 'ai',
        content: `以下文件上传失败：${failedFiles.join('、')}`
      })
    }
  } finally {
    uploadLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

const submitQuery = async () => {
  if (!question.value.trim()) {
    ElMessage.warning('请输入问题')
    return
  }

  const userQuestion = question.value.trim()
  question.value = ''
  messages.value.push({ type: 'user', content: userQuestion })

  await nextTick()
  scrollToBottom()

  queryLoading.value = true
  queryAborted = false

  try {
    const response = await queryQuestion(userQuestion)

    if (queryAborted) return

    const answer = response.answer || response.data || response.msg || '暂无响应'
    messages.value.push({ type: 'ai', content: String(answer) })
  } catch (error) {
    if (queryAborted) {
      messages.value.push({ type: 'ai', content: '查询已中止' })
      return
    }
    ElMessage.error('查询失败，请稍后重试')
    messages.value.push({ type: 'ai', content: '查询失败，请检查 AI 服务。' })
  } finally {
    queryLoading.value = false
    queryAborted = false
    await nextTick()
    scrollToBottom()
  }
}

const abortQuery = () => {
  queryAborted = true
  queryLoading.value = false
  ElMessage.info('已中止本次查询')
}

const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const getHistoryDatasets = async () => {
  loadingHistory.value = true
  try {
    const response = await getDatasets()
    const raw = response.data || response
    historyDatasets.value = raw.datasets || raw.data || raw || []
  } catch (error) {
    ElMessage.error('获取历史数据集失败')
    historyDatasets.value = []
  } finally {
    loadingHistory.value = false
  }
}

const refreshHistory = () => {
  getHistoryDatasets()
}

const handleDeleteDataset = async (dataset) => {
  const id = datasetId(dataset)
  if (!id) {
    ElMessage.warning('当前数据集缺少 ID，无法删除')
    return
  }

  try {
    await ElMessageBox.confirm(`确定删除「${datasetName(dataset)}」吗？`, '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteDataset(id)
    ElMessage.success('删除成功')
    await getHistoryDatasets()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const viewDataset = async (dataset) => {
  const id = datasetId(dataset)
  if (!id) {
    ElMessageBox.alert(
      `文件名: ${datasetName(dataset)}\n上传时间: ${formatTime(datasetTime(dataset))}`,
      '数据集详情',
      { confirmButtonText: '确定' }
    )
    return
  }

  try {
    const response = await getDatasetDetail(id)
    const data = response.data || response
    ElMessageBox.alert(
      `文件名: ${datasetName(dataset)}\n上传时间: ${formatTime(datasetTime(dataset))}\n\n${data.description || '暂无额外信息'}`,
      '数据集详情',
      { confirmButtonText: '确定' }
    )
  } catch (error) {
    ElMessage.error('查看数据集失败')
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return '--'
  const date = new Date(timeStr)
  if (Number.isNaN(date.getTime())) return '--'
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  getHistoryDatasets()
})
</script>

<style scoped>
.rag-shell {
  min-height: 100vh;
  padding: 18px;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 16px;
  background: linear-gradient(180deg, #f6f7f9 0%, #eef1f5 100%);
  color: #1f2937;
}

.kb-sidebar {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 36px);
}

.kb-header {
  padding: 14px;
  border-bottom: 1px solid #eef0f3;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.kb-header h2 {
  margin: 0;
  font-size: 16px;
}

.kb-header p {
  margin: 4px 0 0;
  font-size: 12px;
  color: #6b7280;
}

.kb-list {
  padding: 8px;
  height: calc(100vh - 108px);
}

.kb-item {
  border: 1px solid #eef0f3;
  border-radius: 10px;
  padding: 10px;
  margin-bottom: 8px;
  background: #fff;
}

.kb-item-main {
  min-width: 0;
}

.kb-name {
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.kb-time {
  margin-top: 4px;
  font-size: 12px;
  color: #6b7280;
}

.kb-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}

.kb-empty {
  padding-top: 24px;
}

.chat-panel {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 36px);
  overflow: hidden;
}

.chat-topbar {
  padding: 12px 16px;
  border-bottom: 1px solid #eef0f3;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.chat-title-wrap h1 {
  margin: 0;
  font-size: 18px;
}

.chat-title-wrap span {
  font-size: 12px;
  color: #6b7280;
}

.upload-inline {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.selected-files {
  max-width: 180px;
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-stream {
  flex: 1;
  overflow-y: auto;
  padding: 18px;
  background: #f7f8fa;
}

.chat-empty {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-row {
  display: flex;
  margin-bottom: 12px;
}

.chat-row.is-user {
  justify-content: flex-end;
}

.chat-row.is-ai {
  justify-content: flex-start;
}

.chat-bubble {
  max-width: 80%;
  padding: 10px 12px;
  border-radius: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 14px;
}

.chat-row.is-user .chat-bubble {
  background: #10a37f;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.chat-row.is-ai .chat-bubble {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  color: #111827;
  border-bottom-left-radius: 4px;
}

.loading-bubble {
  width: min(560px, 80%);
}

.composer {
  padding: 12px;
  border-top: 1px solid #eef0f3;
  background: #fff;
}

.composer-actions {
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 12px;
  color: #6b7280;
}

.composer-buttons {
  display: flex;
  gap: 8px;
}

@media (max-width: 960px) {
  .rag-shell {
    grid-template-columns: 1fr;
    padding: 12px;
  }

  .kb-sidebar,
  .chat-panel {
    min-height: auto;
  }

  .kb-list {
    height: 260px;
  }

  .chat-panel {
    min-height: calc(100vh - 330px);
  }

  .selected-files {
    max-width: 120px;
  }
}
</style>
