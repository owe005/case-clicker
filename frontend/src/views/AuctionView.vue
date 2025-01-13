<template>
  <div class="auction-container">
    <!-- Auction History Section -->
    <div class="auction-history-section main-card">
      <h3>Recent Auctions</h3>
      <div class="history-items">
        <div v-for="item in auctionHistory" 
             :key="item.timestamp" 
             class="history-item"
             :class="getItemRarityClass(item.rarity)">
          <div class="history-item-image">
            <img :src="getSkinImagePath(item)" :alt="`${item.weapon} | ${item.name}`">
          </div>
          <div class="history-item-details">
            <div class="history-item-name">
              {{ item.stattrak ? 'StatTrak™ ' : '' }}{{ item.weapon }} | {{ item.name }} ({{ item.wear }})
            </div>
            <div class="history-item-price">
              ${{ item.final_price.toFixed(2) }}
            </div>
            <div class="history-item-winner">
              Won by: {{ item.winner }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Item Details Section -->
    <div class="item-details main-card" :style="getItemDetailsStyle(auctionItem.rarity)">
      <div class="item-header">
        <div class="item-image">
          <img :src="getSkinImagePath(auctionItem)" :alt="`${auctionItem.weapon} | ${auctionItem.name}`">
        </div>
        <div class="item-name">
          {{ auctionItem.stattrak ? 'StatTrak™ ' : '' }}
          {{ auctionItem.weapon }} | {{ auctionItem.name }}
        </div>
      </div>
      <div class="item-info">
        <div class="info-label">Wear:</div>
        <div class="info-value">{{ auctionItem.wear }}</div>
        
        <div class="info-label">Float:</div>
        <div class="info-value">
          <span class="float-value" :class="getFloatClass(auctionItem.float_value)">
            {{ auctionItem.float_value.toFixed(9) }}
          </span>
        </div>
        
        <div class="info-label">Base Price:</div>
        <div class="info-value">${{ auctionItem.base_price.toFixed(2) }}</div>
        
        <div class="info-label">Current Price:</div>
        <div class="info-value">${{ auctionItem.adjusted_price.toFixed(2) }}</div>
      </div>
    </div>
    
    <!-- Bidding Section -->
    <div class="bidding-section main-card">
      <div class="timer" id="timer">{{ formattedTimeLeft }}</div>
      <button class="debug-button" @click="decreaseTimer(1)">-1m</button>
      <div class="current-bid">
        Current Bid: $<span id="currentBid">{{ currentBid.toFixed(2) }}</span>
      </div>
      
      <div class="bid-form">
        <input type="number" 
               class="bid-input" 
               v-model="bidAmount"
               :min="currentBid + 10"
               step="0.01"
               placeholder="Enter bid amount">
        <button class="bid-button" @click="placeBid">Place Bid</button>
      </div>
      
      <!-- Quick Bid Buttons -->
      <div class="quick-bid-buttons">
        <button class="quick-bid" @click="setQuickBid(10)">+$10</button>
        <button class="quick-bid" @click="setQuickBid(50)">+$50</button>
        <button class="quick-bid" @click="setQuickBid(100)">+$100</button>
        <button class="quick-bid" @click="setQuickBid(500)">+$500</button>
      </div>
      
      <div class="bid-history" id="bidHistory">
        <div v-for="bid in bids" :key="bid.timestamp" class="bid-entry">
          <span class="bidder">{{ bid.bidder }}</span>
          <span class="bid-amount">${{ bid.amount.toFixed(2) }}</span>
          <span class="bid-time">{{ new Date(bid.timestamp).toLocaleTimeString() }}</span>
        </div>
      </div>
    </div>

    <!-- Active Bots Section -->
    <div class="active-bots main-card">
      <h3>Bidders <span id="activeCount">
        ({{ activeBotCount }} active / {{ onlineBotCount }} online)
      </span></h3>
      <ul id="biddersList">
        <li v-for="bot in activeBots" 
            :key="bot.name"
            :data-bot="bot.name"
            :class="{
              'offline': bot.status === 'offline',
              'inactive': !bot.active && bot.status === 'online',
              'just-out': bot.justOut
            }">
          {{ bot.name }}
          <span class="status">{{ getBotStatus(bot) }}</span>
        </li>
      </ul>
    </div>

    <!-- Winning Screen -->
    <div v-if="showWinningScreen" class="winning-screen">
      <div class="winning-content">
        <h2>Congratulations!</h2>
        <p>You won the auction!</p>
        <div class="item-image">
          <img :src="getSkinImagePath(wonItem)" :alt="wonItem.weapon + ' | ' + wonItem.name">
        </div>
        <p>{{ wonItem.weapon }} | {{ wonItem.name }}</p>
        <p>Final Price: ${{ finalPrice.toFixed(2) }}</p>
        <p>Countdown: {{ winScreenTimer }}s</p>
        <button @click="closeWinningScreen">Awesome!</button>
      </div>
    </div>

    <!-- Notification -->
    <div class="auction-notification" v-show="notification" @click="notification = ''">
      {{ notification }}
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useStore, CASE_MAPPING } from '../store'
import confetti from 'canvas-confetti'

