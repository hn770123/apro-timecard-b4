/**
 * 認証ストア
 * ログイン状態と権限を管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // 状態
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const loading = ref(false)
  const error = ref(null)

  // 計算プロパティ
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.roles?.includes('admin') || false)
  const isApprover = computed(() => user.value?.roles?.includes('approver') || false)

  /**
   * ログイン
   */
  async function login(email, password) {
    loading.value = true
    error.value = null
    
    try {
      const response = await authApi.login(email, password)
      token.value = response.access_token
      localStorage.setItem('token', response.access_token)
      
      // ユーザー情報を取得
      await fetchCurrentUser()
      
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'ログインに失敗しました'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * ログアウト
   */
  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  /**
   * 現在のユーザー情報を取得
   */
  async function fetchCurrentUser() {
    if (!token.value) return
    
    try {
      user.value = await authApi.getCurrentUser()
    } catch (err) {
      logout()
    }
  }

  /**
   * 初期化時にユーザー情報を取得
   */
  async function initialize() {
    if (token.value) {
      await fetchCurrentUser()
    }
  }

  return {
    // 状態
    user,
    token,
    loading,
    error,
    // 計算プロパティ
    isAuthenticated,
    isAdmin,
    isApprover,
    // アクション
    login,
    logout,
    fetchCurrentUser,
    initialize
  }
})
