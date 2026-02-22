<template>
  <div class="prediction-container">
    <!-- 装饰性背景元素 -->
    <div class="bg-decoration bg-decoration-1"></div>
    <div class="bg-decoration bg-decoration-2"></div>
    <div class="bg-decoration bg-decoration-3"></div>
    
    <div class="prediction-header">
      <h2 class="page-title">学生成绩预测系统</h2>
      <p class="page-description">基于深度学习模型，预测学生的学习成绩表现</p>
    </div>

    <el-card class="main-card">
      <!-- 标签页切换 -->
      <el-tabs v-model="activeTab" class="prediction-tabs">
        <!-- 模型训练标签页 -->
        <el-tab-pane label="1. 模型训练" name="train">
          <div class="train-section">
            <el-alert
              title="训练须知"
              type="info"
              :closable="false"
              class="alert-section"
              show-icon
            >
              请上传CSV文件以训练预测模型。文件格式请参照StudentPerformanceFactors.csv，包含必要的学生特征数据。
            </el-alert>
            
            <el-form :model="trainForm" label-width="120px" class="train-form">
              <el-form-item label="CSV文件上传" prop="file">
                <el-upload
                  ref="uploadRef"
                  :auto-upload="false"
                  :on-change="handleFileChange"
                  :file-list="fileList"
                  accept=".csv"
                  class="upload-demo"
                >
                  <el-button type="primary" :icon="upload">选择CSV文件</el-button>
                  <template #tip>
                    <div class="el-upload__tip">
                      请上传CSV格式文件，大小不超过5MB<br>
                      文件格式需包含以下字段：Hours_Studied, Attendance, Parental_Involvement, Access_to_Resources, Extracurricular_Activities, Sleep_Hours, Previous_Scores等
                    </div>
                  </template>
                </el-upload>
              </el-form-item>
              
              <el-form-item>
                <el-button
                  type="primary"
                  :loading="trainingLoading"
                  @click="handleTrainModel"
                  size="large"
                  class="train-button"
                  :disabled="!trainForm.file"
                >
                  <template #loading>
                    <el-icon><Loading /></el-icon> 训练中...
                  </template>
                  <el-icon><Upload /></el-icon> 上传并训练模型
                </el-button>
              </el-form-item>
            </el-form>

            <!-- 训练结果展示 -->
            <div v-if="trainResult" class="train-result">
              <el-divider content-position="left">训练结果</el-divider>
              <div v-if="trainResult.status === 'success'" class="success-result">
                <el-result
                  icon="success"
                  title="模型训练成功"
                  sub-title=""  
                >
                  <template #extra>
                    <el-descriptions border column="2" class="result-details">
                      <el-descriptions-item label="平均绝对误差(MAE)">{{ trainResult?.test_mae?.toFixed(4) }}</el-descriptions-item>
                      <el-descriptions-item label="测试损失(Loss)">{{ trainResult?.test_loss?.toFixed(4) }}</el-descriptions-item>
                      <el-descriptions-item label="特征数量">{{ trainResult?.feature_count }}</el-descriptions-item>
                      <el-descriptions-item label="模型状态">训练完成</el-descriptions-item>
                    </el-descriptions>
                    
                    <el-collapse class="feature-collapse">
                      <el-collapse-item title="查看所有特征" name="1">
                        <div class="feature-list">
                          <el-tag 
                            v-for="(feature, index) in trainResult?.feature_names" 
                            :key="index" 
                            class="feature-tag"
                            effect="plain"
                            type="info"
                          >
                            {{ feature }}
                          </el-tag>
                        </div>
                      </el-collapse-item>
                    </el-collapse>
                  </template>
                </el-result>
              </div>
              
              <div v-else class="error-result">
                <el-result
                  icon="error"
                  title="模型训练失败"
                  :sub-title="trainResult.message || '请检查文件路径是否正确'"
                />
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 模型信息标签页 -->
        <el-tab-pane label="2. 模型信息" name="info">
          <div class="info-section">
            <el-button
                  type="primary"
                  :loading="modelInfoLoading"
                  @click="fetchModelInfo"
                  size="large"
                  class="info-button"
                  :icon="modelInfoLoading ? '' : 'el-icon-document-checked'"
                >
                  <template #loading>
                    <el-icon><Loading /></el-icon> 获取中...
                  </template>
                  获取模型信息
                </el-button>
            
            <div v-if="modelInfo" class="model-info-result">
              <el-divider content-position="left">模型详细信息</el-divider>
              <div v-if="modelInfo.status === 'success'" class="success-info">
                <el-card class="model-card">
                  <template #header>
                    <div class="card-header">
                      <span>神经网络结构</span>
                    </div>
                  </template>
                  <div class="model-layers">
                    <div 
                      v-for="(layer, index) in modelInfo?.model_info?.layers" 
                      :key="index" 
                      class="model-layer"
                    >
                      <el-card :body-style="{ padding: '15px' }" class="layer-card">
                        <el-descriptions :column="3" :border="false">
                          <el-descriptions-item label="层名称">{{ layer.name }}</el-descriptions-item>
                          <el-descriptions-item label="神经元数量">{{ layer.units }}</el-descriptions-item>
                          <el-descriptions-item label="激活函数">{{ layer.activation }}</el-descriptions-item>
                        </el-descriptions>
                      </el-card>
                    </div>
                  </div>
                </el-card>
                
                <el-card class="feature-card">
                  <template #header>
                    <div class="card-header">
                      <span>分类特征列表</span>
                    </div>
                  </template>
                  <div class="categorical-features">
                    <el-tag 
                      v-for="(feature, index) in modelInfo?.model_info?.categorical_features" 
                      :key="index" 
                      class="feature-tag"
                      effect="plain"
                      type="success"
                    >
                      {{ feature }}
                    </el-tag>
                  </div>
                </el-card>
              </div>
              
              <div v-else class="error-info">
                <el-result
                  icon="error"
                  title="获取模型信息失败"
                  :sub-title="modelInfo.message || '请确保模型已成功训练'"
                />
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 成绩预测标签页 -->
        <el-tab-pane label="3. 成绩预测" name="predict">
          <div class="predict-section">
            <el-alert
              title="预测说明"
              type="info"
              :closable="false"
              class="alert-section"
              show-icon
            >
              请填写学生相关信息，系统将预测其可能的学习成绩。
              <br>
              <span style="color: #0f766e; font-weight: 600;">当前表单已填充基于 StudentPerformanceFactors.csv 的示例数据</span>
            </el-alert>
            
            <el-form :model="predictForm" label-width="180px" class="predict-form">
              <!-- 数值类型输入 -->
              <el-form-item label="学习时长(小时)" prop="Hours_Studied">
                <el-input-number
                  v-model="predictForm.input_data.Hours_Studied"
                  :min="0"
                  :max="100"
                  :step="1"
                  class="number-input"
                />
              </el-form-item>
              
              <el-form-item label="出勤率(%)" prop="Attendance">
                <el-input-number
                  v-model="predictForm.input_data.Attendance"
                  :min="0"
                  :max="100"
                  :step="1"
                  class="number-input"
                />
              </el-form-item>
              
              <el-form-item label="睡眠时长(小时)" prop="Sleep_Hours">
                <el-input-number
                  v-model="predictForm.input_data.Sleep_Hours"
                  :min="0"
                  :max="24"
                  :step="0.5"
                  class="number-input"
                />
              </el-form-item>
              
              <el-form-item label="以往成绩" prop="Previous_Scores">
                <el-input-number
                  v-model="predictForm.input_data.Previous_Scores"
                  :min="0"
                  :max="100"
                  :step="1"
                  class="number-input"
                />
              </el-form-item>
              
              <el-form-item label="辅导次数" prop="Tutoring_Sessions">
                <el-input-number
                  v-model="predictForm.input_data.Tutoring_Sessions"
                  :min="0"
                  :max="50"
                  :step="1"
                  class="number-input"
                />
              </el-form-item>
              
              <el-form-item label="体育活动(小时/周)" prop="Physical_Activity">
                <el-input-number
                  v-model="predictForm.input_data.Physical_Activity"
                  :min="0"
                  :max="40"
                  :step="0.5"
                  class="number-input"
                />
              </el-form-item>
              
              <!-- 下拉选择类型 -->
              <el-form-item label="家长参与度" prop="Parental_Involvement">
                <el-select
                  v-model="predictForm.input_data.Parental_Involvement"
                  placeholder="请选择"
                  class="select-input"
                >
                  <el-option label="低" value="Low" />
                  <el-option label="中" value="Medium" />
                  <el-option label="高" value="High" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="资源获取" prop="Access_to_Resources">
                <el-select
                  v-model="predictForm.input_data.Access_to_Resources"
                  placeholder="请选择"
                  class="select-input"
                >
                  <el-option label="低" value="Low" />
                  <el-option label="中" value="Medium" />
                  <el-option label="高" value="High" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="课外活动" prop="Extracurricular_Activities">
                <el-radio-group v-model="predictForm.input_data.Extracurricular_Activities" class="radio-group">
                  <el-radio label="Yes">是</el-radio>
                  <el-radio label="No">否</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="学习动力" prop="Motivation_Level">
                <el-select
                  v-model="predictForm.input_data.Motivation_Level"
                  placeholder="请选择"
                  class="select-input"
                >
                  <el-option label="低" value="Low" />
                  <el-option label="中" value="Medium" />
                  <el-option label="高" value="High" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="互联网访问" prop="Internet_Access">
                <el-radio-group v-model="predictForm.input_data.Internet_Access" class="radio-group">
                  <el-radio label="Yes">是</el-radio>
                  <el-radio label="No">否</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="家庭收入" prop="Family_Income">
                <el-select
                  v-model="predictForm.input_data.Family_Income"
                  placeholder="请选择"
                  class="select-input"
                >
                  <el-option label="低" value="Low" />
                  <el-option label="中" value="Medium" />
                  <el-option label="高" value="High" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="教师质量" prop="Teacher_Quality">
                <el-select
                  v-model="predictForm.input_data.Teacher_Quality"
                  placeholder="请选择"
                  class="select-input"
                >
                  <el-option label="低" value="Low" />
                  <el-option label="中" value="Medium" />
                  <el-option label="高" value="High" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="学校类型" prop="School_Type">
                <el-select
                  v-model="predictForm.input_data.School_Type"
                  placeholder="请选择"
                  class="select-input"
                >
                  <el-option label="公立" value="Public" />
                  <el-option label="私立" value="Private" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="同伴影响" prop="Peer_Influence">
                <el-select
                  v-model="predictForm.input_data.Peer_Influence"
                  placeholder="请选择"
                  class="select-input"
                >
                  <el-option label="积极" value="Positive" />
                  <el-option label="中性" value="Neutral" />
                  <el-option label="消极" value="Negative" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="学习障碍" prop="Learning_Disabilities">
                <el-radio-group v-model="predictForm.input_data.Learning_Disabilities" class="radio-group">
                  <el-radio label="Yes">是</el-radio>
                  <el-radio label="No">否</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="家长教育水平" prop="Parental_Education_Level">
                <el-select
                  v-model="predictForm.input_data.Parental_Education_Level"
                  placeholder="请选择"
                  class="select-input"
                >
                  <el-option label="高中" value="High School" />
                  <el-option label="学士" value="Bachelor's" />
                  <el-option label="硕士" value="Master's" />
                  <el-option label="博士" value="PhD" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="家到学校距离" prop="Distance_from_Home">
                <el-select
                  v-model="predictForm.input_data.Distance_from_Home"
                  placeholder="请选择"
                  class="select-input"
                >
                  <el-option label="近" value="Near" />
                  <el-option label="中等" value="Medium" />
                  <el-option label="远" value="Far" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="性别" prop="Gender">
                <el-select
                  v-model="predictForm.input_data.Gender"
                  placeholder="请选择"
                  class="select-input"
                >
                  <el-option label="男" value="Male" />
                  <el-option label="女" value="Female" />
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button
                  type="primary"
                  :loading="predictLoading"
                  @click="handlePredictScore"
                  size="large"
                  class="predict-button"
                  :icon="predictLoading ? '' : 'el-icon-calculator'"
                >
                  <template #loading>
                    <el-icon><Loading /></el-icon> 预测中...
                  </template>
                  预测成绩
                </el-button>
              </el-form-item>
            </el-form>

            <!-- 预测结果展示 -->
            <div v-if="predictResult" class="predict-result">
              <el-divider content-position="left">预测结果</el-divider>
              <div v-if="predictResult.status === 'success'" class="success-predict">
                <el-result
                  icon="success"
                  :title="`预测成绩: ${predictResult?.predicted_score?.toFixed(2)}`"
                  :sub-title="predictResult.message"
                >
                  <template #extra>
                    <el-card class="score-card">
                      <div class="score-display">
                        <div class="score-circle">
                          <div class="score-value">{{ predictResult?.predicted_score?.toFixed(0) }}</div>
                        </div>
                        <div class="score-assessment">
                          <el-tag :type="getScoreLevel(predictResult?.predicted_score)" size="large">
                            {{ getScoreDescription(predictResult?.predicted_score) }}
                          </el-tag>
                        </div>
                      </div>
                    </el-card>
                  </template>
                </el-result>
              </div>
              
              <div v-else class="error-predict">
                <el-result
                  icon="error"
                  title="预测失败"
                  :sub-title="predictResult.message || '请检查输入数据是否完整'"
                />
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Upload } from '@element-plus/icons-vue'
import { trainPredictionModel, getModelInfo, predictScore } from '@/api/education/prediction'