export default {
  name: 'AuctionView',
  setup() {
    const store = useStore()
    // State
    const auctionItem = ref({
      weapon: 'Loading...',
      name: '',
      rarity: '',
      stattrak: false,
      wear: '',
      float_value: 0,
      base_price: 0,
      adjusted_price: 0,
      image: '',
      case_type: ''
    })
    const currentBid = ref(0)
    const bidAmount = ref('')
    const bids = ref([])
    const endTime = ref(new Date())
    const activeBots = ref([])
    const showWinningScreen = ref(false)
    const winningAmount = ref(0)
    const notification = ref('')
    const timerInterval = ref(null)
    const pollInterval = ref(null)
    const winScreenTimer = ref(3)
    const winScreenInterval = ref(null)
    const wonItem = ref(null)
    const finalPrice = ref(0)
    const auctionHistory = ref([])

    // Computed
    const reversedBids = computed(() => [...bids.value].reverse())

    const formattedTimeLeft = computed(() => {
      const now = new Date()
      const timeLeft = endTime.value - now

      if (timeLeft <= 0) return '00:00:00'

      const hours = Math.floor(timeLeft / (1000 * 60 * 60))
      const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60))
      const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000)

      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
    })

    const activeBotCount = computed(() => 
      activeBots.value.filter(bot => bot.active && bot.status === 'online').length
    )

    const onlineBotCount = computed(() => 
      activeBots.value.filter(bot => bot.status === 'online').length
    )

    // Methods
    const resetAuctionState = () => {
      auctionItem.value = {
        weapon: 'Loading...',
        name: '',
        rarity: '',
        stattrak: false,
        wear: '',
        float_value: 0,
        base_price: 0,
        adjusted_price: 0,
        image: '',
        case_type: ''
      }
      currentBid.value = 0
      bidAmount.value = ''
      bids.value = []
      endTime.value = new Date()
      showWinningScreen.value = false
      wonItem.value = null
      finalPrice.value = 0
    }

    const fetchAuctionStatus = async () => {
      try {
        const response = await fetch('/get_auction_status')
        const data = await response.json()
        
        if (data.auction_item) {
          // Reset state if a new auction is detected
          if (auctionItem.value.name !== data.auction_item.name) {
            resetAuctionState()
          }
          auctionItem.value = data.auction_item
        }
        if (data.current_bid !== undefined) {
          // Only show outbid notification if the auction hasn't ended
          if (data.bids.length > 0 && 
              bids.value.length > 0 &&
              data.bids[data.bids.length - 1].bidder !== 'You' &&
              bids.value[bids.value.length - 1].bidder === 'You' &&
              data.current_bid !== currentBid.value &&
              !data.ended) {
            notification.value = 'You have been outbid!'
            // Update store balance immediately
            const balanceResponse = await fetch('/get_balance')
            const balanceData = await balanceResponse.json()
            if (balanceData.balance !== undefined) {
              store.state.balance = balanceData.balance
            }
          }
          currentBid.value = data.current_bid
        }
        if (data.end_time) {
          endTime.value = new Date(data.end_time)
        }
        if (data.bids) {
          bids.value = data.bids
        }
        if (data.bot_statuses) {
          updateBotStatuses(data.bot_statuses)
        }

        // Check if auction ended and user won
        if (data.ended && data.winner === 'You' && !showWinningScreen.value) {
          wonItem.value = data.won_item
          finalPrice.value = data.final_price
          showWinScreen()
          notification.value = ''
        } else if (data.ended && !showWinningScreen.value) {
          // If someone else won, reload after a short delay
          setTimeout(() => {
            window.location.reload()
          }, 2000)
        }

        if (data.history) {
          auctionHistory.value = data.history
        }
      } catch (error) {
        console.error('Error fetching auction status:', error)
      }
    }

    const updateBotStatuses = (newStatuses) => {
      activeBots.value = newStatuses.map(bot => ({
        ...bot,
        justOut: !bot.active && bot.status === 'online' && 
                activeBots.value.find(b => b.name === bot.name)?.active
      }))

      // Remove justOut flag after animation
      setTimeout(() => {
        activeBots.value = activeBots.value.map(bot => ({
          ...bot,
          justOut: false
        }))
      }, 500)
    }

    const placeBid = async () => {
      const amount = parseFloat(bidAmount.value)
      if (!amount || isNaN(amount) || amount <= currentBid.value) {
        notification.value = 'Please enter a valid bid amount higher than the current bid'
        return
      }

      try {
        const response = await fetch('/place_bid', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ amount })
        })
        const data = await response.json()

        if (data.error) {
          notification.value = data.error
          return
        }

        // Update state with response data
        currentBid.value = data.current_bid
        bids.value = data.bids
        endTime.value = new Date(data.end_time)
        bidAmount.value = ''

        // Show notification
        notification.value = 'Bid placed successfully!'
        setTimeout(() => notification.value = '', 3000)
      } catch (error) {
        console.error('Error placing bid:', error)
        notification.value = 'Failed to place bid'
      }
    }

    const setQuickBid = (increment) => {
      bidAmount.value = (currentBid.value + increment).toFixed(2)
    }

    const getFloatClass = (float) => {
      if (float <= 0.0009) return 'ultra-rare'
      if (float <= 0.001) return 'very-rare'
      if (float <= 0.006) return 'rare'
      if (float <= 0.015) return 'uncommon'
      return ''
    }

    const getBotStatus = (bot) => {
      if (bot.status === 'offline') return 'offline'
      return bot.active ? 'active' : 'out'
    }

    const getItemDetailsStyle = (rarity) => {
      const colors = {
        'CONTRABAND': ['#4b1e06', '#2d1204', '#e4ae39'],
        'GOLD': ['#423012', '#2a1f0c', '#d4af37'],
        'RED': ['#3d1515', '#2a0f0f', '#eb4b4b'],
        'PINK': ['#3d1537', '#2a0f26', '#eb4b82'],
        'PURPLE': ['#2a1f3d', '#1a1426', '#8847ff'],
        'BLUE': ['#1a2940', '#111c2d', '#4b69ff'],
      }
      const [color1, color2, border] = colors[rarity] || ['#1a1a1a', '#222', '#2a2a2a']
      
      return {
        background: `linear-gradient(145deg, ${color1}, ${color2})`,
        borderColor: border
      }
    }

    const showWinScreen = () => {
      showWinningScreen.value = true
      winScreenTimer.value = 3
      
      // Clear existing intervals
      if (timerInterval.value) clearInterval(timerInterval.value)
      if (pollInterval.value) clearInterval(pollInterval.value)
      if (winScreenInterval.value) clearInterval(winScreenInterval.value)
      
      // Start countdown
      winScreenInterval.value = setInterval(() => {
        winScreenTimer.value--
        if (winScreenTimer.value <= 0) {
          clearInterval(winScreenInterval.value)
          window.location.reload()
        }
      }, 1000)

      // Trigger multiple confetti bursts for a more celebratory effect
      const duration = 3000
      const animationEnd = Date.now() + duration
      const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 1001 }

      function randomInRange(min, max) {
        return Math.random() * (max - min) + min
      }

      const interval = setInterval(() => {
        const timeLeft = animationEnd - Date.now()

        if (timeLeft <= 0) {
          return clearInterval(interval)
        }

        const particleCount = 50 * (timeLeft / duration)
        
        // Trigger confetti from multiple angles
        confetti({
          ...defaults,
          particleCount,
          origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
        })
        confetti({
          ...defaults,
          particleCount,
          origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
        })
      }, 250)
    }

    // Add debug timer decrease function if in debug mode
    const decreaseTimer = async (minutes) => {
      try {
        const response = await fetch('/debug/decrease_timer', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ minutes })
        })
        
        const data = await response.json()
        if (data.error) return
        
        endTime.value = new Date(data.new_end_time)
      } catch (error) {
        console.error('Error decreasing timer:', error)
      }
    }

    function getSkinImagePath(item) {
      if (!item.image) return ''
      
      // Extract just the filename from the full path
      const filename = item.image.split('/').pop()
      
      // For history items, try to use case_type, fallback to case_file, or use a default
      let casePath = 'default'
      if (item.case_type) {
        casePath = CASE_MAPPING[item.case_type] || item.case_type
      } else if (item.case_file) {
        casePath = item.case_file
      }
      
      return `/skins/${casePath}/${filename}`
    }

    const getItemRarityClass = (rarity) => {
      return {
        'rarity-contraband': rarity === 'CONTRABAND',
        'rarity-gold': rarity === 'GOLD',
        'rarity-red': rarity === 'RED',
        'rarity-pink': rarity === 'PINK',
        'rarity-purple': rarity === 'PURPLE',
        'rarity-blue': rarity === 'BLUE'
      }
    }

    // Lifecycle hooks
    onMounted(() => {
      fetchAuctionStatus()
      
      timerInterval.value = setInterval(() => {
        if (new Date() >= endTime.value) {
          clearInterval(timerInterval.value)
          fetchAuctionStatus() // Check final result
          // Don't automatically reload here - let the fetchAuctionStatus handle it
        }
      }, 1000)

      pollInterval.value = setInterval(fetchAuctionStatus, 1000) // Increased poll interval to reduce race conditions
    })

    onUnmounted(() => {
      if (timerInterval.value) clearInterval(timerInterval.value)
      if (pollInterval.value) clearInterval(pollInterval.value)
      if (winScreenInterval.value) clearInterval(winScreenInterval.value)
    })

    return {
      auctionItem,
      currentBid,
      bidAmount,
      bids: reversedBids,
      activeBots,
      showWinningScreen,
      winningAmount,
      notification,
      formattedTimeLeft,
      activeBotCount,
      onlineBotCount,
      placeBid,
      setQuickBid,
      getFloatClass,
      getBotStatus,
      getItemDetailsStyle,
      decreaseTimer,
      getSkinImagePath,
      winScreenTimer,
      wonItem,
      finalPrice,
      auctionHistory,
      getItemRarityClass
    }
  }
}
</script>

