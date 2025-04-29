import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import i18n from './i18n'

import './assets/main.css'

const app = createApp(App)

// Initialiser Pinia
const pinia = createPinia()
app.use(pinia)

// Initialiser le router
app.use(router)

// Initialiser i18n
app.use(i18n)

// Initialiser l'authentification
import { useAuthStore } from './stores/auth'
const auth = useAuthStore()
auth.initializeAuth()

app.mount('#app')
