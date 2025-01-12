<template>
  <div class="min-h-screen flex flex-col bg-gray-darker">
    <!-- Navigation -->
    <nav class="bg-gray-dark/50 backdrop-blur-md py-3 border-b border-yellow/5 sticky top-0 z-40">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex items-center justify-between gap-4">
          <!-- Navigation Dropdown -->
          <div class="relative">
            <button 
              @click="isMenuOpen = !isMenuOpen"
              class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white/70 rounded-lg transition-colors hover:text-white hover:bg-white/5"
            >
              <span>Menu</span>
              <svg 
                class="w-4 h-4 transition-transform duration-200"
                :class="{ 'rotate-180': isMenuOpen }"
                xmlns="http://www.w3.org/2000/svg" 
                viewBox="0 0 20 20" 
                fill="currentColor"
              >
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>

            <!-- Dropdown Menu -->
            <div 
              v-if="isMenuOpen" 
              class="absolute left-0 mt-2 w-48 rounded-lg bg-gray-dark/95 backdrop-blur-lg shadow-lg border border-yellow/5 py-2"
            >
              <router-link 
                v-for="route in routes" 
                :key="route.path"
                :to="route.path"
                class="block px-4 py-2 text-sm text-white/70 hover:text-yellow hover:bg-white/5"
                :class="{ 'text-yellow bg-white/5': currentRoute === route.path }"
                @click="isMenuOpen = false"
              >
                {{ route.name }}
              </router-link>
            </div>
          </div>

          <!-- Level Progress -->
          <div class="flex-1 max-w-xl px-6">
            <div class="flex items-center gap-3">
              <div class="font-display text-sm text-yellow whitespace-nowrap">{{ RANKS[rank] }}</div>
              <div class="flex-1 h-3 bg-gray-darker/80 rounded-full overflow-hidden shadow-[inset_0_1px_2px_rgba(0,0,0,0.3)] border border-yellow/10">
                <div 
                  class="h-full relative transition-all duration-300 ease-out"
                  :style="{ width: rank < 17 ? `${(exp / RANK_EXP[rank] * 100).toFixed(2)}%` : '100%' }"
                >
                  <div class="absolute inset-0 bg-gradient-to-r from-yellow/60 to-yellow/40"></div>
                  <div class="absolute inset-0 bg-gradient-to-r from-yellow via-yellow/80 to-yellow/60 animate-shimmer"
                       style="background-size: 200% 100%"></div>
                </div>
              </div>
              <div class="font-display text-xs font-medium text-white/70 tabular-nums whitespace-nowrap min-w-[120px] text-right">
                {{ rank < 17 ? `${Math.floor(exp).toLocaleString()}/${RANK_EXP[rank].toLocaleString()}` : 'MAX RANK' }}
              </div>
            </div>
          </div>

          <!-- Balance -->
          <div class="font-display text-sm tracking-wider whitespace-nowrap">
            Balance: <span class="text-yellow font-medium">${{ formatNumber(balance) }}</span>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="flex-1 relative">
      <!-- Background Pattern -->
      <div class="absolute inset-0 bg-gradient-dots opacity-50 pointer-events-none"></div>
      <div class="absolute inset-0 bg-gradient-to-b from-gray-darker via-gray-darker/95 to-gray-darker pointer-events-none"></div>
      
      <!-- Content -->
      <div class="relative">
        <router-view 
          :rank="rank"
          :exp="exp"
          :rankExp="RANK_EXP"
          :ranks="RANKS"
        ></router-view>
      </div>
    </div>

    <!-- Watermark -->
    <div class="text-center py-2 text-xs text-white/30 font-display tracking-wide border-t border-yellow/5">
      <span>Made by Ole Kristian Westby</span>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useStore, RANKS, RANK_EXP } from './store'