// 标签页状态
const activeTab = ref('train')

// 训练相关状态
const trainingLoading = ref(false)
const trainForm = reactive({
  file: null
})
const fileList = ref([])
const uploadRef = ref(null)
const trainResult = ref(null)

// 模型信息状态
const modelInfoLoading = ref(false)
const modelInfo = ref(null)

// 预测相关状态
const predictLoading = ref(false)
const predictForm = reactive({
  input_data: {
    Hours_Studied: 30,
    Attendance: 90,
    Parental_Involvement: "Medium",
    Access_to_Resources: "Medium",
    Extracurricular_Activities: "Yes",
    Sleep_Hours: 8,
    Previous_Scores: 75,
    Motivation_Level: "Medium",
    Internet_Access: "Yes",
    Tutoring_Sessions: 2,
    Family_Income: "Medium",
    Teacher_Quality: "High",
    School_Type: "Public",
    Peer_Influence: "Neutral",
    Physical_Activity: 5,
    Learning_Disabilities: "No",
    Parental_Education_Level: "Bachelor's",
    Distance_from_Home: "Medium",
    Gender: "Female"
  }
})
const predictResult = ref(null)

// 处理文件选择
const handleFileChange = (uploadFile) => {
  // 只保留最新选择的文件
  fileList.value = [uploadFile]
  trainForm.file = uploadFile.raw
}

