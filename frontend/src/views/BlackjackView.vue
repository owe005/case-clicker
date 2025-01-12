<template>
  <div class="blackjack-container">
    <!-- Header -->
    <div class="header">
      <h1>Blackjack</h1>
      <p>Try to beat the dealer to 21!</p>
    </div>

    <!-- Game Area -->
    <div class="game-area">
      <!-- Dealer's Hand -->
      <div class="dealer-area">
        <h2>Dealer's Hand <span>{{ animatedDealerValue ? `(${animatedDealerValue})` : '' }}</span></h2>
        <div class="dealer-cards">
          <template v-for="(card, index) in dealerCards" :key="index">
            <div 
              class="card"
              :class="[
                getCardClass(card), 
                { 
                  'hidden-card': index === 1 && !showHoleCard,
                  'revealed': index === 1 && showHoleCard,
                  'drawing': index > 1
                }
              ]"
              :style="{ '--card-index': index }"
            >
              <div v-if="index !== 1 || showHoleCard" class="card-content">
                {{ card.rank }}{{ card.suit }}
              </div>
              <div v-else class="card-back">
                <div class="card-pattern"></div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Player's Hands -->
      <div class="player-area">
        <template v-for="(hand, handIndex) in playerHands" :key="handIndex">
          <div class="hand" :class="{ active: hand.is_current }">
            <h2>Your Hand {{ playerHands.length > 1 ? (handIndex + 1) : '' }} ({{ hand.value }})</h2>
            <div class="player-cards">
              <template v-for="(card, cardIndex) in hand.cards" :key="cardIndex">
                <div 
                  class="card" 
                  :class="[
                    getCardClass(card),
                    { 'drawing': cardIndex >= hand.cards.length - 1 }
                  ]"
                >
                  <div class="card-content">
                    {{ card.rank }}{{ card.suit }}
                  </div>
                </div>
              </template>
            </div>
            <div class="hand-score">Bet: ${{ formatNumber(hand.bet) }}</div>
          </div>
        </template>
      </div>

      <!-- Betting Controls -->
      <div class="betting-controls">
        <div class="quick-bet-buttons">
          <button class="quick-bet" @click="adjustBet(1)" :disabled="gameActive">+$1</button>
          <button class="quick-bet" @click="adjustBet(10)" :disabled="gameActive">+$10</button>
          <button class="quick-bet" @click="adjustBet(100)" :disabled="gameActive">+$100</button>
          <button class="quick-bet" @click="adjustBet(1000)" :disabled="gameActive">+$1000</button>
          <button class="quick-bet" @click="doubleBet" :disabled="gameActive">x2</button>
          <button class="quick-bet" @click="halfBalance" :disabled="gameActive">1/2</button>
          <button class="quick-bet" @click="maxBalance" :disabled="gameActive">Max</button>
          <button class="quick-bet" @click="repeatBet" :disabled="gameActive">Repeat</button>
        </div>
        <div class="bet-input">
          <div class="bet-controls">
            <button class="bet-adjust" @click="decreaseBet" :disabled="gameActive">-</button>
            <input type="number" v-model="betAmount" min="0.01" step="0.01" class="bet-amount" :disabled="gameActive">
            <button class="bet-adjust" @click="increaseBet" :disabled="gameActive">+</button>
          </div>
        </div>
      </div>

      <!-- Game Controls -->
      <div class="game-controls">
        <button class="action-btn deal-btn" @click="startGame" :disabled="!canBet || gameActive">Deal</button>
        <button class="action-btn hit-btn" @click="hit" :disabled="!gameActive || dealerDrawing">Hit</button>
        <button class="action-btn stand-btn" @click="stand" :disabled="!gameActive || dealerDrawing">Stand</button>
        <button class="action-btn double-btn" @click="doubleDown" :disabled="!gameActive || dealerDrawing || !canDouble">Double Down</button>
        <button class="action-btn split-btn" @click="split" :disabled="!gameActive || dealerDrawing || !canSplit">Split</button>
      </div>

      <!-- Insurance Prompt -->
      <div class="insurance-prompt" v-if="insuranceAvailable && !insuranceTaken">
        <h3>Insurance?</h3>
        <p>Dealer is showing an Ace. Would you like to take insurance?</p>
        <div class="insurance-controls">
          <button class="insurance-btn accept" @click="takeInsurance">Yes</button>
          <button class="insurance-btn decline" @click="declineInsurance">No</button>
        </div>
      </div>

      <!-- Game Result -->
      <div class="result-display" v-if="gameOver">
        <h2 class="result-text">{{ finalResult }}</h2>
        <div class="result-amount">{{ netResult }}</div>
        <button class="play-again-btn" @click="resetGame">Play Again</button>
        <button class="return-btn" @click="returnToCasino">Return</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onUnmounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

