<template>
  <div class="min-h-screen bg-gray-darker">
    <!-- Header -->
    <div class="relative py-12 mb-8">
      <div class="absolute inset-0 bg-gradient-to-b from-yellow/5 to-transparent"></div>
      <div class="relative max-w-7xl mx-auto px-4">
        <h1 class="text-4xl font-display font-bold text-white mb-2">Roulette</h1>
        <p class="text-white/70">Classic casino roulette with multipliers!</p>
      </div>
    </div>

    <!-- Game Area -->
    <div class="max-w-7xl mx-auto px-4 pb-12">
      <!-- Previous Rolls -->
      <div class="bg-gray-dark/50 rounded-xl p-6 mb-6">
        <h3 class="text-lg font-medium text-white mb-4">Previous Rolls</h3>
        <div class="flex gap-4 overflow-x-auto py-2">
          <div 
            v-for="roll in previousRolls" 
            :key="roll"
            class="w-12 h-12 rounded-full flex items-center justify-center font-bold text-white flex-shrink-0"
            :class="[
              roll === 0 ? 'bg-green-500' :
              RED_NUMBERS.includes(roll) ? 'bg-red-500' : 'bg-gray-darker'
            ]"
          >
            {{ roll }}
          </div>
        </div>
      </div>

      <!-- Wheel Animation -->
      <div v-show="showWheel" class="wheel-container">
        <!-- Wheel Selector -->
        <div class="wheel-selector">
          <div class="absolute -top-2 left-1/2 -translate-x-1/2 border-8 border-transparent border-t-white"></div>
          <div class="absolute -bottom-2 left-1/2 -translate-x-1/2 border-8 border-transparent border-b-white"></div>
        </div>
        <!-- Wheel Items -->
        <div 
          ref="wheelRef"
          class="wheel"
          :style="wheelStyle"
        >
          <div 
            v-for="number in wheelNumbers" 
            :key="number"
            class="wheel-item"
            :class="[
              number === 0 ? 'bg-green-500' :
              RED_NUMBERS.includes(number) ? 'bg-red-500' : 'bg-gray-darker'
            ]"
          >
            {{ number }}
          </div>
        </div>
      </div>

      <!-- Betting Board -->
      <div class="bg-gray-dark/50 rounded-xl p-6 mb-6 select-none">
        <!-- Betting board and controls section -->
        <div class="relative">
          <!-- Betting Board Content -->
          <div class="relative pl-16">
            <!-- Zero -->
            <div 
              class="absolute left-0 top-0 w-12 h-full bg-green-500 rounded-lg flex items-center justify-center text-white font-bold cursor-pointer zero-tile"
              :class="{ 'ring-2 ring-yellow': selectedBets.has('0') }"
              @click="placeBet('0')"
              data-bet-type="0"
            >
              <span>0</span>
            </div>

            <!-- Numbers Grid -->
            <div class="grid grid-cols-12 gap-1">
              <template v-for="row in 3" :key="row">
                <template v-for="col in 12" :key="col">
                  <div 
                    class="aspect-square rounded-lg flex items-center justify-center text-white font-bold cursor-pointer relative"
                    :class="[
                      getNumberColor((col - 1) * 3 + (4 - row)),
                      { 'ring-2 ring-yellow': selectedBets.has(String((col - 1) * 3 + (4 - row))) }
                    ]"
                    @click="placeBet(String((col - 1) * 3 + (4 - row)))"
                    :data-bet-type="String((col - 1) * 3 + (4 - row))"
                  >
                    <span>{{ (col - 1) * 3 + (4 - row) }}</span>
                  </div>
                </template>
              </template>
            </div>

            <!-- Special Bets -->
            <div class="grid grid-cols-3 gap-1 mt-1 mb-1">
              <div 
                v-for="dozen in ['1st12', '2nd12', '3rd12']" 
                :key="dozen"
                class="bg-gray-darker rounded-lg py-3 text-center text-white font-medium cursor-pointer"
                :class="{ 'ring-2 ring-yellow': selectedBets.has(dozen) }"
                @click="placeBet(dozen)"
                :data-bet-type="dozen"
              >
                <span>{{ dozen }}</span>
              </div>
            </div>

            <div class="grid grid-cols-6 gap-1">
              <div 
                v-for="bet in ['1-18', 'even', 'red', 'black', 'odd', '19-36']" 
                :key="bet"
                class="bg-gray-darker rounded-lg py-3 text-center text-white font-medium cursor-pointer"
                :class="[
                  { 'ring-2 ring-yellow': selectedBets.has(bet) },
                  bet === 'red' ? 'bg-red-500' : '',
                  bet === 'black' ? 'bg-gray-darker' : ''
                ]"
                @click="placeBet(bet)"
                :data-bet-type="bet"
              >
                <span>{{ bet }}</span>
              </div>
            </div>
          </div>

          <!-- Quick Bet Buttons -->
          <div class="mt-6">
            <div class="grid grid-cols-4 gap-2 mb-6">
              <button 
                v-for="amount in [1, 10, 100, 1000]" 
                :key="amount"
                class="px-4 py-2 bg-gray-darker/50 text-white/70 hover:bg-gray-darker hover:text-white rounded-lg transition-all duration-200"
                @click="incrementBet(amount)"
                :disabled="!bettingOpen"
              >
                +${{ amount }}
              </button>
              <button 
                class="px-4 py-2 bg-gray-darker/50 text-white/70 hover:bg-gray-darker hover:text-white rounded-lg transition-all duration-200"
                @click="doubleBet"
                :disabled="!bettingOpen"
              >
                x2
              </button>
              <button 
                class="px-4 py-2 bg-gray-darker/50 text-white/70 hover:bg-gray-darker hover:text-white rounded-lg transition-all duration-200"
                @click="halfBalance"
                :disabled="!bettingOpen"
              >
                1/2
              </button>
              <button 
                class="px-4 py-2 bg-gray-darker/50 text-white/70 hover:bg-gray-darker hover:text-white rounded-lg transition-all duration-200"
                @click="maxBalance"
                :disabled="!bettingOpen"
              >
                Max
              </button>
              <button 
                class="px-4 py-2 bg-gray-darker/50 text-white/70 hover:bg-gray-darker hover:text-white rounded-lg transition-all duration-200"
                @click="clearBets"
                :disabled="!bettingOpen"
              >
                Clear
              </button>
            </div>

            <!-- Bet Input -->
            <div class="mb-6">
              <div class="flex items-center justify-center gap-2">
                <button 
                  class="w-10 h-10 bg-yellow text-gray-darker rounded-lg font-bold"
                  @click="adjustBet(-1)"
                  :disabled="!bettingOpen"
                >
                  -
                </button>
                <input 
                  type="number" 
                  v-model="betAmount"
                  min="0.01"
                  step="0.01"
                  :max="balance"
                  :disabled="!bettingOpen"
                  class="w-40 px-4 py-2 bg-gray-darker text-white text-center rounded-lg"
                  @input="validateBet"
                  @blur="validateBet"
                >
                <button 
                  class="w-10 h-10 bg-yellow text-gray-darker rounded-lg font-bold"
                  @click="adjustBet(1)"
                  :disabled="!bettingOpen"
                >
                  +
                </button>
              </div>
            </div>
          </div>

        </div>

        <!-- Current Bets (outside of overlay) -->
        <div class="mt-6 bg-gray-darker rounded-lg p-4">
          <h3 class="text-lg font-medium text-white mb-4">Current Bets</h3>
          <div class="space-y-2 max-h-48 overflow-y-auto mb-4">
            <div 
              v-for="[bet, amount] in Object.entries(currentBets)" 
              :key="bet"
              class="flex justify-between text-white"
            >
              <span>{{ getBetDisplayName(bet) }}</span>
              <span>${{ amount.toFixed(2) }}</span>
            </div>
          </div>
          <div class="text-lg text-white">
            Total Bet: <span class="text-yellow">${{ totalBetAmount.toFixed(2) }}</span>
          </div>
        </div>
      </div>

      <!-- Timer -->
      <div class="relative bg-gray-darker rounded-lg p-4">
        <!-- Timer bar container -->
        <div class="relative h-1 bg-gray-dark/50">
          <!-- Timer bar -->
          <div 
            class="absolute top-0 left-0 h-full transition-[width] duration-[100ms] linear"
            :class="timeRemaining <= WARNING_TIME ? 'bg-red-500' : 'bg-yellow'"
            :style="{ width: `${(timeRemaining / ROUND_TIME) * 100}%` }"
          ></div>
          <!-- Betting close tick mark -->
          <div 
            class="absolute top-0 h-4 w-1 bg-white -translate-y-1.5 z-10"
            :style="{ left: `${(WARNING_TIME / ROUND_TIME) * 100}%` }"
          >
            <!-- Tick label -->
            <div class="absolute -top-4 left-1/2 -translate-x-1/2 whitespace-nowrap text-xs text-white/70">
              Betting closes
            </div>
          </div>
        </div>
        <div 
          class="text-center text-lg mt-3"
          :class="timeRemaining <= WARNING_TIME ? 'text-red-500' : 'text-white'"
        >
          {{ timeRemaining <= WARNING_TIME ? 'Betting is CLOSED! ' : 'Betting closes in ' }}
          <span class="font-bold">{{ timeRemaining <= WARNING_TIME ? timeRemaining : timeRemaining - WARNING_TIME }}s</span>
        </div>
      </div>
    </div>

    <!-- Result Notification -->
    <div 
      v-if="showResult"
      class="fixed top-4 left-1/2 -translate-x-1/2 bg-gray-dark/95 backdrop-blur-sm px-6 py-4 rounded-xl shadow-xl z-50 flex items-center gap-4"
    >
      <div 
        class="w-12 h-12 rounded-full flex items-center justify-center font-bold text-white"
        :class="[
          lastResult === 0 ? 'bg-green-500' :
          RED_NUMBERS.includes(lastResult) ? 'bg-red-500' : 'bg-gray-darker'
        ]"
      >
        {{ lastResult }}
      </div>
      <div>
        <div class="text-white">{{ resultWon ? 'You Won!' : 'You Lost!' }}</div>
        <div 
          class="text-xl font-bold"
          :class="resultWon ? 'text-green-500' : 'text-red-500'"
        >
          {{ resultWon ? '+' : '-' }}${{ Math.abs(resultAmount).toFixed(2) }}
        </div>
      </div>
    </div>

    <!-- Lightning Numbers Popup -->
    <div 
      v-if="showLightningPopup"
      class="fixed top-4 left-1/2 -translate-x-1/2 bg-gray-dark/95 backdrop-blur-sm px-6 py-4 rounded-xl shadow-xl z-50"
    >
      <h3 class="text-lg font-medium text-white mb-3">Lightning Numbers</h3>
      <div class="flex gap-4">
        <div 
          v-for="(number, index) in lightningNumbers" 
          :key="index"
          class="flex flex-col items-center"
        >
          <div 
            class="w-12 h-12 rounded-full flex items-center justify-center font-bold text-white mb-1"
            :class="[
              number.value === 0 ? 'bg-green-500' :
              RED_NUMBERS.includes(number.value) ? 'bg-red-500' : 'bg-gray-darker'
            ]"
          >
            {{ number.value }}
          </div>
          <div class="text-cyan-400 font-bold">{{ number.multiplier }}x</div>
        </div>
      </div>
    </div>

    <!-- Lightning Win Notification -->
    <div 
      v-if="showLightningWin"
      class="fixed top-4 left-1/2 -translate-x-1/2 bg-gray-dark/95 backdrop-blur-sm px-6 py-4 rounded-xl shadow-xl z-50 flex items-center gap-4"
    >
      <div class="w-12 h-12 rounded-full bg-cyan-400 flex items-center justify-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-black" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <div>
        <div class="text-white">Lightning Win!</div>
        <div class="text-xl font-bold text-cyan-400">
          +${{ lightningWinAmount.toFixed(2) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useStore } from '@/store'

// Import chip images
import chip1 from '@/assets/casino/chip_1.png'
import chip5 from '@/assets/casino/chip_5.png'
import chip10 from '@/assets/casino/chip_10.png'
import chip50 from '@/assets/casino/chip_50.png'
import chip100 from '@/assets/casino/chip_100.png'
import chip500 from '@/assets/casino/chip_500.png'
import chip1000 from '@/assets/casino/chip_1000.png'

// Constants
const RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
const WHEEL_ORDER = [
  0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10,
  5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26
]
const BETTING_TIME = 25 // Time allowed for betting
const WARNING_TIME = 5  // Time after betting closes before result
const ROUND_TIME = BETTING_TIME + WARNING_TIME // Total round time

// Create a map of chip images
const chipImages = {
  1: chip1,
  5: chip5,
  10: chip10,
  50: chip50,
  100: chip100,
  500: chip500,
  1000: chip1000
}

export default {
  name: 'RouletteView',
  setup() {
    // State
    const betAmount = ref('1.00')
    const currentBets = ref({})
    const selectedBets = ref(new Set())
    const previousRolls = ref([])
    const showWheel = ref(false)
    const wheelPosition = ref(0)
    const wheelRef = ref(null)
    const wheelStyle = ref({
      transform: 'translateX(0)',
      transition: 'none'
    })
    const timeRemaining = ref(ROUND_TIME)
    const showResult = ref(false)
    const lastResult = ref(null)
    const resultWon = ref(false)
    const resultAmount = ref(0)
    const bettingOpen = ref(true)
    const balance = ref(0) // Start at 0, will be updated from server
    const timerInterval = ref(null)

    // Function to fetch and update balance
    const updateBalance = async () => {
      try {
        const response = await fetch('/get_balance')
        const data = await response.json()
        if (data.success !== false) {
          console.log('Updating balance:', {
            newBalance: data.balance,
            oldBalance: balance.value,
            type: typeof data.balance
          })
          balance.value = Number(data.balance)
        }
      } catch (error) {
        console.error('Error fetching balance:', error)
      }
    }

    // Fetch initial balance
    onMounted(async () => {
      console.log('Component mounted, fetching initial balance')
      await updateBalance()
      console.log('Initial balance loaded:', {
        balance: balance.value,
        type: typeof balance.value
      })

      // Add event listeners
      document.querySelectorAll('.number, .special-bet').forEach(element => {
        element.addEventListener('click', () => handleNumberClick(element))
      })

      document.querySelectorAll('.quick-bet').forEach(btn => {
        btn.addEventListener('click', () => handleQuickBet(btn))
      })

      // Start game cycle
      startGameCycle()
    })

    // Generate wheel numbers (padding + 3x sequence + padding)
    const wheelNumbers = [
      ...WHEEL_ORDER.slice(-5),
      ...WHEEL_ORDER,
      ...WHEEL_ORDER,
      ...WHEEL_ORDER,
      ...WHEEL_ORDER.slice(0, 5)
    ]

    // Add findNumberIndex function
    const findNumberIndex = (number) => {
      return WHEEL_ORDER.findIndex(n => n === number)
    }

    // Add updatePreviousRolls function
    const updatePreviousRolls = (number) => {
      previousRolls.value.unshift(number)
      if (previousRolls.value.length > 10) {
        previousRolls.value.pop()
      }
    }

    // Add createConfetti function
    const createConfetti = () => {
      const container = document.createElement('div')
      container.id = 'confetti-container'
      container.style.position = 'fixed'
      container.style.top = '0'
      container.style.left = '0'
      container.style.width = '100%'
      container.style.height = '100%'
      container.style.pointerEvents = 'none'
      container.style.zIndex = '9999'
      document.body.appendChild(container)

      const colors = ['#ffd700', '#ff0000', '#00ff00', '#0000ff', '#ff00ff']
      
      for (let i = 0; i < 100; i++) {
        const confetti = document.createElement('div')
        confetti.style.position = 'absolute'
        confetti.style.width = '10px'
        confetti.style.height = '10px'
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)]
        confetti.style.left = Math.random() * 100 + 'vw'
        confetti.style.top = -10 + 'px'
        confetti.style.transform = `rotate(${Math.random() * 360}deg)`
        confetti.style.animation = `confettiFall ${1 + Math.random() * 2}s linear forwards`
        confetti.style.animationDelay = Math.random() * 3 + 's'
        container.appendChild(confetti)
      }

      setTimeout(() => {
        container.remove()
      }, 5000)
    }

    // Add confetti animation keyframes to document
    const style = document.createElement('style')
    style.textContent = `
      @keyframes confettiFall {
        0% {
          transform: translateY(0) rotate(0deg);
          opacity: 1;
        }
        100% {
          transform: translateY(100vh) rotate(720deg);
          opacity: 0;
        }
      }
    `
    document.head.appendChild(style)

    // Computed
    const totalBetAmount = computed(() => {
      return Object.values(currentBets.value).reduce((sum, amount) => sum + Number(amount), 0)
    })

    // Add computed property for available balance
    const availableBalance = computed(() => {
      return Number(balance.value) - Number(totalBetAmount.value)
    })

    // Methods
    const incrementBet = (amount) => {
      const newAmount = Math.min(parseFloat(betAmount.value) + amount, balance.value)
      betAmount.value = Math.max(0.01, newAmount).toFixed(2)
    }

    const doubleBet = () => {
      const newAmount = Math.min(parseFloat(betAmount.value) * 2, balance.value)
      betAmount.value = newAmount.toFixed(2)
    }

    const halfBalance = () => {
      betAmount.value = (balance.value / 2).toFixed(2)
    }

    const maxBalance = () => {
      betAmount.value = balance.value.toFixed(2)
    }

    const adjustBet = (delta) => {
      const newAmount = Math.min(parseFloat(betAmount.value) + delta, balance.value)
      betAmount.value = Math.max(0.01, newAmount).toFixed(2)
    }

    const validateBet = () => {
      let amount = Number(betAmount.value)
      
      // Ensure amount is a valid number and at least 0.01
      if (isNaN(amount) || amount < 0.01) {
        betAmount.value = '0.01'
        return
      }
      
      // Cap at available balance
      if (amount > balance.value) {
        betAmount.value = balance.value.toFixed(2)
      } else {
        // Format to 2 decimal places
        betAmount.value = amount.toFixed(2)
      }
    }

    const placeBet = async (betType) => {
      if (!bettingOpen.value) {
        console.log('Betting is closed')
        return
      }

      // Refresh balance before placing bet
      await updateBalance()

      const amount = Number(betAmount.value)
      console.log('Placing bet:', {
        betType,
        amount,
        currentBalance: balance.value,
        availableBalance: availableBalance.value,
        totalCurrentBets: totalBetAmount.value,
        currentBets: currentBets.value
      })

      if (isNaN(amount) || amount < 0.01) {
        console.log('Invalid bet amount:', amount)
        alert('Please enter a valid bet amount')
        return
      }

      // Use availableBalance for validation
      if (amount > availableBalance.value) {
        console.log('Insufficient funds:', {
          betAmount: amount,
          availableBalance: availableBalance.value,
          totalCurrentBets: totalBetAmount.value,
          balance: balance.value
        })
        alert('Insufficient funds')
        return
      }

      selectedBets.value.add(betType)

      if (currentBets.value[betType]) {
        currentBets.value[betType] = Number(currentBets.value[betType]) + amount
      } else {
        currentBets.value[betType] = amount
      }

      // Decrease balance immediately when placing bet
      const store = useStore()
      balance.value = Number(balance.value) - amount
      store.state.balance = balance.value

      console.log('Bet placed successfully:', {
        betType,
        amount,
        newTotalBets: totalBetAmount.value,
        remainingBalance: availableBalance.value,
        newBalance: balance.value
      })

      // Update visual selection and add chips
      const element = document.querySelector(`[data-bet-type="${betType}"]`)
      if (element) {
        element.classList.add('selected')
        visualizeChips(element, currentBets.value[betType])
      }
    }

    const clearBets = () => {
      currentBets.value = {}
      selectedBets.value.clear()

      // Remove selected class and chips from all betting elements
      document.querySelectorAll('[data-bet-type]').forEach(el => {
        el.classList.remove('selected')
        const chips = el.querySelectorAll('.chip')
        chips.forEach(chip => chip.remove())
      })
    }

    const getBetDisplayName = (bet) => {
      if (bet === '0') return 'Green 0'
      if (!isNaN(bet)) return `Number ${bet}`
      return bet.charAt(0).toUpperCase() + bet.slice(1)
    }

    const getNumberColor = (number) => {
      if (number === 0) return 'bg-green-500'
      return RED_NUMBERS.includes(number) ? 'bg-red-500' : 'bg-gray-darker'
    }

    // Add new reactive refs for lightning features
    const showLightningPopup = ref(false)
    const showLightningWin = ref(false)
    const lightningWinAmount = ref(0)
    const lightningNumbers = ref([])

    // Update generateLightningNumbers function
    const generateLightningNumbers = () => {
      // Clear previous lightning numbers
      document.querySelectorAll('[data-bet-type].lightning').forEach(el => {
        el.classList.remove('lightning')
        el.removeAttribute('data-multiplier')
        const bolt = el.querySelector('.bolt')
        if (bolt) bolt.remove()
      })

      // Determine number of lightning numbers (1-5)
      const numLightning = Math.floor(Math.random() * 5) + 1

      // Define multipliers and their weights
      const multipliers = [
        { value: 50, weight: 45 },
        { value: 100, weight: 30 },
        { value: 200, weight: 15 },
        { value: 300, weight: 5 },
        { value: 400, weight: 3 },
        { value: 500, weight: 2 }
      ]

      // Get random numbers for lightning
      const numbers = []
      const usedNumbers = new Set()
      
      while (numbers.length < numLightning) {
        const number = Math.floor(Math.random() * 37)
        if (!usedNumbers.has(number)) {
          usedNumbers.add(number)
          
          // Select random multiplier based on weights
          const totalWeight = multipliers.reduce((sum, m) => sum + m.weight, 0)
          let random = Math.random() * totalWeight
          let selectedMultiplier
          
          for (const multiplier of multipliers) {
            random -= multiplier.weight
            if (random <= 0) {
              selectedMultiplier = multiplier.value
              break
            }
          }

          numbers.push({
            value: number,
            multiplier: selectedMultiplier
          })

          // Apply lightning effect to number on the board
          const numberEl = document.querySelector(`[data-bet-type="${number}"]`)
          console.log('Looking for element:', `[data-bet-type="${number}"]`, numberEl)
          if (numberEl) {
            numberEl.classList.add('lightning')
            numberEl.setAttribute('data-multiplier', `${selectedMultiplier}x`)
            const bolt = document.createElement('div')
            bolt.className = 'bolt'
            numberEl.appendChild(bolt)
          }
        }
      }

      // Update reactive refs
      lightningNumbers.value = numbers
      showLightningPopup.value = true

      // Hide popup after delay
      setTimeout(() => {
        showLightningPopup.value = false
      }, 3000)

      return numbers
    }

    const visualizeChips = (element, amount) => {
      console.log('Visualizing chips:', { element, amount })

      // Remove existing chips
      element.querySelectorAll('.chip').forEach(chip => chip.remove())

      // Available chip denominations
      const denominations = [1000, 500, 100, 50, 10, 5, 1]
      let remainingAmount = Math.floor(amount)
      let chipsToAdd = []

      // Calculate which chips to use
      for (const denom of denominations) {
        while (remainingAmount >= denom) {
          chipsToAdd.push(denom)
          remainingAmount -= denom
        }
      }

      console.log('Chips to add:', chipsToAdd)

      // Add chips to the element (limit to 5 chips max)
      chipsToAdd.slice(0, 5).forEach((denom, index) => {
        const chip = document.createElement('div')
        chip.className = `chip chip-${denom}`
        chip.style.position = 'absolute'
        chip.style.width = '30px'
        chip.style.height = '30px'
        chip.style.left = '50%'
        chip.style.top = '50%'
        chip.style.transform = `translate(-50%, -50%) translate(${index * 2}px, ${-index * 2}px)`
        chip.style.zIndex = String(1000 + index)
        chip.style.backgroundImage = `url(${chipImages[denom]})`
        chip.style.backgroundSize = 'contain'
        chip.style.backgroundRepeat = 'no-repeat'
        chip.style.backgroundPosition = 'center'
        chip.style.pointerEvents = 'none'
        element.appendChild(chip)
        console.log('Added chip:', { denom, backgroundImage: chip.style.backgroundImage })
      })
    }

    const playGame = async () => {
      try {
        setTimeout(() => {
          // Show wheel animation
          showWheel.value = true
          
          // Get the current lightning numbers from the DOM
          const lightningNumbers = new Set(
            Array.from(document.querySelectorAll('.number.lightning'))
              .map(el => parseInt(el.dataset.number))
          )
          
          // Only send request with bets if there are actual bets
          const hasBets = Object.keys(currentBets.value).length > 0
          const betsToSend = hasBets ? {...currentBets.value} : null  // Send null to indicate no bets
          
          console.log('Starting playGame:', {
            hasBets,
            currentBets: currentBets.value,
            betsToSend,
            balance: balance.value,
            totalBetAmount: totalBetAmount.value
          })
          
          // Clear bets immediately to prevent them from being reused
          clearBets()
          currentBets.value = {}
          selectedBets.value.clear()
          
          fetch('/play_roulette', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
              bets: betsToSend,
              lightningNumbers: Array.from(lightningNumbers),
              clearPreviousBets: !hasBets  // Add flag to clear previous bets
            })
          })
          .then(response => response.json())
          .then(data => {
            console.log('Received game result:', {
              data,
              hasBets,
              betsToSend,
              balance: balance.value
            })

            if (data.error) {
              console.error('Game error:', data.error)
              alert(data.error)
              startGameCycle()
              return
            }

            // Calculate wheel position
            const numberIndex = findNumberIndex(data.result)
            const itemWidth = 90 // 80px width + 10px margin
            const paddingItems = 5
            const basePosition = (paddingItems + 37 + numberIndex) * itemWidth
            const containerWidth = wheelRef.value.parentElement.offsetWidth
            const maxOffset = itemWidth * 0.45
            const randomOffset = (Math.random() * maxOffset * 2) - maxOffset
            const centeringOffset = (containerWidth / 2) - (itemWidth / 2) - randomOffset
            const finalPosition = basePosition - centeringOffset

            // Reset wheel position with a large positive offset
            wheelStyle.value = {
              transform: 'translateX(2000px)',
              transition: 'none'
            }

            // Force reflow
            wheelRef.value.offsetHeight

            // Start spinning animation
            requestAnimationFrame(() => {
              wheelStyle.value = {
                transform: `translateX(-${finalPosition}px)`,
                transition: 'transform 4s cubic-bezier(0.22, 1, 0.36, 1)'
              }
            })

            setTimeout(() => {
              // Update previous rolls
              updatePreviousRolls(data.result)
              
              console.log('Processing game result:', {
                hasBets,
                hasWinnings: data.winnings !== undefined,
                result: data.result,
                winnings: data.winnings,
                totalBet: data.total_bet,
                betsToSend,
                balance: balance.value
              })

              // Only show result and update balance if there were bets THIS round
              // AND we sent actual bets to the server (not an empty object)
              if (hasBets && Object.keys(betsToSend).length > 0 && data.winnings !== undefined) {
                // Update reactive state for result display
                lastResult.value = data.result
                resultWon.value = data.winnings > data.total_bet
                resultAmount.value = data.winnings > data.total_bet ? 
                  data.winnings - data.total_bet : // If won, show net win
                  data.total_bet // If lost, show amount lost

                showResult.value = true

                // Create confetti if won
                if (resultWon.value) {
                  createConfetti()
                }

                // Update balance after showing result
                setTimeout(() => {
                  console.log('Updating balance after result:', {
                    currentBalance: balance.value,
                    winnings: data.winnings,
                    totalBet: data.total_bet
                  })

                  fetch('/update_roulette_balance', {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json'
                    }
                  })
                  .then(response => response.json())
                  .then(updateData => {
                    console.log('Balance update response:', updateData)
                    if (updateData.success) {
                      balance.value = updateData.balance
                      // Update store balance as well
                      const store = useStore()
                      store.state.balance = balance.value
                      console.log('Updated balance:', {
                        newBalance: balance.value,
                        storeBalance: store.state.balance
                      })
                    }
                  })
                }, 500)

                // Hide result after 4 seconds
                setTimeout(() => {
                  showResult.value = false
                }, 4000)
              }

              // Start next round after a delay
              setTimeout(() => {
                startGameCycle()
              }, 2000)
            }, 4000)
          })
          .catch(error => {
            console.error('Error in playGame:', error)
            startGameCycle()
          })
        }, 1000) // Add 1 second delay to allow timer bar transition to complete
      } catch (error) {
        console.error('Error in playGame outer try-catch:', error)
        startGameCycle()
      }
    }

    // Start game cycle
    const startGameCycle = () => {
      timeRemaining.value = ROUND_TIME
      bettingOpen.value = true

      // Clear previous chips and lightning numbers
      clearBets()
      document.querySelectorAll('.number.lightning').forEach(el => {
        el.classList.remove('lightning')
        el.removeAttribute('data-multiplier')
        const bolt = el.querySelector('.bolt')
        if (bolt) bolt.remove()
      })

      // Hide wheel
      showWheel.value = false

      // Reset wheel position without animation
      wheelStyle.value = {
        transform: 'translateX(0)',
        transition: 'none'
      }

      const startTime = Date.now()
      const endTime = startTime + (ROUND_TIME * 1000)
      
      if (timerInterval.value) {
        clearInterval(timerInterval.value)
      }
      
      timerInterval.value = setInterval(() => {
        const now = Date.now()
        const remaining = Math.max(0, endTime - now)
        timeRemaining.value = Math.ceil(remaining / 1000)

        if (Math.ceil(remaining / 1000) === WARNING_TIME && bettingOpen.value) {
          // Close betting and generate lightning numbers
          bettingOpen.value = false
          
          // Close bets on server if any bets were placed
          if (Object.keys(currentBets.value).length > 0) {
            fetch('/close_roulette_bets', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ bets: currentBets.value })
            })
            .then(response => response.json())
            .then(data => {
              if (!data.success) {
                // If server failed, refund bets
                const totalBets = Object.values(currentBets.value).reduce((sum, amount) => sum + parseFloat(amount), 0)
                balance.value += totalBets
                clearBets()
              }
            })
          }
          
          generateLightningNumbers()
        }

        if (remaining <= 0) {
          if (timerInterval.value) {
            clearInterval(timerInterval.value)
          }
          playGame()
        }
      }, 50)
    }

    // Update handleNumberClick to use async placeBet
    const handleNumberClick = async (element) => {
      if (!bettingOpen.value) {
        console.log('Betting is closed')
        return
      }

      // Refresh balance before checking
      await updateBalance()

      const amount = parseFloat(betAmount.value)
      console.log('Number clicked:', {
        element,
        amount,
        currentBalance: balance.value,
        availableBalance: availableBalance.value
      })

      if (isNaN(amount) || amount <= 0) {
        console.log('Invalid bet amount:', amount)
        alert('Please enter a valid bet amount')
        return
      }

      // Use availableBalance for validation
      if (Number(amount) > availableBalance.value) {
        console.log('Insufficient funds in handleNumberClick:', {
          betAmount: Number(amount),
          availableBalance: availableBalance.value,
          totalCurrentBets: totalBetAmount.value,
          balance: balance.value
        })
        alert('Insufficient funds')
        return
      }

      const betType = element.dataset.number || element.dataset.bet
      console.log('Proceeding with bet:', { betType, amount })
      await placeBet(betType)
    }

    // Quick bet handlers
    const handleQuickBet = (btn) => {
      const currentBet = parseFloat(betAmount.value) || 0
      let newAmount

      if (btn.classList.contains('increment-bet')) {
        const incrementAmount = parseFloat(btn.dataset.amount)
        newAmount = currentBet + incrementAmount
      } else if (btn.classList.contains('half-balance')) {
        newAmount = balance.value / 2
      } else if (btn.classList.contains('double-bet')) {
        newAmount = Math.min(currentBet * 2, balance.value)
      } else if (btn.classList.contains('max-balance')) {
        newAmount = balance.value
      } else if (btn.classList.contains('clear-bets')) {
        clearBets()
        return
      } else if (btn.classList.contains('clear-input')) {
        betAmount.value = '1.00'
        return
      }

      // Ensure bet doesn't go below 0.01 and doesn't exceed balance
      newAmount = Math.max(0.01, Math.min(newAmount, balance.value))
      betAmount.value = newAmount.toFixed(2)
    }

    // Lifecycle
    onMounted(() => {
      // Fetch initial balance
      fetch('/get_balance')
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            balance.value = parseFloat(data.balance)
            console.log('Initial balance loaded:', {
              balance: balance.value,
              type: typeof balance.value
            })
          }
        })
        .catch(error => console.error('Error fetching balance:', error))

      // Add event listeners
      document.querySelectorAll('.number, .special-bet').forEach(element => {
        element.addEventListener('click', () => handleNumberClick(element))
      })

      document.querySelectorAll('.quick-bet').forEach(btn => {
        btn.addEventListener('click', () => handleQuickBet(btn))
      })

      // Start game cycle
      startGameCycle()
    })

    onUnmounted(() => {
      if (timerInterval.value) {
        clearInterval(timerInterval.value)
      }
    })

    return {
      // Constants
      RED_NUMBERS,
      BETTING_TIME,
      WARNING_TIME,
      ROUND_TIME,
      // State
      betAmount,
      currentBets,
      selectedBets,
      previousRolls,
      showWheel,
      wheelPosition,
      wheelNumbers,
      timeRemaining,
      showResult,
      lastResult,
      resultWon,
      resultAmount,
      // Computed
      totalBetAmount,
      availableBalance,
      // Methods
      incrementBet,
      doubleBet,
      halfBalance,
      maxBalance,
      adjustBet,
      validateBet,
      placeBet,
      clearBets,
      getBetDisplayName,
      getNumberColor,
      bettingOpen,
      generateLightningNumbers,
      visualizeChips,
      showLightningPopup,
      showLightningWin,
      lightningWinAmount,
      lightningNumbers,
      findNumberIndex,
      updatePreviousRolls,
      createConfetti,
      wheelRef,
      wheelStyle,
      balance,
      handleNumberClick,
      handleQuickBet,
    }
  }
}
</script>