import { createPinia } from 'pinia'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import 'vue-sonner/style.css'
import './style.css'
import './composables/useTheme'

createApp(App).use(createPinia()).use(router).mount('#app')
