import request from '@/utils/request'

export function listForumPosts() {
  return request({ url: '/education/pad/forum/posts', method: 'get' })
}

export function createForumPost(data) {
  return request({ url: '/education/pad/forum/post', method: 'post', data })
}

export function replyForumPost(postId, data) {
  return request({ url: `/education/pad/forum/${postId}/reply`, method: 'post', data })
}

export function getForumNotice() {
  return request({ url: '/education/pad/forum/notice', method: 'get' })
}

export function markForumRead() {
  return request({ url: '/education/pad/forum/notice/read', method: 'post' })
}
