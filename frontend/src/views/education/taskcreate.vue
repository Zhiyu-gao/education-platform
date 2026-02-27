<template>
  <div class="app-container task-create-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>创建教师任务</span>
          <el-tag type="info" effect="plain">管理者 Pad 端</el-tag>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="taskForm"
        :rules="rules"
        label-width="110px"
        class="task-form"
      >
        <el-form-item label="教师 ID" prop="teacherId">
          <el-input-number v-model="taskForm.teacherId" :min="1" :step="1" controls-position="right" />
        </el-form-item>

        <el-form-item label="任务标题" prop="title">
          <el-input
            v-model.trim="taskForm.title"
            maxlength="64"
            show-word-limit
            placeholder="请输入任务标题"
          />
        </el-form-item>

        <el-form-item label="任务内容" prop="content">
          <el-input
            v-model.trim="taskForm.content"
            type="textarea"
            :rows="5"
            maxlength="500"
            show-word-limit
            placeholder="请输入任务说明、验收标准与截止要求"
          />
        </el-form-item>

        <el-form-item label="任务状态" prop="status">
          <el-select v-model="taskForm.status" placeholder="请选择任务状态">
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="submitForm">发布任务</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { createTeacherTask } from '@/api/education/pad'

const formRef = ref()
const submitting = ref(false)

const statusOptions = [
  { label: '待处理', value: 'TODO' },
  { label: '进行中', value: 'DOING' },
  { label: '已完成', value: 'DONE' }
]

const initialTaskForm = () => ({
  teacherId: undefined,
  title: '',
  content: '',
  status: 'TODO'
})

const taskForm = reactive(initialTaskForm())

const rules = {
  teacherId: [{ required: true, message: '请输入教师 ID', trigger: 'blur' }],
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入任务内容', trigger: 'blur' }],
  status: [{ required: true, message: '请选择任务状态', trigger: 'change' }]
}

async function submitForm() {
  if (!formRef.value || submitting.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await createTeacherTask({
      teacherId: Number(taskForm.teacherId),
      title: taskForm.title,
      content: taskForm.content,
      status: taskForm.status
    })
    ElMessage.success('任务创建成功')
    resetForm()
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  Object.assign(taskForm, initialTaskForm())
  formRef.value?.clearValidate()
}
</script>

<style scoped lang="scss">
.task-create-page {
  max-width: 760px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.task-form {
  padding-top: 8px;
}
</style>
