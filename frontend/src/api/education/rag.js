import request from '@/utils/request'

const aiBaseURL = import.meta.env.VITE_AI_BASE_API || 'http://127.0.0.1:8000'

// 上传Excel文件
export function uploadExcel(file) {
  const formData = new FormData()
  // 使用file.raw获取原始File对象，因为从Element Plus组件中传递的是包装后的file对象
  formData.append('file', file.raw || file)
  console.log('准备上传文件到 /rag-api/upload-excel')
  return request({
    url: '/upload-excel',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
      'isToken': false // 不添加认证信息
    },
    baseURL: aiBaseURL,
    timeout: 60000 // 设置60秒超时，处理大文件
  })
}

// 批量上传文件
export function uploadExcelFiles(files = []) {
  const formData = new FormData()
  files.forEach((file) => {
    formData.append('files', file.raw || file)
  })
  return request({
    url: '/upload-excel',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
      'isToken': false
    },
    baseURL: aiBaseURL,
    timeout: 120000
  })
}

// 查询问题
export function queryQuestion(question) {
  console.log('准备查询问题到 /rag-api/query:', question)
  return request({
    url: '/query',
    method: 'get',
    params: { question },
    headers: {
      'isToken': false // 不添加认证信息
    },
    baseURL: aiBaseURL,
    timeout: 60000 // 设置60秒超时，处理复杂查询
  })
}

// 获取历史数据集
export function getDatasets() {
  console.log('准备获取历史数据集')
  return request({
    url: '/datasets',
    method: 'get',
    headers: {
      'isToken': false // 不添加认证信息
    },
    baseURL: aiBaseURL,
    timeout: 60000
  })
}

// 删除数据集
export function deleteDataset(datasetId) {
  console.log('准备删除数据集:', datasetId)
  return request({
    url: `/datasets/${datasetId}`,
    method: 'delete',
    headers: {
      'isToken': false // 不添加认证信息
    },
    baseURL: aiBaseURL,
    timeout: 60000
  })
}

// 查看数据集详情
export function getDatasetDetail(datasetId) {
  console.log('准备查看数据集详情:', datasetId)
  return request({
    url: `/datasets/${datasetId}`,
    method: 'get',
    headers: {
      'isToken': false // 不添加认证信息
    },
    baseURL: aiBaseURL,
    timeout: 60000
  })
}
