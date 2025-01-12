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

// Add navigation guard to ensure store is initialized
router.beforeEach(async (to, from, next) => {
    try {
        // Fetch user data if not already loaded
        if (!store.state.lastUpdate || Date.now() - store.state.lastUpdate > 5000) {
            await store.fetchUserData()
        }
        next()
    } catch (error) {
        console.error('Failed to initialize store:', error)
        next()
    }
})

// Provide store to app
app.provide('store', store)

app.use(router)
app.mount('#app')