// 训练模型 - 双层嵌套：response.result
const handleTrainModel = async () => {
  if (!trainForm.file) {
    ElMessage.warning('请选择CSV文件')
    return
  }
  
  // 检查文件类型
  if (trainForm.file.type !== 'text/csv' && !trainForm.file.name.endsWith('.csv')) {
    ElMessage.warning('请上传CSV格式的文件')
    return
  }
  
  trainingLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', trainForm.file)
    const response = await trainPredictionModel(formData)
    trainResult.value = response.result
    if (trainResult.value.status === 'success') {
      ElMessage.success(`✅ 文件上传成功！模型训练完成\n📊 平均绝对误差: ${trainResult.value.test_mae.toFixed(4)}\n📈 特征数量: ${trainResult.value.feature_count}`)
    } else {
      ElMessage.error(trainResult.value.message || '模型训练失败')
    }
  } catch (error) {
    trainResult.value = { status: 'error', message: '网络错误，请检查服务是否运行' }
    ElMessage.error('训练失败，请稍后重试')
  } finally {
    trainingLoading.value = false
    fileList.value = []
    trainForm.file = null
    if(uploadRef.value) uploadRef.value.clearFiles()
  }
}

// 获取模型信息 - 单层结构：直接赋值response
const fetchModelInfo = async () => {
  modelInfoLoading.value = true
  try {
    const response = await getModelInfo()
    modelInfo.value = response
    if (modelInfo.value.status === 'success') {
      ElMessage.success('获取模型信息成功')
    } else {
      ElMessage.error(modelInfo.value.message || '获取模型信息失败')
    }
  } catch (error) {
    modelInfo.value = { status: 'error', message: '网络错误，请检查服务是否运行' }
    ElMessage.error('获取失败，请稍后重试')
  } finally {
    modelInfoLoading.value = false
  }
}

