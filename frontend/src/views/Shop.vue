<template>
  <div class="min-h-screen bg-gray-darker">
    <!-- Shop Header -->
    <div class="relative py-12 mb-8">
      <div class="absolute inset-0 bg-gradient-to-b from-yellow/5 to-transparent"></div>
      <div class="relative max-w-7xl mx-auto px-4">
        <h1 class="text-4xl font-display font-bold text-white mb-2">CS2 Shop</h1>
        <p class="text-white/70">Browse and purchase cases, skins, stickers, and more</p>
      </div>
    </div>

    <!-- Shop Content -->
    <div class="max-w-7xl mx-auto px-4 pb-12">
      <!-- Categories -->
      <div class="flex gap-2 mb-8 overflow-x-auto pb-2 scrollbar-none">
        <button 
          v-for="category in categories" 
          :key="category.id"
          class="px-4 py-2 rounded-lg font-medium transition-all duration-200 whitespace-nowrap"
          :class="[
            currentCategory === category.id 
              ? 'bg-yellow text-gray-darker' 
              : 'bg-gray-dark/50 text-white/70 hover:bg-gray-dark hover:text-white'
          ]"
          @click="currentCategory = category.id"
        >
          {{ category.name }}
        </button>
      </div>

      <!-- Cases Grid -->
      <div v-if="currentCategory === 'cases'" class="space-y-8">
        <div v-for="[rank, group] in sortedRankGroups" :key="rank" class="space-y-4">
          <!-- Rank Group Header -->
          <div class="flex items-center gap-4">
            <h2 class="text-xl font-display font-medium" 
                :class="Number(rank) <= store.state.rank ? 'text-yellow' : 'text-white/50'">
              {{ RANKS[rank] }}
            </h2>
            <div class="flex-1 h-px bg-yellow/10"></div>
            <span class="text-sm text-white/50">
              {{ Number(rank) <= store.state.rank ? 'Unlocked' : 'Locked' }}
            </span>
          </div>

          <!-- Cases Grid for this Rank -->
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            <div v-for="case_item in group" :key="case_item.case_type" class="group">
              <div class="relative bg-gray-dark/50 rounded-xl p-6 transition-all duration-300 hover:bg-gray-dark/70 h-[320px] flex flex-col"
                   :class="{ 'opacity-75': isCaseLocked(case_item.name) }">
                <!-- Hover Glow Effect -->
                <div class="absolute inset-0 bg-gradient-to-r from-yellow/0 via-yellow/10 to-yellow/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl"></div>
                
                <!-- Lock Overlay for Locked Cases -->
                <div v-if="isCaseLocked(case_item.name)" 
                     class="absolute inset-0 backdrop-blur-[1px] rounded-xl flex items-center justify-center z-10">
                  <div class="bg-black/80 px-4 py-2 rounded-lg backdrop-blur-sm">
                    <div class="flex items-center gap-2 text-red-500">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                      </svg>
                      <span class="font-display">Unlocks at {{ RANKS[CASE_RANK_REQUIREMENTS[case_item.name]] }}</span>
                    </div>
                  </div>
                </div>
                
                <!-- Content -->
                <div class="relative flex-1 flex flex-col">
                  <!-- Image and Name (Clickable for contents) -->
                  <div @click="viewCaseContents(case_item.case_type)" 
                       class="cursor-pointer flex flex-col h-[220px]"
                       :class="{ 'pointer-events-none': isCaseLocked(case_item.name) }">
                    <div class="aspect-square w-full p-4 flex-shrink-0">
                      <img :src="getCaseImagePath(case_item)" 
                           :alt="case_item.name" 
                           class="w-full h-full object-contain transition-all duration-300"
                           :class="{ 'grayscale': isCaseLocked(case_item.name) }">
                    </div>
                    <h3 class="font-display text-white group-hover:text-yellow transition-colors duration-200 line-clamp-2 min-h-[3rem]">
                      {{ case_item.name }}
                    </h3>
                  </div>
                  
                  <!-- Buy Section -->
                  <div class="flex items-center justify-between mt-4">
                    <span class="text-yellow font-medium min-w-[60px]">${{ formatNumber(case_item.price) }}</span>
                    <div class="flex items-center gap-2 flex-shrink-0">
                      <input 
                        type="number" 
                        min="1" 
                        v-model="case_item.quantity" 
                        :disabled="isCaseLocked(case_item.name)"
                        class="w-16 px-2 py-1 bg-gray-darker text-white rounded-lg text-center disabled:opacity-50"
                      >
                      <button 
                        @click.stop="buyCase(case_item.case_type)"
                        :disabled="isCaseLocked(case_item.name)"
                        class="px-4 py-1.5 rounded-lg transition-all duration-200"
                        :class="[
                          isCaseLocked(case_item.name)
                            ? 'bg-gray-dark/50 text-white/30 cursor-not-allowed'
                            : 'bg-yellow/10 hover:bg-yellow/20 text-yellow'
                        ]"
                      >
                        {{ isCaseLocked(case_item.name) ? 'Locked' : 'Buy' }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sticker Capsules Grid -->
      <div v-if="currentCategory === 'stickers'" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        <div v-for="capsule in stickerCapsules" :key="capsule.type" class="group">
          <div class="relative bg-gray-dark/50 rounded-xl p-5 transition-all duration-300 hover:bg-gray-dark/70 h-[320px] flex flex-col">
            <!-- Hover Glow Effect -->
            <div class="absolute inset-0 bg-gradient-to-r from-yellow/0 via-yellow/10 to-yellow/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl"></div>
            
            <!-- Content -->
            <div class="relative flex-1 flex flex-col">
              <!-- Image and Name (Clickable for contents) -->
              <div @click="viewCapsuleContents(capsule.type)" class="cursor-pointer flex flex-col h-[220px]">
                <div class="aspect-square w-full p-4 flex-shrink-0">
                  <img :src="getCapsuleImagePath(capsule)" 
                       :alt="capsule.name" 
                       class="w-full h-full object-contain transition-all duration-300">
                </div>
                <h3 class="font-display text-sm text-white truncate">
                  {{ capsule.name }}
                </h3>
              </div>
              
              <!-- Buy Section -->
              <div class="flex items-center justify-between mt-4">
                <span class="text-yellow font-medium min-w-[80px] mr-2">${{ formatNumber(capsule.price) }}</span>
                <div class="flex items-center gap-1 flex-shrink-0">
                  <input 
                    type="number" 
                    min="1" 
                    v-model="capsule.quantity" 
                    class="w-14 px-2 py-1 bg-gray-darker text-white rounded-lg text-center"
                  >
                  <button 
                    @click.stop="buyCapsule(capsule.type)"
                    class="px-3 py-1.5 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200"
                  >
                    Buy
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Capsule Contents Overlay -->
      <div 
        v-if="showCapsuleContents"
        class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50"
        @click.self="showCapsuleContents = false"
      >
        <div class="bg-gray-dark rounded-xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto mx-4">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h2 class="text-2xl font-display text-white">{{ selectedCapsule?.name }}</h2>
              <p class="text-sm text-white/50">Sticker Capsule</p>
            </div>
            <button 
              @click="showCapsuleContents = false"
              class="text-white/50 hover:text-white"
            >
              ×
            </button>
          </div>
          
          <div class="space-y-6">
            <!-- Pink Items -->
            <div v-if="selectedCapsule?.stickers?.pink?.length" class="space-y-2">
              <h3 class="text-lg font-display text-pink-500">Exotic Stickers <span class="text-sm text-white/50">({{ formatNumber(selectedCapsule.probabilities?.pink || 0) }}%)</span></h3>
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                <div v-for="sticker in selectedCapsule.stickers.pink" :key="sticker.name" class="bg-gray-darker rounded-lg p-4">
                  <img :src="getStickerImagePath(sticker)" :alt="sticker.name" class="w-full h-32 object-contain mb-2">
                  <div class="text-sm text-white">{{ sticker.name }}</div>
                </div>
              </div>
            </div>

            <!-- Purple Items -->
            <div v-if="selectedCapsule?.stickers?.purple?.length" class="space-y-2">
              <h3 class="text-lg font-display text-purple-500">Remarkable Stickers <span class="text-sm text-white/50">({{ formatNumber(selectedCapsule.probabilities?.purple || 0) }}%)</span></h3>
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                <div v-for="sticker in selectedCapsule.stickers.purple" :key="sticker.name" class="bg-gray-darker rounded-lg p-4">
                  <img :src="getStickerImagePath(sticker)" :alt="sticker.name" class="w-full h-32 object-contain mb-2">
                  <div class="text-sm text-white">{{ sticker.name }}</div>
                </div>
              </div>
            </div>

            <!-- Blue Items -->
            <div v-if="selectedCapsule?.stickers?.blue?.length" class="space-y-2">
              <h3 class="text-lg font-display text-blue-500">High Grade Stickers <span class="text-sm text-white/50">({{ formatNumber(selectedCapsule.probabilities?.blue || 0) }}%)</span></h3>
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                <div v-for="sticker in selectedCapsule.stickers.blue" :key="sticker.name" class="bg-gray-darker rounded-lg p-4">
                  <img :src="getStickerImagePath(sticker)" :alt="sticker.name" class="w-full h-32 object-contain mb-2">
                  <div class="text-sm text-white">{{ sticker.name }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Case Contents Overlay -->
      <div 
        v-if="showCaseContents"
        class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50"
        @click.self="showCaseContents = false"
      >
        <div class="bg-gray-dark rounded-xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto mx-4">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h2 class="text-2xl font-display text-white">{{ selectedCase?.name }}</h2>
              <p class="text-sm text-white/50">StatTrak™ Available (10% Chance)</p>
            </div>
            <button 
              @click="showCaseContents = false"
              class="text-white/50 hover:text-white"
            >
              ×
            </button>
          </div>
          
          <div class="space-y-6">
            <!-- Contraband Items -->
            <div v-if="selectedCase?.skins?.contraband" class="space-y-2">
              <h3 class="text-lg font-display" style="color: #FF8C00">Contraband Items <span class="text-sm text-white/50">(0.026%)</span></h3>
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                <div v-for="item in selectedCase.skins.contraband" :key="item.weapon + item.name" class="bg-gray-darker rounded-lg p-4">
                  <img :src="getSkinImagePath(item, selectedCase.image)" :alt="item.name" class="w-full h-32 object-contain mb-2">
                  <div class="text-sm text-white">{{ item.weapon }} | {{ item.name }}</div>
                </div>
              </div>
            </div>

            <!-- Gold Items -->
            <div v-if="selectedCase?.skins?.gold" class="space-y-2">
              <h3 class="text-lg font-display text-yellow">★ Rare Special Items <span class="text-sm text-white/50">(0.26%)</span></h3>
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                <div v-for="item in selectedCase.skins.gold" :key="item.weapon + item.name" class="bg-gray-darker rounded-lg p-4">
                  <img :src="getSkinImagePath(item, selectedCase.image)" :alt="item.name" class="w-full h-32 object-contain mb-2">
                  <div class="text-sm text-white">{{ item.weapon }} | {{ item.name }}</div>
                </div>
              </div>
            </div>

            <!-- Red Items -->
            <div v-if="selectedCase?.skins?.red" class="space-y-2">
              <h3 class="text-lg font-display text-red-500">Covert Items <span class="text-sm text-white/50">(0.90%)</span></h3>
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                <div v-for="item in selectedCase.skins.red" :key="item.weapon + item.name" class="bg-gray-darker rounded-lg p-4">
                  <img :src="getSkinImagePath(item, selectedCase.image)" :alt="item.name" class="w-full h-32 object-contain mb-2">
                  <div class="text-sm text-white">{{ item.weapon }} | {{ item.name }}</div>
                </div>
              </div>
            </div>

            <!-- Pink Items -->
            <div v-if="selectedCase?.skins?.pink" class="space-y-2">
              <h3 class="text-lg font-display text-pink-500">Classified Items <span class="text-sm text-white/50">(4.10%)</span></h3>
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                <div v-for="item in selectedCase.skins.pink" :key="item.weapon + item.name" class="bg-gray-darker rounded-lg p-4">
                  <img :src="getSkinImagePath(item, selectedCase.image)" :alt="item.name" class="w-full h-32 object-contain mb-2">
                  <div class="text-sm text-white">{{ item.weapon }} | {{ item.name }}</div>
                </div>
              </div>
            </div>

            <!-- Purple Items -->
            <div v-if="selectedCase?.skins?.purple" class="space-y-2">
              <h3 class="text-lg font-display text-purple-500">Restricted Items <span class="text-sm text-white/50">(20.08%)</span></h3>
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                <div v-for="item in selectedCase.skins.purple" :key="item.weapon + item.name" class="bg-gray-darker rounded-lg p-4">
                  <img :src="getSkinImagePath(item, selectedCase.image)" :alt="item.name" class="w-full h-32 object-contain mb-2">
                  <div class="text-sm text-white">{{ item.weapon }} | {{ item.name }}</div>
                </div>
              </div>
            </div>

            <!-- Blue Items -->
            <div v-if="selectedCase?.skins?.blue" class="space-y-2">
              <h3 class="text-lg font-display text-blue-500">Mil-Spec Items <span class="text-sm text-white/50">(74.66%)</span></h3>
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                <div v-for="item in selectedCase.skins.blue" :key="item.weapon + item.name" class="bg-gray-darker rounded-lg p-4">
                  <img :src="getSkinImagePath(item, selectedCase.image)" :alt="item.name" class="w-full h-32 object-contain mb-2">
                  <div class="text-sm text-white">{{ item.weapon }} | {{ item.name }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Skins Section -->
      <div v-if="currentCategory === 'skins'" class="space-y-6">
        <!-- Featured Section -->
        <div class="bg-gray-dark/50 rounded-xl p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-display text-white">Featured Skins</h2>
            <div class="text-sm text-white/50">
              Refreshes in: <span class="text-yellow">{{ refreshCountdown }}</span>
            </div>
          </div>

          <div class="grid grid-cols-5 gap-4">
            <div v-for="(skin, rarity) in sortedFeaturedSkins" :key="rarity" 
                 class="group">
              <div class="relative bg-gray-darker rounded-lg p-4 transition-all duration-300 hover:bg-gray-dark/70 hover:scale-[1.02] hover:shadow-xl">
                <!-- Rarity Indicator -->
                <div class="absolute inset-x-0 top-0 h-1 rounded-t-lg" :class="{
                  'bg-yellow': rarity === 'GOLD',
                  'bg-red-500': rarity === 'RED',
                  'bg-pink-500': rarity === 'PINK',
                  'bg-purple-500': rarity === 'PURPLE',
                  'bg-blue-500': rarity === 'BLUE'
                }"></div>
                
                <!-- Glow Effect -->
                <div class="absolute inset-0 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                     :class="{
                       'bg-gradient-to-br from-yellow/5 via-transparent to-yellow/5': rarity === 'GOLD',
                       'bg-gradient-to-br from-red-500/5 via-transparent to-red-500/5': rarity === 'RED',
                       'bg-gradient-to-br from-pink-500/5 via-transparent to-pink-500/5': rarity === 'PINK',
                       'bg-gradient-to-br from-purple-500/5 via-transparent to-purple-500/5': rarity === 'PURPLE',
                       'bg-gradient-to-br from-blue-500/5 via-transparent to-blue-500/5': rarity === 'BLUE'
                     }"
                ></div>
                
                <!-- Content -->
                <div class="relative pt-2">
                  <!-- Image -->
                  <div class="aspect-square mb-4">
                    <img :src="getSkinImagePath(skin)" :alt="`${skin.weapon} | ${skin.name}`" 
                         class="w-full h-full object-contain transform transition-transform duration-300 group-hover:scale-105"
                         @error="$event.target.src = '/skins/weapon_case_1/ak47_case_hardened.png'">
                  </div>
                  
                  <!-- Info -->
                  <div class="space-y-2">
                    <h3 class="font-display text-sm text-white truncate" :class="{ 'text-yellow': skin.stattrak }">
                      {{ skin.stattrak ? 'StatTrak™ ' : '' }}{{ skin.weapon }} | {{ skin.name }}
                    </h3>
                    <div class="flex items-center gap-2 text-xs text-white/50">
                      <span>{{ skin.wear }}</span>
                    </div>
                    <div class="flex items-center justify-between pt-2">
                      <span class="text-yellow font-medium">${{ formatNumber(skin.price) }}</span>
                      <button @click="purchaseSkin(skin)" 
                              class="px-3 py-1 bg-yellow/10 hover:bg-yellow/20 text-yellow text-sm rounded transition-all duration-200">
                        Purchase
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Notification Overlay -->
    <div 
      v-if="notification.show"
      class="fixed top-0 left-1/2 transform -translate-x-1/2 mt-6 z-50"
    >
      <div 
        class="bg-gray-dark/90 backdrop-blur-sm text-white px-6 py-3 rounded-lg shadow-lg"
        :class="{ 'animate-bounce': notification.bounce }"
      >
        {{ notification.message }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { useStore, CASE_MAPPING, RANKS, CASE_RANK_REQUIREMENTS } from '../store'

export default {
  name: 'ShopView',
  setup() {
    const store = useStore()
    const currentCategory = ref('cases')
    const cases = ref({})
    const showCaseContents = ref(false)
    const selectedCase = ref(null)
    const featuredSkins = ref({})
    const lastRefreshTime = ref(null)
    const refreshCountdown = ref('59:59')
    const refreshInterval = ref(null)
    const notification = ref({
      show: false,
      message: '',
      bounce: false,
      timeout: null,
      lastCase: null,
      purchaseCount: 0
    })
    const stickerCapsules = ref({})
    const showCapsuleContents = ref(false)
    const selectedCapsule = ref(null)
    
    const categories = [
      { id: 'cases', name: 'Cases' },
      { id: 'skins', name: 'Skins' },
      { id: 'stickers', name: 'Sticker Capsules' },
      { id: 'collections', name: 'Collections' },
      { id: 'souvenir', name: 'Souvenir Packages' }
    ]

    // Format number function
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

    // Add computed property to check if a case is locked
    const isCaseLocked = (caseName) => {
      const requiredRank = CASE_RANK_REQUIREMENTS[caseName] || 0;
      return store.state.rank < requiredRank;
    };

    // Load cases from backend
    async function loadCases() {
      try {
        const response = await fetch('/api/data/case_contents/all')
        const data = await response.json()
        if (data.error) {
          console.error('Error loading cases:', data.error)
          return
        }
        // Add quantity field to each case
        Object.values(data).forEach(case_data => {
          case_data.quantity = 1
        })
        cases.value = data
      } catch (error) {
        console.error('Error loading cases:', error)
      }
    }

    // Load featured skins
    async function loadFeaturedSkins() {
      try {
        const response = await fetch('/get_featured_skins')
        const data = await response.json()
        
        if (data.error) {
          console.error('Error:', data.error)
          return
        }
        
        featuredSkins.value = data.skins
        lastRefreshTime.value = data.refreshTime * 1000 // Convert to milliseconds
        updateCountdown()
      } catch (error) {
        console.error('Error loading featured skins:', error)
      }
    }

    // Update countdown timer
    function updateCountdown() {
      if (!lastRefreshTime.value) return

      function update() {
        const now = Date.now()
        const timeLeft = 3600000 - (now - lastRefreshTime.value) // 1 hour in milliseconds

        if (timeLeft <= 0) {
          loadFeaturedSkins()
          return
        }

        const minutes = Math.floor(timeLeft / 60000)
        const seconds = Math.floor((timeLeft % 60000) / 1000)
        refreshCountdown.value = `${minutes}:${seconds.toString().padStart(2, '0')}`
      }

      // Clear existing interval
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
      }

      update() // Initial update
      refreshInterval.value = setInterval(update, 1000)
    }

    // Show notification
    function showNotification(message, duration = 2000, caseType = null) {
      // If there's an existing notification and it's the same case
      if (notification.value.show && caseType && caseType === notification.value.lastCase) {
        // Increment the purchase count
        notification.value.purchaseCount += cases.value[caseType].quantity
        // Update message with new count
        notification.value.message = `Purchased ${notification.value.purchaseCount}x ${cases.value[caseType].name}!`
        // Make it bounce
        notification.value.bounce = true
        setTimeout(() => {
          notification.value.bounce = false
        }, 200)
        // Reset the timeout
        if (notification.value.timeout) {
          clearTimeout(notification.value.timeout)
        }
      } else {
        // New notification
        notification.value.show = true
        notification.value.message = message
        notification.value.lastCase = caseType
        notification.value.purchaseCount = caseType ? cases.value[caseType].quantity : 0
      }

      notification.value.timeout = setTimeout(() => {
        notification.value.show = false
        notification.value.message = ''
        notification.value.lastCase = null
        notification.value.purchaseCount = 0
      }, duration)
    }

    // Buy case function
    async function buyCase(caseType) {
      try {
        const response = await fetch('/buy_case', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            case_type: caseType,
            quantity: cases.value[caseType].quantity
          })
        })
        
        const data = await response.json()
        if (data.error) {
          showNotification(data.error)
          return
        }

        // Update store balance
        store.updateUserData({ balance: data.balance })
        
        // Show success notification with case type for tracking
        showNotification(`Purchased ${cases.value[caseType].quantity}x ${cases.value[caseType].name}!`, 2000, caseType)
      } catch (error) {
        console.error('Error buying case:', error)
        showNotification('Failed to purchase case')
      }
    }

    // Purchase skin
    async function purchaseSkin(skin) {
      try {
        // Only send the required fields
        const skinData = {
          weapon: skin.weapon,
          name: skin.name,
          wear: skin.wear,
          stattrak: skin.stattrak,
          case_type: skin.case_type,
          case_file: skin.case_file,
          price: skin.price,
          image: skin.image,
          rarity: skin.rarity || Object.keys(featuredSkins.value).find(rarity => featuredSkins.value[rarity] === skin)
        }
        
        const response = await fetch('/buy_skin', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(skinData)
        })

        const data = await response.json()
        if (data.error) {
          showNotification(data.error)
          return
        }

        // Update balance
        store.updateUserData({ balance: data.balance })
        showNotification(`Purchased ${skin.weapon} | ${skin.name}!`)
      } catch (error) {
        console.error('Error:', error)
        showNotification('Failed to purchase skin')
      }
    }

    // View case contents
    async function viewCaseContents(caseType) {
      try {
        const response = await fetch(`/api/data/case_contents/${caseType}`)
        const data = await response.json()
        if (data.error) {
          console.error('Error loading case contents:', data.error)
          return
        }

        // Filter gold items based on case type
        if (data.skins?.gold) {
          if (caseType === 'hydra' || caseType === 'glove') {
            // Show only specific gloves for these cases
            const gloveImages = [
              'sportgloves_pandoras_box.png',
              'specialistgloves_emerald_web.png',
              'motogloves_spearmint.png',
              'handwraps_slaughter.png',
              'drivergloves_crimson_weave.png',
              'bloodhoundgloves_charred.png'
            ]
            data.skins.gold = data.skins.gold.filter(item => gloveImages.includes(item.image))
          } else if (caseType === 'snakebite' || caseType === 'broken_fang' || caseType === 'recoil') {
            // Show only specific gloves for these cases
            const gloveImages = [
              'sportgloves_slingshot.png',
              'drivergloves_snow_leopard.png',
              'brokenfanggloves_jade.png',
              'handwraps_caution.png',
              'specialistgloves_tiger_strike.png',
              'motogloves_finish_line.png'
            ]
            data.skins.gold = data.skins.gold.filter(item => gloveImages.includes(item.image))
          } else if (caseType === 'revolution' || caseType === 'clutch') {
            // Get one of each glove type
            const gloveTypes = new Set()
            data.skins.gold = data.skins.gold.filter(item => {
              if (!gloveTypes.has(item.weapon)) {
                gloveTypes.add(item.weapon)
                return true
              }
              return false
            })
          } else if (caseType === 'chroma' || caseType === 'chroma_2' || caseType === 'chroma_3') {
            // Show only Doppler knives
            data.skins.gold = data.skins.gold.filter(item => item.name === 'Doppler')
          } else if (caseType === 'gamma' || caseType === 'gamma_2' || caseType === 'riptide' || caseType === 'dreams_&_nightmares') {
            // Show only Gamma Doppler knives
            data.skins.gold = data.skins.gold.filter(item => item.name === 'Gamma Doppler')
          } else if (caseType === 'spectrum' || caseType === 'spectrum_2' || caseType === 'prisma' || caseType === 'prisma_2') {
            // Show only Doppler knives
            data.skins.gold = data.skins.gold.filter(item => item.name === 'Doppler')
          } else {
            // For all other cases, show only vanilla knives
            data.skins.gold = data.skins.gold.filter(item => 
              !item.name || item.name === 'Vanilla' || 
              item.name.toLowerCase() === item.weapon.toLowerCase().replace('★ ', '')
            )
          }
        }

        selectedCase.value = data
        showCaseContents.value = true
      } catch (error) {
        console.error('Error loading case contents:', error)
      }
    }

    function getCaseImagePath(case_data) {
      return `/cases/${case_data.image}`
    }

    function getSkinImagePath(skin, case_image) {
      // If case_image is provided (for case contents), use it
      if (case_image) {
        // Get the case type from the image name (e.g., 'operation_bravo_case.png' -> 'bravo')
        const caseType = Object.keys(CASE_MAPPING).find(key => 
          case_image.includes(CASE_MAPPING[key]) || 
          CASE_MAPPING[key].includes(case_image.replace('.png', ''))
        )
        return `/skins/${CASE_MAPPING[caseType]}/${skin.image}`
      }
      
      // For featured skins
      const casePath = CASE_MAPPING[skin.case_type] || skin.case_file
      return `/skins/${casePath}/${skin.image}`
    }

    // Sort featured skins by rarity
    const sortedFeaturedSkins = computed(() => {
      const rarityOrder = {
        'GOLD': 5,
        'RED': 4,
        'PINK': 3,
        'PURPLE': 2,
        'BLUE': 1
      }
      
      return Object.fromEntries(
        Object.entries(featuredSkins.value)
          .sort(([rarityA], [rarityB]) => rarityOrder[rarityB] - rarityOrder[rarityA])
      )
    })

    // Add computed property for grouped cases
    const groupedCases = computed(() => {
      const casesArray = Object.entries(cases.value).map(([case_type, case_data]) => ({
        case_type,
        ...case_data
      }));

      // Group cases by rank requirement using CASE_RANK_REQUIREMENTS
      const groups = {};
      casesArray.forEach(case_item => {
        const requiredRank = CASE_RANK_REQUIREMENTS[case_item.name] || 0;
        if (!groups[requiredRank]) {
          groups[requiredRank] = [];
        }
        groups[requiredRank].push(case_item);
      });

      // Log cases grouped under Silver I
      console.log('Cases under Silver I:', groups[0]);

      // Sort cases within each group by price
      Object.values(groups).forEach(group => {
        group.sort((a, b) => a.price - b.price);
      });

      return groups;
    });

    // Add computed property for sorted rank groups
    const sortedRankGroups = computed(() => {
      return Object.entries(groupedCases.value)
        .sort(([rankA], [rankB]) => Number(rankA) - Number(rankB));
    });

    // Load sticker capsules from backend
    async function loadStickerCapsules() {
      try {
        const response = await fetch('/api/data/sticker_capsule_contents/all')
        const data = await response.json()
        if (data.error) {
          console.error('Error loading sticker capsules:', data.error)
          return
        }
        // Add quantity field to each capsule
        Object.values(data).forEach(capsule => {
          capsule.quantity = 1
        })
        stickerCapsules.value = data
      } catch (error) {
        console.error('Error loading sticker capsules:', error)
      }
    }

    // Buy sticker capsule function
    async function buyCapsule(capsuleType) {
      try {
        const response = await fetch('/buy_sticker_capsule', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            capsule_type: capsuleType,
            quantity: stickerCapsules.value[capsuleType].quantity
          })
        })
        
        const data = await response.json()
        if (data.error) {
          showNotification(data.error)
          return
        }

        // Update store balance
        store.updateUserData({ balance: data.balance })
        
        // Show success notification
        showNotification(`Purchased ${stickerCapsules.value[capsuleType].quantity}x ${stickerCapsules.value[capsuleType].name}!`)
      } catch (error) {
        console.error('Error buying sticker capsule:', error)
        showNotification('Failed to purchase sticker capsule')
      }
    }

    // View capsule contents
    async function viewCapsuleContents(capsuleType) {
      try {
        const response = await fetch(`/api/data/sticker_capsule_contents/${capsuleType}`)
        const data = await response.json()
        if (data.error) {
          console.error('Error loading capsule contents:', data.error)
          return
        }

        selectedCapsule.value = data
        showCapsuleContents.value = true
      } catch (error) {
        console.error('Error loading capsule contents:', error)
      }
    }

    function getCapsuleImagePath(capsule) {
      return `/stickers/${capsule.type}.png`
    }

    function getStickerImagePath(sticker) {
      // Extract capsule type from the selected capsule
      const capsuleType = selectedCapsule.value.type
      return `/sticker_skins/${capsuleType}/${sticker.image}`
    }

    // Watch for category changes
    watch(currentCategory, (newCategory) => {
      if (newCategory === 'skins') {
        loadFeaturedSkins()
      } else if (newCategory === 'stickers') {
        loadStickerCapsules()
      }
    })

    onMounted(() => {
      loadCases()
      if (currentCategory.value === 'skins') {
        loadFeaturedSkins()
      } else if (currentCategory.value === 'stickers') {
        loadStickerCapsules()
      }
    })

    // Clean up interval on component unmount
    onUnmounted(() => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
      }
    })

    return {
      currentCategory,
      categories,
      cases,
      showCaseContents,
      selectedCase,
      featuredSkins,
      sortedFeaturedSkins,
      refreshCountdown,
      notification,
      buyCase,
      viewCaseContents,
      getCaseImagePath,
      getSkinImagePath,
      purchaseSkin,
      isCaseLocked,
      RANKS,
      CASE_RANK_REQUIREMENTS,
      groupedCases,
      sortedRankGroups,
      store,
      stickerCapsules,
      showCapsuleContents,
      selectedCapsule,
      buyCapsule,
      viewCapsuleContents,
      getCapsuleImagePath,
      getStickerImagePath,
      formatNumber,
    }
  }
}
</script> 

<style>
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.animate-bounce {
  animation: bounce 0.2s ease-in-out;
}

/* Add transition for grayscale effect */
.grayscale {
  filter: grayscale(100%);
}
</style> 