<style scoped>
.auction-container {
  display: grid;
  grid-template-columns: repeat(4, 400px);
  gap: 20px;
  padding: 20px;
  justify-content: center;
  margin: 0 auto;
  max-width: 1700px;
}

.main-card {
  background: #1a1a1a;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  border: 2px solid #2a2a2a;
  padding: 20px;
  width: 400px;
  height: 600px;
  display: flex;
  flex-direction: column;
  flex: none;
  overflow: hidden;
}

.auction-history-section {
  margin: 0;
}

.auction-history-section h3,
.active-bots h3 {
  margin: 0 0 10px 0;
  padding: 0;
  font-size: 1.2em;
  color: #fff;
}

.history-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
  overflow-y: auto;
  flex: 1;
  padding-right: 10px;
  margin: 0;
}

.history-item {
  flex-shrink: 0;
  min-height: 100px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  padding: 15px;
  display: flex;
  align-items: flex-start;
  gap: 15px;
  width: 100%;
  max-width: 360px;
  transition: transform 0.2s;
}

.history-item:hover {
  transform: translateY(-2px);
}

.history-item-image {
  width: 120px;
  height: 90px;
  flex: 0 0 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  padding: 5px;
  overflow: hidden;
}

.history-item-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.history-item-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 2px 0;
  min-width: 0; /* Allow text to wrap properly */
  width: 100%;
}

