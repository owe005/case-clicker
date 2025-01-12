<template>
  <div class="min-h-screen bg-gray-darker">
    <!-- Header -->
    <div class="relative py-12 mb-8">
      <div class="absolute inset-0 bg-gradient-to-b from-yellow/5 to-transparent"></div>
      <div class="relative max-w-7xl mx-auto px-4">
        <h1 class="text-4xl font-display font-bold text-white mb-2">Blackjack</h1>
        <p class="text-white/70">Try to beat the dealer to 21!</p>
      </div>
    </div>

    <!-- Game Area -->
    <div class="max-w-7xl mx-auto px-4 pb-12">
      <div class="bg-gray-dark/50 rounded-xl p-6 md:p-8">
        <!-- Notification Area -->
        <div v-if="gameOver" class="text-center mb-8">
          <div class="text-3xl font-bold text-white bg-black/50 p-4 rounded-lg" :class="getResultClass(finalResult)">
            {{ finalResult }}
          </div>
          <div class="mt-4">
            <button 
              @click="resetGame"
              class="px-6 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200"
            >
              Play Again
            </button>
            <button 
              @click="returnToCasino"
              class="px-6 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200 ml-4"
            >
              Return to Casino
            </button>
          </div>
        </div>

        <!-- Balance Display -->
        <div class="flex justify-between items-center mb-8">
          <div class="text-white">
            <span class="text-white/70">Balance:</span>
            <span class="ml-2 text-xl font-medium">${{ formatNumber(balance) }}</span>
          </div>
          <div v-if="!gameActive && !gameOver" class="flex items-center space-x-4">
            <input 
              type="number" 
              v-model="betAmount"
              class="bg-gray-darker px-4 py-2 rounded-lg text-white w-32"
              placeholder="Bet amount"
              min="0.01"
              step="0.01"
            >
            <button 
              @click="startGame"
              class="px-6 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200"
              :disabled="!canBet"
            >
              Place Bet
            </button>
          </div>
        </div>

        <!-- Game Table -->
        <div class="relative min-h-[500px] bg-green-800/20 rounded-xl p-6 md:p-8">
          <!-- Dealer's Hand -->
          <div class="mb-16">
            <h3 class="text-white/70 mb-4">Dealer's Hand {{ dealerValue ? `(${dealerValue})` : '' }}</h3>
            <div class="flex space-x-4">
              <template v-for="(card, index) in dealerCards" :key="index">
                <div 
                  class="w-24 h-36 rounded-lg shadow-lg transition-transform duration-300 hover:transform hover:-translate-y-2"
                  :class="[index === 1 && !showHoleCard ? 'bg-gray-dark' : getCardClass(card)]"
                >
                  <div v-if="index !== 1 || showHoleCard" class="h-full flex items-center justify-center text-2xl font-bold">
                    {{ card.rank }}{{ card.suit }}
                  </div>
                </div>
              </template>
            </div>
          </div>

          <!-- Player's Hands -->
          <div>
            <div v-for="(hand, handIndex) in playerHands" :key="handIndex" class="mb-8">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-white/70">
                  Player's Hand {{ playerHands.length > 1 ? (handIndex + 1) : '' }} 
                  ({{ hand.value }})
                </h3>
                <div class="text-white/70">
                  Bet: ${{ formatNumber(hand.bet) }}
                </div>
              </div>
              
              <!-- Cards -->
              <div class="flex space-x-4 mb-4">
                <div 
                  v-for="(card, cardIndex) in hand.cards" 
                  :key="cardIndex"
                  class="w-24 h-36 rounded-lg shadow-lg transition-transform duration-300 hover:transform hover:-translate-y-2"
                  :class="getCardClass(card)"
                >
                  <div class="h-full flex items-center justify-center text-2xl font-bold">
                    {{ card.rank }}{{ card.suit }}
                  </div>
                </div>
              </div>

              <!-- Action Buttons -->
              <div v-if="gameActive && hand.is_current" class="flex space-x-4">
                <button 
                  @click="hit"
                  class="px-6 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200"
                  :disabled="!hand.is_current"
                >
                  Hit
                </button>
                <button 
                  @click="stand"
                  class="px-6 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200"
                  :disabled="!hand.is_current"
                >
                  Stand
                </button>
                <button 
                  v-if="hand.can_double"
                  @click="doubleDown"
                  class="px-6 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200"
                  :disabled="!hand.is_current || balance < hand.bet"
                >
                  Double Down
                </button>
                <button 
                  v-if="hand.can_split"
                  @click="split"
                  class="px-6 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200"
                  :disabled="!hand.is_current || balance < hand.bet"
                >
                  Split
                </button>
                <button 
                  v-if="insuranceAvailable && !hand.insurance"
                  @click="takeInsurance"
                  class="px-6 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200"
                  :disabled="!hand.is_current || balance < (hand.bet / 2)"
                >
                  Insurance
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import axios from 'axios'

