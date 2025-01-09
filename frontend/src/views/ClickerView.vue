<template>
  <div class="min-h-screen bg-gray-darker">
    <!-- Header -->
    <div class="relative py-12 mb-8">
      <div class="absolute inset-0 bg-gradient-to-b from-yellow/5 to-transparent"></div>
      <div class="relative max-w-7xl mx-auto px-4">
        <h1 class="text-4xl font-display font-bold text-white mb-2">Clicker</h1>
        <p class="text-white/70">Click to earn money and cases</p>
      </div>
    </div>

    <!-- Clicker Content -->
    <div class="max-w-7xl mx-auto px-4 pb-12">
      <!-- Tabs -->
      <div class="flex gap-2 mb-8 overflow-x-auto pb-2 scrollbar-none">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          class="px-4 py-2 rounded-lg font-medium transition-all duration-200 whitespace-nowrap"
          :class="[
            currentTab === tab.id 
              ? 'bg-yellow text-gray-darker' 
              : 'bg-gray-dark/50 text-white/70 hover:bg-gray-dark hover:text-white'
          ]"
          @click="currentTab = tab.id"
        >
          {{ tab.name }}
        </button>
      </div>

      <!-- Money Clicker Section -->
      <div v-if="currentTab === 'money'" class="flex flex-col items-center gap-8">
        <!-- Stats -->
        <div class="grid grid-cols-3 gap-6 w-full max-w-2xl">
          <div class="bg-gray-dark/50 rounded-xl p-4 text-center">
            <div class="text-white/70 text-sm mb-1">Multiplier</div>
            <div class="text-yellow text-xl font-medium">{{ currentMultiplier }}x</div>
          </div>
          <div class="bg-gray-dark/50 rounded-xl p-4 text-center">
            <div class="text-white/70 text-sm mb-1">Crit Chance</div>
            <div class="text-yellow text-xl font-medium">{{ critChance }}%</div>
          </div>
          <div class="bg-gray-dark/50 rounded-xl p-4 text-center">
            <div class="text-white/70 text-sm mb-1">Auto Click</div>
            <div class="text-yellow text-xl font-medium">{{ autoClickRate }}/s</div>
          </div>
        </div>

        <!-- Clicker Button -->
        <div class="relative">
          <button 
            @click="handleMoneyClick"
            class="w-48 h-48 rounded-full bg-gradient-to-br from-yellow/20 to-yellow/10 hover:from-yellow/30 hover:to-yellow/20 
                   flex items-center justify-center transition-all duration-200 transform active:scale-95 group"
          >
            <div class="absolute inset-0 rounded-full bg-gradient-to-r from-yellow/20 via-yellow/10 to-yellow/5 
                        animate-pulse group-hover:animate-none"></div>
            <div class="relative flex flex-col items-center">
              <img src="@/assets/coin.png" alt="Coin" class="w-24 h-24 mb-2">
              <div class="text-yellow font-medium">{{ currentMultiplier }}x</div>
            </div>
          </button>
        </div>
      </div>

      <!-- Case Clicker Section -->
      <div v-if="currentTab === 'case'" class="flex flex-col items-center gap-8">
        <!-- Stats -->
        <div class="grid grid-cols-2 gap-6 w-full max-w-xl">
          <div class="bg-gray-dark/50 rounded-xl p-4 text-center">
            <div class="text-white/70 text-sm mb-1">Progress per Click</div>
            <div class="text-yellow text-xl font-medium">{{ progressPerClick }}%</div>
          </div>
          <div class="bg-gray-dark/50 rounded-xl p-4 text-center">
            <div class="text-white/70 text-sm mb-1">Case Quality</div>
            <div class="text-yellow text-xl font-medium">{{ caseQuality }}</div>
          </div>
        </div>

        <!-- Progress Bar -->
        <div class="w-full max-w-xl bg-gray-dark/50 rounded-full h-4 overflow-hidden">
          <div 
            class="h-full bg-gradient-to-r from-yellow via-yellow/80 to-yellow/60 transition-all duration-300"
            :style="{ width: `${caseProgress}%` }"
          ></div>
        </div>

        <!-- Clicker Button -->
        <div class="relative">
          <button 
            @click="handleCaseClick"
            class="w-48 h-48 rounded-xl bg-gradient-to-br from-yellow/20 to-yellow/10 hover:from-yellow/30 hover:to-yellow/20 
                   flex items-center justify-center transition-all duration-200 transform active:scale-95 group"
          >
            <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-yellow/20 via-yellow/10 to-yellow/5 
                        animate-pulse group-hover:animate-none"></div>
            <img :src="currentCaseImage" alt="Case" class="w-32 h-32">
          </button>
        </div>
      </div>
    </div>

    <!-- Case Earned Modal -->
    <div 
      v-if="showCaseModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      @click.self="showCaseModal = false"
    >
      <div class="bg-gray-dark rounded-xl p-8 max-w-md w-full mx-4 text-center">
        <h3 class="text-2xl font-display text-yellow mb-6">Case Earned!</h3>
        <img :src="earnedCase.image" :alt="earnedCase.name" class="w-48 h-48 mx-auto mb-6">
        <div class="text-white text-lg mb-2">{{ earnedCase.name }}</div>
        <div class="text-yellow text-xl font-medium mb-6">${{ earnedCase.price.toFixed(2) }}</div>
        <button 
          class="px-6 py-3 bg-yellow text-gray-darker rounded-lg font-medium transition-all duration-200 hover:bg-yellow/90"
          @click="showCaseModal = false"
        >
          Continue
        </button>
      </div>
    </div>

    <!-- Floating Chest -->
    <div 
      v-show="showChest"
      ref="floatingChest"
      @click="handleChestClick"
      class="fixed text-4xl cursor-pointer select-none transition-transform duration-300 animate-bounce"
      style="transform-origin: center center;"
    >
      🎁
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue'

