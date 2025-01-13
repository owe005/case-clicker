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
                    :src="getSkinImage(item)" 
                    :alt="item.weapon + ' | ' + item.name"
                    class="w-16 h-16 object-contain"
                    @error="handleImageError"
                  >
                  <div>
                    <div class="text-sm text-white">
                      {{ item.stattrak ? 'StatTrak™ ' : '' }}{{ item.weapon }} | {{ item.name }}
                    </div>
                    <div class="text-xs text-white/50">{{ item.wear }}</div>
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
                    :src="getSkinImage(item)" 
                    :alt="item.weapon + ' | ' + item.name"
                    class="w-16 h-16 object-contain"
                    @error="handleImageError"
                  >
                  <div>
                    <div class="text-sm text-white">
                      {{ item.stattrak ? 'StatTrak™ ' : '' }}{{ item.weapon }} | {{ item.name }}
                    </div>
                    <div class="text-xs text-white/50">{{ item.wear }}</div>
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

    <!-- Chat Area -->
    <div 
      class="fixed bottom-0 right-4 w-80 bg-gray-dark/95 backdrop-blur-md rounded-t-xl border border-yellow/10 shadow-lg"
      :class="{ 'h-auto': chatMinimized }"
    >
      <div class="p-3 border-b border-yellow/10 flex items-center justify-between">
        <div class="text-sm font-medium text-white">Trade Chat</div>
        <button 
          @click="chatMinimized = !chatMinimized"
          class="text-white/50 hover:text-white"
        >
          {{ chatMinimized ? '+' : '−' }}
        </button>
      </div>
      <template v-if="!chatMinimized">
        <div ref="chatMessages" class="h-80 p-4 overflow-y-auto">
          <div v-for="msg in chatMessages" :key="msg.id" class="mb-4">
            <div class="text-xs text-white/50 mb-1">{{ msg.sender }}</div>
            <div 
              class="inline-block rounded-lg px-3 py-2 text-sm"
              :class="msg.isBot ? 'bg-gray-dark/50 text-white' : 'bg-yellow text-gray-darker'"
            >
              {{ msg.message }}
            </div>
            <div class="text-xs text-white/30 mt-1">{{ msg.time }}</div>
          </div>
        </div>
        <div class="p-3 border-t border-yellow/10 flex gap-2">
          <input 
            v-model="chatInput"
            @keyup.enter="sendChatMessage"
            type="text" 
            placeholder="Type a message..." 
            class="flex-1 bg-gray-dark/50 rounded-lg px-3 py-2 text-sm text-white placeholder:text-white/30 focus:outline-none focus:ring-1 focus:ring-yellow/30"
          >
          <button 
            @click="sendChatMessage"
            class="px-4 py-2 bg-yellow text-gray-darker rounded-lg text-sm font-medium hover:bg-yellow/90"
          >
            Send
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useStore } from '../store'
import { CASE_MAPPING } from '../store'

