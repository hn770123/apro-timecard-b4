<!--
/**
 * ユーザー管理画面
 * ユーザーの追加/変更（管理者権限必要）
 */
-->
<template>
  <div class="user-management">
    <div class="page-header d-flex justify-between align-center">
      <h1 class="page-title">ユーザー管理</h1>
      <button @click="openCreateModal" class="btn btn-primary">
        新規ユーザー作成
      </button>
    </div>
    
    <!-- ローディング -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>
    
    <!-- エラー -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    
    <!-- ユーザー一覧 -->
    <div v-else>
      <table class="table">
        <thead>
          <tr>
            <th>氏名</th>
            <th>メールアドレス</th>
            <th>所属</th>
            <th>権限</th>
            <th>状態</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.user_id">
            <td>{{ user.name }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.department }}</td>
            <td>
              <span v-if="user.is_approver" class="badge badge-approved">承認者</span>
              <span v-if="user.is_admin" class="badge badge-submitted">管理者</span>
              <span v-if="!user.is_approver && !user.is_admin" class="badge badge-draft">一般</span>
            </td>
            <td>
              <span :class="user.is_active ? 'status-active' : 'status-inactive'">
                {{ user.is_active ? '有効' : '無効' }}
              </span>
            </td>
            <td>
              <button @click="openEditModal(user)" class="btn btn-outline btn-sm">
                編集
              </button>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="6" class="text-center">ユーザーがいません</td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- ユーザー編集モーダル -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">
            {{ isEditMode ? 'ユーザー編集' : '新規ユーザー作成' }}
          </h2>
          <button @click="closeModal" class="modal-close">&times;</button>
        </div>
        <form @submit.prevent="saveUser">
          <div class="modal-body">
            <div class="form-group">
              <label for="email" class="form-label">メールアドレス</label>
              <input
                id="email"
                v-model="formData.email"
                type="email"
                class="form-control"
                required
              />
            </div>
            
            <div v-if="!isEditMode" class="form-group">
              <label for="password" class="form-label">パスワード</label>
              <input
                id="password"
                v-model="formData.password"
                type="password"
                class="form-control"
                minlength="8"
                required
              />
              <small class="form-text">8文字以上</small>
            </div>
            
            <div class="form-group">
              <label for="name" class="form-label">氏名</label>
              <input
                id="name"
                v-model="formData.name"
                type="text"
                class="form-control"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="department" class="form-label">所属</label>
              <input
                id="department"
                v-model="formData.department"
                type="text"
                class="form-control"
                required
              />
            </div>
            
            <div class="form-group">
              <label class="form-label">権限</label>
              <div class="checkbox-group">
                <label class="checkbox-label">
                  <input
                    type="checkbox"
                    v-model="formData.is_approver"
                  />
                  承認者（他ユーザーの月報を承認可能）
                </label>
                <label class="checkbox-label">
                  <input
                    type="checkbox"
                    v-model="formData.is_admin"
                  />
                  管理者（ユーザーの追加/変更が可能）
                </label>
              </div>
            </div>
            
            <div v-if="isEditMode" class="form-group">
              <label class="form-label">状態</label>
              <div class="checkbox-group">
                <label class="checkbox-label">
                  <input
                    type="checkbox"
                    v-model="formData.is_active"
                  />
                  アカウント有効
                </label>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-secondary">
              キャンセル
            </button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usersApi } from '@/services/api'

const users = ref([])
const loading = ref(true)
const error = ref(null)
const showModal = ref(false)
const saving = ref(false)
const editingUserId = ref(null)

const isEditMode = computed(() => !!editingUserId.value)

const formData = ref({
  email: '',
  password: '',
  name: '',
  department: '',
  is_approver: false,
  is_admin: false,
  is_active: true
})

/**
 * ユーザー一覧を取得
 */
async function fetchUsers() {
  loading.value = true
  error.value = null
  
  try {
    users.value = await usersApi.list()
  } catch (err) {
    error.value = err.response?.data?.detail || 'データの取得に失敗しました'
  } finally {
    loading.value = false
  }
}

/**
 * 新規作成モーダルを開く
 */
function openCreateModal() {
  editingUserId.value = null
  formData.value = {
    email: '',
    password: '',
    name: '',
    department: '',
    is_approver: false,
    is_admin: false,
    is_active: true
  }
  showModal.value = true
}

/**
 * 編集モーダルを開く
 */
function openEditModal(user) {
  editingUserId.value = user.user_id
  formData.value = {
    email: user.email,
    password: '',
    name: user.name,
    department: user.department,
    is_approver: user.is_approver,
    is_admin: user.is_admin,
    is_active: user.is_active
  }
  showModal.value = true
}

/**
 * モーダルを閉じる
 */
function closeModal() {
  showModal.value = false
  editingUserId.value = null
}

/**
 * ユーザーを保存
 */
async function saveUser() {
  saving.value = true
  
  try {
    if (isEditMode.value) {
      const updateData = {
        email: formData.value.email,
        name: formData.value.name,
        department: formData.value.department,
        is_approver: formData.value.is_approver,
        is_admin: formData.value.is_admin,
        is_active: formData.value.is_active
      }
      await usersApi.update(editingUserId.value, updateData)
    } else {
      await usersApi.create(formData.value)
    }
    
    closeModal()
    await fetchUsers()
  } catch (err) {
    alert(err.response?.data?.detail || '保存に失敗しました')
  } finally {
    saving.value = false
  }
}

onMounted(fetchUsers)
</script>

<style scoped>
.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.status-active {
  color: var(--success-color);
}

.status-inactive {
  color: var(--danger-color);
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.form-text {
  font-size: 0.75rem;
  color: var(--secondary-color);
}
</style>