export default {
  name: 'BlackjackView',
  setup() {
    const router = useRouter()
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
    const insuranceAmount = ref(0)
    const lastBetAmount = ref(1)
    const insuranceTaken = ref(false)
    const netResult = ref('')
    const animationTimer = ref(null)
    const animationStartTime = ref(null)
    const forceUpdate = ref(0)
    const dealerDrawing = ref(false)

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

    const canSplit = computed(() => {
      return playerHands.value[0]?.can_split || false
    })

    const canDouble = computed(() => {
      const currentHand = playerHands.value.find(hand => hand.is_current)
      return currentHand && currentHand.cards.length === 2 && !currentHand.doubled
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
          lastBetAmount.value = betAmount.value
        }
      } catch (error) {
        console.error('Error starting game:', error)
      }
    }

    const updateGameState = (state) => {
      dealerCards.value = state.dealer_hand.cards
      dealerValue.value = state.dealer_hand.value
      playerHands.value = state.player_hands
      
      const wasHoleCardHidden = !showHoleCard.value
      showHoleCard.value = state.game_over || state.dealer_hand.show_hole_card
      
      // Start animation timer when hole card is revealed
      if (wasHoleCardHidden && showHoleCard.value) {
        // Set dealer drawing state
        dealerDrawing.value = true
        
        // Clear any existing timer
        if (animationTimer.value) {
          clearInterval(animationTimer.value)
        }
        
        // Start new animation sequence
        animationStartTime.value = Date.now()
        
        // Create interval to update computed value
        animationTimer.value = setInterval(() => {
          // Force update by incrementing counter
          forceUpdate.value++
          
          // Calculate total animation time needed
          const totalAnimationTime = 1500 + (Math.max(0, dealerCards.value.length - 2) * 1000)
          
          // If animation is complete, show game over state
          if (Date.now() - animationStartTime.value >= totalAnimationTime) {
            clearInterval(animationTimer.value)
            animationTimer.value = null
            dealerDrawing.value = false
            
            // Only now show game over state
            gameOver.value = state.game_over
            if (gameOver.value) {
              finalResult.value = calculateFinalResult(state.player_hands)
            }
          }
        }, 100) // Update every 100ms
      }
      
      // If not revealing hole card, update game state immediately
      if (!wasHoleCardHidden) {
        gameOver.value = state.game_over
        if (gameOver.value) {
          finalResult.value = calculateFinalResult(state.player_hands)
        }
      }
      
      insuranceAvailable.value = state.insurance_available && dealerCards.value[0]?.rank === 'A'
    }

    const calculateFinalResult = (hands) => {
      let win = false;
      let lose = false;
      let totalWon = 0;
      let totalBet = 0;

      hands.forEach(hand => {
        totalBet += hand.bet;
        
        // Handle different win conditions
        switch(hand.result) {
          case 'BLACKJACK':
            win = true;
            totalWon += hand.bet * 2.5; // Blackjack pays 3:2
            break;
          case 'WIN':
          case 'DEALER BUST':
            win = true;
            totalWon += hand.bet * 2; // Regular win pays 1:1 (return bet + win equal amount)
            break;
          case 'PUSH':
            totalWon += hand.bet; // Push returns original bet
            break;
          case 'LOSE':
          case 'BUST':
            lose = true;
            break;
        }
      });

      const netAmount = totalWon - totalBet;
      netResult.value = netAmount >= 0 ? 
        `+$${netAmount.toFixed(2)}` : 
        `-$${Math.abs(netAmount).toFixed(2)}`;

      if (win && !lose) {
        return 'You Win!';
      } else if (lose && !win) {
        return 'You Lose!';
      } else if (win && lose) {
        return 'Mixed Results';
      } else if (totalWon === totalBet) {
        return 'Push';
      }
      return 'Game Over';
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
      try {
        const response = await axios.post('/api/blackjack/split')
        if (response.data.success) {
          updateGameState(response.data.state)
          balance.value = response.data.balance
        }
      } catch (error) {
        console.error('Error splitting:', error)
      }
    }

    const takeInsurance = async () => {
      try {
        const response = await axios.post('/api/blackjack/insurance', {
          amount: playerHands.value[0].bet / 2 // Insurance is always half the original bet
        })
        if (response.data.success) {
          updateGameState(response.data.state)
          balance.value = response.data.balance
          insuranceTaken.value = true
          insuranceAvailable.value = false
        }
      } catch (error) {
        console.error('Error taking insurance:', error)
      }
    }

    const declineInsurance = () => {
      insuranceAvailable.value = false
      insuranceTaken.value = true
    }

    const resetGame = () => {
      gameActive.value = false
      gameOver.value = false
      finalResult.value = ''
      playerHands.value = []
      dealerCards.value = []
      dealerValue.value = null
      insuranceTaken.value = false
      insuranceAvailable.value = false
      dealerDrawing.value = false
      
      // Clear animation state
      if (animationTimer.value) {
        clearInterval(animationTimer.value)
      }
      animationTimer.value = null
      animationStartTime.value = null
    }

    const returnToCasino = () => {
      router.push('/casino')
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

    const formatNumber = (num) => {
      return Number(num).toFixed(2)
    }

    const adjustBet = (amount) => {
      const newBet = Math.min(balance.value, Math.max(0.01, betAmount.value + amount));
      betAmount.value = parseFloat(newBet.toFixed(2));
    }

    const increaseBet = () => {
      adjustBet(1);
    }

    const decreaseBet = () => {
      adjustBet(-1);
    }

    const doubleBet = () => {
      adjustBet(betAmount.value);
    }

    const halfBalance = () => {
      betAmount.value = parseFloat((balance.value / 2).toFixed(2));
    }

    const maxBalance = () => {
      betAmount.value = parseFloat(balance.value.toFixed(2));
    }

    const repeatBet = () => {
      adjustBet(lastBetAmount.value);
    }

    // Add new computed property for animated dealer value
    const animatedDealerValue = computed(() => {
      // Include forceUpdate in computation to ensure reactivity
      forceUpdate.value
      
      if (!showHoleCard.value) {
        // Before hole card is revealed, only show first card value
        return dealerCards.value[0]?.value || null
      }
      
      if (!animationStartTime.value) {
        return dealerCards.value[0]?.value || null
      }

      // After hole card is revealed, calculate value based on animation timing
      const elapsed = Date.now() - animationStartTime.value
      let visibleCards = dealerCards.value.slice(0, 2) // First two cards

      // Add additional cards based on animation timing
      for (let i = 2; i < dealerCards.value.length; i++) {
        const cardDelay = 1500 + (i - 2) * 1000 // 1.5s initial delay + 1s per card
        if (elapsed >= cardDelay) {
          visibleCards.push(dealerCards.value[i])
        }
      }

      // Calculate total value of visible cards
      let total = 0
      let aces = 0
      
      for (const card of visibleCards) {
        if (card.is_ace) {
          aces++
        }
        total += card.value
      }
      
      // Handle aces
      while (total > 21 && aces > 0) {
        total -= 10
        aces--
      }
      
      return total || null
    })

    // Clean up interval on component unmount
    onUnmounted(() => {
      if (animationTimer.value) {
        clearInterval(animationTimer.value);
      }
    });

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
      insuranceAmount,
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
      formatNumber,
      adjustBet,
      increaseBet,
      decreaseBet,
      doubleBet,
      halfBalance,
      maxBalance,
      repeatBet,
      insuranceTaken,
      declineInsurance,
      netResult,
      animatedDealerValue,
      dealerDrawing,
      canSplit,
      canDouble
    }
  }
}
</script>

