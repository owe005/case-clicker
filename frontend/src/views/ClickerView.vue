<template>
  <div class="min-h-screen bg-gray-darker">
    <!-- Floating Text Container -->
    <div class="fixed inset-0 pointer-events-none z-[100]">
      <TransitionGroup name="float">
        <div
          v-for="text in floatingTexts"
          :key="text.id"
          class="floating-money absolute"
          :class="{ 'critical': text.isCritical }"
          :style="{
            left: `${text.x}px`,
            top: `${text.y}px`,
            transform: 'translate(-50%, -50%)'
          }"
        >
          {{ text.content }}
        </div>
      </TransitionGroup>
    </div>

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
            <div class="text-white/70 text-sm mb-1 select-none">Multiplier</div>
            <div class="text-yellow text-xl font-medium select-none">{{ currentMultiplier }}x</div>
          </div>
          <div class="bg-gray-dark/50 rounded-xl p-4 text-center">
            <div class="text-white/70 text-sm mb-1 select-none">Crit Chance</div>
            <div class="text-yellow text-xl font-medium select-none">{{ critChance }}%</div>
          </div>
          <div class="bg-gray-dark/50 rounded-xl p-4 text-center">
            <div class="text-white/70 text-sm mb-1 select-none">Auto Click</div>
            <div class="text-yellow text-xl font-medium select-none">{{ autoClickRate }}/s</div>
          </div>
        </div>

        <!-- USD per Second Display -->
        <div class="bg-gray-dark/50 rounded-xl p-4 text-center w-full max-w-2xl">
          <div class="text-white/70 text-sm mb-1 select-none">Earnings Rate</div>
          <div class="text-yellow text-xl font-medium select-none">${{ earningsPerSecond }}/s</div>
        </div>

        <!-- Clicker Button -->
        <div class="relative" @mouseleave="handleMouseLeave">
          <button 
            @click="handleMoneyClick"
            class="clicker-btn w-32 h-32 rounded-full bg-gradient-to-br from-yellow/20 to-yellow/10 hover:from-yellow/30 hover:to-yellow/20 
                   flex items-center justify-center transition-all duration-200 transform active:scale-95 group overflow-hidden relative z-10"
          >
            <div class="absolute inset-0 rounded-full bg-gradient-to-r from-yellow/20 via-yellow/10 to-yellow/5 
                        animate-pulse group-hover:animate-none"></div>
            <img src="/img/coin.png" alt="Coin" class="w-32 h-32 object-contain relative z-10" draggable="false">
          </button>
          <div class="text-yellow font-medium text-center mt-2 select-none">{{ currentMultiplier }}x</div>
        </div>
      </div>

      <!-- Case Clicker Section -->
      <div v-if="currentTab === 'case'" class="flex flex-col items-center gap-8">
        <!-- Stats -->
        <div class="grid grid-cols-2 gap-6 w-full max-w-xl">
          <div class="bg-gray-dark/50 rounded-xl p-4 text-center">
            <div class="text-white/70 text-sm mb-1 select-none">Progress per Click</div>
            <div class="text-yellow text-xl font-medium select-none">{{ progressPerClick }}%</div>
          </div>
          <div class="bg-gray-dark/50 rounded-xl p-4 text-center">
            <div class="text-white/70 text-sm mb-1 select-none">Case Quality</div>
            <div class="text-yellow text-xl font-medium select-none">{{ caseQuality }}</div>
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
            class="clicker-btn w-32 h-32 rounded-xl bg-gradient-to-br from-yellow/20 to-yellow/10 hover:from-yellow/30 hover:to-yellow/20 
                   flex items-center justify-center transition-all duration-200 transform active:scale-95 group relative z-10"
          >
            <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-yellow/20 via-yellow/10 to-yellow/5 
                        animate-pulse group-hover:animate-none"></div>
            <img :src="currentCaseImage" alt="Case" class="w-32 h-32 object-contain relative z-10" draggable="false">
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
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useStore } from '@/store'
import '@/assets/clicker.css'

