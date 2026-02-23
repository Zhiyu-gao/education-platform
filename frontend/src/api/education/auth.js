import request from '@/utils/request'

// 教育端匿名登录（无验证码）
export function loginEducationUser(data) {
  return request({
    url: '/education/pad/auth/login',
    method: 'post',
    headers: {
      isToken: false,
      repeatSubmit: false
    },
    data
  })
}

// 教育端匿名注册（按 roleKey 自动分配角色）
export function registerEducationUser(data) {
  return request({
    url: '/education/pad/auth/register',
    method: 'post',
    headers: {
      isToken: false,
      repeatSubmit: false
    },
    data
  })
}
