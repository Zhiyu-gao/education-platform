const TokenKey = 'Admin-Token'

export function getToken() {
  return sessionStorage.getItem(TokenKey)
}

export function setToken(token) {
  sessionStorage.setItem(TokenKey, token)
  return token
}

export function removeToken() {
  sessionStorage.removeItem(TokenKey)
}
