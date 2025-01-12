<template>
  <div class="min-h-screen bg-gray-darker">
    <!-- Header -->
    <div class="relative py-12 mb-8">
      <div class="absolute inset-0 bg-gradient-to-b from-yellow/5 to-transparent"></div>
      <div class="relative max-w-7xl mx-auto px-4">
        <h1 class="text-4xl font-display font-bold text-white mb-2">Blackjack</h1>
        <p class="text-white/70">Try to beat the dealer to 21</p>
      </div>
    </div>

    <!-- Game Area -->
    <div class="max-w-7xl mx-auto px-4 pb-12">
      <div class="bg-gray-dark/50 rounded-xl p-8 relative overflow-hidden">
        <!-- Background Pattern -->
        <div class="absolute inset-0 bg-[radial-gradient(#ffffff11_1px,transparent_1px)] [background-size:16px_16px] [mask-image:radial-gradient(ellipse_50%_50%_at_50%_50%,black,transparent)]"></div>
        
        <!-- Dealer's Area -->
        <div class="mb-12 relative">
          <h2 class="text-xl font-display text-white mb-4">
            Dealer's Hand <span class="text-yellow">{{ dealerScore }}</span>
          </h2>
          <div class="flex justify-center items-center min-h-[180px] p-6 bg-gray-darker/50 rounded-xl border border-white/5">
            <TransitionGroup 
              name="card" 
              tag="div" 
              class="flex gap-4"
            >
              <div 
                v-for="(card, index) in dealerCards" 
                :key="card.id || index"
                class="relative w-32 h-48 rounded-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2"
                :class="[
                  card.hidden ? 'bg-gray-dark shadow-lg' : 'bg-white shadow-xl',
                  `translate-x-${index * 2}`
                ]"
                :style="{ zIndex: index }"
              >
                <div v-if="card.hidden" class="absolute inset-0 flex items-center justify-center">
                  <div class="text-4xl text-yellow animate-pulse">?</div>
                </div>
                <div v-else class="absolute inset-0 flex flex-col items-center justify-center">
                  <div 
                    class="text-3xl font-medium"
                    :class="['♥', '♦'].includes(card.suit) ? 'text-red-500' : 'text-gray-900'"
                  >
                    {{ card.rank }}
                  </div>
                  <div 
                    class="text-4xl mt-1"
                    :class="['♥', '♦'].includes(card.suit) ? 'text-red-500' : 'text-gray-900'"
                  >
                    {{ card.suit }}
                  </div>
                </div>
                <div class="absolute inset-0 rounded-xl ring-1 ring-black/5"></div>
              </div>
            </TransitionGroup>
          </div>
        </div>

        <!-- Player's Area -->
        <div class="mb-12">
          <h2 class="text-xl font-display text-white mb-4">Your Hand</h2>
          <div class="flex justify-center gap-8">
            <TransitionGroup 
              name="hand" 
              tag="div" 
              class="flex flex-wrap gap-8"
            >
              <div 
                v-for="(hand, handIndex) in playerHands" 
                :key="handIndex"
                class="flex flex-col gap-4 transition-all duration-300"
                :class="{ 
                  'ring-2 ring-yellow rounded-xl p-4 bg-yellow/5': handIndex === currentHand,
                  'opacity-50': handIndex !== currentHand && playerHands.length > 1
                }"
              >
                <TransitionGroup 
                  name="card" 
                  tag="div" 
                  class="flex gap-4"
                >
                  <div 
                    v-for="(card, cardIndex) in hand" 
                    :key="card.id || cardIndex"
                    class="relative w-32 h-48 rounded-xl bg-white shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2"
                    :class="`translate-x-${cardIndex * 2}`"
                    :style="{ zIndex: cardIndex }"
                  >
                    <div class="absolute inset-0 flex flex-col items-center justify-center">
                      <div 
                        class="text-3xl font-medium"
                        :class="['♥', '♦'].includes(card.suit) ? 'text-red-500' : 'text-gray-900'"
                      >
                        {{ card.rank }}
                      </div>
                      <div 
                        class="text-4xl mt-1"
                        :class="['♥', '♦'].includes(card.suit) ? 'text-red-500' : 'text-gray-900'"
                      >
                        {{ card.suit }}
                      </div>
                    </div>
                    <div class="absolute inset-0 rounded-xl ring-1 ring-black/5"></div>
                  </div>
                </TransitionGroup>
                <div class="text-center">
                  <span class="text-yellow font-medium">Score: {{ playerScores[handIndex] }}</span>
                  <span v-if="handIndex === currentHand" class="text-white/50 text-sm ml-2">(Current Hand)</span>
                </div>
              </div>
            </TransitionGroup>
          </div>
        </div>

        <!-- Betting Controls -->
        <div class="mb-8">
          <div class="flex flex-wrap gap-4 justify-center mb-6">
            <button 
              v-for="amount in [1, 10, 100, 1000]"
              :key="amount"
              class="px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105"
              :class="[
                gameInProgress ? 
                'bg-gray-dark/50 text-white/30 cursor-not-allowed' : 
                'bg-yellow/10 hover:bg-yellow/20 text-yellow active:scale-95'
              ]"
              @click="incrementBet(amount)"
              :disabled="gameInProgress"
            >
              +${{ amount }}
            </button>
            <button 
              class="px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105"
              :class="[
                gameInProgress ? 
                'bg-gray-dark/50 text-white/30 cursor-not-allowed' : 
                'bg-yellow/10 hover:bg-yellow/20 text-yellow active:scale-95'
              ]"
              @click="doubleBet"
              :disabled="gameInProgress"
            >
              x2
            </button>
            <button 
              class="px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105"
              :class="[
                gameInProgress ? 
                'bg-gray-dark/50 text-white/30 cursor-not-allowed' : 
                'bg-yellow/10 hover:bg-yellow/20 text-yellow active:scale-95'
              ]"
              @click="halfBalance"
              :disabled="gameInProgress"
            >
              1/2
            </button>
            <button 
              class="px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105"
              :class="[
                gameInProgress ? 
                'bg-gray-dark/50 text-white/30 cursor-not-allowed' : 
                'bg-yellow/10 hover:bg-yellow/20 text-yellow active:scale-95'
              ]"
              @click="maxBalance"
              :disabled="gameInProgress"
            >
              Max
            </button>
            <button 
              class="px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105"
              :class="[
                gameInProgress ? 
                'bg-gray-dark/50 text-white/30 cursor-not-allowed' : 
                'bg-yellow/10 hover:bg-yellow/20 text-yellow active:scale-95'
              ]"
              @click="repeatBet"
              :disabled="gameInProgress"
            >
              Repeat
            </button>
          </div>

          <div class="flex justify-center mb-6">
            <div class="flex items-center gap-2 bg-gray-darker/50 rounded-lg p-2">
              <button 
                class="px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105"
                :class="[
                  gameInProgress ? 
                  'bg-gray-dark/50 text-white/30 cursor-not-allowed' : 
                  'bg-yellow/10 hover:bg-yellow/20 text-yellow active:scale-95'
                ]"
                @click="incrementBet(-1)"
                :disabled="gameInProgress"
              >
                -
              </button>
              <input 
                v-model="betInput"
                type="number" 
                min="0.01" 
                step="0.01"
                class="w-32 px-4 py-2 bg-gray-darker text-yellow text-center rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow/50 transition-all duration-200"
                :class="gameInProgress ? 'opacity-50 cursor-not-allowed' : ''"
                :disabled="gameInProgress"
              >
              <button 
                class="px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105"
                :class="[
                  gameInProgress ? 
                  'bg-gray-dark/50 text-white/30 cursor-not-allowed' : 
                  'bg-yellow/10 hover:bg-yellow/20 text-yellow active:scale-95'
                ]"
                @click="incrementBet(1)"
                :disabled="gameInProgress"
              >
                +
              </button>
            </div>
          </div>
        </div>

        <!-- Game Controls -->
        <div class="flex flex-wrap justify-center gap-4">
          <button 
            class="px-6 py-3 rounded-lg font-medium transition-all duration-200 transform hover:scale-105"
            :class="[
              !validateBet() ? 
              'bg-gray-dark/50 text-white/30 cursor-not-allowed' : 
              'bg-yellow text-gray-darker hover:bg-yellow/90 active:scale-95'
            ]"
            @click="handleDeal"
            :disabled="!validateBet()"
          >
            Deal
          </button>
          <button 
            class="px-6 py-3 rounded-lg font-medium transition-all duration-200 transform hover:scale-105"
            :class="[
              !canHit ? 
              'bg-gray-dark/50 text-white/30 cursor-not-allowed' : 
              'bg-green-500 text-white hover:bg-green-600 active:scale-95'
            ]"
            @click="handleHit"
            :disabled="!canHit"
          >
            Hit
          </button>
          <button 
            class="px-6 py-3 rounded-lg font-medium transition-all duration-200 transform hover:scale-105"
            :class="[
              !canStand ? 
              'bg-gray-dark/50 text-white/30 cursor-not-allowed' : 
              'bg-red-500 text-white hover:bg-red-600 active:scale-95'
            ]"
            @click="handleStand"
            :disabled="!canStand"
          >
            Stand
          </button>
          <button 
            class="px-6 py-3 rounded-lg font-medium transition-all duration-200 transform hover:scale-105"
            :class="[
              !canDouble ? 
              'bg-gray-dark/50 text-white/30 cursor-not-allowed' : 
              'bg-blue-500 text-white hover:bg-blue-600 active:scale-95'
            ]"
            @click="handleDouble"
            :disabled="!canDouble"
          >
            Double Down
          </button>
          <button 
            class="px-6 py-3 rounded-lg font-medium transition-all duration-200 transform hover:scale-105"
            :class="[
              !canSplit ? 
              'bg-gray-dark/50 text-white/30 cursor-not-allowed' : 
              'bg-purple-500 text-white hover:bg-purple-600 active:scale-95'
            ]"
            @click="handleSplit"
            :disabled="!canSplit"
          >
            Split
          </button>
        </div>

        <!-- Insurance Prompt -->
        <Transition name="modal">
          <div 
            v-if="showInsurance"
            class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
          >
            <div class="bg-gray-dark rounded-xl p-8 max-w-md w-full mx-4 transform transition-all duration-300">
              <h3 class="text-xl font-display text-white mb-4">Insurance?</h3>
              <p class="text-white/70 mb-6">Dealer is showing an Ace. Would you like to take insurance?</p>
              <div class="flex flex-col gap-4">
                <input 
                  v-model="insuranceAmount"
                  type="number" 
                  min="0.01" 
                  step="0.01"
                  class="w-full px-4 py-2 bg-gray-darker text-yellow text-center rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow/50 transition-all duration-200"
                >
                <div class="flex gap-4">
                  <button 
                    class="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg transition-all duration-200 hover:bg-green-600 transform hover:scale-105 active:scale-95"
                    @click="handleInsurance(true)"
                  >
                    Yes
                  </button>
                  <button 
                    class="flex-1 px-4 py-2 bg-red-500 text-white rounded-lg transition-all duration-200 hover:bg-red-600 transform hover:scale-105 active:scale-95"
                    @click="handleInsurance(false)"
                  >
                    No
                  </button>
                </div>
              </div>
            </div>
          </div>
        </Transition>

        <!-- Result Display -->
        <Transition name="modal">
          <div 
            v-if="showResult"
            class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
          >
            <div class="bg-gray-dark rounded-xl p-8 max-w-md w-full mx-4 text-center transform transition-all duration-300">
              <h2 class="text-2xl font-display text-white mb-4">{{ resultText }}</h2>
              <div 
                class="text-4xl font-bold mb-8"
                :class="resultIsWin ? 'text-green-500' : 'text-red-500'"
              >
                {{ resultAmount }}
              </div>
              <div class="flex gap-4">
                <button 
                  class="flex-1 px-6 py-3 bg-yellow text-gray-darker rounded-lg font-medium transition-all duration-200 hover:bg-yellow/90 transform hover:scale-105 active:scale-95"
                  @click="handlePlayAgain"
                >
                  Play Again
                </button>
                <router-link 
                  to="/casino" 
                  class="flex-1 px-6 py-3 bg-gray-darker text-white rounded-lg font-medium transition-all duration-200 hover:bg-gray-dark/70 text-center transform hover:scale-105"
                >
                  Return
                </router-link>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card-enter-active,