// 预测成绩 - 单层结构：直接赋值response
const handlePredictScore = async () => {
  predictLoading.value = true
  try {
    const response = await predictScore(predictForm)
    predictResult.value = response
    if (predictResult.value.status === 'success') {
      ElMessage.success('预测成功')
    } else {
      ElMessage.error(predictResult.value.message || '预测失败')
    }
  } catch (error) {
    predictResult.value = { status: 'error', message: '网络错误，请检查服务是否运行' }
    ElMessage.error('预测失败，请稍后重试')
  } finally {
    predictLoading.value = false
  }
}

// 获取成绩等级
const getScoreLevel = (score) => {
  if (!score) return 'info'
  if (score >= 90) return 'success'
  if (score >= 80) return 'primary'
  if (score >= 70) return 'warning'
  return 'danger'
}

// 获取成绩描述
const getScoreDescription = (score) => {
  if (!score) return '待预测'
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 70) return '中等'
  if (score >= 60) return '及格'
  return '不及格'
}

// 页面挂载时自动获取模型信息（可选功能）
onMounted(() => {
  // fetchModelInfo();
})
</script>

<style scoped>
.prediction-container {
  padding: 20px;
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}

.bg-decoration {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.14;
  z-index: 0;
}

.bg-decoration-1 {
  width: 280px;
  height: 280px;
  background: #0ea5e9;
  top: 8%;
  left: 4%;
}

