import router from './router'
import { ElMessage } from 'element-plus'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import { getToken } from '@/utils/auth'
import { isHttp, isPathMatch } from '@/utils/validate'
import { isRelogin } from '@/utils/request'
import useUserStore from '@/store/modules/user'
import useSettingsStore from '@/store/modules/settings'
import usePermissionStore from '@/store/modules/permission'

NProgress.configure({ showSpinner: false })

const whiteList = ['/login', '/register', '/education/auth']

const isWhiteList = (path) => {
  return whiteList.some(pattern => isPathMatch(pattern, path))
}

const normalizeRoles = (roles = []) => roles.map(role => String(role || '').toLowerCase())
const isManagerRole = (roles = []) => roles.includes('admin') || roles.includes('manager')
const isPadOnlyPath = (path = '') => path === '/education' || path.startsWith('/education/')
const shouldForcePad = (path = '') => {
  if (isWhiteList(path)) return false
  if (path === '/401' || path === '/404') return false
  return !isPadOnlyPath(path)
}

router.beforeEach((to, from, next) => {
  NProgress.start()
  if (getToken()) {
    to.meta.title && useSettingsStore().setTitle(to.meta.title)
    /* has token*/
    if (to.path === '/login') {
      next({ path: '/' })
      NProgress.done()
    } else if (isWhiteList(to.path)) {
      next()
    } else {
      if (useUserStore().roles.length === 0) {
        isRelogin.show = true
        // 判断当前用户是否已拉取完user_info信息
        useUserStore().getInfo().then(() => {
          isRelogin.show = false
          const userRoles = useUserStore().roles || []
          usePermissionStore().generateRoutes(userRoles).then(accessRoutes => {
            // 根据roles权限生成可访问的路由表
            accessRoutes.forEach(route => {
              if (!isHttp(route.path) && (!route.name || !router.hasRoute(route.name))) {
                router.addRoute(route) // 动态添加可访问路由表
              }
            })
            const normalizedRoles = normalizeRoles(userRoles)
            if (!isManagerRole(normalizedRoles) && shouldForcePad(to.path)) {
              next({ path: '/education/pad', replace: true })
              return
            }
            next({ ...to, replace: true }) // hack方法 确保addRoutes已完成
          })
        }).catch(err => {
          useUserStore().logOut().then(() => {
            ElMessage.error(err)
            next({ path: '/' })
          })
        })
      } else {
        const normalizedRoles = normalizeRoles(useUserStore().roles || [])
        if (usePermissionStore().addRoutes.length === 0) {
          usePermissionStore().generateRoutes(useUserStore().roles || []).then(accessRoutes => {
            accessRoutes.forEach(route => {
              if (!isHttp(route.path) && (!route.name || !router.hasRoute(route.name))) {
                router.addRoute(route)
              }
            })
            if (!isManagerRole(normalizedRoles) && shouldForcePad(to.path)) {
              next({ path: '/education/pad', replace: true })
              return
            }
            next({ ...to, replace: true })
          })
          return
        }
        if (!isManagerRole(normalizedRoles) && shouldForcePad(to.path)) {
          next({ path: '/education/pad', replace: true })
          return
        }
        next()
      }
    }
  } else {
    // 没有token
    if (isWhiteList(to.path)) {
      // 在免登录白名单，直接进入
      next()
    } else {
      if (isPadOnlyPath(to.path)) {
        next(`/education/auth?redirect=${to.fullPath}`)
      } else {
        next(`/login?redirect=${to.fullPath}`) // 否则全部重定向到登录页
      }
      NProgress.done()
    }
  }
})

router.afterEach(() => {
  NProgress.done()
})
