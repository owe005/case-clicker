import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/shop',
    name: 'Shop',
    component: () => import('../views/Shop.vue')
  },
  {
    path: '/inventory',
    name: 'Inventory',
    component: () => import('../views/Inventory.vue')
  },
  {
    path: '/clicker',
    name: 'Clicker',
    component: () => import('../views/ClickerView.vue')
  },
  {
    path: '/upgrades',
    name: 'Upgrades',
    component: () => import('../views/UpgradesView.vue')
  },
  {
    path: '/casino',
    name: 'Casino',
    component: () => import('../views/CasinoView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router 