export default {
  name: 'ClickerView',
  setup() {
    const store = useStore()
    
    // State
    const currentTab = ref('money')
    const showCaseModal = ref(false)
    const showChest = ref(false)
    const earnedCase = ref({
      name: '',
      image: '',
      price: 0
    })

    const tabs = [
      { id: 'money', name: 'Money Clicker' },
      { id: 'case', name: 'Case Clicker' }
    ]

    const cases = [
      'weapon_case_1.png',
      'esports_2013_case.png',
      'operation_bravo_case.png',
      // ... add more cases
    ]

    const currentCaseImage = ref(`/static/media/cases/${cases[0]}`)

    // Computed properties from store
    const currentMultiplier = computed(() => store.state.clicker.currentMultiplier)
    const critChance = computed(() => store.state.upgrades.critical_strike)
    const autoClickRate = computed(() => {
      const level = store.state.upgrades.auto_clicker
      if (level <= 0) return 0
      
      // For levels 1-9: Clicks per second increase from 0.1 to 0.9
      if (level <= 9) return level * 0.1
      
      // For levels 10+: One click per second plus additional clicks based on level
      return level - 9
    })
    const progressPerClick = computed(() => store.state.upgrades.progress_per_click)
    const caseQuality = computed(() => store.state.upgrades.case_quality)
    const caseProgress = computed(() => store.state.clicker.caseProgress)

    // Add click tracking state
    const clickHistory = ref([])
    const CLICK_HISTORY_WINDOW = 5000 // Track clicks over 5 seconds
    const manualClicksPerSecond = ref(0)

    // Update clicks per second every 100ms
    const updateClicksPerSecond = () => {
      const now = Date.now()
      clickHistory.value = clickHistory.value.filter(time => now - time < CLICK_HISTORY_WINDOW)
      manualClicksPerSecond.value = clickHistory.value.length / (CLICK_HISTORY_WINDOW / 1000)
    }

    // Set up interval to update clicks per second
    let updateInterval
    onMounted(() => {
      updateInterval = setInterval(updateClicksPerSecond, 100)

      // Start auto clicker if level > 0
      if (store.state.upgrades.auto_clicker > 0) {
        store.startAutoClicker(store.state.upgrades.auto_clicker)
      }

      // Add listener for auto clicker text
      window.addEventListener('autoClickerText', handleAutoClickText)
    })

    onBeforeUnmount(() => {
      if (updateInterval) clearInterval(updateInterval)
      window.removeEventListener('autoClickerText', handleAutoClickText)
      store.stopAutoClicker()
    })

    // Add earnings per second computed property
    const earningsPerSecond = computed(() => {
      const baseValue = store.state.clicker.baseClickValue || 0.01
      const autoClicks = parseFloat(autoClickRate.value)
      const critRate = critChance.value / 100
      const totalClicksPerSecond = autoClicks + manualClicksPerSecond.value
      
      // Calculate average value per click including crits
      const avgCritMultiplier = 1 + (critRate * 3) // Crits do 4x damage, so +3x extra
      const valuePerClick = baseValue * avgCritMultiplier
      
      // Calculate earnings per second from all clicks
      return (valuePerClick * totalClicksPerSecond).toFixed(3)
    })

    // Add to the setup() data section
    const manualClickQueue = ref({
        normal: 0,
        critical: 0
    })
    const isProcessingManualClicks = ref(false)
    const lastManualClickProcess = ref(Date.now())

    // Update handleMoneyClick
    const handleMoneyClick = async (event, isAutoClick = false) => {
        // Only add to click history for manual clicks
        if (!isAutoClick) {
            clickHistory.value.push(Date.now())

            // Calculate critical strike
            let isCritical = false
            const criticalChance = critChance.value / 100
            
            if (criticalChance > 0) {
                const roll = Math.random()
                if (roll < criticalChance) {
                    isCritical = true
                }
            }

            // Get click position for floating text
            let x, y
            const clickerBtn = document.querySelector('.clicker-btn')
            if (clickerBtn) {
                const rect = clickerBtn.getBoundingClientRect()
                x = rect.left + rect.width / 2
                y = rect.top + rect.height / 2

                // Add floating text immediately
                addFloatingText(
                    x, 
                    y, 
                    `+$${(currentMultiplier.value * store.state.clicker.baseClickValue).toFixed(3)}`,
                    isCritical
                )
            }

            // Update multiplier
            store.updateClickerMultiplier()

            // Add to manual click queue
            if (isCritical) {
                manualClickQueue.value.critical++
            } else {
                manualClickQueue.value.normal++
            }

            // Process clicks if we have enough in the queue or enough time has passed
            const now = Date.now()
            const timeSinceLastProcess = now - lastManualClickProcess.value
            const totalQueuedClicks = manualClickQueue.value.normal + manualClickQueue.value.critical

            if (totalQueuedClicks >= 10 || timeSinceLastProcess >= 1000) {
                await processManualClicks()
            }
        }
    }

    // Add processManualClicks function
    const processManualClicks = async () => {
        if (isProcessingManualClicks.value || 
            (manualClickQueue.value.normal === 0 && manualClickQueue.value.critical === 0)) {
            return
        }

        isProcessingManualClicks.value = true

        try {
            const data = await store.handleBatchMoneyClicks(
                manualClickQueue.value.normal,
                manualClickQueue.value.critical,
                0,
                0
            )

            if (data) {
                // Clear queues
                manualClickQueue.value.normal = 0
                manualClickQueue.value.critical = 0
                lastManualClickProcess.value = Date.now()
            }
        } catch (error) {
            console.error('Error processing manual clicks:', error)
        } finally {
            isProcessingManualClicks.value = false
        }
    }

    // Watch for changes in auto clicker level
    watch(() => store.state.upgrades.auto_clicker, (newLevel) => {
      if (newLevel > 0) {
        store.autoClicker.startAutoClicker(store, newLevel)
      } else {
        store.autoClicker.stopAutoClicker()
      }
    })

    // Add floating text state
    const floatingTexts = ref([])
    let textId = 0

    const addFloatingText = (x, y, content, isCritical = false) => {
      const id = textId++
      floatingTexts.value.push({ id, x, y, content, isCritical })
      
      // Start animation in next frame
      requestAnimationFrame(() => {
        const text = floatingTexts.value.find(t => t.id === id)
        if (text) {
          text.y -= 50 // Move up by 50px
          text.opacity = 0
        }
      })

      // Remove after animation
      setTimeout(() => {
        floatingTexts.value = floatingTexts.value.filter(t => t.id !== id)
      }, 1000)
    }

    // Methods
    const isProcessingClick = ref(false)
    const pendingClicks = ref([])

    const handleCaseClick = async () => {
      if (isProcessingClick.value) return // Skip if already processing

      // Get click position from case clicker button
      const caseClickerBtn = document.querySelector('.case-clicker-btn')
      if (!caseClickerBtn) return

      const rect = caseClickerBtn.getBoundingClientRect()
      const x = rect.left + rect.width / 2
      const y = rect.top + rect.height / 2

      // Add floating text
      addFloatingText(x, y, `+${progressPerClick.value}%`, false)

      // Add click to pending queue
      pendingClicks.value.push({ type: 'case' })

      // Process clicks if we have enough in the queue or not currently processing
      if (pendingClicks.value.length >= 10 || !isProcessingClick.value) {
        await processCaseClicks()
      }
    }

    const processCaseClicks = async () => {
      if (isProcessingClick.value || pendingClicks.value.length === 0) return

      isProcessingClick.value = true

      try {
        // Process all pending clicks in one batch
        const clicks = pendingClicks.value.filter(click => click.type === 'case')
        pendingClicks.value = pendingClicks.value.filter(click => click.type !== 'case') // Remove case clicks

        if (clicks.length > 0) {
          const data = await store.handleBatchCaseClicks(clicks.length)
          if (!data) {
            // If there's an error, add the clicks back to the queue
            pendingClicks.value.push(...clicks)
          } else if (data.earned_cases && data.earned_cases.length > 0) {
            // Show modal for the last earned case
            const lastCase = data.earned_cases[data.earned_cases.length - 1]
            earnedCase.value = {
              name: lastCase.name,
              image: `/static/media/cases/${lastCase.image}`,
              price: lastCase.price
            }
            showCaseModal.value = true
          }
        }
      } catch (error) {
        console.error('Error processing case clicks:', error)
      } finally {
        isProcessingClick.value = false
        
        // If there are more clicks in the queue, process them
        if (pendingClicks.value.some(click => click.type === 'case')) {
          await processCaseClicks()
        }
      }
    }

    const handleChestClick = async () => {
      if (showChest.value) {
        showChest.value = false
        
        // Random reward between 1-100 USD
        const reward = Math.floor(Math.random() * 100) + 1
        
        // Create floating reward text
        const rewardText = document.createElement('div')
        rewardText.className = 'floating-reward'
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
        
        // Send reward to backend
        await store.handleChestReward(reward)
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

    // Reset multiplier when mouse leaves clicker area
    const handleMouseLeave = () => {
      store.resetClickerMultiplier()
    }

    // Watch for tab changes
    watch(currentTab, (newTab) => {
      store.updateCurrentTab(newTab)
    }, { immediate: true })

    // Handle auto clicker floating text
    const handleAutoClickText = (event) => {
      // Only show auto clicker text if we're on the money tab
      if (currentTab.value !== 'money') return

      const { value, isCritical } = event.detail
      const clickerBtn = document.querySelector('.clicker-btn')
      
      if (clickerBtn) {
        const rect = clickerBtn.getBoundingClientRect()
        const x = rect.left + rect.width / 2 + ((Math.random() - 0.5) * rect.width * 0.5)
        const y = rect.top + rect.height / 2 + ((Math.random() - 0.5) * rect.height * 0.5)

        addFloatingText(
          x,
          y,
          `+$${value.toFixed(3)}`,
          isCritical
        )
      }
    }

    // Lifecycle hooks
    onMounted(async () => {
      // Fetch initial user data first
      await store.fetchUserData()
      
      scheduleNextChest()
      
      // Initialize with random case image
      const randomCase = cases[Math.floor(Math.random() * cases.length)]
      currentCaseImage.value = `/static/media/cases/${randomCase}`

      // Add listener for auto clicker text
      window.addEventListener('autoClickerText', handleAutoClickText)

      // Start auto clicker if level > 0 and we're on money tab
      if (store.state.upgrades.auto_clicker > 0 && currentTab.value === 'money') {
        store.startAutoClicker(store.state.upgrades.auto_clicker)
      }

      // Add route change listener
      const handleRouteChange = () => {
        store.stopAutoClicker()
      }
      window.addEventListener('popstate', handleRouteChange)

      // Clean up route change listener on unmount
      onBeforeUnmount(() => {
        window.removeEventListener('popstate', handleRouteChange)
      })
    })

    onBeforeUnmount(() => {
      if (chestTimeout) clearTimeout(chestTimeout)
      if (chestInterval) clearTimeout(chestInterval)
      if (updateInterval) clearInterval(updateInterval)
      window.removeEventListener('autoClickerText', handleAutoClickText)

      // Make absolutely sure auto clicker is stopped
      store.stopAutoClicker()
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
      handleChestClick,
      handleMouseLeave,
      floatingTexts,
      isProcessingClick,
      pendingClicks,
      earningsPerSecond,
      manualClickQueue,
      isProcessingManualClicks,
      lastManualClickProcess,
      processManualClicks
    }
  }
}
</script>

<style>
.float-enter-active,
.float-leave-active {
  transition: all 1s ease;
}

.float-enter-from {
  opacity: 1;
  transform: translate(-50%, -50%);
}

.float-leave-to {
  opacity: 0;
  transform: translate(-50%, -100px);
}
</style> 