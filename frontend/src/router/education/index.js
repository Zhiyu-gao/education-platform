/**
 * 教育 Pad 端路由（全屏独立，不使用若依 Layout）
 */

const educationAccessRoles = ['admin', 'manager', 'teacher', 'student', 'ROLE_DEFAULT']

const educationRoutes = [
  {
    path: '/education',
    redirect: '/education/auth?redirect=/education/pad',
    hidden: true
  },
  {
    path: '/education/pad',
    component: () => import('@/views/education/pad'),
    name: 'EducationPad',
    roles: educationAccessRoles,
    meta: {
      title: 'Pad教育端',
      noCache: true
    }
  },
  {
    path: '/education/dashboard',
    redirect: '/education/auth?redirect=/education/pad',
    hidden: true
  },
  {
    path: '/education/index',
    redirect: '/education/auth?redirect=/education/pad',
    hidden: true
  },
  {
    path: '/education/rag',
    component: () => import('@/views/education/rag'),
    name: 'EducationRag',
    roles: educationAccessRoles,
    meta: {
      title: 'AI 智能问答',
      noCache: true
    },
    hidden: true
  },
  {
    path: '/education/prediction',
    component: () => import('@/views/education/prediction'),
    name: 'EducationPrediction',
    roles: educationAccessRoles,
    meta: {
      title: 'AI 成绩预测',
      noCache: true
    },
    hidden: true
  },
  {
    path: '/education/:pathMatch(.*)*',
    redirect: '/education/auth?redirect=/education/pad',
    hidden: true
  },
  {
    path: '/pad',
    redirect: '/education/auth?redirect=/education/pad',
    hidden: true
  },
  {
    path: '/pad/:pathMatch(.*)*',
    redirect: '/education/auth?redirect=/education/pad',
    hidden: true
  }
]

export default educationRoutes
