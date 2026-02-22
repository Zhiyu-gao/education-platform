import request from '@/utils/request'

export function createHomework(data) {
  return request({ url: '/education/pad/homework', method: 'post', data })
}

export function listTeacherHomework() {
  return request({ url: '/education/pad/homework/teacher', method: 'get' })
}

export function listStudentHomework() {
  return request({ url: '/education/pad/homework/student', method: 'get' })
}

export function submitHomework(homeworkId, data) {
  return request({ url: `/education/pad/homework/${homeworkId}/submit`, method: 'post', data })
}

export function listTeacherHomeworkSubmissions() {
  return request({ url: '/education/pad/homework/submissions', method: 'get' })
}

export function listStudentHomeworkSubmissions() {
  return request({ url: '/education/pad/homework/submissions/student', method: 'get' })
}

export function scoreHomework(data) {
  return request({ url: '/education/pad/homework/score', method: 'post', data })
}

export function createExam(data) {
  return request({ url: '/education/pad/exam', method: 'post', data })
}

export function listTeacherExam() {
  return request({ url: '/education/pad/exam/teacher', method: 'get' })
}

export function listStudentExam() {
  return request({ url: '/education/pad/exam/student', method: 'get' })
}

export function submitExam(examId, data) {
  return request({ url: `/education/pad/exam/${examId}/submit`, method: 'post', data })
}

export function scoreExam(data) {
  return request({ url: '/education/pad/exam/score', method: 'post', data })
}

export function listStudentExamScore() {
  return request({ url: '/education/pad/exam/score/student', method: 'get' })
}

export function listManagerScores() {
  return request({ url: '/education/pad/manager/scores', method: 'get' })
}

export function listStudentSelfScores() {
  return request({ url: '/education/pad/student/scores', method: 'get' })
}

export function createTeacherTask(data) {
  return request({ url: '/education/pad/manager/teacher-task', method: 'post', data })
}

export function listTeacherTasks() {
  return request({ url: '/education/pad/teacher/tasks', method: 'get' })
}

export function listTeacherScores() {
  return request({ url: '/education/pad/teacher/scores', method: 'get' })
}
