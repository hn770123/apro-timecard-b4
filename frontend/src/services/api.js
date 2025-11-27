/**
 * API通信サービス
 * axiosを使用したHTTPクライアント
 */
import axios from 'axios'

// APIベースURL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

/**
 * axiosインスタンス
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * リクエストインターセプター
 * 認証トークンを自動付与
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

/**
 * レスポンスインターセプター
 * 認証エラー時の処理
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

/**
 * 認証API
 */
export const authApi = {
  /**
   * ログイン
   */
  async login(email, password) {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)
    
    const response = await apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },
  
  /**
   * 現在のユーザー情報取得
   */
  async getCurrentUser() {
    const response = await apiClient.get('/auth/me')
    return response.data
  }
}

/**
 * ユーザー管理API
 */
export const usersApi = {
  /**
   * ユーザー一覧取得
   */
  async list() {
    const response = await apiClient.get('/users')
    return response.data
  },
  
  /**
   * ユーザー作成
   */
  async create(userData) {
    const response = await apiClient.post('/users', userData)
    return response.data
  },
  
  /**
   * ユーザー取得
   */
  async get(userId) {
    const response = await apiClient.get(`/users/${userId}`)
    return response.data
  },
  
  /**
   * ユーザー更新
   */
  async update(userId, userData) {
    const response = await apiClient.put(`/users/${userId}`, userData)
    return response.data
  },
  
  /**
   * ユーザー削除
   */
  async delete(userId) {
    await apiClient.delete(`/users/${userId}`)
  }
}

/**
 * 勤務パターンAPI
 */
export const workPatternsApi = {
  /**
   * パターン一覧取得
   */
  async list(yearMonth) {
    const response = await apiClient.get('/work-patterns', { params: { year_month: yearMonth } })
    return response.data
  },
  
  /**
   * パターン作成
   */
  async create(patternData) {
    const response = await apiClient.post('/work-patterns', patternData)
    return response.data
  },
  
  /**
   * パターン更新
   */
  async update(patternId, patternData) {
    const response = await apiClient.put(`/work-patterns/${patternId}`, patternData)
    return response.data
  },
  
  /**
   * パターン削除
   */
  async delete(patternId) {
    await apiClient.delete(`/work-patterns/${patternId}`)
  },
  
  /**
   * 前月からコピー
   */
  async copyFromPrevious(targetYearMonth) {
    const response = await apiClient.post('/work-patterns/copy-from-previous', null, {
      params: { target_year_month: targetYearMonth }
    })
    return response.data
  }
}

/**
 * 月次記録API
 */
export const monthlyRecordsApi = {
  /**
   * 月次記録一覧取得
   */
  async list() {
    const response = await apiClient.get('/monthly-records')
    return response.data
  },
  
  /**
   * 月次記録作成
   */
  async create(recordData) {
    const response = await apiClient.post('/monthly-records', recordData)
    return response.data
  },
  
  /**
   * 月次記録取得
   */
  async get(recordId) {
    const response = await apiClient.get(`/monthly-records/${recordId}`)
    return response.data
  },
  
  /**
   * 月次記録更新
   */
  async update(recordId, recordData) {
    const response = await apiClient.put(`/monthly-records/${recordId}`, recordData)
    return response.data
  },
  
  /**
   * 承認待ち一覧取得
   */
  async listPending() {
    const response = await apiClient.get('/monthly-records/pending')
    return response.data
  },
  
  /**
   * 承認アクション
   */
  async approval(recordId, action, comment = null) {
    const response = await apiClient.post(`/monthly-records/${recordId}/approval`, {
      action,
      comment
    })
    return response.data
  }
}

/**
 * 日次記録API
 */
export const dailyRecordsApi = {
  /**
   * 日次記録一覧取得
   */
  async list(monthlyRecordId) {
    const response = await apiClient.get(`/daily-records/monthly/${monthlyRecordId}`)
    return response.data
  },
  
  /**
   * 日次記録作成
   */
  async create(monthlyRecordId, recordData) {
    const response = await apiClient.post('/daily-records', recordData, {
      params: { monthly_record_id: monthlyRecordId }
    })
    return response.data
  },
  
  /**
   * 日次記録取得
   */
  async get(recordId) {
    const response = await apiClient.get(`/daily-records/${recordId}`)
    return response.data
  },
  
  /**
   * 日次記録更新
   */
  async update(recordId, recordData) {
    const response = await apiClient.put(`/daily-records/${recordId}`, recordData)
    return response.data
  },
  
  /**
   * 日次記録削除
   */
  async delete(recordId) {
    await apiClient.delete(`/daily-records/${recordId}`)
  }
}

export default apiClient
