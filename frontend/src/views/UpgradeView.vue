<template>
  <div class="min-h-screen bg-gray-darker">
    <!-- Header -->
    <div class="relative py-12 mb-8">
      <div class="absolute inset-0 bg-gradient-to-b from-yellow/5 to-transparent"></div>
      <div class="relative max-w-7xl mx-auto px-4">
        <h1 class="text-4xl font-display font-bold text-white mb-2">Upgrade</h1>
        <p class="text-white/70">Try to upgrade your skins to more valuable ones!</p>
      </div>
    </div>

    <!-- Game Area -->
    <div class="max-w-7xl mx-auto px-4 pb-12">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Inventory Section -->
        <div class="bg-gray-dark/50 rounded-xl p-6">
          <h2 class="text-xl font-display text-white mb-4">Your Inventory</h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 max-h-[600px] overflow-y-auto p-2">
            <div 
              v-for="item in inventory" 
              :key="item.id"
              class="relative group cursor-pointer transition-all duration-300"
              :class="[
                `rarity-${item.rarity.toLowerCase()}`,
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
                  <div class="text-yellow text-sm">${{ formatNumber(item.price) }}</div>
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
              :class="`rarity-${item.rarity.toLowerCase()}`"
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
                  <div class="text-yellow text-sm">${{ formatNumber(item.price) }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Multiplier Selector -->
          <div class="mt-6 flex flex-col items-center gap-4">
            <div class="text-xl">
              Total Value: <span class="text-yellow">${{ formatNumber(selectedValue) }}</span>
            </div>
            <div class="flex flex-wrap justify-center gap-2">
              <button 
                v-for="mult in multipliers" 
                :key="mult.value"
                class="px-4 py-2 rounded-lg font-medium transition-all duration-200"
                :class="[
                  currentMultiplier === mult.value 
                    ? 'bg-yellow text-gray-darker' 
                    : 'bg-gray-darker text-white/70 hover:bg-gray-darker/70 hover:text-white'
                ]"
                @click="setMultiplier(mult.value)"
              >
                {{ mult.value }}x ({{ mult.chance }}%)
              </button>
            </div>
            <div class="text-xl">
              Potential Win: <span class="text-yellow">${{ formatNumber(potentialWin) }}</span>
            </div>
            <button 
              class="px-8 py-3 bg-yellow text-gray-darker rounded-lg font-medium transition-all duration-200 hover:bg-yellow/90 disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="selectedItems.size === 0"
              @click="startUpgrade"
            >
              Upgrade
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Result Modal -->
    <div 
      v-if="showResult || showSuspense"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
    >
      <!-- Suspense Animation -->
      <div v-if="showSuspense" class="w-full max-w-4xl mx-auto px-4">
        <div class="flex items-center justify-between gap-8">
          <!-- Selected Items Side -->
          <div class="flex-1 bg-gray-dark/80 rounded-xl p-6 transform transition-all duration-500"
               :class="{ 'translate-x-[-100%] opacity-0': suspenseComplete }">
            <h3 class="text-xl font-display text-white mb-4 text-center">Your Items</h3>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
              <div v-for="item in Array.from(selectedItems)" 
                   :key="item.id"
                   class="bg-gray-darker rounded-lg p-3"
                   :class="`rarity-${item.rarity.toLowerCase()}`">
                <img :src="getItemImage(item)" 
                     :alt="item.name"
                     class="w-full h-24 object-contain mb-2">
                <div class="text-xs truncate text-white">
                  {{ item.weapon }} | {{ item.name }}
                </div>
                <div class="text-yellow text-xs">${{ formatNumber(item.price) }}</div>
              </div>
            </div>
            <div class="text-center mt-4">
              <div class="text-xl text-yellow">
                Total: ${{ formatNumber(selectedValue) }}
              </div>
            </div>
          </div>

          <!-- VS Text -->
          <div class="text-center transform transition-all duration-500"
               :class="{ 'scale-150': suspenseComplete }">
            <div class="text-6xl font-display font-bold upgrade-arrow"
                 :class="{
                   'animate-processing': !suspenseComplete,
                   'text-green-500': suspenseComplete && result?.won,
                   'text-red-500 rotate-180': suspenseComplete && !result?.won
                 }">↑</div>
            <div class="text-sm text-white/70 mt-2">{{ currentMultiplier }}x</div>
          </div>

          <!-- Potential Reward Side -->
          <div class="flex-1 bg-gray-dark/80 rounded-xl p-6 transform transition-all duration-500"
               :class="{ 'translate-x-[100%] opacity-0': suspenseComplete }">
            <h3 class="text-xl font-display text-white mb-4 text-center">Potential Reward</h3>
            <div class="flex items-center justify-center h-[calc(100%-2rem)]">
              <div class="text-3xl text-yellow font-display">
                ${{ formatNumber(potentialWin) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Result Content -->
      <div v-else class="bg-gray-dark rounded-xl p-8 max-w-2xl w-full mx-4"
           :class="{ 'animate-fade-in': !showSuspense }">
        <h2 
          class="text-2xl font-display text-center mb-6"
          :class="result.won ? 'text-green-500' : 'text-red-500'"
        >
          {{ result.won ? 'Upgrade Successful!' : 'Upgrade Failed' }}
        </h2>
        <div class="text-center mb-8">
          <template v-if="result.won">
            <template v-if="result.multiple_skins">
              <p class="text-white/70 mb-4">
                Due to the high value of your upgrade, you've received multiple skins worth 
                <span class="text-yellow">${{ formatNumber(result.total_value) }}</span>:
              </p>
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div 
                  v-for="skin in result.skins" 
                  :key="skin.id"
                  class="bg-gray-darker rounded-lg p-3"
                  :class="`rarity-${skin.rarity.toLowerCase()}`"
                >
                  <img 
                    :src="getItemImage(skin)" 
                    :alt="skin.name"
                    class="w-full h-24 object-contain mb-2"
                  >
                  <div class="text-xs truncate text-white">{{ skin.weapon }} | {{ skin.name }}</div>
                  <div class="text-yellow text-xs">${{ formatNumber(skin.price) }}</div>
                </div>
              </div>
            </template>
            <template v-else>
              <div 
                class="bg-gray-darker rounded-lg p-4 max-w-xs mx-auto"
                :class="`rarity-${result.skins[0].rarity.toLowerCase()}`"
              >
                <img 
                  :src="getItemImage(result.skins[0])" 
                  :alt="result.skins[0].name"
                  class="w-full h-40 object-contain mb-4"
                >
                <div class="text-white">{{ result.skins[0].weapon }} | {{ result.skins[0].name }}</div>
                <div class="text-yellow">${{ formatNumber(result.skins[0].price) }}</div>
              </div>
            </template>
          </template>
          <template v-else>
            <p class="text-white/70">Better luck next time!</p>
          </template>
        </div>
        <div class="flex justify-center">
          <button 
            class="px-8 py-3 bg-yellow text-gray-darker rounded-lg font-medium transition-all duration-200 hover:bg-yellow/90"
            @click="closeResult"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { CASE_MAPPING } from '../store'

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
  name: 'UpgradeView',
  setup() {
    // State
    const inventory = ref([])
    const selectedItems = ref(new Set())
    const currentMultiplier = ref(2)
    const showResult = ref(false)
    const result = ref(null)
    const showSuspense = ref(false)
    const suspenseComplete = ref(false)

    // Constants
    const multipliers = [
      { value: 2, chance: 46 },
      { value: 3, chance: 30.67 },
      { value: 5, chance: 18.4 },
      { value: 10, chance: 9.2 },
      { value: 100, chance: 0.92 }
    ]

    // Computed
    const selectedValue = computed(() => {
      return Array.from(selectedItems.value).reduce((total, item) => total + item.price, 0)
    })

    const potentialWin = computed(() => {
      return selectedValue.value * currentMultiplier.value
    })

    // Methods
    const loadInventory = async () => {
      try {
        const response = await fetch('/get_jackpot_inventory')
        const data = await response.json()
        
        if (data.error) {
          console.error('Error:', data.error)
          return
        }
        
        inventory.value = data.inventory.sort((a, b) => b.price - a.price)
      } catch (error) {
        console.error('Error loading inventory:', error)
      }
    }

    const getItemImage = (item) => {
      if (item.is_sticker) {
        const capsuleType = item.case_type || item.capsule_type
        return `/sticker_skins/${capsuleType}/${item.image}`
      }
      if (!item.weapon || !item.name) {
        return '/skins/placeholder.png'
      }
      return getSkinImagePath(item)
    }

    function getSkinImagePath(item) {
      const casePath = CASE_MAPPING[item.case_type] || item.case_type
      return `/skins/${casePath}/${item.image}`
    }

    const toggleItem = (item) => {
      if (selectedItems.value.has(item)) {
        selectedItems.value.delete(item)
      } else if (selectedItems.value.size < 10) {
        selectedItems.value.add(item)
      }
    }

    const setMultiplier = (value) => {
      currentMultiplier.value = value
    }

    const startUpgrade = async () => {
      if (selectedItems.value.size === 0) return

      try {
        showSuspense.value = true
        suspenseComplete.value = false
        result.value = null

        // Start suspense animation
        await new Promise(resolve => setTimeout(resolve, 2000))

        const response = await fetch('/play_upgrade', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            items: Array.from(selectedItems.value),
            multiplier: currentMultiplier.value
          })
        })

        const data = await response.json()
        if (data.error) {
          console.error('Server error:', data.error)
          alert(data.error)
          return
        }

        // Set result first, then complete suspense
        result.value = data
        suspenseComplete.value = true
        
        // Wait longer to show the win/loss arrow
        await new Promise(resolve => setTimeout(resolve, 1000))

        // Hide suspense and show result
        showSuspense.value = false
        showResult.value = true
      } catch (error) {
        console.error('Error:', error)
        alert('Failed to process upgrade')
      }
    }

    const closeResult = () => {
      showResult.value = false
      showSuspense.value = false
      suspenseComplete.value = false
      result.value = null
      selectedItems.value.clear()
      loadInventory()
    }

    // Initial load
    loadInventory()

    return {
      inventory,
      selectedItems,
      currentMultiplier,
      multipliers,
      selectedValue,
      potentialWin,
      showResult,
      result,
      getItemImage,
      toggleItem,
      setMultiplier,
      startUpgrade,
      closeResult,
      showSuspense,
      suspenseComplete,
      formatNumber
    }
  }
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.upgrade-arrow {
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

.animate-processing {
  animation: processing 2s infinite;
}

@keyframes processing {
  0% {
    transform: rotate(0deg) scale(1);
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
  }
  50% {
    transform: rotate(180deg) scale(1.2);
    text-shadow: 0 0 20px rgba(255, 255, 255, 0.8);
  }
  100% {
    transform: rotate(360deg) scale(1);
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
  }
}
</style> 