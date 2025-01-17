<template>
  <div class="min-h-screen bg-gray-darker">
    <!-- Header -->
    <div class="relative py-12 mb-8">
      <div class="absolute inset-0 bg-gradient-to-b from-yellow/5 to-transparent"></div>
      <div class="relative max-w-7xl mx-auto px-4">
        <h1 class="text-4xl font-display font-bold text-white mb-2">Jackpot</h1>
        <p class="text-white/70">Bet your skins against other players for a chance to win big!</p>
      </div>
    </div>

    <!-- Game Area -->
    <div class="max-w-7xl mx-auto px-4 pb-12">
      <!-- Mode Selector and Total Pot -->
      <div class="bg-gray-dark/50 rounded-xl p-6 mb-6">
        <div class="flex flex-col items-center gap-4">
          <!-- Mode Selector -->
          <div class="flex gap-2 flex-wrap justify-center">
            <button 
              v-for="mode in modes" 
              :key="mode.id"
              class="px-4 py-2 rounded-lg font-medium transition-all duration-200"
              :class="[
                currentMode === mode.id 
                  ? 'bg-yellow text-gray-darker' 
                  : 'bg-gray-dark/50 text-white/70 hover:bg-gray-dark hover:text-white',
                gameInProgress ? 'opacity-50 cursor-not-allowed' : ''
              ]"
              @click="setMode(mode.id)"
              :disabled="gameInProgress"
            >
              {{ mode.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Game Setup Section -->
      <div v-if="!gameInProgress" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Inventory Section -->
        <div class="bg-gray-dark/50 rounded-xl p-6">
          <h2 class="text-xl font-display text-white mb-4">Your Inventory</h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 max-h-[600px] overflow-y-auto p-2">
            <div 
              v-for="item in eligibleItems" 
              :key="item.id"
              class="relative group cursor-pointer transition-all duration-300"
              :class="[
                `rarity-${(item.rarity || '').toLowerCase()}`,
                selectedItems.has(item) ? 'ring-2 ring-yellow' : 'hover:scale-105'
              ]"
              @click="toggleItem(item)"
            >
              <div class="bg-gray-darker rounded-lg p-3">
                <img 
                  :src="getItemImage(item)" 
                  :alt="item.name"
                  class="w-full h-32 object-contain mb-2"
                >
                <div class="space-y-1">
                  <div 
                    class="text-sm truncate"
                    :class="{ 'text-[#CF6A32]': item.stattrak }"
                  >
                    {{ item.is_sticker ? item.name : `${item.stattrak ? 'StatTrak™ ' : ''}${item.weapon} | ${item.name}` }}
                  </div>
                  <div class="text-xs text-white/50">{{ item.wear }}</div>
                  <div class="text-yellow text-sm">${{ item.price.toFixed(2) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Selected Items Section -->
        <div class="bg-gray-dark/50 rounded-xl p-6">
          <h2 class="text-xl font-display text-white mb-4">
            Selected Items (<span class="text-yellow">{{ selectedItems.size }}</span>/10)
          </h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 max-h-[500px] overflow-y-auto p-2">
            <div 
              v-for="item in Array.from(selectedItems)" 
              :key="item.id"
              class="relative group cursor-pointer transition-all duration-300"
              :class="`rarity-${(item.rarity || '').toLowerCase()}`"
              @click="toggleItem(item)"
            >
              <div class="bg-gray-darker rounded-lg p-3">
                <img 
                  :src="getItemImage(item)" 
                  :alt="item.name"
                  class="w-full h-32 object-contain mb-2"
                >
                <div class="space-y-1">
                  <div 
                    class="text-sm truncate"
                    :class="{ 'text-[#CF6A32]': item.stattrak }"
                  >
                    {{ item.is_sticker ? item.name : `${item.stattrak ? 'StatTrak™ ' : ''}${item.weapon} | ${item.name}` }}
                  </div>
                  <div class="text-xs text-white/50">{{ item.wear }}</div>
                  <div class="text-yellow text-sm">${{ item.price.toFixed(2) }}</div>
                </div>
              </div>
            </div>
          </div>
          <!-- Total Value and Start Button -->
          <div class="mt-6 flex flex-col items-center gap-4">
            <div class="text-xl">
              Total Value: <span class="text-yellow">${{ selectedValue.toFixed(2) }}</span>
            </div>
            <button 
              class="px-8 py-3 bg-yellow text-gray-darker rounded-lg font-medium transition-all duration-200 hover:bg-yellow/90 disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="selectedItems.size === 0"
              @click="startGame"
            >
              Start Game
            </button>
          </div>
        </div>
      </div>

      <!-- Game Progress Section -->
      <div v-else class="bg-gray-dark/50 rounded-xl p-6">
        <!-- Total Pot -->
        <div class="text-center mb-8">
          <div class="text-2xl font-display text-white mb-2">Total Pot</div>
          <div class="text-4xl text-yellow">${{ totalPot.toFixed(2) }}</div>
          <div class="text-white/70 mt-2">Your chance: {{ winChance }}%</div>
        </div>

        <!-- Jackpot Wheel -->
        <div v-if="showWheel" class="relative h-32 bg-gray-darker/50 rounded-lg overflow-hidden mb-8">
          <!-- Pointer -->
          <div class="absolute left-1/2 top-0 bottom-0 w-0.5 bg-yellow z-10">
            <div class="absolute -top-2 left-1/2 -translate-x-1/2 border-8 border-transparent border-t-yellow"></div>
            <div class="absolute -bottom-2 left-1/2 -translate-x-1/2 border-8 border-transparent border-b-yellow"></div>
          </div>
          <!-- Wheel Items -->
          <div 
            ref="wheelRef"
            class="jackpot-wheel"
            :style="{ transform: wheelTransform }"
          >
            <div 
              v-for="(item, index) in wheelItems" 
              :key="index"
              class="flex-shrink-0 w-32 h-full p-4 bg-gray-dark border-2 border-gray-darker mx-1"
            >
              <div class="flex flex-col items-center">
                <img :src="getPlayerAvatar(item.name)" class="w-16 h-16 rounded-full mb-2">
                <div class="text-sm truncate text-center">{{ item.name }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Players Joining -->
        <div class="space-y-4">
          <div v-if="joiningInProgress" class="flex items-center justify-center gap-2 text-lg text-white/70">
            <span>{{ currentJoiningPlayer }} is joining</span>
            <div class="flex">
              <span class="animate-dots">.</span>
              <span class="animate-dots-delay-1">.</span>
              <span class="animate-dots-delay-2">.</span>
            </div>
          </div>

          <!-- Player Entries -->
          <div v-for="player in players" :key="player.name" class="bg-gray-darker/50 rounded-lg p-4">
            <div class="grid grid-cols-4 gap-4 items-center">
              <div class="text-lg font-medium">{{ player.name }}</div>
              <div class="text-yellow">${{ player.value.toFixed(2) }}</div>
              <div class="text-yellow">{{ player.chance }}%</div>
              <template v-if="!player.isUser">
                <div class="text-white/70">
                  {{ Array.isArray(player.items) ? player.items.length : 0 }} items
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- Winner Modal -->
      <div 
        v-if="showWinner"
        class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      >
        <div class="bg-gray-dark rounded-xl p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
          <h2 class="text-2xl font-display text-center mb-6">Winner</h2>
          <div class="text-center mb-8">
            <div class="text-xl mb-2">{{ winner.name }}</div>
            <div class="text-3xl text-yellow">${{ winner.totalValue.toFixed(2) }}</div>
          </div>
          <!-- Winner Items -->
          <div v-if="winner.isUser" class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
            <div 
              v-for="item in winner.items" 
              :key="item.id"
              class="bg-gray-darker rounded-lg p-3"
              :class="`rarity-${(item.rarity || '').toLowerCase()}`"
            >
              <img 
                :src="getItemImage(item)" 
                :alt="item.name"
                class="w-full h-24 object-contain mb-2"
              >
              <div class="text-xs truncate">
                {{ item.is_sticker ? item.name : `${item.weapon} | ${item.name}` }}
              </div>
              <div class="text-yellow text-xs">${{ item.price.toFixed(2) }}</div>
            </div>
          </div>
          <div class="flex justify-center">
            <button 
              class="px-8 py-3 bg-yellow text-gray-darker rounded-lg font-medium transition-all duration-200 hover:bg-yellow/90"
              @click="closeWinner"
            >
              Continue
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { CASE_MAPPING } from '../store'

export default {
  name: 'JackpotView',
  setup() {
    // Constants
    const BOT_AVATARS = {
      '_Astrid47': 'bot1.png',
      'Kai.Jayden_02': 'bot2.png',
      'Orion_Phoenix98': 'bot3.png',
      'ElaraB_23': 'bot4.png',
      'Theo.91': 'bot5.png',
      'Nova-Lyn': 'bot6.png',
      'FelixHaven19': 'bot7.png',
      'Aria.Stella85': 'bot8.png',
      'Lucien_Kai': 'bot9.png',
      'Mira-Eclipse': 'bot10.png'
    }

    const modes = [
      { id: 'low', label: '$0-10' },
      { id: 'medium', label: '$10-100' },
      { id: 'high', label: '$100-1000' },
      { id: 'extreme', label: '$1000+' }
    ]

    const modeLimits = {
      'low': { min: 0, max: 10 },
      'medium': { min: 10, max: 100 },
      'high': { min: 100, max: 1000 },
      'extreme': { min: 1000, max: Infinity }
    }

    // State
    const currentMode = ref('low')
    const inventory = ref([])
    const selectedItems = ref(new Set())
    const gameInProgress = ref(false)
    const joiningInProgress = ref(false)
    const currentJoiningPlayer = ref('')
    const players = ref([])
    const showWheel = ref(false)
    const showWinner = ref(false)
    const winner = ref(null)
    const wheelRef = ref(null)
    const wheelItems = ref([])
    const totalPot = ref(0)
    const winChance = ref(0)

    // Computed
    const eligibleItems = computed(() => {
      const { min, max } = modeLimits[currentMode.value]
      return inventory.value.filter(item => {
        const price = parseFloat(item.price)
        return price >= min && price <= max
      }).sort((a, b) => b.price - a.price)
    })

    const selectedValue = computed(() => {
      return Array.from(selectedItems.value).reduce((total, item) => total + item.price, 0)
    })

    // Methods
    const setMode = (mode) => {
      currentMode.value = mode
      selectedItems.value.clear()
      loadInventory()
    }

    const loadInventory = async () => {
      try {
        const response = await fetch('/get_jackpot_inventory')
        const data = await response.json()
        
        if (data.error) {
          console.error('Error:', data.error)
          return
        }
        
        inventory.value = data.inventory
      } catch (error) {
        console.error('Error loading inventory:', error)
      }
    }

    const toggleItem = (item) => {
      if (selectedItems.value.has(item)) {
        selectedItems.value.delete(item)
      } else if (selectedItems.value.size < 10) {
        selectedItems.value.add(item)
      }
    }

    function getItemImage(item) {
      if (item.is_sticker) {
        const capsuleType = item.case_type || item.capsule_type
        return `/sticker_skins/${capsuleType}/${item.image}`
      }
      if (item.is_capsule) {
        return `/stickers/${item.type || item.case_type}.png`
      }
      const casePath = CASE_MAPPING[item.case_type] || 'weapon_case_1'
      return `/skins/${casePath}/${item.image || 'placeholder.png'}`
    }

    const getPlayerAvatar = (name) => {
      return name === 'You' 
        ? '/casino/player_avatar.png'
        : `/casino/${BOT_AVATARS[name]}`
    }

    const startGame = async () => {
      if (selectedItems.value.size === 0) return

      try {
        const response = await fetch('/start_jackpot', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            items: Array.from(selectedItems.value),
            mode: currentMode.value
          })
        })

        const data = await response.json()

        if (data.error) {
          console.error('Server error:', data.error)
          alert(data.error)
          return
        }

        gameInProgress.value = true
        startGameProgress(data)
      } catch (error) {
        console.error('Error:', error)
        alert('Failed to start game')
      }
    }

    const startGameProgress = (gameData) => {
      joiningInProgress.value = true
      players.value = []
      let currentIndex = 0

      const addNextPlayer = () => {
        if (currentIndex < gameData.players.length) {
          const player = gameData.players[currentIndex]
          currentJoiningPlayer.value = player.name

          setTimeout(() => {
            players.value.push(player)
            updateChances()
            currentIndex++
            if (currentIndex < gameData.players.length) {
              addNextPlayer()
            } else {
              joiningInProgress.value = false
              setTimeout(() => startWheel(gameData.winner), 1000)
            }
          }, 800)
        }
      }

      addNextPlayer()
    }

    const updateChances = () => {
      const total = players.value.reduce((sum, player) => sum + player.value, 0)
      totalPot.value = total

      players.value.forEach(player => {
        player.chance = ((player.value / total) * 100).toFixed(2)
        if (player.name === 'You') {
          winChance.value = player.chance
        }
      })
    }

    const startWheel = (winnerData) => {
      console.log('Starting wheel with winner:', winnerData.name)
      showWheel.value = true
      const segments = 5 // Total number of segments
      const itemsPerSegment = 20 // Items per segment
      const baseItems = []
      
      // Position the winner in the exact center of the middle segment
      const winningPosition = Math.floor(itemsPerSegment / 2) // Center position in segment
      console.log('Winning position in segment:', winningPosition)

      // Create weighted array for random selection
      const weightedPlayers = []
      players.value.forEach(player => {
        const weight = Math.round(parseFloat(player.chance) * 100)
        for (let i = 0; i < weight; i++) {
          weightedPlayers.push(player)
        }
      })

      // Generate random items for one segment
      for (let i = 0; i < itemsPerSegment; i++) {
        const randomIndex = Math.floor(Math.random() * weightedPlayers.length)
        const randomPlayer = weightedPlayers[randomIndex]
        baseItems.push({
          name: randomPlayer.name,
          isWinner: false
        })
      }

      // Create full wheel items
      wheelItems.value = []
      const middleSegmentIndex = Math.floor(segments / 2)
      console.log('Middle segment index:', middleSegmentIndex)

      for (let i = 0; i < segments; i++) {
        const currentSegmentItems = [...baseItems]
        if (i === middleSegmentIndex) {
          console.log('Placing winner in middle segment at position:', winningPosition)
          currentSegmentItems[winningPosition] = {
            name: winnerData.name,
            isWinner: true
          }
        }
        wheelItems.value.push(...currentSegmentItems)
      }

      // Log the wheel items around the expected winner position
      const expectedWinnerIndex = (middleSegmentIndex * itemsPerSegment) + winningPosition
      console.log('Expected winner index:', expectedWinnerIndex)
      console.log('Items around winner:')
      for (let i = expectedWinnerIndex - 2; i <= expectedWinnerIndex + 2; i++) {
        console.log(`Item ${i}:`, wheelItems.value[i]?.name)
      }

      // Start spin animation after items are rendered
      setTimeout(() => {
        if (wheelRef.value) {
          const itemWidth = 128 // w-32 = 8rem = 128px
          const containerWidth = wheelRef.value.parentElement.offsetWidth
          const centerOffset = (containerWidth / 2) - (itemWidth / 2)

          // Reset position and force reflow
          wheelRef.value.style.transition = 'none'
          wheelRef.value.style.transform = 'translateX(0)'
          wheelRef.value.offsetHeight

          // Find the winning item in the DOM
          const winnerIndex = (middleSegmentIndex * itemsPerSegment) + winningPosition
          const winningItem = wheelRef.value.children[winnerIndex]
          const finalPosition = winningItem.offsetLeft - centerOffset

          console.log('Animation details:', {
            itemWidth,
            containerWidth,
            centerOffset,
            winnerIndex,
            finalPosition,
            winningItemOffset: winningItem.offsetLeft,
            expectedItem: wheelItems.value[winnerIndex]?.name
          })

          // Apply the transform with easing
          wheelRef.value.style.transition = 'transform 8s cubic-bezier(0.32, 0.64, 0.45, 1)'
          wheelRef.value.style.transform = `translateX(-${finalPosition}px)`

          // Show winner after wheel animation
          setTimeout(() => {
            // Verify final position
            const finalTransform = wheelRef.value.style.transform
            console.log('Final wheel position:', finalTransform)
            console.log('Expected winner:', winnerData.name)
            console.log('Item at pointer:', wheelItems.value[winnerIndex]?.name)

            showWheel.value = false
            winner.value = winnerData
            showWinner.value = true
          }, 8500)
        }
      }, 100)
    }

    const closeWinner = () => {
      showWinner.value = false
      gameInProgress.value = false
      selectedItems.value.clear()
      loadInventory()
    }

    // Initial load
    loadInventory()

    return {
      currentMode,
      modes,
      totalPot,
      eligibleItems,
      selectedItems,
      selectedValue,
      gameInProgress,
      joiningInProgress,
      currentJoiningPlayer,
      players,
      showWheel,
      showWinner,
      winner,
      wheelRef,
      wheelItems,
      winChance,
      setMode,
      toggleItem,
      getItemImage,
      getPlayerAvatar,
      startGame,
      closeWinner
    }
  }
}
</script> 