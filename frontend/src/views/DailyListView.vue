<!--
/**
 * 日次記録一覧画面
 * 月間の日次勤務データを一覧表示
 */
-->
<template>
  <div class="daily-list">
    <div class="page-header">
      <router-link to="/monthly" class="back-link">
        ← 月報一覧に戻る
      </router-link>
      <h1 class="page-title">
        {{ monthlyRecord?.name }} - {{ formatYearMonth(monthlyRecord?.year_month) }}
      </h1>
      <div class="header-info d-flex gap-2 mt-1">
        <span>所属: {{ monthlyRecord?.department }}</span>
        <span :class="['badge', getStatusBadgeClass(monthlyRecord?.status)]">
          {{ getStatusLabel(monthlyRecord?.status) }}
        </span>
      </div>
    </div>
    
    <!-- 集計サマリー -->
    <div v-if="monthlyRecord" class="card summary-card">
      <div class="summary-grid">
        <div class="summary-item">
          <span class="summary-label">勤務日数</span>
          <span class="summary-value">{{ monthlyRecord.total_work_days }}日</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">総労働時間</span>
          <span class="summary-value">{{ formatMinutes(monthlyRecord.total_work_minutes) }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">残業時間</span>
          <span class="summary-value">{{ formatMinutes(monthlyRecord.total_overtime_minutes) }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">深夜残業</span>
          <span class="summary-value">{{ formatMinutes(monthlyRecord.total_night_overtime_minutes) }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">遅刻</span>
          <span class="summary-value">{{ formatMinutes(monthlyRecord.total_late_minutes) }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">早退</span>
          <span class="summary-value">{{ formatMinutes(monthlyRecord.total_early_leave_minutes) }}</span>
        </div>
      </div>
    </div>
    
    <!-- 操作ボタン -->
    <div v-if="monthlyRecord?.can_edit" class="d-flex gap-1 mb-2">
      <router-link
        :to="{ name: 'daily-edit', params: { recordId: recordId } }"
        class="btn btn-primary"
      >
        新規日次入力
      </router-link>
    </div>
    
    <!-- ローディング -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>
    
    <!-- エラー -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    
    <!-- 日次記録一覧 -->
    <div v-else>
      <table class="table">
        <thead>
          <tr>
            <th>日付</th>
            <th>勤務種類</th>
            <th>出勤</th>
            <th>退勤</th>
            <th>労働時間</th>
            <th>残業</th>
            <th>遅刻</th>
            <th>早退</th>
            <th>補足</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="record in dailyRecords" :key="record.record_id">
            <td>{{ formatDate(record.record_date) }}</td>
            <td>
              <span :class="['work-type', `type-${record.work_type}`]">
                {{ getWorkTypeLabel(record.work_type) }}
              </span>
            </td>
            <td>{{ record.start_time || '-' }}</td>
            <td>{{ record.end_time || '-' }}</td>
            <td>{{ formatMinutes(record.work_minutes) }}</td>
            <td>{{ formatMinutes(record.overtime_minutes) }}</td>
            <td>{{ record.late_minutes > 0 ? formatMinutes(record.late_minutes) : '-' }}</td>
            <td>{{ record.early_leave_minutes > 0 ? formatMinutes(record.early_leave_minutes) : '-' }}</td>
            <td>
              <span v-if="record.is_note_required && !record.note" class="alert-icon" title="補足が必要です">
                ⚠️
              </span>
              {{ record.note || '-' }}
            </td>
            <td>
              <router-link
                v-if="monthlyRecord?.can_edit"
                :to="{ name: 'daily-edit', params: { recordId: recordId, dailyId: record.record_id } }"
                class="btn btn-outline btn-sm"
              >
                編集
              </router-link>
              <span v-else>-</span>
            </td>
          </tr>
          <tr v-if="dailyRecords.length === 0">
            <td colspan="10" class="text-center">データがありません</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { monthlyRecordsApi, dailyRecordsApi } from '@/services/api'

const route = useRoute()
const recordId = route.params.recordId

const monthlyRecord = ref(null)
const dailyRecords = ref([])
const loading = ref(true)
const error = ref(null)

/**
 * データを取得
 */
async function fetchData() {
  loading.value = true
  error.value = null
  
  try {
    // 月次記録を取得
    monthlyRecord.value = await monthlyRecordsApi.get(recordId)
    
    // 日次記録を取得
    dailyRecords.value = await dailyRecordsApi.list(recordId)
  } catch (err) {
    error.value = err.response?.data?.detail || 'データの取得に失敗しました'
  } finally {
    loading.value = false
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
 * 日付をフォーマット
 */
function formatDate(dateStr) {
  const date = new Date(dateStr)
  const dayNames = ['日', '月', '火', '水', '木', '金', '土']
  const day = date.getDate()
  const dayOfWeek = dayNames[date.getDay()]
  return `${day}日(${dayOfWeek})`
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

/**
 * 勤務種類ラベルを取得
 */
function getWorkTypeLabel(type) {
  const labels = {
    work: '出勤',
    remote: 'リモート',
    late: '遅刻',
    early_leave: '早退',
    late_and_early: '遅刻/早退',
    holiday_legal: '休日(法定)',
    holiday_extra: '休日(法定外)'
  }
  return labels[type] || type
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

onMounted(fetchData)
</script>

<style scoped>
.back-link {
  display: inline-block;
  margin-bottom: 0.5rem;
  color: var(--secondary-color);
}

.header-info {
  font-size: 0.875rem;
  color: var(--secondary-color);
}

.summary-card {
  margin-bottom: 1.5rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.summary-item {
  text-align: center;
}

.summary-label {
  display: block;
  font-size: 0.875rem;
  color: var(--secondary-color);
}

.summary-value {
  display: block;
  font-size: 1.25rem;
  font-weight: 600;
}

.work-type {
  padding: 0.125rem 0.5rem;
  border-radius: var(--border-radius);
  font-size: 0.875rem;
}

.type-work, .type-remote {
  background-color: #d4edda;
  color: #155724;
}

.type-late, .type-early_leave, .type-late_and_early {
  background-color: #fff3cd;
  color: #856404;
}

.type-holiday_legal, .type-holiday_extra {
  background-color: #e2e3e5;
  color: #383d41;
}

.alert-icon {
  cursor: help;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}
</style>
