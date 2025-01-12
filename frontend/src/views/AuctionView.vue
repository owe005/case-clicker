<template>
  <div class="auction-container">
    <!-- Item Details Section -->
    <div class="item-details" :style="getItemDetailsStyle(auctionItem.rarity)">
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
        
        <div class="info-label">Estimated Value:</div>
        <div class="info-value">${{ auctionItem.adjusted_price.toFixed(2) }}</div>
      </div>
    </div>
    
    <!-- Bidding Section -->
    <div class="bidding-section">
      <div class="timer" id="timer">{{ formattedTimeLeft }}</div>
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
    <div class="active-bots">
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
    <div class="winning-screen" v-if="showWinningScreen">
      <div class="winning-content">
        <div class="winning-title">Congratulations!</div>
        <div class="winning-details">
          You won the auction for:
          <div class="item-name">
            {{ auctionItem.stattrak ? 'StatTrak™ ' : '' }}
            {{ auctionItem.weapon }} | {{ auctionItem.name }}
          </div>
        </div>
        <div class="winning-amount">Final Price: $<span>{{ winningAmount.toFixed(2) }}</span></div>
        <button class="close-winning" @click="closeWinningScreen">Awesome!</button>
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
import { CASE_MAPPING } from '../store'

export default {
  name: 'AuctionView',
  setup() {
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
      case_type: ''  // Add case_type to track which case the skin is from
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
    const fetchAuctionStatus = async () => {
      try {
        const response = await fetch('/get_auction_status')
        const data = await response.json()
        
        if (data.auction_item) {
          auctionItem.value = data.auction_item
        }
        if (data.current_bid !== undefined) {
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
        if (data.ended && data.winner === 'You') {
          showWinningScreen.value = true
          winningAmount.value = data.final_price || currentBid.value
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

    const closeWinningScreen = () => {
      showWinningScreen.value = false
      window.location.reload()
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
      const weaponName = item.weapon.toLowerCase()
        .replace(/-/g, '')
        .replace(/ /g, '')
        .replace('553', '553')
        .replace('galil ar', 'galil')
        .replace('galilar', 'galil')
      const skinName = item.name.toLowerCase().replace(/ /g, '_')
      const casePath = CASE_MAPPING[item.case_type] || 'weapon_case_1'
      return `/static/media/skins/${casePath}/${weaponName}_${skinName}.png`
    }

    // Lifecycle hooks
    onMounted(() => {
      fetchAuctionStatus()
      
      timerInterval.value = setInterval(() => {
        if (new Date() >= endTime.value) {
          clearInterval(timerInterval.value)
          fetchAuctionStatus() // Check final result
        }
      }, 1000)

      pollInterval.value = setInterval(fetchAuctionStatus, 2000)
    })

    onUnmounted(() => {
      if (timerInterval.value) clearInterval(timerInterval.value)
      if (pollInterval.value) clearInterval(pollInterval.value)
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
      closeWinningScreen,
      decreaseTimer,
      getSkinImagePath
    }
  }
}
</script>

<style scoped>
/* All the styles from auction.html are already in casino-games.css */
</style> 