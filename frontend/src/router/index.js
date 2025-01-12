import { createRouter, createWebHistory } from 'vue-router'
import JackpotView from '../views/JackpotView.vue'
import CoinflipView from '../views/CoinflipView.vue'
import RouletteView from '../views/RouletteView.vue'
import TradingView from '../views/TradingView.vue'
import BlackjackView from '../views/BlackjackView.vue'

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
  },
  {
    path: '/blackjack',
    name: 'Blackjack',
    component: BlackjackView
  },
  {
    path: '/jackpot',
    name: 'jackpot',
    component: JackpotView
  },
  {
    path: '/coinflip',
    name: 'coinflip',
    component: CoinflipView
  },
  {
    path: '/crash',
    name: 'Crash',
    component: () => import('../views/CrashView.vue')
  },
  {
    path: '/upgrade',
    name: 'Upgrade',
    component: () => import('../views/UpgradeView.vue')
  },
  {
    path: '/roulette',
    name: 'roulette',
    component: RouletteView
  },
  {
    path: '/trading',
    name: 'trading',
    component: TradingView
  },
  {
    path: '/achievements',
    name: 'Achievements',
    component: () => import('../views/AchievementsView.vue')
  },
  {
    path: '/auction',
    name: 'Auction',
    component: () => import('../views/AuctionView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router 