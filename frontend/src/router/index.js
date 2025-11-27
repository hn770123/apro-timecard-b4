/**
 * Vue Router 設定
 * ルーティング定義
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// ビューをレイジーロード
const LoginView = () => import('@/views/LoginView.vue')
const MonthlyListView = () => import('@/views/MonthlyListView.vue')
const DailyListView = () => import('@/views/DailyListView.vue')
const DailyEditView = () => import('@/views/DailyEditView.vue')
const UserManagementView = () => import('@/views/UserManagementView.vue')
const ApprovalListView = () => import('@/views/ApprovalListView.vue')

/**
 * ルート定義
 */
const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/monthly'
  },
  {
    path: '/monthly',
    name: 'monthly-list',
    component: MonthlyListView,
    meta: { requiresAuth: true }
  },
  {
    path: '/monthly/:recordId/daily',
    name: 'daily-list',
    component: DailyListView,
    meta: { requiresAuth: true }
  },
  {
    path: '/monthly/:recordId/daily/:dailyId?',
    name: 'daily-edit',
    component: DailyEditView,
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'user-management',
    component: UserManagementView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/approvals',
    name: 'approval-list',
    component: ApprovalListView,
    meta: { requiresAuth: true, requiresApprover: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

/**
 * ナビゲーションガード
 * 認証状態と権限をチェック
 */
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 認証が必要なルート
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }
  
  // ログイン済みでログインページにアクセス
  if (to.name === 'login' && authStore.isAuthenticated) {
    return next({ name: 'monthly-list' })
  }
  
  // 管理者権限が必要
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    return next({ name: 'monthly-list' })
  }
  
  // 承認者権限が必要
  if (to.meta.requiresApprover && !authStore.isApprover) {
    return next({ name: 'monthly-list' })
  }
  
  next()
})

export default router
