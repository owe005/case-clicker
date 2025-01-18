<template>
  <div class="min-h-screen bg-gray-darker">
    <!-- Header -->
    <div class="relative py-12 mb-8">
      <div class="absolute inset-0 bg-gradient-to-b from-yellow/5 to-transparent"></div>
      <div class="relative max-w-7xl mx-auto px-4">
        <h1 class="text-4xl font-display font-bold text-white mb-2">Trading</h1>
        <p class="text-white/70">Trade skins with other players</p>
        <div class="mt-4 text-white/50">Next reset in: <span id="resetTimer">--:--:--</span></div>
      </div>
    </div>

    <!-- Content -->
    <div class="max-w-7xl mx-auto px-4 pb-12">
      <!-- Trade Filters -->
      <div class="flex flex-wrap gap-3 mb-8">
        <button 
          v-for="filter in filters" 
          :key="filter.id"
          class="px-4 py-2 rounded-lg font-medium transition-all duration-200"
          :class="[
            currentFilter === filter.id 
              ? 'bg-yellow text-gray-darker' 
              : 'bg-gray-dark/50 text-white/70 hover:bg-gray-dark hover:text-white'
          ]"
          @click="currentFilter = filter.id"
        >
          {{ filter.name }}
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-8 text-white/50">
        Loading trades...
      </div>

      <!-- Trades Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="(trade, index) in filteredTrades" 
          :key="trade.botName + index"
          class="glass-panel p-6 relative group transition-all duration-300"
        >
          <!-- Trade Header -->
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-gray-dark/50 flex items-center justify-center overflow-hidden">
                <img :src="'/casino/' + trade.botAvatar" :alt="trade.botName" class="w-full h-full object-cover">
              </div>
              <div>
                <div class="font-display text-yellow">{{ trade.botName }}</div>
              </div>
            </div>
            <div 
              class="px-2 py-1 rounded text-xs font-medium"
              :class="{
                'bg-emerald-400/20 text-emerald-400': trade.type === 'buy',
                'bg-red-400/20 text-red-400': trade.type === 'sell',
                'bg-purple-400/20 text-purple-400': trade.type === 'swap'
              }"
            >
              {{ trade.type.charAt(0).toUpperCase() + trade.type.slice(1) }}
            </div>
          </div>

          <!-- Trade Content -->
          <div class="space-y-4">
            <!-- Offering -->
            <div>
              <div class="text-sm text-white/50 mb-2">Offering:</div>
              <div v-for="(item, itemIndex) in trade.offering" :key="'offering-' + itemIndex" 
                   class="bg-gray-dark/30 rounded-lg p-3 flex items-center gap-3 mb-2">
                <template v-if="item.type === 'money'">
                  <div class="text-emerald-400 font-medium">${{ item.amount.toFixed(2) }}</div>
                </template>
                <template v-else>
                  <img 
                    :src="getItemImage(item)" 
                    :alt="getItemAlt(item)"
                    class="w-16 h-16 object-contain"
                    @error="handleImageError"
                  >
                  <div>
                    <div class="text-sm text-white">
                      {{ getItemDisplayName(item) }}
                    </div>
                    <div class="text-xs text-white/50">{{ item.wear || item.rarity }}</div>
                    <div class="text-sm text-yellow">${{ item.price.toFixed(2) }}</div>
                  </div>
                </template>
              </div>
            </div>

            <!-- Requesting -->
            <div>
              <div class="text-sm text-white/50 mb-2">Requesting:</div>
              <div v-for="(item, itemIndex) in trade.requesting" :key="'requesting-' + itemIndex" 
                   class="bg-gray-dark/30 rounded-lg p-3 flex items-center gap-3 mb-2">
                <template v-if="item.type === 'money'">
                  <div class="text-emerald-400 font-medium">${{ item.amount.toFixed(2) }}</div>
                </template>
                <template v-else>
                  <img 
                    :src="getItemImage(item)" 
                    :alt="getItemAlt(item)"
                    class="w-16 h-16 object-contain"
                    @error="handleImageError"
                  >
                  <div>
                    <div class="text-sm text-white">
                      {{ getItemDisplayName(item) }}
                    </div>
                    <div class="text-xs text-white/50">{{ item.wear || item.rarity }}</div>
                    <div class="text-sm text-yellow">${{ item.price.toFixed(2) }}</div>
                  </div>
                </template>
              </div>
            </div>

            <!-- Trade Button -->
            <button 
              class="w-full py-2 px-4 bg-yellow text-gray-darker rounded-lg font-medium transition-all duration-200 hover:bg-yellow/90"
              @click="handleTrade(index)"
            >
              Trade Now
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Trade Confirmation Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
      <div class="bg-gray-dark max-w-lg w-full mx-4 rounded-xl p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-display text-white">Confirm Trade</h3>
          <button @click="showModal = false" class="text-white/50 hover:text-white">&times;</button>
        </div>
        <div v-if="selectedTrade" class="space-y-4">
          <p class="text-white">Are you sure you want to trade with {{ selectedTrade.botName }}?</p>
          
          <!-- Trade Details -->
          <div class="space-y-4">
            <div>
              <div class="text-sm text-white/50 mb-2">You will receive:</div>
              <div v-for="(item, index) in selectedTrade.offering" :key="'modal-offering-' + index" 
                   class="text-white">
                <template v-if="item.type === 'money'">
                  <div class="text-emerald-400">${{ item.amount.toFixed(2) }}</div>
                </template>
                <template v-else>
                  {{ item.stattrak ? 'StatTrak™ ' : '' }}{{ item.weapon }} | {{ item.name }} ({{ item.wear }})
                </template>
              </div>
            </div>
            
            <div>
              <div class="text-sm text-white/50 mb-2">You will give:</div>
              <div v-for="(item, index) in selectedTrade.requesting" :key="'modal-requesting-' + index" 
                   class="text-white">
                <template v-if="item.type === 'money'">
                  <div class="text-emerald-400">${{ item.amount.toFixed(2) }}</div>
                </template>
                <template v-else>
                  {{ item.stattrak ? 'StatTrak™ ' : '' }}{{ item.weapon }} | {{ item.name }} ({{ item.wear }})
                </template>
              </div>
            </div>
          </div>

          <div class="flex justify-end gap-3 mt-6">
            <button 
              @click="showModal = false"
              class="px-4 py-2 bg-red-500/20 text-red-500 rounded-lg hover:bg-red-500/30"
            >
              Cancel
            </button>
            <button 
              @click="completeTrade"
              class="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600"
            >
              Confirm
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast Container -->
    <div class="fixed bottom-4 left-1/2 -translate-x-1/2 space-y-2">
      <div v-for="toast in toasts" :key="toast.id"
           class="px-4 py-2 rounded-lg shadow-lg transition-all duration-300"
           :class="[
             toast.type === 'success' ? 'bg-emerald-500 text-white' : 'bg-red-500 text-white',
             'animate-slide-up'
           ]">
        {{ toast.message }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from '../store'
import { CASE_MAPPING } from '../store'

export default {
  name: 'TradingView',
  setup() {
    const store = useStore()

    const currentFilter = ref('all')
    const isLoading = ref(true)
    const trades = ref([])
    const showModal = ref(false)
    const selectedTrade = ref(null)
    const selectedTradeIndex = ref(null)
    const toasts = ref([])


    const filters = [
      { id: 'all', name: 'All Trades' },
      { id: 'buy', name: 'Buy Skins' },
      { id: 'sell', name: 'Sell Skins' },
      { id: 'swap', name: 'Swap Skins' }
    ]

    const filteredTrades = computed(() => {
      if (currentFilter.value === 'all') return trades.value
      return trades.value.filter(trade => trade.type === currentFilter.value)
    })

    // Helper function to get item image URL
    const getItemImage = (item) => {
      if (item.type === 'money') return ''
      if (item.is_sticker) {
        return `/sticker_skins/${item.case_type}/${item.image}`
      }
      if (!item.image || !item.case_type) {
        return '/skins/rare_item.png'
      }
      const casePath = CASE_MAPPING[item.case_type] || item.case_type
      return `/skins/${casePath}/${item.image}`
    }

    // Helper function to get item alt text
    const getItemAlt = (item) => {
      if (item.type === 'money') return 'Money'
      if (item.is_sticker) return item.name
      return `${item.weapon} | ${item.name}`
    }

    // Helper function to get item display name
    const getItemDisplayName = (item) => {
      if (item.type === 'money') return `$${item.amount.toFixed(2)}`
      if (item.is_sticker) return item.name
      return `${item.stattrak ? 'StatTrak™ ' : ''}${item.weapon} | ${item.name}`
    }

    // Handle image loading errors
    const handleImageError = (event) => {
      event.target.src = '/skins/rare_item.png'
    }

    // Fetch trades from the server
    const fetchTrades = async () => {
      try {
        isLoading.value = true
        const response = await fetch('/get_trades')
        const data = await response.json()

        if (data.error) {
          showToast(data.error, 'error')
          return
        }

        trades.value = data.trades
      } catch (error) {
        console.error('Error fetching trades:', error)
        showToast('Failed to load trades', 'error')
      } finally {
        isLoading.value = false
      }
    }

    // Handle trade button click
    const handleTrade = (index) => {
      selectedTrade.value = trades.value[index]
      selectedTradeIndex.value = index
      showModal.value = true
    }

    // Complete the trade
    const completeTrade = async () => {
      try {
        const response = await fetch('/complete_trade', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ trade: selectedTrade.value })
        })

        const data = await response.json()

        if (data.error) {
          if (data.error === 'Trade no longer available') {
            trades.value.splice(selectedTradeIndex.value, 1)
            showToast('This trade is no longer available', 'error')
          } else {
            showToast(data.error, 'error')
          }
          showModal.value = false
          return
        }

        // Update store with new data
        store.updateUserData(data)

        // Remove the completed trade
        trades.value.splice(selectedTradeIndex.value, 1)
        showModal.value = false

        // Show success message
        showToast(`Trade completed! +${Math.floor(data.expGained)} EXP`, 'success')
      } catch (error) {
        console.error('Error completing trade:', error)
        showToast('Failed to complete trade', 'error')
      }
    }

    // Toast notification system
    const showToast = (message, type = 'success') => {
      const toast = {
        id: Date.now(),
        message,
        type
      }
      toasts.value.push(toast)
      setTimeout(() => {
        toasts.value = toasts.value.filter(t => t.id !== toast.id)
      }, 3000)
    }

    // Timer update
    const updateTimer = () => {
      const now = new Date()
      const tomorrow = new Date(now)
      tomorrow.setDate(tomorrow.getDate() + 1)
      tomorrow.setHours(0, 0, 0, 0)
      
      const timeLeft = tomorrow - now
      const hours = Math.floor(timeLeft / (1000 * 60 * 60))
      const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60))
      const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000)
      
      const timerElement = document.getElementById('resetTimer')
      if (timerElement) {
        timerElement.textContent = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
      }
    }

    // Lifecycle hooks
    onMounted(() => {
      fetchTrades()
      updateTimer()
    })

    return {
      currentFilter,
      filters,
      trades,
      filteredTrades,
      isLoading,
      showModal,
      selectedTrade,
      toasts,
      getItemImage,
      getItemAlt,
      getItemDisplayName,
      handleImageError,
      handleTrade,
      completeTrade
    }
  }
}
</script>

<style>
.glass-panel {
  @apply bg-gray-dark/95 backdrop-blur-md border border-yellow/10 rounded-xl;
}

.animate-slide-up {
  animation: slideUp 0.3s ease-out forwards;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(1rem);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 