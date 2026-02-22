import auth from '@/plugins/auth'
import router, { constantRoutes, dynamicRoutes } from '@/router'
import { getRouters } from '@/api/menu'
import Layout from '@/layout/index'
import ParentView from '@/components/ParentView'
import InnerLink from '@/layout/components/InnerLink'

// 匹配views里面所有的.vue文件
const modules = import.meta.glob('./../../views/**/*.vue')

const usePermissionStore = defineStore(
  'permission',
  {
    state: () => ({
      routes: [],
      addRoutes: [],
      defaultRoutes: [],
      topbarRouters: [],
      sidebarRouters: []
    }),
    actions: {
      setRoutes(routes) {
        this.addRoutes = routes
        this.routes = constantRoutes.concat(routes)
      },
      setDefaultRoutes(routes) {
        this.defaultRoutes = constantRoutes.concat(routes)
      },
      setTopbarRoutes(routes) {
        this.topbarRouters = routes
      },
      setSidebarRouters(routes) {
        this.sidebarRouters = routes
      },
      generateRoutes(roles = []) {
        return new Promise(resolve => {
          const roleKeys = normalizeRoles(roles)
          const isManager = isManagerRole(roleKeys)
          const isPadOnly = !isManager

          if (isPadOnly) {
            const padRoutes = filterDynamicRoutes(dynamicRoutes, roleKeys)
            this.setRoutes(padRoutes)
            this.setSidebarRouters(constantRoutes.concat(padRoutes))
            this.setDefaultRoutes(padRoutes)
            this.setTopbarRoutes(padRoutes)
            resolve(padRoutes)
            return
          }

          // 向后端请求路由数据
          getRouters().then(res => {
            const sdata = JSON.parse(JSON.stringify(res.data))
            const rdata = JSON.parse(JSON.stringify(res.data))
            const defaultData = JSON.parse(JSON.stringify(res.data))
            const sidebarRoutes = filterAsyncRouter(sdata)
            const rewriteRoutes = filterAsyncRouter(rdata, false, true)
            const defaultRoutes = filterAsyncRouter(defaultData)
            const asyncRoutes = filterDynamicRoutes(dynamicRoutes, roleKeys)
            asyncRoutes.forEach(route => { router.addRoute(route) })
            this.setRoutes(rewriteRoutes)
            this.setSidebarRouters(constantRoutes.concat(sidebarRoutes))
            this.setDefaultRoutes(sidebarRoutes)
            this.setTopbarRoutes(defaultRoutes)
            resolve(rewriteRoutes)
          })
        })
      }
    }
  })

// 遍历后台传来的路由字符串，转换为组件对象
function filterAsyncRouter(asyncRouterMap, lastRouter = false, type = false) {
  return asyncRouterMap.filter(route => {
    if (type && route.children) {
      route.children = filterChildren(route.children)
    }
    if (route.component) {
      // Layout ParentView 组件特殊处理
      if (route.component === 'Layout') {
        route.component = Layout
      } else if (route.component === 'ParentView') {
        route.component = ParentView
      } else if (route.component === 'InnerLink') {
        route.component = InnerLink
      } else {
        route.component = loadView(route.component)
      }
    }
    if (route.children != null && route.children && route.children.length) {
      route.children = filterAsyncRouter(route.children, route, type)
    } else {
      delete route['children']
      delete route['redirect']
    }
    return true
  })
}

function filterChildren(childrenMap, lastRouter = false) {
  var children = []
  childrenMap.forEach(el => {
    el.path = lastRouter ? lastRouter.path + '/' + el.path : el.path
    if (el.children && el.children.length && el.component === 'ParentView') {
      children = children.concat(filterChildren(el.children, el))
    } else {
      children.push(el)
    }
  })
  return children
}

// 动态路由遍历，验证是否具备权限
export function filterDynamicRoutes(routes, roles = []) {
  const res = []
  const roleKeys = normalizeRoles(roles)
  routes.forEach(route => {
    const current = { ...route }
    const children = current.children ? filterDynamicRoutes(current.children, roleKeys) : []
    if (children.length > 0) {
      current.children = children
    }
    const passByPerm = !current.permissions || auth.hasPermiOr(current.permissions)
    const passByRole = !current.roles || hasRoleIn(current.roles, roleKeys)
    if (passByPerm && passByRole) {
      res.push(current)
    } else if (children.length > 0) {
      delete current.roles
      delete current.permissions
      res.push(current)
    }
  })
  return res
}

function normalizeRoles(roles = []) {
  return roles.map(role => String(role || '').toLowerCase())
}

function hasRoleIn(routeRoles = [], currentRoles = []) {
  const targetRoles = routeRoles.map(role => String(role || '').toLowerCase())
  return targetRoles.some(role => currentRoles.includes(role))
}

function isManagerRole(currentRoles = []) {
  return currentRoles.includes('admin') || currentRoles.includes('manager')
}

export const loadView = (view) => {
  let res
  for (const path in modules) {
    const dir = path.split('views/')[1].split('.vue')[0]
    if (dir === view) {
      res = () => modules[path]()
    }
  }
  return res
}

export default usePermissionStore