.bg-decoration-2 {
  width: 320px;
  height: 320px;
  background: #14b8a6;
  bottom: 8%;
  right: 6%;
}

.bg-decoration-3 {
  width: 220px;
  height: 220px;
  background: #f59e0b;
  top: 45%;
  right: 26%;
}

.prediction-header {
  margin-bottom: 22px;
  text-align: center;
  position: relative;
  z-index: 1;
}

.page-title {
  font-size: 30px;
  font-weight: 700;
  margin-bottom: 10px;
  color: #0b3b51;
}

.page-description {
  font-size: 15px;
  color: #475569;
  margin: 0 auto;
}

.main-card {
  position: relative;
  z-index: 1;
  overflow: hidden;
}

.prediction-tabs {
  padding: 24px;
}

:deep(.el-tabs__header) {
  margin-bottom: 24px !important;
}

:deep(.el-tabs__item) {
  font-size: 15px !important;
  font-weight: 600 !important;
}

.alert-section {
  margin-bottom: 22px;
  border-radius: 12px;
}

.train-form,
.predict-form {
  margin-bottom: 26px;
}

:deep(.el-form-item) {
  margin-bottom: 22px;
}

:deep(.el-form-item__label) {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

.form-input,
.number-input,
.select-input {
  width: 100%;
  max-width: 460px;
}

.train-button,
.info-button,
.predict-button {
  width: 220px;
  height: 46px;
  border-radius: 23px;
  font-size: 15px;
  font-weight: 600;
}

.train-result,
.model-info-result,
.predict-result {
  margin-top: 26px;
}

:deep(.el-divider__text) {
  font-size: 17px;
  font-weight: 600;
  color: #0f172a;
  background-color: transparent;
  padding: 0 14px;
}

.result-details {
  margin-bottom: 16px;
}

.feature-list,
.categorical-features {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.feature-tag {
  margin-bottom: 6px;
  border-radius: 16px;
}

.model-layers {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 16px;
}

.layer-card {
  border-radius: 12px;
  border-left: 4px solid #0284c7;
}

.card-header {
  font-weight: 700;
  font-size: 15px;
  color: #0f172a;
}

.model-card,
.feature-card {
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
}

.radio-group {
  display: flex;
  gap: 20px;
}

.score-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 26px;
}

.score-circle {
  width: 148px;
  height: 148px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0f766e, #0284c7);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 44px;
  font-weight: 700;
  margin-bottom: 18px;
  box-shadow: 0 8px 24px rgba(2, 132, 199, 0.28);
}

.score-assessment {
  margin-top: 12px;
}

@media (max-width: 768px) {
  .prediction-container {
    padding: 12px;
  }

  .prediction-tabs {
    padding: 16px 12px;
  }

  .page-title {
    font-size: 24px;
  }

  .page-description {
    font-size: 14px;
  }

  .form-input,
  .number-input,
  .select-input {
    max-width: 100%;
  }

  .train-button,
  .info-button,
  .predict-button {
    width: 100%;
    max-width: 280px;
  }

  .radio-group {
    flex-direction: column;
    gap: 12px;
  }

  .score-circle {
    width: 120px;
    height: 120px;
    font-size: 34px;
  }
}
</style>
