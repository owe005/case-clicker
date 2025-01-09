<template>
  <div class="min-h-screen flex flex-col bg-gray-darker">
    <!-- Navigation -->
    <nav class="bg-gray-dark/50 backdrop-blur-md py-3 border-b border-yellow/5 sticky top-0 z-40">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex items-center justify-between gap-4">
          <!-- Navigation Links -->
          <div class="flex gap-3">
            <router-link 
              v-for="route in routes" 
              :key="route.path"
              :to="route.path"
              class="nav-link"
              :class="{ active: currentRoute === route.path }"
            >
              {{ route.name }}
            </router-link>
            <router-link to="/upgrades" class="nav-link">
              Upgrades
            </router-link>
            <router-link to="/casino" class="nav-link">
              Casino
            </router-link>
          </div>

          <!-- Level Progress -->
          <div class="flex-1 max-w-xl px-6">
            <div class="flex items-center gap-3">
              <div class="font-display text-sm text-yellow whitespace-nowrap">{{ ranks[rank] }}</div>
              <div class="flex-1 h-2 bg-gray-darker rounded-full overflow-hidden shadow-[inset_0_1px_2px_rgba(0,0,0,0.2)]">
                <div 
                  class="h-full relative transition-all duration-300"
                  :style="{ width: rank < 17 ? `${(exp / rankExp[rank] * 100).toFixed(2)}%` : '100%' }"
                >
                  <div class="absolute inset-0 bg-gradient-to-r from-yellow/60 to-yellow/40"></div>
                  <div class="absolute inset-0 bg-gradient-to-r from-yellow via-yellow/80 to-yellow/60 animate-shimmer"
                       style="background-size: 200% 100%"></div>
                </div>
              </div>
              <div class="font-display text-xs font-medium text-white/70 tabular-nums whitespace-nowrap">
                {{ rank < 17 ? `${Math.floor(exp).toLocaleString()}/${rankExp[rank].toLocaleString()}` : 'MAX RANK' }}
              </div>
            </div>
          </div>

          <!-- Balance -->
          <div class="font-display text-sm tracking-wider whitespace-nowrap">
            Balance: <span class="text-yellow font-medium">${{ balance.toFixed(2) }}</span>
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
          :rankExp="rankExp"
          :ranks="ranks"
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
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const route = useRoute()
    const rank = ref(0)
    const exp = ref(0)
    const balance = ref(1000)

    const ranks = [
      'Silver I', 'Silver II', 'Silver III', 'Silver IV', 'Silver Elite', 'Silver Elite Master',
      'Gold Nova I', 'Gold Nova II', 'Gold Nova III', 'Gold Nova Master',
      'Master Guardian I', 'Master Guardian II', 'Master Guardian Elite', 'Distinguished Master Guardian',
      'Legendary Eagle', 'Legendary Eagle Master', 'Supreme Master First Class', 'Global Elite'
    ]

    const rankExp = [
      100, 200, 400, 800, 1600, 3200,
      6400, 12800, 25600, 51200, 102400, 204800,
      409600, 819200, 1638400, 3276800, 6553600
    ]

    const routes = [
      { path: '/', name: 'Home' },
      { path: '/shop', name: 'Shop' },
      { path: '/inventory', name: 'Inventory' },
      { path: '/clicker', name: 'Clicker' },
      { path: '/upgrades', name: 'Upgrades' }
    ]

    const currentRoute = computed(() => route.path)

    return {
      rank,
      exp,
      balance,
      ranks,
      rankExp,
      routes,
      currentRoute
    }
  }
}
</script>
