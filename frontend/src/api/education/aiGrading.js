import request from '@/utils/request'

const aiBaseURL = import.meta.env.VITE_AI_BASE_API || 'http://127.0.0.1:8000'

export function uploadAiReference(file) {
  const formData = new FormData()
  formData.append('file', file.raw || file)
  return request({
    url: '/ai-grade/reference',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
      isToken: false
    },
    baseURL: aiBaseURL,
    timeout: 120000
  })
}

export function aiGradeSingle({ file, referenceId = '', rubric = '', maxScore = 100, questionCount = 12 }) {
  const formData = new FormData()
  formData.append('studentFile', file.raw || file)
  formData.append('referenceId', referenceId || '')
  formData.append('rubric', rubric || '')
  formData.append('maxScore', String(maxScore || 100))
  formData.append('questionCount', String(questionCount || 12))
  return request({
    url: '/ai-grade/single',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
      isToken: false
    },
    baseURL: aiBaseURL,
    timeout: 120000
  })
}
