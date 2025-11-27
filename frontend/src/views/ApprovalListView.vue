<!--
/**
 * 承認待ち一覧画面
 * 承認待ちの月報を表示し、承認/差し戻し操作を行う（承認者権限必要）
 */
-->
<template>
  <div class="approval-list">
    <div class="page-header">
      <h1 class="page-title">承認待ち一覧</h1>
    </div>
    
    <!-- ローディング -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>
    
    <!-- エラー -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    
    <!-- 承認待ち一覧 -->
    <div v-else>
      <table class="table">
        <thead>
          <tr>
            <th>年月</th>
            <th>氏名</th>
            <th>所属</th>
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
                  @click="approveRecord(record)"
                  class="btn btn-success btn-sm"
                >
                  承認
                </button>
                <button
                  @click="rejectRecord(record)"
                  class="btn btn-danger btn-sm"
                >
                  差し戻し
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="records.length === 0">
            <td colspan="7" class="text-center">承認待ちの月報はありません</td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- コメント入力モーダル -->
    <div v-if="showCommentModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">
            {{ isApproving ? '承認' : '差し戻し' }}
          </h2>
          <button @click="closeModal" class="modal-close">&times;</button>
        </div>
        <form @submit.prevent="submitAction">
          <div class="modal-body">
            <p>
              <strong>{{ selectedRecord?.name }}</strong> の
              {{ formatYearMonth(selectedRecord?.year_month) }} を
              {{ isApproving ? '承認' : '差し戻し' }}しますか？
            </p>
            <div class="form-group mt-2">
              <label for="comment" class="form-label">コメント（任意）</label>
              <textarea
                id="comment"
                v-model="comment"
                class="form-control"
                rows="3"
                placeholder="コメントを入力"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-secondary">
              キャンセル
            </button>
            <button
              type="submit"
              :class="['btn', isApproving ? 'btn-success' : 'btn-danger']"
              :disabled="processing"
            >
              {{ processing ? '処理中...' : (isApproving ? '承認する' : '差し戻す') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { monthlyRecordsApi } from '@/services/api'

const records = ref([])
const loading = ref(true)
const error = ref(null)
const showCommentModal = ref(false)
const selectedRecord = ref(null)
const isApproving = ref(true)
const comment = ref('')
const processing = ref(false)

/**
 * 承認待ち一覧を取得
 */
async function fetchRecords() {
  loading.value = true
  error.value = null
  
  try {
    records.value = await monthlyRecordsApi.listPending()
  } catch (err) {
    error.value = err.response?.data?.detail || 'データの取得に失敗しました'
  } finally {
    loading.value = false
  }
}

/**
 * 承認モーダルを開く
 */
function approveRecord(record) {
  selectedRecord.value = record
  isApproving.value = true
  comment.value = ''
  showCommentModal.value = true
}

/**
 * 差し戻しモーダルを開く
 */
function rejectRecord(record) {
  selectedRecord.value = record
  isApproving.value = false
  comment.value = ''
  showCommentModal.value = true
}

/**
 * モーダルを閉じる
 */
function closeModal() {
  showCommentModal.value = false
  selectedRecord.value = null
}

/**
 * 承認/差し戻しを実行
 */
async function submitAction() {
  processing.value = true
  
  try {
    const action = isApproving.value ? 'approve' : 'reject'
    await monthlyRecordsApi.approval(
      selectedRecord.value.record_id,
      action,
      comment.value || null
    )
    
    closeModal()
    await fetchRecords()
  } catch (err) {
    alert(err.response?.data?.detail || '処理に失敗しました')
  } finally {
    processing.value = false
  }
}

/**
 * 年月をフォーマット
 */
function formatYearMonth(yearMonth) {
  if (!yearMonth) return ''
  const [year, month] = yearMonth.split('-')
  return `${year}年${parseInt(month)}月`
}

/**
 * 分を時間:分形式にフォーマット
 */
function formatMinutes(minutes) {
  if (!minutes) return '0:00'
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours}:${mins.toString().padStart(2, '0')}`
}

onMounted(fetchRecords)
</script>

<style scoped>
.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}
</style>
