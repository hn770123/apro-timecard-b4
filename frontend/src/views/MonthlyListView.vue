<!--
/**
 * 月次記録一覧画面
 * 月間勤務一覧を表示し、日次入力や承認への遷移を行う
 */
-->
<template>
  <div class="monthly-list">
    <div class="page-header d-flex justify-between align-center">
      <h1 class="page-title">月報一覧</h1>
      <button @click="showCreateModal = true" class="btn btn-primary">
        新規作成
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
    
    <!-- 月次記録一覧 -->
    <div v-else>
      <table class="table">
        <thead>
          <tr>
            <th>年月</th>
            <th>氏名</th>
            <th>所属</th>
            <th>ステータス</th>
            <th>勤務日数</th>
            <th>労働時間</th>
            <th>残業時間</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="record in records" :key="record.record_id">
            <td>{{ formatYearMonth(record.year_month) }}</td>
            <td>{{ record.name }}</td>
            <td>{{ record.department }}</td>
            <td>
              <span :class="['badge', getStatusBadgeClass(record.status)]">
                {{ getStatusLabel(record.status) }}
              </span>
            </td>
            <td>{{ record.total_work_days }}日</td>
            <td>{{ formatMinutes(record.total_work_minutes) }}</td>
            <td>{{ formatMinutes(record.total_overtime_minutes) }}</td>
            <td>
              <div class="d-flex gap-1">
                <router-link
                  :to="{ name: 'daily-list', params: { recordId: record.record_id } }"
                  class="btn btn-outline btn-sm"
                >
                  詳細
                </router-link>
                <button
                  v-if="record.can_edit && record.status === 'draft'"
                  @click="submitRecord(record)"
                  class="btn btn-primary btn-sm"
                >
                  申請
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="records.length === 0">
            <td colspan="8" class="text-center">データがありません</td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- 新規作成モーダル -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">月報の新規作成</h2>
          <button @click="showCreateModal = false" class="modal-close">&times;</button>
        </div>
        <form @submit.prevent="createRecord">
          <div class="modal-body">
            <div class="form-group">
              <label for="yearMonth" class="form-label">年月</label>
              <input
                id="yearMonth"
                v-model="newRecord.year_month"
                type="month"
                class="form-control"
                required
              />
            </div>
            <div class="form-group">
              <label for="name" class="form-label">氏名</label>
              <input
                id="name"
                v-model="newRecord.name"
                type="text"
                class="form-control"
                required
              />
            </div>
            <div class="form-group">
              <label for="department" class="form-label">所属</label>
              <input
                id="department"
                v-model="newRecord.department"
                type="text"
                class="form-control"
                required
              />
            </div>
            <div class="form-group">
              <label for="standardWorkHours" class="form-label">1日標準就労時間（時間）</label>
              <input
                id="standardWorkHours"
                v-model.number="newRecord.standard_work_hours"
                type="number"
                min="0"
                max="24"
                step="0.5"
                class="form-control"
                required
              />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="showCreateModal = false" class="btn btn-secondary">
              キャンセル
            </button>
            <button type="submit" class="btn btn-primary" :disabled="creating">
              {{ creating ? '作成中...' : '作成' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { monthlyRecordsApi } from '@/services/api'

const authStore = useAuthStore()

const records = ref([])
const loading = ref(true)
const error = ref(null)
const showCreateModal = ref(false)
const creating = ref(false)

// 新規作成用データ
const newRecord = ref({
  year_month: new Date().toISOString().slice(0, 7),
  name: '',
  department: '',
  standard_work_hours: 8.0
})

/**
 * 月次記録一覧を取得
 */
async function fetchRecords() {
  loading.value = true
  error.value = null
  
  try {
    records.value = await monthlyRecordsApi.list()
  } catch (err) {
    error.value = err.response?.data?.detail || 'データの取得に失敗しました'
  } finally {
    loading.value = false
  }
}

/**
 * 新規月次記録を作成
 */
async function createRecord() {
  creating.value = true
  
  try {
    await monthlyRecordsApi.create(newRecord.value)
    showCreateModal.value = false
    await fetchRecords()
    
    // フォームをリセット
    newRecord.value = {
      year_month: new Date().toISOString().slice(0, 7),
      name: authStore.user?.name || '',
      department: authStore.user?.department || '',
      standard_work_hours: 8.0
    }
  } catch (err) {
    alert(err.response?.data?.detail || '作成に失敗しました')
  } finally {
    creating.value = false
  }
}

/**
 * 承認申請
 */
async function submitRecord(record) {
  if (!confirm('この月報を申請しますか？')) return
  
  try {
    await monthlyRecordsApi.approval(record.record_id, 'submit')
    await fetchRecords()
  } catch (err) {
    alert(err.response?.data?.detail || '申請に失敗しました')
  }
}

/**
 * 年月をフォーマット
 */
function formatYearMonth(yearMonth) {
  const [year, month] = yearMonth.split('-')
  return `${year}年${parseInt(month)}月`
}

/**
 * 分を時間:分形式にフォーマット
 */
function formatMinutes(minutes) {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours}:${mins.toString().padStart(2, '0')}`
}

/**
 * ステータスラベルを取得
 */
function getStatusLabel(status) {
  const labels = {
    draft: '下書き',
    submitted: '申請中',
    approved: '承認済み',
    rejected: '差し戻し'
  }
  return labels[status] || status
}

/**
 * ステータスバッジクラスを取得
 */
function getStatusBadgeClass(status) {
  return `badge-${status}`
}

onMounted(async () => {
  await fetchRecords()
  
  // 初期値をユーザー情報から設定
  if (authStore.user) {
    newRecord.value.name = authStore.user.name
    newRecord.value.department = authStore.user.department
  }
})
</script>

<style scoped>
.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}
</style>