<style scoped>
.blackjack-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  color: #e4e4e4;
}

.game-area {
  background: #2a2a2a;
  padding: 30px;
  border-radius: 15px;
  margin-top: 20px;
}

.dealer-area, .player-area {
  margin-bottom: 30px;
}

.dealer-cards, .player-cards {
  display: flex;
  gap: 10px;
  min-height: 150px;
  padding: 10px;
  background: #1a1a1a;
  border-radius: 10px;
}

.card {
  width: 100px;
  height: 140px;
  background: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: black;
  position: relative;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  transform-style: preserve-3d;
  transition: transform 0.6s;
}

.card.red {
  color: #d63031;
}

.card.hidden {
  background: transparent;
  color: white;
}

.betting-controls {
  margin-bottom: 20px;
}

.quick-bet-buttons {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 20px;
}

.quick-bet {
  background: #3a3a3a;
  border: none;
  padding: 10px;
  color: #e4e4e4;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.2s;
}

.quick-bet:hover {
  background: #4a4a4a;
}

.bet-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.bet-adjust {
  background: #4CAF50;
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 5px;
  font-size: 20px;
  cursor: pointer;
}

.bet-amount {
  padding: 10px;
  width: 150px;
  border: 2px solid #3a3a3a;
  background: #1a1a1a;
  color: #e4e4e4;
  border-radius: 5px;
  text-align: center;
  font-size: 20px;
}