.history-item-name {
  font-size: 0.9em;
  line-height: 1.3;
  margin-bottom: 2px;
  color: #fff;
  /* Handle text wrapping properly */
  white-space: pre-wrap; /* Preserve spaces and allow wrapping */
  word-wrap: break-word; /* Break words that are too long */
  overflow-wrap: break-word;
  hyphens: auto;
  width: 100%;
  max-width: 210px; /* Account for image width and padding */
}

.history-item-price {
  font-size: 1.1em;
  font-weight: bold;
  color: #4CAF50;
  margin: 2px 0;
}

.history-item-winner {
  font-size: 0.8em;
  color: #888;
  margin-top: 2px;
}

/* Adjust item details card */
.item-details {
  margin: 0;
  overflow: hidden;
}

/* Adjust bidding section */
.bidding-section {
  margin: 0;
}

.bid-history {
  flex: 1;
  overflow-y: auto;
  margin-top: 10px;
  padding-right: 10px;
}

/* Adjust active bots section */
.active-bots {
  margin: 0;
}

#biddersList {
  flex: 1;
  overflow-y: auto;
  margin-top: 10px;
  padding-right: 10px;
}

/* Make scrollbars look nice */
.main-card ::-webkit-scrollbar {
  width: 8px;
}

.main-card ::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}

