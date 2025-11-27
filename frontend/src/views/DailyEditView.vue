<!--
/**
 * 日次記録編集画面
 * 日ごとの勤務データを入力/編集
 */
-->
<template>
  <div class="daily-edit">
    <div class="page-header">
      <router-link
        :to="{ name: 'daily-list', params: { recordId: recordId } }"
        class="back-link"
      >
        ← 日次一覧に戻る
      </router-link>
      <h1 class="page-title">
        {{ isEdit ? '日次記録の編集' : '日次記録の新規入力' }}
      </h1>
    </div>
    
    <!-- ローディング -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>
    
    <!-- エラー -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    
    <!-- フォーム -->
    <form v-else @submit.prevent="saveRecord" class="card">
      <div class="form-row">
        <div class="form-group">
          <label for="recordDate" class="form-label">日付</label>
          <input
            id="recordDate"
            v-model="formData.record_date"
            type="date"
            class="form-control"
            :disabled="isEdit"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="patternNumber" class="form-label">勤務パターン</label>
          <select
            id="patternNumber"
            v-model="formData.pattern_number"
            class="form-control"
          >
            <option :value="1">パターン1</option>
            <option :value="2">パターン2</option>
            <option :value="3">パターン3</option>
          </select>
        </div>
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label for="workType" class="form-label">勤務の種類</label>
          <select
            id="workType"
            v-model="formData.work_type"
            class="form-control"
            required
          >
            <option value="work">出勤</option>
            <option value="remote">出勤（リモート）</option>
            <option value="late">遅刻</option>
            <option value="early_leave">早退</option>
            <option value="late_and_early">遅刻かつ早退</option>
            <option value="holiday_legal">休日（法定）</option>
            <option value="holiday_extra">休日（法定外）</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="leaveType" class="form-label">休暇種類</label>
          <select
            id="leaveType"
            v-model="formData.leave_type"
            class="form-control"
          >
            <option value="none">なし</option>
            <option value="paid">有休</option>
            <option value="absence">欠勤</option>
            <option value="special">特休</option>
            <option value="condolence">慶弔</option>
          </select>
        </div>
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label for="startTime" class="form-label">出勤時刻</label>
          <input
            id="startTime"
            v-model="formData.start_time"
            type="time"
            class="form-control"
          />
        </div>
        
        <div class="form-group">
          <label for="endTime" class="form-label">退勤時刻</label>
          <input
            id="endTime"
            v-model="formData.end_time"
            type="time"
            class="form-control"
          />
        </div>
      </div>
      
      <!-- 手動調整エリア -->
      <details class="manual-adjust">
        <summary>時間の手動調整（自動計算を上書き）</summary>
        <div class="form-row mt-1">
          <div class="form-group">
            <label for="lateMinutes" class="form-label">遅刻時間（分）</label>
            <input
              id="lateMinutes"
              v-model.number="formData.late_minutes"
              type="number"
              min="0"
              class="form-control"
            />
          </div>
          
          <div class="form-group">
            <label for="earlyLeaveMinutes" class="form-label">早退時間（分）</label>
            <input
              id="earlyLeaveMinutes"
              v-model.number="formData.early_leave_minutes"
              type="number"
              min="0"
              class="form-control"
            />
          </div>
          
          <div class="form-group">
            <label for="overtimeMinutes" class="form-label">残業時間（分）</label>
            <input
              id="overtimeMinutes"
              v-model.number="formData.overtime_minutes"
              type="number"
              min="0"
              class="form-control"
            />
          </div>
        </div>
      </details>
      
      <div class="form-group">
        <label for="note" class="form-label">
          補足欄
          <span v-if="isNoteRequired" class="required-mark">（必須）</span>
        </label>
        <textarea
          id="note"
          v-model="formData.note"
          class="form-control"
          rows="3"
          :class="{ error: isNoteRequired && !formData.note }"
          placeholder="出勤以外の場合は理由を入力してください"
        ></textarea>
        <p v-if="isNoteRequired && !formData.note" class="error-message">
          出勤以外の場合は補足欄への入力が必要です
        </p>
      </div>
      
      <div class="form-actions">
        <router-link
          :to="{ name: 'daily-list', params: { recordId: recordId } }"
          class="btn btn-secondary"
        >
          キャンセル
        </router-link>
        <button
          v-if="isEdit"
          type="button"
          @click="deleteRecord"
          class="btn btn-danger"
          :disabled="saving"
        >
          削除
        </button>
        <button type="submit" class="btn btn-primary" :disabled="saving">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { dailyRecordsApi } from '@/services/api'

const route = useRoute()
const router = useRouter()

const recordId = route.params.recordId
const dailyId = route.params.dailyId

const isEdit = computed(() => !!dailyId)

const loading = ref(false)
const error = ref(null)
const saving = ref(false)

const formData = ref({
  record_date: '',
  work_type: 'work',
  leave_type: 'none',
  pattern_number: 1,
  start_time: '',
  end_time: '',
  late_minutes: null,
  early_leave_minutes: null,
  overtime_minutes: null,
  note: ''
})

// 補足欄が必須かどうか
const isNoteRequired = computed(() => {
  return !['work', 'remote'].includes(formData.value.work_type)
})

/**
 * 既存データを取得（編集時）
 */
async function fetchData() {
  if (!isEdit.value) return
  
  loading.value = true
  error.value = null
  
  try {
    const record = await dailyRecordsApi.get(dailyId)
    formData.value = {
      record_date: record.record_date,
      work_type: record.work_type,
      leave_type: record.leave_type,
      pattern_number: record.pattern_number,
      start_time: record.start_time || '',
      end_time: record.end_time || '',
      late_minutes: record.late_minutes || null,
      early_leave_minutes: record.early_leave_minutes || null,
      overtime_minutes: record.overtime_minutes || null,
      note: record.note || ''
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'データの取得に失敗しました'
  } finally {
    loading.value = false
  }
}

/**
 * レコードを保存
 */
async function saveRecord() {
  // 補足欄のバリデーション
  if (isNoteRequired.value && !formData.value.note) {
    alert('出勤以外の場合は補足欄への入力が必要です')
    return
  }
  
  saving.value = true
  
  try {
    if (isEdit.value) {
      await dailyRecordsApi.update(dailyId, formData.value)
    } else {
      await dailyRecordsApi.create(recordId, formData.value)
    }
    
    router.push({ name: 'daily-list', params: { recordId } })
  } catch (err) {
    alert(err.response?.data?.detail || '保存に失敗しました')
  } finally {
    saving.value = false
  }
}

/**
 * レコードを削除
 */
async function deleteRecord() {
  if (!confirm('この日次記録を削除しますか？')) return
  
  saving.value = true
  
  try {
    await dailyRecordsApi.delete(dailyId)
    router.push({ name: 'daily-list', params: { recordId } })
  } catch (err) {
    alert(err.response?.data?.detail || '削除に失敗しました')
  } finally {
    saving.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.back-link {
  display: inline-block;
  margin-bottom: 0.5rem;
  color: var(--secondary-color);
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.manual-adjust {
  margin: 1rem 0;
  padding: 1rem;
  background-color: var(--light-color);
  border-radius: var(--border-radius);
}

.manual-adjust summary {
  cursor: pointer;
  color: var(--secondary-color);
}

.required-mark {
  color: var(--danger-color);
  font-size: 0.875rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}
</style>
