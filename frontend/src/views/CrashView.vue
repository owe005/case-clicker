<template>
  <div class="min-h-screen bg-gray-darker">
    <!-- Header -->
    <div class="relative py-12 mb-8">
      <div class="absolute inset-0 bg-gradient-to-b from-yellow/5 to-transparent"></div>
      <div class="relative max-w-7xl mx-auto px-4">
        <h1 class="text-4xl font-display font-bold text-white mb-2">Crash</h1>
        <p class="text-white/70">Watch the multiplier grow and cash out before it crashes!</p>
      </div>
    </div>

    <!-- Game Area -->
    <div class="max-w-7xl mx-auto px-4 pb-12">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Chart and Multiplier -->
        <div class="lg:col-span-2">
          <div class="bg-gray-dark/50 rounded-xl p-6">
            <div class="relative aspect-[2/1] bg-gray-darker rounded-lg overflow-hidden">
              <canvas ref="chartRef" class="w-full h-full"></canvas>
              <div 
                class="absolute inset-0 flex items-center justify-center text-5xl font-bold transition-colors duration-200"
                :class="gameState === 'crashed' ? 'text-red-500' : 'text-green-500'"
              >
                {{ currentMultiplier.toFixed(2) }}x
              </div>
            </div>
          </div>
        </div>

        <!-- Betting Controls -->
        <div class="bg-gray-dark/50 rounded-xl p-6">
          <!-- Quick Bet Buttons -->
          <div class="grid grid-cols-4 gap-2 mb-4">
            <button 
              v-for="amount in [1, 10, 100, 1000]" 
              :key="amount"
              class="px-3 py-2 bg-gray-darker hover:bg-gray-darker/70 text-white/70 rounded-lg transition-colors duration-200"
              @click="addToBet(amount)"
              :disabled="gameState === 'playing'"
            >
              +${{ formatNumber(amount) }}
            </button>
            <button 
              class="px-3 py-2 bg-gray-darker hover:bg-gray-darker/70 text-white/70 rounded-lg transition-colors duration-200"
              @click="doubleBet"
              :disabled="gameState === 'playing'"
            >
              x2
            </button>
            <button 
              class="px-3 py-2 bg-gray-darker hover:bg-gray-darker/70 text-white/70 rounded-lg transition-colors duration-200"
              @click="halfBalance"
              :disabled="gameState === 'playing'"
            >
              1/2
            </button>
            <button 
              class="px-3 py-2 bg-gray-darker hover:bg-gray-darker/70 text-white/70 rounded-lg transition-colors duration-200"
              @click="maxBalance"
              :disabled="gameState === 'playing'"
            >
              Max
            </button>
            <button 
              class="px-3 py-2 bg-gray-darker hover:bg-gray-darker/70 text-white/70 rounded-lg transition-colors duration-200"
              @click="repeatBet"
              :disabled="gameState === 'playing'"
            >
              Repeat
            </button>
          </div>

          <!-- Bet Amount Input -->
          <div class="flex items-center space-x-2 mb-4">
            <button 
              class="px-3 py-2 bg-gray-darker hover:bg-gray-darker/70 text-white/70 rounded-lg transition-colors duration-200"
              @click="() => adjustBet('decrease')"
              :disabled="gameState === 'playing'"
            >
              -
            </button>
            <input
              type="number"
              v-model="betAmount"
              class="w-full bg-gray-darker text-white text-center py-2 px-3 rounded-lg"
              :disabled="gameState === 'playing'"
              step="0.01"
              min="0"
            />
            <button 
              class="px-3 py-2 bg-gray-darker hover:bg-gray-darker/70 text-white/70 rounded-lg transition-colors duration-200"
              @click="() => adjustBet('increase')"
              :disabled="gameState === 'playing'"
            >
              +
            </button>
          </div>

          <!-- Auto Cashout Input -->
          <div class="bg-gray-darker rounded-lg p-4 mb-6">
            <div class="flex items-center justify-between mb-2">
              <label class="text-white/70 font-medium">Auto Cashout</label>
              <div class="flex items-center gap-2">
                <button 
                  v-for="multiplier in [1.5, 2, 5, 10]"
                  :key="multiplier"
                  class="px-2 py-1 bg-yellow/10 hover:bg-yellow/20 text-yellow text-sm rounded transition-colors duration-200"
                  @click="setAutoCashout(multiplier)"
                  :disabled="gameState === 'playing'"
                >
                  {{ multiplier }}x
                </button>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button 
                class="w-10 h-10 bg-gray-dark hover:bg-gray-dark/70 text-white/70 rounded-lg transition-colors duration-200 flex items-center justify-center"
                @click="adjustAutoCashout('decrease')"
                :disabled="gameState === 'playing'"
              >
                -
              </button>
              <div class="flex-1 bg-gray-dark text-white px-4 py-2 rounded-lg text-center">
                {{ autoCashout ? Number(autoCashout).toFixed(2) : '0.00' }}x
              </div>
              <button 
                class="w-10 h-10 bg-gray-dark hover:bg-gray-dark/70 text-white/70 rounded-lg transition-colors duration-200 flex items-center justify-center"
                @click="adjustAutoCashout('increase')"
                :disabled="gameState === 'playing'"
              >
                +
              </button>
            </div>
            <p class="text-white/50 text-sm mt-2">
              Automatically cash out when the multiplier reaches this value
            </p>
          </div>

          <!-- Game Buttons -->
          <div class="space-y-3">
            <button 
              class="w-full py-3 rounded-lg font-medium transition-all duration-200"
              :class="[
                gameState === 'waiting' 
                  ? 'bg-green-500 hover:bg-green-600 text-white' 
                  : 'bg-gray-darker text-white/30 cursor-not-allowed'
              ]"
              :disabled="gameState !== 'waiting'"
              @click="placeBet"
            >
              Place Bet
            </button>
            <button 
              class="w-full py-3 rounded-lg font-medium transition-all duration-200"
              :class="[
                gameState === 'playing' 
                  ? 'bg-red-500 hover:bg-red-600 text-white' 
                  : 'bg-gray-darker text-white/30 cursor-not-allowed'
              ]"
              :disabled="gameState !== 'playing'"
              @click="cashout"
            >
              Cashout
            </button>
          </div>

          <!-- Potential Win Display -->
          <div class="mt-6 text-center">
            <div v-if="gameState === 'playing' && !hasAutoCashedOut" class="text-white/70">
              Potential Win: <span class="text-green-500">${{ formatNumber(potentialWin) }}</span>
            </div>
            <div v-if="hasAutoCashedOut" class="space-y-2">
              <div class="text-white/70">
                You Won: <span class="text-green-500">${{ formatNumber(cashoutAmount) }}</span>
              </div>
              <div class="text-white/50 text-sm">
                Could Win: <span class="text-white/70">${{ formatNumber(couldWinAmount) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Game History -->
      <div class="mt-6 bg-gray-dark/50 rounded-xl p-6">
        <h3 class="text-xl font-display text-white mb-4">Previous Crashes</h3>
        <div class="flex flex-wrap gap-2">
          <div 
            v-for="(crash, index) in gameHistory" 
            :key="index"
            class="relative px-4 py-2 bg-red-500 text-white rounded-lg font-medium"
          >
            {{ crash.multiplier.toFixed(2) }}x
            <div 
              v-if="crash.cashoutPoint"
              class="absolute -top-2 -right-2 px-2 py-0.5 bg-green-500 text-white text-xs rounded-full"
            >
              {{ crash.cashoutPoint.toFixed(2) }}x
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, inject } from 'vue'
import Chart from 'chart.js/auto'

export default {
  name: 'CrashView',
  setup() {
    const store = inject('store')
    // Chart reference
    const chartRef = ref(null)
    let chart = null

    // Utility function for formatting numbers
    const formatNumber = (num) => {
      const number = Number(num)
      if (isNaN(number)) return '0.00'
      if (number >= 1000000) {
        return (number / 1000000).toFixed(2) + 'M'
      } else if (number >= 1000) {
        return (number / 1000).toFixed(2) + 'K'
      } else {
        return number.toFixed(2)
      }
    }

    // Game state
    const gameState = ref('waiting') // waiting, playing, crashed
    const currentMultiplier = ref(1.00)
    const betAmount = ref(1.00)
    const autoCashout = ref('')
    const lastBetAmount = ref(1.00)
    const gameHistory = ref([])
    const hasAutoCashedOut = ref(false)
    const cashoutPoint = ref(null)
    const potentialWin = ref(0)
    const cashoutAmount = ref(0)
    const couldWinAmount = ref(0)
    let crashHandler = null

    // Get balance from store
    const balance = computed(() => store.state.balance)

    // Update store balance
    const updateBalance = (newBalance) => {
      store.updateUserData({ balance: newBalance })
    }

    // Chart data
    const chartData = {
      labels: [],
      values: []
    }

    // Initialize chart
    const initializeChart = () => {
      if (chart) {
        chart.destroy()
      }

      const ctx = chartRef.value.getContext('2d')
      chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: [],
          datasets: [{
            label: 'Multiplier',
            data: [],
            borderColor: '#22c55e',
            borderWidth: 2,
            fill: false,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: { duration: 0 },
          scales: {
            x: { display: false },
            y: {
              beginAtZero: true,
              grid: { color: '#374151' },
              ticks: { color: '#9ca3af' }
            }
          },
          plugins: { legend: { display: false } }
        }
      })
    }

    // Update chart
    const updateChart = (multiplier) => {
      chartData.labels.push(chartData.labels.length)
      chartData.values.push(multiplier)
      chart.data.labels = chartData.labels
      chart.data.datasets[0].data = chartData.values
      chart.update()
    }

    // Reset chart
    const resetChart = () => {
      chartData.labels = []
      chartData.values = []
      initializeChart()
    }

    // Betting functions
    const addToBet = (amount) => {
      if (gameState.value !== 'playing') {
        const currentBet = parseFloat(betAmount.value)
        const newAmount = Math.max(0, currentBet + amount)
        betAmount.value = parseFloat(newAmount.toFixed(2))
      }
    }

    const doubleBet = () => {
      if (gameState.value !== 'playing') {
        betAmount.value = parseFloat((parseFloat(betAmount.value) * 2).toFixed(2))
      }
    }

    const halfBalance = async () => {
      if (gameState.value !== 'playing') {
        betAmount.value = parseFloat((balance.value / 2).toFixed(2))
      }
    }

    const maxBalance = async () => {
      if (gameState.value !== 'playing') {
        betAmount.value = parseFloat(balance.value.toFixed(2))
      }
    }

    const repeatBet = () => {
      if (gameState.value !== 'playing') {
        betAmount.value = lastBetAmount.value
      }
    }

    const adjustBet = (action) => {
      if (gameState.value !== 'playing') {
        const currentBet = parseFloat(betAmount.value)
        let increment = 0.1
        
        if (currentBet >= 1000) {
          increment = 100
        } else if (currentBet >= 100) {
          increment = 10
        } else if (currentBet >= 10) {
          increment = 1
        }
        
        const delta = action === 'increase' ? 1 : -1
        const newAmount = Math.max(0, currentBet + (increment * delta))
        betAmount.value = parseFloat(newAmount.toFixed(2))
      }
    }

    // Auto cashout functions
    const setAutoCashout = (value) => {
      if (gameState.value !== 'playing') {
        autoCashout.value = value.toFixed(2)
      }
    }

    const adjustAutoCashout = (action) => {
      if (gameState.value !== 'playing') {
        const currentValue = parseFloat(autoCashout.value) || 1.01
        if (action === 'increase') {
          autoCashout.value = Math.min(1000, (currentValue + 0.25)).toFixed(2)
        } else {
          autoCashout.value = Math.max(1.01, (currentValue - 0.25)).toFixed(2)
        }
      }
    }

    // Game functions
    const placeBet = async () => {
      if (gameState.value !== 'waiting') return

      const bet = parseFloat(betAmount.value)
      const autoCashoutValue = parseFloat(autoCashout.value) || null

      // Validate auto cashout
      if (autoCashoutValue !== null && autoCashoutValue < 1.01) {
        alert('Auto cashout must be at least 1.01x')
        return
      }

      try {
        const response = await fetch('/play_crash', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            amount: bet,
            auto_cashout: autoCashoutValue 
          })
        })

        const data = await response.json()
        if (data.error) {
          alert(data.error)
          return
        }

        lastBetAmount.value = bet
        gameState.value = 'playing'
        currentMultiplier.value = 1.00
        hasAutoCashedOut.value = false
        cashoutPoint.value = null
        resetChart()
        startGameLoop(autoCashoutValue)

      } catch (error) {
        console.error('Error:', error)
        alert('Failed to place bet')
      }
    }

    const cashout = async () => {
      if (gameState.value !== 'playing') return

      const manualCashoutPoint = currentMultiplier.value

      try {
        const response = await fetch('/crash_cashout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ multiplier: currentMultiplier.value })
        })

        const data = await response.json()
        if (data.error) {
          console.error(data.error)
          handleCrash()
          return
        }

        handleWin(currentMultiplier.value, data.balance)
        hasAutoCashedOut.value = true
        cashoutPoint.value = manualCashoutPoint

      } catch (error) {
        console.error('Error:', error)
        handleCrash()
      }
    }

    const startGameLoop = (autoCashoutMultiplier) => {
      let startTime = Date.now()
      const houseEdge = 0.08
      const instantCrashProb = 0.01
      
      const r = Math.random()
      
      let finalCrashMultiplier
      if (r < instantCrashProb) {
        finalCrashMultiplier = 1.00
      } else {
        finalCrashMultiplier = Math.max(1.00, 
          (0.95 / (1 - houseEdge)) / (r - instantCrashProb + 0.02))
      }

      const gameInterval = setInterval(() => {
        if (gameState.value !== 'playing') {
          clearInterval(gameInterval)
          return
        }

        const elapsedTime = (Date.now() - startTime) / 1000
        currentMultiplier.value = Math.min(
          finalCrashMultiplier,
          Math.max(1.00, Math.pow(Math.E, 0.06 * elapsedTime))
        )
        
        updateChart(currentMultiplier.value)
        updatePotentialWin()

        // Handle auto-cashout
        if (autoCashoutMultiplier && !hasAutoCashedOut.value && currentMultiplier.value >= autoCashoutMultiplier) {
          hasAutoCashedOut.value = true
          cashoutPoint.value = currentMultiplier.value
          cashout()
        }

        // Check for crash
        if (currentMultiplier.value >= finalCrashMultiplier) {
          handleCrash(finalCrashMultiplier)
        }
      }, 50)
    }

    const handleCrash = (crashMultiplier) => {
      if (gameState.value === 'crashed') return

      gameState.value = 'crashed'
      const finalMultiplier = crashMultiplier || currentMultiplier.value
      currentMultiplier.value = finalMultiplier

      if (chart) {
        chart.data.datasets[0].borderColor = '#ef4444'
        chart.update()
      }

      gameHistory.value.unshift({
        multiplier: finalMultiplier,
        cashoutPoint: cashoutPoint.value
      })

      if (gameHistory.value.length > 10) {
        gameHistory.value.pop()
      }

      setTimeout(resetGame, 2000)
    }

    const handleWin = (multiplier, newBalance) => {
      const bet = parseFloat(betAmount.value) || 0
      cashoutAmount.value = bet * multiplier
      
      // Update balance using store
      if (newBalance !== undefined) {
        updateBalance(newBalance)
      }
      
      // Update potential wins after cashout
      const updatePotentialAfterCashout = () => {
        if (gameState.value === 'playing') {
          couldWinAmount.value = bet * currentMultiplier.value
        }
      }
      
      const potentialInterval = setInterval(updatePotentialAfterCashout, 50)
      
      // Store original crash handler
      const originalHandler = crashHandler || handleCrash
      crashHandler = (crashMultiplier) => {
        clearInterval(potentialInterval)
        originalHandler(crashMultiplier)
      }
      
      hasAutoCashedOut.value = true
      cashoutPoint.value = multiplier
    }

    const resetGame = () => {
      gameState.value = 'waiting'
      currentMultiplier.value = 1.00
      hasAutoCashedOut.value = false
      cashoutPoint.value = null
      potentialWin.value = 0
      resetChart()
    }

    const updatePotentialWin = () => {
      if (gameState.value === 'playing' && !hasAutoCashedOut.value) {
        potentialWin.value = parseFloat(betAmount.value) * currentMultiplier.value
      }
    }

    // Lifecycle hooks
    onMounted(() => {
      initializeChart()
    })

    onUnmounted(() => {
      if (chart) {
        chart.destroy()
      }
      // Clean up any remaining intervals
      crashHandler = null
    })

    return {
      chartRef,
      gameState,
      currentMultiplier,
      betAmount,
      autoCashout,
      gameHistory,
      hasAutoCashedOut,
      potentialWin,
      cashoutAmount,
      couldWinAmount,
      balance,
      addToBet,
      doubleBet,
      halfBalance,
      maxBalance,
      repeatBet,
      adjustBet,
      placeBet,
      cashout,
      setAutoCashout,
      adjustAutoCashout,
      formatNumber,
    }
  }
}
</script>

<style scoped>
.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.potential-win {
  text-align: center;
  color: #888;
  font-size: 16px;
}

.win-amount {
  color: #4CAF50;
  font-weight: bold;
  margin-left: 5px;
}

.cashout-info {
  margin-top: 10px;
  padding: 10px;
  background: rgba(76, 175, 80, 0.1);
  border-radius: 5px;
}

.cashout-info.hidden {
  display: none;
}

.won-amount, .potential-after-cashout {
  margin: 5px 0;
}

.cashout-amount {
  color: #4CAF50;
  font-weight: bold;
  margin-left: 5px;
}

.could-win-amount {
  color: #888;
  font-weight: bold;
  margin-left: 5px;
}

.potential-after-cashout {
  font-size: 0.9em;
  opacity: 0.8;
}

.current-potential.hidden {
  display: none;
}

.history-item {
  position: relative;
  padding: 8px 12px;
  border-radius: 5px;
  font-weight: bold;
  min-width: 80px;
  text-align: center;
}

.cashout-indicator {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #4CAF50;
  color: white;
  border-radius: 12px;
  padding: 2px 6px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
}

input[type="number"] {
  -moz-appearance: textfield;
}

input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style> 