.main-card ::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.main-card ::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

.debug-button {
  position: fixed;
  bottom: 10px;
  right: 10px;
  padding: 5px 10px;
  background: #333;
  color: #fff;
  border: 1px solid #666;
  border-radius: 4px;
  cursor: pointer;
  z-index: 1000;
}

.debug-button:hover {
  background: #444;
}

.winning-screen .item-image {
  margin: 20px auto;
  max-width: 300px;
  background: rgba(0, 0, 0, 0.3);
  padding: 20px;
  border-radius: 8px;
}

.winning-screen .item-image img {
  width: 100%;
  height: auto;
  object-fit: contain;
}

.winning-screen .countdown {
  margin-top: 20px;
  font-size: 1.2em;
  color: #888;
}

.winning-screen {
  background: linear-gradient(135deg, #1a1a1a, #222);
  animation: fadeIn 0.5s ease-out;
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
}

.winning-content {
  background: rgba(0, 0, 0, 0.8);
  padding: 30px;
  border-radius: 12px;
  text-align: center;
  max-width: 500px;
  border: 2px solid #4CAF50;
  box-shadow: 0 0 30px rgba(76, 175, 80, 0.3);
  color: #fff;
  font-family: 'Inter', sans-serif;
}

.winning-content h2 {
  font-size: 2em;
  color: #4CAF50;
  margin-bottom: 20px;
  animation: bounce 1s infinite;
}

.winning-content p {
  font-size: 1.2em;
  margin: 10px 0;
}

.winning-content button {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
  margin-top: 20px;
  transition: background 0.3s;
}

.winning-content button:hover {
  background: #45a049;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-10px); }
  60% { transform: translateY(-5px); }
}

.confetti {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1000;
}

/* Rarity colors */
.rarity-contraband {
  border: 1px solid #e4ae39;
  background: linear-gradient(135deg, rgba(75, 30, 6, 0.3), rgba(45, 18, 4, 0.3));
}

.rarity-gold {
  border: 1px solid #d4af37;
  background: linear-gradient(135deg, rgba(66, 48, 18, 0.3), rgba(42, 31, 12, 0.3));
}

.rarity-red {
  border: 1px solid #eb4b4b;
  background: linear-gradient(135deg, rgba(61, 21, 21, 0.3), rgba(42, 15, 15, 0.3));
}

.rarity-pink {
  border: 1px solid #eb4b82;
  background: linear-gradient(135deg, rgba(61, 21, 55, 0.3), rgba(42, 15, 38, 0.3));
}

.rarity-purple {
  border: 1px solid #8847ff;
  background: linear-gradient(135deg, rgba(42, 31, 61, 0.3), rgba(26, 20, 38, 0.3));
}

.rarity-blue {
  border: 1px solid #4b69ff;
  background: linear-gradient(135deg, rgba(26, 41, 64, 0.3), rgba(17, 28, 45, 0.3));
}

/* Ensure content areas are scrollable */
.history-items,
.bid-history,
#biddersList {
  flex: 1;
  overflow-y: auto;
  margin-top: 10px;
  padding-right: 10px;
  height: 0; /* Force content to respect flex container */
}

/* Ensure images don't break layout */
.item-image img,
.history-item-image img {
  max-width: 100%;
  height: auto;
  object-fit: contain;
}
</style> 