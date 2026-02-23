import request from '@/utils/request'

export function listChatContacts() {
  return request({ url: '/education/pad/chat/contacts', method: 'get' })
}

export function listChatMessages(peerUserId) {
  return request({ url: '/education/pad/chat/messages', method: 'get', params: { peerUserId } })
}

export function sendChatMessage(data) {
  return request({ url: '/education/pad/chat/send', method: 'post', data })
}

export function listChatGroups() {
  return request({ url: '/education/pad/chat/groups', method: 'get' })
}

export function listGroupChatMessages(groupId) {
  return request({ url: '/education/pad/chat/group/messages', method: 'get', params: { groupId } })
}

export function sendGroupChatMessage(data) {
  return request({ url: '/education/pad/chat/group/send', method: 'post', data })
}

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
