<!--
/**
 * メインアプリケーションコンポーネント
 * ナビゲーションとルータービューを含む
 */
-->
<template>
  <div id="app">
    <!-- ナビゲーションバー（ログイン時のみ表示） -->
    <nav v-if="authStore.isAuthenticated" class="navbar">
      <div class="navbar-container">
        <router-link to="/" class="navbar-brand">
          勤務月報システム
        </router-link>
        
        <ul class="navbar-nav">
          <li>
            <router-link to="/monthly" class="nav-link">
              月報一覧
            </router-link>
          </li>
          <li v-if="authStore.isApprover">
            <router-link to="/approvals" class="nav-link">
              承認待ち
            </router-link>
          </li>
          <li v-if="authStore.isAdmin">
            <router-link to="/users" class="nav-link">
              ユーザー管理
            </router-link>
          </li>
          <li>
            <span class="nav-link user-info">
              {{ authStore.user?.name }}
            </span>
          </li>
          <li>
            <button @click="handleLogout" class="btn btn-outline btn-sm">
              ログアウト
            </button>
          </li>
        </ul>
      </div>
    </nav>
    
    <!-- メインコンテンツ -->
    <main class="container">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

/**
 * 初期化時にユーザー情報を取得
 */
onMounted(async () => {
  await authStore.initialize()
})

/**
 * ログアウト処理
 */
function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar-nav {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  color: var(--secondary-color);
  font-weight: normal;
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}
</style>
