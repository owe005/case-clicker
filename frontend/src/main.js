import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { useStore } from './store'
import './assets/tailwind.css'
import './assets/app.css'
import './assets/roulette.css'
import './assets/clicker.css'

const app = createApp(App)

// Initialize store
const store = useStore()

// Provide store to app
app.provide('store', store)

app.use(router)
app.mount('#app')
