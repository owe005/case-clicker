<template>
  <div class="min-h-screen bg-gray-darker">
    <!-- Header -->
    <div class="relative py-12 mb-8">
      <div class="absolute inset-0 bg-gradient-to-b from-yellow/5 to-transparent"></div>
      <div class="relative max-w-7xl mx-auto px-4">
        <h1 class="text-4xl font-display font-bold text-white mb-2">Coinflip</h1>
        <p class="text-white/70">50/50 chance to double your bet!</p>
      </div>
    </div>

    <!-- Game Area -->
    <div class="max-w-7xl mx-auto px-4 pb-12">
      <!-- Betting Section -->
      <div v-if="!gameInProgress" class="bg-gray-dark/50 rounded-xl p-6">
        <!-- Quick Bet Buttons -->
        <div class="grid grid-cols-4 gap-2 mb-6">
          <button 
            v-for="amount in [1, 10, 100, 1000]" 
            :key="amount"
            class="px-4 py-2 bg-gray-darker/50 text-white/70 hover:bg-gray-darker hover:text-white rounded-lg transition-all duration-200"
            @click="incrementBet(amount)"
          >
            +${{ formatNumber(amount) }}
          </button>
          <button 
            class="px-4 py-2 bg-gray-darker/50 text-white/70 hover:bg-gray-darker hover:text-white rounded-lg transition-all duration-200"
            @click="doubleBet"
          >
            x2
          </button>
          <button 
            class="px-4 py-2 bg-gray-darker/50 text-white/70 hover:bg-gray-darker hover:text-white rounded-lg transition-all duration-200"
            @click="halfBalance"
          >
            1/2
          </button>
          <button 
            class="px-4 py-2 bg-gray-darker/50 text-white/70 hover:bg-gray-darker hover:text-white rounded-lg transition-all duration-200"
            @click="maxBalance"
          >
            Max
          </button>
          <button 
            class="px-4 py-2 bg-gray-darker/50 text-white/70 hover:bg-gray-darker hover:text-white rounded-lg transition-all duration-200"
            @click="repeatBet"
          >
            Repeat
          </button>
        </div>

        <!-- Bet Amount Input -->
        <div class="flex items-center space-x-2 mb-4">
          <button 
            class="px-3 py-2 bg-gray-darker hover:bg-gray-darker/70 text-white/70 rounded-lg transition-colors duration-200"
            @click="() => adjustBet('decrease')"
            :disabled="gameInProgress"
          >
            -
          </button>
          <input
            type="number"
            v-model="betAmount"
            class="w-full bg-gray-darker text-white text-center py-2 px-3 rounded-lg"
            :disabled="gameInProgress"
            step="0.01"
            min="0"
          />
          <button 
            class="px-3 py-2 bg-gray-darker hover:bg-gray-darker/70 text-white/70 rounded-lg transition-colors duration-200"
            @click="() => adjustBet('increase')"
            :disabled="gameInProgress"
          >
            +
          </button>
        </div>

        <!-- Side Selection -->
        <div class="grid grid-cols-2 gap-4 mb-6">
          <button 
            class="p-6 bg-gray-darker rounded-lg transition-all duration-200"
            :class="[
              selectedSide === 'ct' ? 'ring-2 ring-yellow' : 'hover:bg-gray-darker/70'
            ]"
            @click="selectSide('ct')"
          >
            <div class="flex flex-col items-center gap-4">
              <img 
                src="/static/media/casino/ct_side.png" 
                alt="CT Side"
                class="w-32 h-32 object-contain"
              >
              <div class="text-white">Counter-Terrorist</div>
              <div class="text-white/50">50%</div>
            </div>
          </button>
          <button 
            class="p-6 bg-gray-darker rounded-lg transition-all duration-200"
            :class="[
              selectedSide === 't' ? 'ring-2 ring-yellow' : 'hover:bg-gray-darker/70'
            ]"
            @click="selectSide('t')"
          >
            <div class="flex flex-col items-center gap-4">
              <img 
                src="/static/media/casino/t_side.png" 
                alt="T Side"
                class="w-32 h-32 object-contain"
              >
              <div class="text-white">Terrorist</div>
              <div class="text-white/50">50%</div>
            </div>
          </button>
        </div>

        <!-- Potential Win -->
        <div class="text-center mb-6">
          <div class="text-white/70">
            Potential Win: <span class="text-yellow">${{ formatNumber(parseFloat(betAmount) * 2) }}</span>
          </div>
        </div>

        <!-- Place Bet Button -->
        <button 
          class="w-full px-8 py-3 bg-yellow text-gray-darker rounded-lg font-medium transition-all duration-200 hover:bg-yellow/90 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="!canPlaceBet"
          @click="startGame"
        >
          {{ !selectedSide ? 'Choose a side' : 'Place Bet' }}
        </button>
      </div>

      <!-- Game View -->
      <div v-else class="bg-gray-dark/50 rounded-xl p-6">
        <div class="grid grid-cols-3 gap-8 items-center mb-8">
          <!-- Player Side -->
          <div class="bg-gray-darker rounded-lg p-6">
            <div class="flex items-center gap-4 mb-4">
              <img 
                src="/static/media/casino/player_avatar.png" 
                alt="Player"
                class="w-12 h-12 rounded-full"
              >
              <div>
                <div class="text-white font-medium">You</div>
                <div class="text-yellow">${{ formatNumber(parseFloat(betAmount)) }}</div>
              </div>
            </div>
            <img 
              :src="`/static/media/casino/${selectedSide}_side.png`"
              :alt="selectedSide"
              class="w-24 h-24 mx-auto"
            >
          </div>

          <!-- Center Coin -->
          <div class="text-center">
            <div 
              ref="coinRef"
              class="relative w-48 h-48 mx-auto mb-4 coin-container"
            >
              <div 
                class="coin"
                :style="{ transform: `rotateY(${coinRotation}deg)` }"
              >
                <div class="coin-side">
                  <img 
                    src="/static/media/casino/ct_side.png" 
                    alt="CT Side"
                    class="w-full h-full object-contain"
                  >
                </div>
                <div class="coin-side back">
                  <img 
                    src="/static/media/casino/t_side.png" 
                    alt="T Side"
                    class="w-full h-full object-contain"
                  >
                </div>
              </div>
            </div>
            <div class="text-2xl text-red-500 font-bold">VS</div>
            <div class="text-yellow mt-2">
              Total Pot: ${{ formatNumber(parseFloat(betAmount) * 2) }}
            </div>
          </div>

          <!-- Bot Side -->
          <div class="bg-gray-darker rounded-lg p-6">
            <div class="flex items-center gap-4 mb-4">
              <img 
                src="/static/media/casino/bot_avatar.png" 
                alt="Bot"
                class="w-12 h-12 rounded-full"
              >
              <div>
                <div class="text-white font-medium">{{ botName }}</div>
                <div class="text-yellow">${{ formatNumber(parseFloat(betAmount)) }}</div>
              </div>
            </div>
            <img 
              :src="`/static/media/casino/${selectedSide === 'ct' ? 't' : 'ct'}_side.png`"
              :alt="selectedSide === 'ct' ? 't' : 'ct'"
              class="w-24 h-24 mx-auto"
            >
          </div>
        </div>

        <!-- Result Display -->
        <div v-if="showResult" class="text-center">
          <div class="text-2xl font-bold mb-2" :class="gameWon ? 'text-green-500' : 'text-red-500'">
            {{ gameWon ? 'You Won!' : 'You Lost!' }}
          </div>
          <div class="text-3xl" :class="gameWon ? 'text-yellow' : 'text-white/70'">
            {{ gameWon ? `+$${formatNumber(parseFloat(betAmount) * 2)}` : `-$${formatNumber(parseFloat(betAmount))}` }}
          </div>
        </div>

        <!-- Game Buttons -->
        <div v-if="showResult" class="flex justify-center gap-4 mt-8">
          <button 
            class="px-8 py-3 bg-yellow text-gray-darker rounded-lg font-medium transition-all duration-200 hover:bg-yellow/90"
            @click="resetGame"
          >
            Play Again
          </button>
          <router-link 
            to="/casino"
            class="px-8 py-3 bg-red-500 text-white rounded-lg font-medium transition-all duration-200 hover:bg-red-600"
          >
            Return
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useStore } from '../store'