.card-leave-active {
  transition: all 0.3s ease;
}

.card-enter-from {
  opacity: 0;
  transform: translateY(-30px) scale(0.9);
}

.card-leave-to {
  opacity: 0;
  transform: translateY(30px) scale(0.9);
}

.hand-enter-active,
.hand-leave-active {
  transition: all 0.3s ease;
}

.hand-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.hand-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from {
  opacity: 0;
  transform: scale(0.9);
}

.modal-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>

<script>
import { ref, computed, onUnmounted } from 'vue'
import { useStore } from '../store'

export default {
  name: 'BlackjackView',
  setup() {
    const store = useStore()
    const balance = computed(() => store.state.balance)

    const betInput = ref(1.00)
    const gameInProgress = ref(false)
    const lastBetAmount = ref(1.00)
    const dealerCards = ref([])
    const playerHands = ref([[]])
    const currentHand = ref(0)
    const dealerScore = ref('')
    const playerScores = ref([])
    const canHit = ref(false)
    const canStand = ref(false)
    const canDouble = ref(false)
    const canSplit = ref(false)
    const showInsurance = ref(false)
    const insuranceAmount = ref(0)
    const showResult = ref(false)
    const resultText = ref('')
    const resultAmount = ref('')
    const resultIsWin = ref(false)

    // Add unique IDs to cards for animation purposes
    let nextCardId = 1

    const validateBet = () => {
      const amount = Math.round((parseFloat(betInput.value) || 0) * 100) / 100
      const isValidBet = !isNaN(amount) && amount > 0 && amount <= balance.value
      
      if (amount > balance.value) {
        betInput.value = balance.value.toFixed(2)
      }
      
      return isValidBet && !gameInProgress.value
    }

    const incrementBet = (amount) => {
      const newAmount = Math.round((parseFloat(betInput.value) + amount) * 100) / 100
      betInput.value = Math.min(Math.max(newAmount, 0.01), balance.value).toFixed(2)
    }

    const doubleBet = () => {
      const newAmount = Math.round((parseFloat(betInput.value) * 2) * 100) / 100
      betInput.value = Math.min(newAmount, balance.value).toFixed(2)
    }

    const halfBalance = () => {
      betInput.value = (balance.value / 2).toFixed(2)
    }

    const maxBalance = () => {
      betInput.value = balance.value.toFixed(2)
    }

    const repeatBet = () => {
      betInput.value = Math.min(lastBetAmount.value, balance.value).toFixed(2)
    }

    const handleDeal = async () => {
      const amount = parseFloat(betInput.value)
      if (!validateBet()) {
        alert('Invalid bet amount')
        return
      }
      
      try {
        // Disable controls and set game in progress before making request
        gameInProgress.value = true
        canHit.value = false
        canStand.value = false
        canDouble.value = false
        canSplit.value = false
        
        const response = await fetch('/play_blackjack', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'deal', amount })
        })
        
        const data = await response.json()
        if (data.error) {
          // Reset game state on error
          gameInProgress.value = false
          alert(data.error)
          return
        }
        
        lastBetAmount.value = amount
        await updateGameState(data)
        // Only start state check if game was successfully started
        if (gameInProgress.value) {
          startStateCheck()
        }
      } catch (error) {
        console.error('Error:', error)
        gameInProgress.value = false
        alert('Failed to start game')
      }
    }

    const handleHit = async () => {
      if (!canHit.value) return
      
      try {
        const response = await fetch('/play_blackjack', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'hit' })
        })
        
        const data = await response.json()
        if (data.error) {
          alert(data.error)
          return
        }
        
        await updateGameState(data)
      } catch (error) {
        console.error('Hit failed:', error)
        alert('Failed to hit')
      }
    }

    const handleStand = async () => {
      console.log('Stand requested, canStand:', canStand.value, 'gameInProgress:', gameInProgress.value)
      if (!canStand.value || !gameInProgress.value) {
        console.log('Stand rejected - not allowed or no game in progress')
        return
      }
      
      try {
        // Disable controls immediately to prevent double clicks
        const previousControls = {
          canHit: canHit.value,
          canStand: canStand.value,
          canDouble: canDouble.value,
          canSplit: canSplit.value
        }
        canHit.value = false
        canStand.value = false
        canDouble.value = false
        canSplit.value = false
        
        const response = await fetch('/play_blackjack', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'stand' })
        })
        
        const data = await response.json()
        console.log('Stand response:', data)
        
        if (data.error) {
          console.error('Stand error:', data.error)
          if (data.error === 'No game in progress') {
            // Verify game state before resetting
            try {
              const stateResponse = await fetch('/play_blackjack', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'check_state' })
              })
              const stateData = await stateResponse.json()
              
              if (stateData.error === 'No game in progress') {
                handlePlayAgain()
              } else {
                // Restore game state from server
                await updateGameState(stateData)
                // Retry the stand action
                const retryResponse = await fetch('/play_blackjack', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ action: 'stand' })
                })
                const retryData = await retryResponse.json()
                if (!retryData.error) {
                  await updateGameState(retryData)
                  return
                }
              }
            } catch (stateError) {
              console.error('Failed to verify game state:', stateError)
            }
            handlePlayAgain()
          } else {
            // Restore previous control states on error
            Object.assign({ canHit, canStand, canDouble, canSplit }, previousControls)
            alert(data.error)
          }
          return
        }
        
        console.log('Stand successful, updating game state')
        await updateGameState(data)
      } catch (error) {
        console.error('Stand failed:', error)
        alert('Failed to stand')
      }
    }

    const handleDouble = async () => {
      console.log('Double down requested, canDouble:', canDouble.value)
      if (!canDouble.value || !gameInProgress.value) {
        console.log('Double down rejected - not allowed or no game in progress')
        return
      }
      
      try {
        // Disable controls immediately
        canHit.value = false
        canStand.value = false
        canDouble.value = false
        canSplit.value = false
        
        const response = await fetch('/play_blackjack', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            action: 'double',
            amount: parseFloat(betInput.value)
          })
        })
        
        const data = await response.json()
        console.log('Double down response:', data)
        
        if (data.error) {
          console.error('Double down error:', data.error)
          if (data.error === 'No game in progress') {
            handlePlayAgain()
          } else {
            alert(data.error)
          }
          return
        }
        
        console.log('Double down successful, updating game state')
        await updateGameState(data)
      } catch (error) {
        console.error('Double down failed:', error)
        alert('Failed to double down')
      }
    }

    const handleSplit = async () => {
      if (!canSplit.value) return
      
      try {
        const response = await fetch('/play_blackjack', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'split' })
        })
        
        const data = await response.json()
        if (data.error) {
          alert(data.error)
          return
        }
        
        await updateGameState(data)
      } catch (error) {
        console.error('Error:', error)
        alert('Failed to split')
      }
    }

    const handleInsurance = async (accept) => {
      if (!accept) {
        showInsurance.value = false
        // After declining insurance, check for blackjacks
        try {
          const response = await fetch('/play_blackjack', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'check_blackjack' })
          })
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
          
          const data = await response.json()
          if (data.error) {
            if (data.error === 'No game in progress') {
              // Try to recover the game state
              const stateResponse = await fetch('/play_blackjack', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'check_state' })
              })
              
              if (stateResponse.ok) {
                const stateData = await stateResponse.json()
                if (!stateData.error) {
                  await updateGameState(stateData)
                  return
                }
              }
              handlePlayAgain()
            }
            alert(data.error)
            return
          }
          
          await updateGameState(data)
        } catch (error) {
          console.error('Error checking for blackjack:', error)
          alert('Failed to check for blackjack')
        }
        return
      }

      try {
        showInsurance.value = false // Hide modal before making request
        const response = await fetch('/take_insurance', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ amount: insuranceAmount.value })
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        if (data.error) {
          alert(data.error)
          return
        }
        
        // After taking insurance, check for blackjacks
        const blackjackResponse = await fetch('/play_blackjack', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'check_blackjack' })
        })
        
        if (!blackjackResponse.ok) {
          throw new Error(`HTTP error! status: ${blackjackResponse.status}`)
        }
        
        const blackjackData = await blackjackResponse.json()
        if (blackjackData.error) {
          if (blackjackData.error === 'No game in progress') {
            // Try to recover the game state
            const stateResponse = await fetch('/play_blackjack', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ action: 'check_state' })
            })
            
            if (stateResponse.ok) {
              const stateData = await stateResponse.json()
              if (!stateData.error) {
                await updateGameState(stateData)
                return
              }
            }
            handlePlayAgain()
          }
          alert(blackjackData.error)
          return
        }
        
        await updateGameState(blackjackData)
      } catch (error) {
        console.error('Error:', error)
        alert('Failed to process insurance')
      }
    }

    const handlePlayAgain = () => {
      stopStateCheck()
      showResult.value = false
      dealerCards.value = []
      playerHands.value = [[]]
      dealerScore.value = ''
      playerScores.value = []
      gameInProgress.value = false
      canHit.value = false
      canStand.value = false
      canDouble.value = false
      canSplit.value = false
      nextCardId = 1
    }

    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

    const animateDealerActions = async (dealerActions) => {
      // First just reveal the hole card by removing the hidden property
      if (dealerActions.length > 0) {
        await sleep(500)
        dealerCards.value = dealerCards.value.map(card => ({
          ...card,
          id: card.id,  // Preserve existing IDs
          hidden: false
        }))
        dealerScore.value = `(${dealerActions[0].score})`
      }

      // Then animate each hit by only adding new cards
      let previousCards = dealerActions[0].cards.length
      for (let i = 1; i < dealerActions.length; i++) {
        await sleep(800)
        const currentAction = dealerActions[i]
        // Keep existing cards with their IDs and add new ones
        dealerCards.value = [
          ...dealerCards.value.slice(0, previousCards),
          ...currentAction.cards.slice(previousCards).map(card => ({
            ...card,
            id: nextCardId++
          }))
        ]
        previousCards = currentAction.cards.length
        dealerScore.value = `(${currentAction.score})`
      }
    }

    const updateGameState = async (data) => {
      console.log('Updating game state with data:', data)
      
      // First validate the data
      if (!data || !data.dealer || !data.player) {
        console.error('Invalid game state data:', data)
        handlePlayAgain()
        return
      }

      // Handle error state
      if (data.error) {
        console.error('Game state error:', data.error)
        if (data.error === 'No game in progress') {
          handlePlayAgain()
        } else {
          alert(data.error)
        }
        return
      }

      // Update store balance first
      if (data.balance !== undefined) {
        store.updateUserData({ balance: data.balance })
      }

      // Handle insurance if available before updating any visual state
      if (data.canInsure) {
        console.log('Showing insurance prompt')
        showInsurance.value = true
        insuranceAmount.value = (data.betAmount / 2).toFixed(2)
        
        // Update dealer cards but force second card to be hidden
        dealerCards.value = data.dealer.cards.map((card, index) => ({
          ...card,
          id: `dealer_${nextCardId++}`,
          hidden: index === 1  // Always hide second card during insurance
        }))
        
        // Update other state but maintain game in progress
        gameInProgress.value = true
        currentHand.value = data.player.currentHand
        playerHands.value = data.player.hands.map(hand =>
          hand.map(card => ({
            ...card,
            id: `player_${nextCardId++}`
          }))
        )
        playerScores.value = data.player.scores
        return
      }

      // Update game state flags
      const wasInProgress = gameInProgress.value
      gameInProgress.value = !data.gameOver
      console.log('Game in progress:', wasInProgress, '->', gameInProgress.value)

      // Update dealer cards with proper ID management
      dealerCards.value = data.dealer.cards.map((card, index) => ({
        ...card,
        id: `dealer_${nextCardId++}`,
        hidden: index === 1 && data.dealer.cards.length === 2 && !data.gameOver && !data.dealerBlackjack
      }))
      console.log('Updated dealer cards:', dealerCards.value)

      // Update player hands with proper ID management
      playerHands.value = data.player.hands.map(hand =>
        hand.map(card => ({
          ...card,
          id: `player_${nextCardId++}`
        }))
      )
      console.log('Updated player hands:', playerHands.value)

      // Update scores and current hand
      currentHand.value = data.player.currentHand
      dealerScore.value = (data.gameOver || data.dealerBlackjack) ? `(${data.dealer.score})` : ''
      playerScores.value = data.player.scores

      // Wait for initial render
      console.log('Waiting for cards to render...')
      await sleep(500)
      console.log('Cards should be rendered now')

      // Handle dealer blackjack
      if (data.dealerBlackjack) {
        console.log('Handling dealer blackjack')
        // Reveal dealer's hole card
        dealerCards.value = dealerCards.value.map(card => ({
          ...card,
          hidden: false
        }))
        dealerScore.value = `(${data.dealer.score})`
        await sleep(500)

        showResult.value = true
        resultText.value = data.message
        const playerHasBlackjack = data.player.scores[0] === 21 && data.player.hands[0].length === 2
        if (playerHasBlackjack) {
          resultAmount.value = `$0.00`
          resultIsWin.value = true
        } else {
          resultAmount.value = `-$${data.betAmount.toFixed(2)}`
          resultIsWin.value = false
        }
        console.log('Dealer blackjack handled')
        return
      }

      // Handle game over state
      if (data.gameOver) {
        console.log('Handling game over state')
        // Reveal all cards
        dealerCards.value = dealerCards.value.map(card => ({
          ...card,
          hidden: false
        }))
        dealerScore.value = `(${data.dealer.score})`

        // Handle dealer actions if any
        if (data.dealerActions && data.dealerActions.length > 0) {
          console.log('Animating dealer actions:', data.dealerActions)
          await animateDealerActions(data.dealerActions)
        }

        await sleep(500)

        // Calculate result
        let totalWon = 0
        let totalBet = data.betAmount + (data.splitBetAmount || 0)
        
        data.won.forEach((won, i) => {
          const bet = i === 0 ? data.betAmount : data.splitBetAmount
          if (won === 'blackjack') totalWon += bet * 2.5
          else if (won === true) totalWon += bet * 2
          else if (won === null) totalWon += bet
        })
        
        const netResult = totalWon - totalBet
        
        showResult.value = true
        resultText.value = data.message
        resultAmount.value = netResult >= 0 ? 
          `+$${netResult.toFixed(2)}` : 
          `-$${Math.abs(netResult).toFixed(2)}`
        resultIsWin.value = netResult >= 0
        console.log('Game over handled, final result:', {
          message: resultText.value,
          amount: resultAmount.value,
          isWin: resultIsWin.value
        })
      } else {
        console.log('Game continuing, current state:', {
          currentHand: currentHand.value,
          playerScores: playerScores.value,
          canHit: data.canHit,
          canStand: data.canStand,
          canDouble: data.canDouble,
          canSplit: data.canSplit
        })
        
        // Update controls based on server state
        canHit.value = data.canHit || false
        canStand.value = data.canStand || false
        canDouble.value = data.canDouble || false
        canSplit.value = data.canSplit || false
      }
    }

    // Add periodic state check with exponential backoff and better error handling
    let stateCheckInterval
    let stateCheckAttempts = 0
    const MAX_STATE_CHECK_INTERVAL = 10000 // 10 seconds
    const MAX_CHECK_ATTEMPTS = 5 // Maximum number of consecutive failed attempts
    
    const startStateCheck = () => {
      if (stateCheckInterval) {
        clearTimeout(stateCheckInterval)
      }
      stateCheckAttempts = 0
      checkGameState()
    }

    const checkGameState = async () => {
      if (!gameInProgress.value) return
      
      try {
        const response = await fetch('/play_blackjack', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'check_state' })
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        if (data.error === 'No game in progress') {
          // Only reset if we're sure there's no game
          if (stateCheckAttempts >= MAX_CHECK_ATTEMPTS) {
            console.log('Game state check failed multiple times, resetting game')
            handlePlayAgain()
            return
          }
          stateCheckAttempts++
        } else if (!data.error) {
          // Reset attempts on successful check
          stateCheckAttempts = 0
          // Update controls based on server state
          canHit.value = data.canHit || false
          canStand.value = data.canStand || false
          canDouble.value = data.canDouble || false
          canSplit.value = data.canSplit || false
          
          // If game is over, stop checking
          if (data.gameOver) {
            stopStateCheck()
            return
          }
        }
        
        // Schedule next check with exponential backoff
        const interval = Math.min(1000 * Math.pow(1.5, stateCheckAttempts), MAX_STATE_CHECK_INTERVAL)
        stateCheckInterval = setTimeout(checkGameState, interval)
      } catch (error) {
        console.error('Game state check failed:', error)
        stateCheckAttempts++
        
        // If we've failed too many times, reset the game
        if (stateCheckAttempts >= MAX_CHECK_ATTEMPTS) {
          console.log('Too many failed state checks, resetting game')
          handlePlayAgain()
          return
        }
        
        // Schedule retry with exponential backoff
        const interval = Math.min(1000 * Math.pow(1.5, stateCheckAttempts), MAX_STATE_CHECK_INTERVAL)
        stateCheckInterval = setTimeout(checkGameState, interval)
      }
    }

    const stopStateCheck = () => {
      if (stateCheckInterval) {
        clearTimeout(stateCheckInterval)
        stateCheckInterval = null
      }
    }

    // Clean up interval when component is unmounted
    onUnmounted(() => {
      stopStateCheck()
    })

    return {
      balance,
      betInput,
      gameInProgress,
      dealerCards,
      playerHands,
      currentHand,
      dealerScore,
      playerScores,
      canHit,
      canStand,
      canDouble,
      canSplit,
      showInsurance,
      insuranceAmount,
      showResult,
      resultText,
      resultAmount,
      resultIsWin,
      validateBet,
      incrementBet,
      doubleBet,
      halfBalance,
      maxBalance,
      repeatBet,
      handleDeal,
      handleHit,
      handleStand,
      handleDouble,
      handleSplit,
      handleInsurance,
      handlePlayAgain
    }
  }
}
</script> 