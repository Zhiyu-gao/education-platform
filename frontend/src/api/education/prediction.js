import request from '@/utils/request'

const aiBaseURL = import.meta.env.VITE_AI_BASE_API || 'http://127.0.0.1:8000'

// 训练预测模型
export function trainPredictionModel(data) {
  return request({
    url: '/train-prediction-model',
    method: 'post',
    data: data,
    baseURL: aiBaseURL,
    timeout: 60000,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取模型信息
export function getModelInfo() {
  return request({
    url: '/model-info',
    method: 'get',
    baseURL: aiBaseURL,
    timeout: 60000
  })
}

// 预测成绩
export function predictScore(data) {
  return request({
    url: '/predict-score',
    method: 'post',
    data: data,
    baseURL: aiBaseURL,
    timeout: 60000
  })
}