const BOT_NAMES = [
  "_Astrid47", "Kai.Jayden_02", "Orion_Phoenix98", "ElaraB_23", 
  "Theo.91", "Nova-Lyn", "FelixHaven19", "Aria.Stella85", 
  "Lucien_Kai", "Mira-Eclipse"
]

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

export default {
  name: 'CoinflipView',
  setup() {
    const store = useStore()
    const balance = computed(() => store.state.balance)

    // State
    const betAmount = ref('1.00')
    const selectedSide = ref(null)
    const gameInProgress = ref(false)
    const showResult = ref(false)
    const gameWon = ref(false)
    const coinRotation = ref(0)
    const lastBetAmount = ref('1.00')
    const botName = ref(BOT_NAMES[Math.floor(Math.random() * BOT_NAMES.length)])

    // Computed
    const canPlaceBet = computed(() => {
      const amount = parseFloat(betAmount.value)
      return !isNaN(amount) && amount > 0 && amount <= balance.value && selectedSide.value
    })

    // Methods
    const incrementBet = (amount) => {
      const newAmount = parseFloat(betAmount.value) + amount
      betAmount.value = Math.min(Math.max(0.01, newAmount), balance.value).toFixed(2)
    }

    const doubleBet = () => {
      const newAmount = parseFloat(betAmount.value) * 2
      betAmount.value = Math.min(newAmount, balance.value).toFixed(2)
    }

    const halfBalance = () => {
      betAmount.value = (balance.value / 2).toFixed(2)
    }

    const maxBalance = () => {
      betAmount.value = balance.value.toFixed(2)
    }

    const repeatBet = () => {
      const amount = Math.min(parseFloat(lastBetAmount.value), balance.value)
      betAmount.value = amount.toFixed(2)
    }

    const adjustBet = (delta) => {
      const currentBet = parseFloat(betAmount.value)
      let increment = 1

      // Scale increment based on current bet amount
      if (currentBet >= 1000) {
        increment = 100
      } else if (currentBet >= 100) {
        increment = 10
      } else if (currentBet >= 10) {
        increment = 1
      } else {
        increment = 0.1
      }

      const newAmount = currentBet + (delta * increment)
      betAmount.value = Math.min(Math.max(0.01, newAmount), balance.value).toFixed(2)
    }

    const validateBet = () => {
      const amount = parseFloat(betAmount.value)
      
      if (isNaN(amount) || amount < 0.01) {
        betAmount.value = '0.01'
      } else if (amount > balance.value) {
        betAmount.value = balance.value.toFixed(2)
      }
    }

    const selectSide = (side) => {
      selectedSide.value = side
    }

    const startGame = async () => {
      gameInProgress.value = true
      showResult.value = false
      const currentBalance = store.state.balance
      const betValue = parseFloat(betAmount.value)

      try {
        // Immediately deduct bet amount from balance
        store.updateUserData({ balance: currentBalance - betValue })

        const response = await fetch('/play_coinflip', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            amount: betValue,
            side: selectedSide.value
          })
        })

        const data = await response.json()

        if (data.error) {
          // If there's an error, refund the bet amount
          store.updateUserData({ balance: currentBalance })
          alert(data.error)
          resetGame()
          return
        }

        // Store last bet amount
        lastBetAmount.value = betAmount.value

        // Animate coin flip
        const rotations = 10
        const finalRotation = rotations * 360 + (data.result === 't' ? 180 : 0)
        coinRotation.value = finalRotation

        // Show result after animation
        setTimeout(async () => {
          gameWon.value = data.won
          showResult.value = true

          // Only update balance if player won (add winnings)
          if (data.won) {
            try {
              const updateResponse = await fetch('/update_coinflip_balance', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                }
              })
              const updateData = await updateResponse.json()
              if (updateData.success) {
                // Add original bet + winnings after animation
                store.updateUserData({ balance: updateData.balance })
              }
            } catch (error) {
              console.error('Error updating balance:', error)
            }
          }
        }, 3100)

      } catch (error) {
        // If there's an error, refund the bet amount
        store.updateUserData({ balance: currentBalance })
        console.error('Error:', error)
        alert('Failed to play coinflip')
        resetGame()
      }
    }

    const resetGame = () => {
      gameInProgress.value = false
      showResult.value = false
      selectedSide.value = null
      coinRotation.value = 0
      botName.value = BOT_NAMES[Math.floor(Math.random() * BOT_NAMES.length)]
    }

    return {
      balance,
      betAmount,
      selectedSide,
      gameInProgress,
      showResult,
      gameWon,
      coinRotation,
      botName,
      canPlaceBet,
      incrementBet,
      doubleBet,
      halfBalance,
      maxBalance,
      repeatBet,
      adjustBet,
      validateBet,
      selectSide,
      startGame,
      resetGame,
      formatNumber
    }
  }
}
</script> 

<style>
.glass-panel {
  @apply bg-gray-dark/95 backdrop-blur-md border border-yellow/10 rounded-xl;
}

.coin-container {
  perspective: 1000px;
}

.coin {
  position: relative;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
  transition: transform 3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.coin-side {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
}

.coin-side.back {
  transform: rotateY(180deg);
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