export default {
  name: 'BlackjackView',
  setup() {
    const balance = ref(0)
    const betAmount = ref(1)
    const gameActive = ref(false)
    const dealerCards = ref([])
    const dealerValue = ref(null)
    const playerHands = ref([])
    const showHoleCard = ref(false)
    const insuranceAvailable = ref(false)
    const gameOver = ref(false)
    const finalResult = ref('')

    // Load initial balance
    const loadBalance = async () => {
      try {
        const response = await axios.get('/get_balance')
        balance.value = response.data.balance
      } catch (error) {
        console.error('Error loading balance:', error)
      }
    }
    loadBalance()

    const canBet = computed(() => {
      return betAmount.value > 0 && betAmount.value <= balance.value
    })

    const startGame = async () => {
      try {
        const response = await axios.post('/api/blackjack/start', {
          bet: betAmount.value
        })
        
        if (response.data.success) {
          updateGameState(response.data.state)
          balance.value = response.data.balance
          gameActive.value = true
          gameOver.value = false
          finalResult.value = ''
        }
      } catch (error) {
        console.error('Error starting game:', error)
      }
    }

    const updateGameState = (state) => {
      console.log('Updating game state...', state)
      dealerCards.value = state.dealer_hand.cards
      dealerValue.value = state.dealer_hand.value
      playerHands.value = state.player_hands
      showHoleCard.value = state.game_over || state.dealer_hand.show_hole_card
      insuranceAvailable.value = state.insurance_available || (dealerCards.value[0]?.rank === 'A')
      
      if (state.game_over) {
        gameActive.value = false
        gameOver.value = true
        finalResult.value = calculateFinalResult(state.player_hands)
      }
      console.log('Game state updated:', {
        dealerCards: dealerCards.value,
        dealerValue: dealerValue.value,
        playerHands: playerHands.value,
        showHoleCard: showHoleCard.value,
        insuranceAvailable: insuranceAvailable.value,
        gameActive: gameActive.value,
        gameOver: gameOver.value
      })
    }

    const calculateFinalResult = (hands) => {
      let win = false
      let lose = false

      console.log('Calculating final result...')
      hands.forEach(hand => {
        console.log('Hand result:', hand.result)
        if (hand.result === 'WIN' || hand.result === 'BLACKJACK') {
          win = true
        } else if (hand.result === 'LOSE' || hand.result === 'BUST') {
          lose = true
        }
      })

      console.log('Win:', win, 'Lose:', lose)

      if (win && !lose) {
        return 'You Win!'
      } else if (lose && !win) {
        return 'You Lose!'
      } else if (win && lose) {
        return 'Mixed Results'
      }
      return 'Game Over'  // Default message if no specific result
    }

    const hit = async () => {
      try {
        const response = await axios.post('/api/blackjack/hit')
        if (response.data.success) {
          updateGameState(response.data.state)
          if (response.data.balance !== undefined) {
            balance.value = response.data.balance
          }
        }
      } catch (error) {
        console.error('Error hitting:', error)
      }
    }

    const stand = async () => {
      try {
        const response = await axios.post('/api/blackjack/stand')
        if (response.data.success) {
          updateGameState(response.data.state)
          if (response.data.balance !== undefined) {
            balance.value = response.data.balance
          }
        }
      } catch (error) {
        console.error('Error standing:', error)
      }
    }

    const doubleDown = async () => {
      try {
        const response = await axios.post('/api/blackjack/double')
        if (response.data.success) {
          updateGameState(response.data.state)
          balance.value = response.data.balance
        }
      } catch (error) {
        console.error('Error doubling down:', error)
      }
    }

    const split = async () => {
      console.log('Attempting to split...')
      try {
        const response = await axios.post('/api/blackjack/split')
        if (response.data.success) {
          console.log('Split successful, updating game state...')
          updateGameState(response.data.state)
          balance.value = response.data.balance
        } else {
          console.log('Split failed:', response.data)
        }
      } catch (error) {
        console.error('Error splitting:', error)
      }
    }

    const takeInsurance = async () => {
      try {
        const response = await axios.post('/api/blackjack/insurance')
        if (response.data.success) {
          updateGameState(response.data.state)
          balance.value = response.data.balance
        }
      } catch (error) {
        console.error('Error taking insurance:', error)
      }
    }

    const resetGame = () => {
      gameActive.value = false
      gameOver.value = false
      finalResult.value = ''
      playerHands.value = []
      dealerCards.value = []
      dealerValue.value = null
    }

    const returnToCasino = () => {
      // Logic to return to the casino view
      console.log('Returning to casino...')
    }

    const getCardClass = (card) => {
      const suitColors = {
        '♠': 'bg-gray-800 text-white',
        '♣': 'bg-gray-800 text-white',
        '♥': 'bg-red-800 text-white',
        '♦': 'bg-red-800 text-white'
      }
      return suitColors[card.suit] || 'bg-gray-800 text-white'
    }

    const getResultClass = (result) => {
      const resultColors = {
        'BLACKJACK': 'text-yellow',
        'WIN': 'text-green-500',
        'PUSH': 'text-white',
        'LOSE': 'text-red-500',
        'BUST': 'text-red-500',
        'DEALER BUST': 'text-green-500',
        'DEALER BLACKJACK': 'text-red-500'
      }
      return resultColors[result] || 'text-white'
    }

    const formatNumber = (num) => {
      return Number(num).toFixed(2)
    }

    return {
      balance,
      betAmount,
      gameActive,
      dealerCards,
      dealerValue,
      playerHands,
      showHoleCard,
      insuranceAvailable,
      gameOver,
      finalResult,
      canBet,
      startGame,
      hit,
      stand,
      doubleDown,
      split,
      takeInsurance,
      resetGame,
      returnToCasino,
      getCardClass,
      getResultClass,
      formatNumber
    }
  }
}
</script>

<style scoped>
.shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
</style>