export default {
  name: 'ClickerView',
  setup() {
    // State
    const currentTab = ref('money')
    const currentMultiplier = ref(1.0)
    const critChance = ref(0)
    const autoClickRate = ref(0)
    const progressPerClick = ref(1)
    const caseQuality = ref(1)
    const caseProgress = ref(0)
    const showCaseModal = ref(false)
    const showChest = ref(false)
    const comboClickCount = ref(0)
    const clicksToCombo = ref(20)
    const maxMultiplier = ref(2.0)
    const baseClickValue = ref(0.01)
    const pendingClicks = ref(0)
    const isProcessingClick = ref(false)
    const lastProgress = ref(0)

    const tabs = [
      { id: 'money', name: 'Money Clicker' },
      { id: 'case', name: 'Case Clicker' }
    ]

    const earnedCase = ref({
      name: '',
      image: '',
      price: 0
    })

    const cases = [
      'weapon_case_1.png',
      'esports_2013_case.png',
      'operation_bravo_case.png',
      // ... add more cases
    ]

    const currentCaseImage = ref(`/static/media/cases/${cases[0]}`)

    // Methods
    const handleMoneyClick = async () => {
      if (!isProcessingClick.value) {
        try {
          // Increment combo on manual clicks
          comboClickCount.value++
          
          if (comboClickCount.value >= clicksToCombo.value) {
            comboClickCount.value = 0
            currentMultiplier.value = Math.min(
              parseFloat((currentMultiplier.value + 0.1).toFixed(1)),
              maxMultiplier.value
            )
          }

          // Calculate critical strike
          let isCritical = false
          const criticalChance = critChance.value / 100
          
          if (criticalChance > 0) {
            const roll = Math.random()
            if (roll < criticalChance) {
              isCritical = true
            }
          }

          // Create floating money text
          createFloatingMoney(currentMultiplier.value * baseClickValue.value, isCritical)

          // TODO: Send click to backend
          // const response = await fetch('/click', {...})
        } catch (error) {
          console.error('Error processing click:', error)
        }
      }
    }

    const handleCaseClick = async () => {
      pendingClicks.value++
      
      if (!isProcessingClick.value) {
        await processClicks()
      }
    }

    const processClicks = async () => {
      isProcessingClick.value = true
      
      while (pendingClicks.value > 0) {
        try {
          // TODO: Replace with actual API call
          // const response = await fetch('/case_click', {...})
          
          // Simulate progress
          lastProgress.value = Math.min(lastProgress.value + progressPerClick.value, 100)
          caseProgress.value = lastProgress.value
          
          if (caseProgress.value >= 100) {
            // Case earned
            earnedCase.value = {
              name: 'CS2 Case',
              image: '/static/media/cases/cs2_case.png',
              price: 2.99
            }
            showCaseModal.value = true
            lastProgress.value = 0
            caseProgress.value = 0
            pendingClicks.value = 0
            break
          }
          
          pendingClicks.value--
        } catch (error) {
          console.error('Error processing case click:', error)
          break
        }
      }
      
      isProcessingClick.value = false
      
      if (pendingClicks.value > 0) {
        processClicks()
      }
    }

    const createFloatingMoney = (amount, isCritical) => {
      const moneyText = document.createElement('div')
      moneyText.className = `fixed text-yellow font-medium transition-all duration-1000 pointer-events-none
                            ${isCritical ? 'text-pink-500 font-bold text-xl' : ''}`
      moneyText.textContent = `+$${amount.toFixed(3)}`
      
      // Position near the clicker button
      const button = document.querySelector('.clicker-btn')
      if (button) {
        const rect = button.getBoundingClientRect()
        moneyText.style.left = `${rect.left + rect.width/2}px`
        moneyText.style.top = `${rect.top + rect.height/2}px`
        moneyText.style.transform = 'translate(-50%, -50%)'
        
        // Animate
        requestAnimationFrame(() => {
          moneyText.style.transform = 'translate(-50%, -100px)'
          moneyText.style.opacity = '0'
        })
        
        document.body.appendChild(moneyText)
        setTimeout(() => moneyText.remove(), 1000)
      }
    }

    const handleChestClick = async () => {
      if (showChest.value) {
        showChest.value = false
        
        // Random reward between 1-100 USD
        const reward = Math.floor(Math.random() * 100) + 1
        
        // Create floating reward text
        const rewardText = document.createElement('div')
        rewardText.className = 'fixed text-yellow text-xl font-bold transition-all duration-1000 pointer-events-none'
        rewardText.textContent = `+$${reward.toFixed(2)}`
        
        const chest = document.querySelector('.floating-chest')
        if (chest) {
          const rect = chest.getBoundingClientRect()
          rewardText.style.left = `${rect.left + rect.width/2}px`
          rewardText.style.top = `${rect.top}px`
          rewardText.style.transform = 'translate(-50%, 0)'
          
          // Animate
          requestAnimationFrame(() => {
            rewardText.style.transform = 'translate(-50%, -50px)'
            rewardText.style.opacity = '0'
          })
          
          document.body.appendChild(rewardText)
          setTimeout(() => rewardText.remove(), 1000)
        }
        
        // TODO: Send reward to backend
        // await fetch('/chest_reward', {...})
      }
    }

    // Chest spawning system
    let chestTimeout = null
    let chestInterval = null

    const spawnChest = () => {
      showChest.value = true
      
      if (chestTimeout) {
        clearTimeout(chestTimeout)
      }
      
      // Remove chest after 20 seconds
      chestTimeout = setTimeout(() => {
        showChest.value = false
      }, 20000)
    }

    const scheduleNextChest = () => {
      if (chestInterval) {
        clearTimeout(chestInterval)
      }
      
      const spawnWithRandomDelay = () => {
        // Random delay between 2-10 minutes
        const minDelay = 120000
        const maxDelay = 600000
        const randomDelay = Math.floor(Math.random() * (maxDelay - minDelay + 1)) + minDelay
        
        chestInterval = setTimeout(() => {
          spawnChest()
          spawnWithRandomDelay()
        }, randomDelay)
      }
      
      spawnWithRandomDelay()
    }

    // Lifecycle hooks
    onMounted(() => {
      scheduleNextChest()
      
      // Initialize with random case image
      const randomCase = cases[Math.floor(Math.random() * cases.length)]
      currentCaseImage.value = `/static/media/cases/${randomCase}`
    })

    onBeforeUnmount(() => {
      if (chestTimeout) clearTimeout(chestTimeout)
      if (chestInterval) clearTimeout(chestInterval)
    })

    return {
      currentTab,
      currentMultiplier,
      critChance,
      autoClickRate,
      progressPerClick,
      caseQuality,
      caseProgress,
      showCaseModal,
      showChest,
      tabs,
      earnedCase,
      currentCaseImage,
      handleMoneyClick,
      handleCaseClick,
      handleChestClick
    }
  }
}
</script>

<style scoped>
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.animate-bounce {
  animation: bounce 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style> 