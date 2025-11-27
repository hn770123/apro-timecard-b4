/**
 * メインエントリーポイント
 * Vue.jsアプリケーションを初期化
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'

// アプリケーションを作成
const app = createApp(App)

// Piniaストアを使用
app.use(createPinia())

// Vue Routerを使用
app.use(router)

// アプリケーションをマウント
app.mount('#app')