.game-controls {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 20px;
}

.action-btn {
  padding: 10px 30px;
  border: none;
  border-radius: 5px;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #666 !important;
  color: #999 !important;
}

.deal-btn {
  background: #4CAF50;
  color: white;
}

.hit-btn {
  background: #2196F3;
  color: white;
}

.stand-btn {
  background: #f44336;
  color: white;
}

.double-btn {
  background: #9c27b0;
  color: white;
}

.result-display {
  text-align: center;
  margin-top: 20px;
  padding: 20px;
  border-radius: 10px;
}

.result-display.win {
  background: linear-gradient(135deg, #2a2a2a, #1a472a);
}

.result-display.lose {
  background: linear-gradient(135deg, #2a2a2a, #4a1a1a);
}

.result-text {
  font-size: 24px;
  margin-bottom: 10px;
}

.result-amount {
  font-size: 32px;
  margin-bottom: 20px;
}

.result-amount.win {
  color: #4CAF50;
}

.result-amount.lose {
  color: #f44336;
}

.hidden {
  display: none;
}

.play-again-btn, .return-btn {
  padding: 10px 30px;
  border: none;
  border-radius: 5px;
  font-size: 18px;
  cursor: pointer;
  margin: 0 10px;
  transition: all 0.2s;
}

.play-again-btn {
  background: #4CAF50;
  color: white;
}

.return-btn {
  background: #f44336;
  color: white;
  text-decoration: none;
  display: inline-block;
}

.player-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.player-hands {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
}

.hand {
  background: #1a1a1a;
  padding: 15px;
  border-radius: 10px;
  min-width: 300px;
}

.hand.active {
  border: 2px solid #4CAF50;
}

.hand-cards {
  display: flex;
  gap: 10px;
  min-height: 150px;
}

.hand-score {
  margin-top: 10px;
  font-size: 18px;
  color: #888;
}

.split-btn {
  background: #FF9800;
  color: white;
}

.dealer-cards {
  min-width: 300px;
  margin: 0 auto;
  position: relative;
}

.insurance-prompt {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: #2a2a2a;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  z-index: 1000;
  box-shadow: 0 0 20px rgba(0,0,0,0.5);
}

.insurance-controls {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 15px;
}

.insurance-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.insurance-btn.accept {
  background: #4CAF50;
  color: white;
}

.insurance-btn.decline {
  background: #f44336;
  color: white;
}

.card-back {
  width: 100%;
  height: 100%;
  background: #2d3436;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.card-pattern {
  position: absolute;
  inset: 0;
  background-image: repeating-linear-gradient(
    45deg,
    #2d3436 0px,
    #2d3436 10px,
    #34495e 10px,
    #34495e 20px
  );
  opacity: 0.8;
}

.hidden-card {
  background: #2d3436 !important;
  color: white !important;
}

.card.hidden {
  display: none;
}

.quick-bet:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #2a2a2a;
}

.bet-adjust:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #2a2a2a;
}

.bet-amount:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #2a2a2a;
}

/* Card animations */
@keyframes cardFlip {
  0% {
    transform: rotateY(0deg);
  }
  100% {
    transform: rotateY(180deg);
  }
}

@keyframes cardDraw {
  0% {
    opacity: 0;
    transform: translateY(-100px) scale(0.8);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.card {
  width: 100px;
  height: 140px;
  background: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: black;
  position: relative;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  transform-style: preserve-3d;
  transition: transform 0.6s;
}

.card.drawing {
  animation: cardDraw 0.4s ease-out forwards;
  animation-delay: calc(1.5s + (var(--card-index) - 2) * 1s);
  opacity: 0;
}

.card.flipping {
  animation: cardFlip 0.6s ease-in-out forwards;
}

.card-content {
  backface-visibility: hidden;
}

.card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  transform: rotateY(180deg);
}

.hidden-card {
  transform: rotateY(180deg);
  transition: transform 0.6s ease-in-out;
}

.hidden-card.revealed {
  transform: rotateY(0deg);
}
</style>