export default {
  name: 'TradingView',
  setup() {
    const store = useStore()
    
    const BOT_PERSONALITIES = {
      "_Astrid47": "A friendly and professional trader who specializes in high-tier skins. Very knowledgeable about skin patterns and float values.",
      "Kai.Jayden_02": "A young enthusiastic trader who loves discussing market trends and making predictions about future skin prices.",
      "Orion_Phoenix98": "An experienced collector focused on rare items and special patterns. Somewhat reserved but very helpful.",
      "ElaraB_23": "A casual trader who enjoys discussing both trading and the game itself. Often shares tips about trading strategies.",
      "Theo.91": "A veteran trader who's been in the CS:GO trading scene since the beginning. Likes to share stories about old trades.",
      "Nova-Lyn": "A competitive player who trades on the side. Often discusses pro matches and how they affect skin prices.",
      "FelixHaven19": "A mathematical trader who loves discussing probabilities and market statistics.",
      "Aria.Stella85": "A collector of StatTrak weapons who specializes in tracking kill counts and rare StatTrak items.",
      "Lucien_Kai": "A knife expert who knows everything about patterns, especially for Doppler and Case Hardened skins.",
      "Mira-Eclipse": "A sticker specialist who focuses on craft suggestions and sticker combinations."
    }

    const currentFilter = ref('all')
    const isLoading = ref(true)
    const trades = ref([])
    const showModal = ref(false)
    const selectedTrade = ref(null)
    const selectedTradeIndex = ref(null)
    const toasts = ref([])
    const chatInput = ref('')
    const chatMinimized = ref(false)
    const chatActive = ref(false)
    const lastMessageTime = ref(Date.now())
    const conversationTimer = ref(null)
    const chatMessages = ref([
      { id: 1, sender: 'System', message: 'Welcome to the trading chat!', isBot: true, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
    ])

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

    // Helper function to get skin image URL
    const getSkinImage = (item) => {
      if (item.type === 'money') return ''
      if (!item.image || !item.case_type) {
        return '/skins/rare_item.png'
      }
      const casePath = CASE_MAPPING[item.case_type] || item.case_type
      return `/skins/${casePath}/${item.image}`
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

    // Chat functionality
    const sendChatMessage = async () => {
      if (!chatInput.value.trim()) return

      const message = chatInput.value
      chatInput.value = ''

      // Add user message
      addChatMessage(message, 'You', false)
      lastMessageTime.value = Date.now()

      // Start conversation if not active
      if (!chatActive.value) {
        chatActive.value = true
        startConversationLoop()
      }

      try {
        // Get responding bot
        const botResponse = await fetch('/select_responding_bot', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message,
            chatHistory: chatMessages.value
          })
        })

        const botData = await botResponse.json()
        if (botData.error) throw new Error(botData.error)

        // Get bot's response
        setTimeout(async () => {
          const response = await fetch('/chat_with_bot', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              botName: botData.selectedBot,
              message,
              chatHistory: chatMessages.value,
              isAmbient: false
            })
          })

          const data = await response.json()
          if (data.error) throw new Error(data.error)

          addChatMessage(data.message, botData.selectedBot, true)
        }, Math.random() * 1500 + 500)
      } catch (error) {
        console.error('Chat error:', error)
      }
    }

    const addChatMessage = (message, sender, isBot = false) => {
      const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      chatMessages.value.push({
        id: Date.now(),
        sender,
        message: message.replace(`${sender}: `, '').replace(`${sender} `, ''),
        isBot,
        time
      })

      // Scroll to bottom on next tick
      nextTick(() => {
        const chatContainer = document.querySelector('.chat-messages')
        if (chatContainer) {
          chatContainer.scrollTop = chatContainer.scrollHeight
        }
      })
    }

    const startConversationLoop = () => {
      if (conversationTimer.value) {
        clearInterval(conversationTimer.value)
      }

      conversationTimer.value = setInterval(async () => {
        // Check if chat has been inactive
        if (Date.now() - lastMessageTime.value > 120000) {
          chatActive.value = false
          clearInterval(conversationTimer.value)
          return
        }

        // Random ambient message chance
        if (Math.random() > 0.2) return

        try {
          // Get a random bot that hasn't spoken recently
          const recentSpeakers = new Set(
            chatMessages.value.slice(-5)
              .filter(msg => msg.isBot)
              .map(msg => msg.sender)
          )

          // Filter out recent speakers from bot selection
          const availableBots = Object.keys(BOT_PERSONALITIES || {})
            .filter(bot => !recentSpeakers.has(bot))

          // Use a random available bot or any bot if all have spoken recently
          const randomBot = availableBots.length > 0 ? 
            availableBots[Math.floor(Math.random() * availableBots.length)] :
            Object.keys(BOT_PERSONALITIES || {})[Math.floor(Math.random() * Object.keys(BOT_PERSONALITIES || {}).length)]

          const response = await fetch('/chat_with_bot', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              botName: randomBot,
              message: "Keep it very short (max 10 words)",
              chatHistory: chatMessages.value.slice(-3),
              isAmbient: true
            })
          })

          const data = await response.json()
          if (!data.error) {
            addChatMessage(data.message, data.botName, true)
            lastMessageTime.value = Date.now()
          }
        } catch (error) {
          console.error('Ambient chat error:', error)
        }
      }, 10000)
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
      const timerInterval = setInterval(updateTimer, 1000)

      onUnmounted(() => {
        clearInterval(timerInterval)
        if (conversationTimer.value) {
          clearInterval(conversationTimer.value)
        }
      })
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
      chatMessages,
      chatInput,
      chatMinimized,
      getSkinImage,
      handleImageError,
      handleTrade,
      completeTrade,
      sendChatMessage
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