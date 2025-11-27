<!--
/**
 * ログイン画面
 * メールアドレスとパスワードでログイン
 */
-->
<template>
  <div class="login-container">
    <div class="login-card card">
      <h1 class="login-title">勤務月報システム</h1>
      <p class="login-subtitle">ログイン</p>
      
      <!-- エラーメッセージ -->
      <div v-if="authStore.error" class="alert alert-danger">
        {{ authStore.error }}
      </div>
      
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email" class="form-label">メールアドレス</label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="form-control"
            placeholder="example@company.com"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="password" class="form-label">パスワード</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="form-control"
            placeholder="パスワードを入力"
            required
          />
        </div>
        
        <button
          type="submit"
          class="btn btn-primary btn-block"
          :disabled="authStore.loading"
        >
          {{ authStore.loading ? 'ログイン中...' : 'ログイン' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')

/**
 * ログイン処理
 */
async function handleLogin() {
  const success = await authStore.login(email.value, password.value)
  
  if (success) {
    // リダイレクト先があればそこへ、なければ月報一覧へ
    const redirect = route.query.redirect || '/monthly'
    router.push(redirect)
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
}

.login-card {
  width: 100%;
  max-width: 400px;
}

.login-title {
  text-align: center;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.login-subtitle {
  text-align: center;
  color: var(--secondary-color);
  margin-bottom: 1.5rem;
}

.btn-block {
  display: block;
  width: 100%;
}
</style>