export default {
  name: 'App',
  setup() {
    const route = useRoute()
    const store = useStore()
    const isMenuOpen = ref(false)

    const routes = [
      { path: '/', name: 'Home' },
      { path: '/shop', name: 'Shop' },
      { path: '/inventory', name: 'Inventory' },
      { path: '/clicker', name: 'Clicker' },
      { path: '/upgrades', name: 'Upgrades' },
      { path: '/casino', name: 'Casino' },
      { path: '/trading', name: 'Trading' },
      { path: '/achievements', name: 'Achievements' },
      { path: '/auction', name: 'Auction' }
    ]

    const currentRoute = computed(() => route.path)

    // Computed values from store
    const rank = computed(() => store.state.rank)
    const exp = computed(() => store.state.exp)
    const balance = computed(() => store.state.balance)

    // Close menu when clicking outside
    const handleClickOutside = (event) => {
      if (isMenuOpen.value && !event.target.closest('.relative')) {
        isMenuOpen.value = false
      }
    }

    // Set up polling for user data updates
    let pollInterval
    onMounted(() => {
      // Initial fetch
      store.fetchUserData()
      
      // Set up polling every 2 seconds
      pollInterval = setInterval(() => {
        store.fetchUserData()
      }, 2000)

      // Add click outside listener
      document.addEventListener('click', handleClickOutside)
    })

    // Clean up interval and event listener on component unmount
    onUnmounted(() => {
      if (pollInterval) {
        clearInterval(pollInterval)
      }
      document.removeEventListener('click', handleClickOutside)
      store.cleanup() // Clean up auto clicker
    })

    // Utility functions for achievements and level up
    const createConfetti = () => {
      const confettiContainer = document.createElement('div')
      confettiContainer.className = 'confetti-container'
      document.body.appendChild(confettiContainer)
      
      const colors = ['#ffd700', '#ff0000', '#00ff00', '#0000ff', '#ff00ff', '#00ffff']
      
      for (let i = 0; i < 100; i++) {
        const confetti = document.createElement('div')
        confetti.className = 'confetti'
        confetti.style.left = Math.random() * 100 + 'vw'
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)]
        confetti.style.animation = `confettiFall ${1 + Math.random() * 2}s linear forwards`
        confetti.style.animationDelay = Math.random() * 3 + 's'
        confettiContainer.appendChild(confetti)
      }
      
      setTimeout(() => {
        confettiContainer.remove()
      }, 5000)
    }

    const showLevelUpBanner = (newRank) => {
      const banner = document.createElement('div')
      banner.className = 'level-up-banner'
      banner.innerHTML = `<h2>LEVEL UP: ${newRank}</h2>`
      document.body.appendChild(banner)
      
      setTimeout(() => {
        banner.remove()
      }, 3000)
    }

    const showAchievementPopup = (achievement) => {
      const popup = document.createElement('div')
      popup.className = 'achievement-popup'
      
      const rewardsText = achievement.exp_reward > 0 
        ? `+$${achievement.reward.toLocaleString()} • ${achievement.exp_reward.toLocaleString()} EXP`
        : `+$${achievement.reward.toLocaleString()}`
      
      popup.innerHTML = `
        <div class="icon">${achievement.icon}</div>
        <div class="content">
          <div class="title">Achievement Unlocked!</div>
          <div class="description">${achievement.title}</div>
          <div class="rewards">${rewardsText}</div>
        </div>
      `
      
      document.body.appendChild(popup)
      
      setTimeout(() => {
        popup.remove()
      }, 4000)
    }

    const handleAchievementComplete = (data) => {
      // Update store instead of local state
      store.updateUserData(data)
      
      // Show achievement completion popup if there's achievement data
      if (data.achievement) {
        showAchievementPopup(data.achievement)
      }
      
      // Show level up animation if needed
      if (data.levelUp) {
        createConfetti()
        showLevelUpBanner(RANKS[store.state.rank])
      }
    }

    // Utility function for formatting numbers
    const formatNumber = (num) => {
      if (num >= 1000000) {
        return (num / 1000000).toFixed(2) + 'M'
      } else if (num >= 1000) {
        return (num / 1000).toFixed(2) + 'K'
      } else {
        return num.toFixed(2)
      }
    }

    return {
      rank,
      exp,
      balance,
      RANKS,
      RANK_EXP,
      routes,
      currentRoute,
      isMenuOpen,
      handleAchievementComplete,
      formatNumber,
    }
  }
}
</script>

<style>
/* Add these styles for the exp bar animation */
@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.animate-shimmer {
  animation: shimmer 3s linear infinite;
}

/* Adjust nav link styles */
.nav-link {
  @apply px-3 py-1.5 text-sm font-medium text-white/70 rounded-lg transition-colors hover:text-white hover:bg-white/5;
}

.nav-link.active {
  @apply text-yellow bg-yellow/10;
}
</style>
