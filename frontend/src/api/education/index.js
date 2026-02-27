import request from '@/utils/request'

// 查询学生成绩列表
export function listStudentPerformance(query) {
  return request({
    url: '/student/performance/list',
    method: 'get',
    params: query
  })
}

// 查询学生成绩详细
export function getStudentPerformance(id) {
  return request({
    url: '/student/performance/' + id,
    method: 'get'
  })
}

// 新增学生成绩
export function addStudentPerformance(data) {
  return request({
    url: '/student/performance',
    method: 'post',
    data
  })
}

// 修改学生成绩
export function updateStudentPerformance(data) {
  return request({
    url: '/student/performance',
    method: 'put',
    data
  })
}

// 删除学生成绩
export function delStudentPerformance(id) {
  return request({
    url: `/student/performance/${id}`,
    method: 'delete'
  })
}

// 批量删除学生成绩
export function batchDelStudentPerformance(ids) {
  return request({
    url: '/student/performance/batch',
    method: 'delete',
    data: ids
  })
}
