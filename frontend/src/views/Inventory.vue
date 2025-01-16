<template>
  <div class="min-h-screen bg-gray-darker">
    <!-- Audio Elements -->
    <audio ref="spinningSound" preload="auto">
      <source src="/case_spinning.mp3" type="audio/mpeg">
    </audio>
    <audio ref="showcaseSound" preload="auto">
      <source src="/case_showcase.mp3" type="audio/mpeg">
    </audio>

    <!-- Inventory Header -->
    <div class="relative py-12 mb-8">
      <div class="absolute inset-0 bg-gradient-to-b from-yellow/5 to-transparent"></div>
      <div class="relative max-w-7xl mx-auto px-4">
        <h1 class="text-4xl font-display font-bold text-white mb-2">Inventory</h1>
        <p class="text-white/70">Manage your skins, cases, and items</p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="max-w-7xl mx-auto px-4 py-12 text-center">
      <div class="animate-spin w-8 h-8 border-4 border-yellow border-t-transparent rounded-full mx-auto mb-4"></div>
      <p class="text-white/70">Loading inventory...</p>
    </div>

    <!-- Inventory Content -->
    <div v-else class="max-w-7xl mx-auto px-4 pb-12">
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

      <!-- Skins Section -->
      <div v-if="currentCategory === 'skins'" class="space-y-6">
        <!-- Controls -->
        <div class="flex items-center justify-between gap-4 flex-wrap">
          <!-- Sort Controls -->
          <div class="flex gap-2">
            <button 
              v-for="sort in sortOptions" 
              :key="sort.id"
              class="px-4 py-2 rounded-lg font-medium transition-all duration-200"
              :class="[
                currentSort === sort.id 
                  ? 'bg-yellow text-gray-darker' 
                  : 'bg-gray-dark/50 text-white/70 hover:bg-gray-dark hover:text-white'
              ]"
              @click="sortItems(sort.id)"
            >
              {{ sort.name }}
            </button>
          </div>

          <!-- Sell All Button -->
          <button 
            v-if="totalValue > 0"
            class="px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-500 rounded-lg transition-all duration-200 font-medium"
            @click="showSellAllModal = true"
          >
            Sell All: ${{ totalValue.toFixed(2) }}
          </button>
        </div>

        <!-- Skins Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-6 gap-4">
          <div v-for="item in sortedSkins" :key="item.stackKey || item.timestamp" class="group">
            <div class="relative bg-gray-dark/50 rounded-xl p-4 transition-all duration-300 hover:bg-gray-dark/70 h-[320px] flex flex-col"
                 :class="{ 'cursor-pointer': item.isStack || item.isExpanded }"
                 @click="(item.isStack || item.isExpanded) ? toggleStack(item.stackKey) : null">
              <!-- Rarity Indicator -->
              <div class="absolute inset-x-0 top-0 h-1 rounded-t-xl z-10" :class="getRarityColor(item.rarity)"></div>
              
              <!-- Content -->
              <div class="relative pt-2 flex-1 flex flex-col">
                <!-- Image -->
                <div class="aspect-square mb-4 relative">
                  <img 
                    :src="getSkinImagePath(item)"
                    :alt="`${item.weapon} | ${item.name}`"
                    class="w-full h-full object-contain"
                  >
                  <!-- Stack Count Badge -->
                  <span v-if="item.isStack" 
                        class="absolute bottom-2 right-2 bg-black/80 text-white px-2 py-1 rounded text-sm">
                    x{{ item.quantity }}
                  </span>
                  <!-- Expand/Collapse Indicator -->
                  <span v-if="item.isStack || item.isExpanded" 
                        class="absolute top-2 right-2 text-xs text-white/70 bg-black/50 px-2 py-1 rounded">
                    {{ item.isExpanded ? 'Click to collapse' : 'Click to expand' }}
                  </span>
                </div>
                
                <!-- Info -->
                <div class="flex flex-col flex-1">
                  <h3 class="font-display text-sm text-white line-clamp-2 min-h-[2.5rem]" :class="{ 'text-yellow': item.stattrak }">
                    {{ item.stattrak ? 'StatTrak™ ' : '' }}{{ item.is_sticker ? item.name : `${item.weapon} | ${item.name}` }}
                  </h3>
                  <div class="flex items-center gap-2 text-xs text-white/50 mt-1">
                    <span>{{ item.wear }}</span>
                    <span v-if="item.wear">•</span>
                    <span v-if="item.float_value !== undefined" class="font-mono whitespace-nowrap" :class="getFloatClass(item.float_value)">
                      {{ item.float_value.toFixed(8) }}
                    </span>
                  </div>
                  <div class="flex items-center justify-between mt-2">
                    <span class="text-yellow font-medium">${{ formatPrice(item.displayPrice || item.price) }}</span>
                    <button 
                      class="px-3 py-1 bg-red-500/10 hover:bg-red-500/20 text-red-500 text-sm rounded transition-all duration-200"
                      @click.stop="sellItem(item)"
                    >
                      {{ item.isStack ? 'Sell All' : 'Sell' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Cases Section -->
      <div v-else-if="currentCategory === 'cases'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
        <div v-for="item in cases" :key="item.type" 
             class="bg-gray-dark rounded-xl p-4 flex flex-col items-center">
          <img :src="getCaseImagePath(item)" :alt="item.name" class="w-48 h-48 object-contain mb-4">
          <h3 class="text-lg font-display text-white mb-2">{{ item.name }}</h3>
          <p class="text-white/70 mb-4">Quantity: {{ item.quantity }}</p>
          <div class="flex flex-wrap gap-2 justify-center">
            <button 
              v-for="count in getAvailableOpenCounts(item)" 
              :key="count"
              class="case-open-btn"
              :class="{
                'primary': count === 1,
                'opacity-50 cursor-not-allowed': count > item.quantity
              }"
              :disabled="count > item.quantity"
              @click="() => {
                console.log('Opening case:', item.type, 'count:', count);
                openCase(item.type, count);
              }"
            >
              <span class="relative z-10">Open {{ count }}x</span>
            </button>
          </div>
        </div>
        <div v-if="cases.length === 0" class="col-span-full text-center py-12">
          <h2 class="text-2xl font-display text-white mb-4">No Cases Found</h2>
          <p class="text-white/70 mb-6">You don't have any cases in your inventory.</p>
          <a href="/shop" class="inline-block px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200">
            Buy Cases
          </a>
        </div>
      </div>

      <!-- Sticker Capsules Section -->
      <div v-else-if="currentCategory === 'capsules'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
        <div v-for="item in capsules" :key="item.type" 
             class="bg-gray-dark rounded-xl p-4 flex flex-col items-center">
          <img :src="getCapsuleImagePath(item)" :alt="item.name" class="w-48 h-48 object-contain mb-4">
          <h3 class="text-lg font-display text-white mb-2">{{ item.name }}</h3>
          <p class="text-white/70 mb-4">Quantity: {{ item.quantity }}</p>
          <div class="flex flex-wrap gap-2 justify-center">
            <button 
              v-for="count in getAvailableOpenCounts(item)" 
              :key="count"
              class="case-open-btn"
              :class="{
                'primary': count === 1,
                'opacity-50 cursor-not-allowed': count > item.quantity
              }"
              :disabled="count > item.quantity"
              @click="() => {
                console.log('Opening capsule:', item.type, 'count:', count);
                openCapsule(item.type, count);
              }"
            >
              <span class="relative z-10">Open {{ count }}x</span>
            </button>
          </div>
        </div>
        <div v-if="capsules.length === 0" class="col-span-full text-center py-12">
          <h2 class="text-2xl font-display text-white mb-4">No Sticker Capsules Found</h2>
          <p class="text-white/70 mb-6">You don't have any sticker capsules in your inventory.</p>
          <a href="/shop" class="inline-block px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200">
            Buy Sticker Capsules
          </a>
        </div>
      </div>
    </div>

    <!-- Sell All Modal -->
    <div 
      v-if="showSellAllModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      @click.self="showSellAllModal = false"
    >
      <div class="bg-gray-dark rounded-xl p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-display text-white mb-4">Confirm Sell All</h3>
        <p class="text-white/70 mb-6">
          Are you sure you want to sell all skins for <span class="text-yellow">${{ totalValue.toFixed(2) }}</span>?
        </p>
        <div class="flex gap-3">
          <button 
            class="flex-1 px-4 py-2 bg-red-500 text-white rounded-lg transition-all duration-200 hover:bg-red-600"
            @click="sellAll"
          >
            Confirm
          </button>
          <button 
            class="flex-1 px-4 py-2 bg-gray-darker text-white rounded-lg transition-all duration-200 hover:bg-gray-dark/70"
            @click="showSellAllModal = false"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Case Opening Overlay -->
    <div 
      v-if="showCaseOpeningOverlay"
      class="fixed inset-0 bg-black/90 backdrop-blur-sm flex items-center justify-center z-50"
    >
      <div class="flex flex-col gap-2 w-full max-w-4xl p-4">
        <div v-for="(container, index) in spinnerContainers" :key="index" 
             class="spinner-container"
             :class="{ 'hidden': index >= spinCount }"
             style="margin-bottom: 2px">
          <div :id="`spinner-${index}`" class="spinner">
            <div v-for="(item, itemIndex) in container.items" :key="itemIndex"
                 class="spinner-item" 
                 :class="[
                   `rarity-${item.rarity}`,
                   { 'winning': itemIndex === container.winningPosition }
                 ]">
              <div class="spinner-item-image">
                <img :src="getSpinnerItemImage(item)" :alt="item.name">
              </div>
              <template v-if="item.rarity === 'GOLD' || item.rarity === 'CONTRABAND'">
                <div class="item-name rare">★</div>
                <div class="item-skin rare">Rare Special Item</div>
              </template>
              <template v-else>
                <div class="item-name" :class="{ 'stattrak': item.stattrak }">
                  {{ item.stattrak ? 'StatTrak™ ' : '' }}{{ item.weapon }}
                </div>
                <div class="item-skin">{{ item.name }}</div>
              </template>
            </div>
          </div>
          <div class="absolute top-0 left-1/2 h-full w-1 bg-yellow/50 -translate-x-1/2 pointer-events-none"></div>
        </div>
      </div>
    </div>

    <!-- Showcase Overlay -->
    <div 
      v-if="showShowcaseOverlay"
      class="fixed inset-0 bg-black/90 backdrop-blur-sm flex items-center justify-center z-50"
    >
      <div class="showcase-container" :data-items="wonItems.length">
        <div class="grid gap-4"
             :class="{
               'grid-cols-1': wonItems.length === 1,
               'grid-cols-2': wonItems.length === 2,
               'grid-cols-3': wonItems.length === 3,
               'grid-cols-2 lg:grid-cols-4': wonItems.length === 4,
               'grid-cols-2 md:grid-cols-3 2xl:grid-cols-5': wonItems.length === 5
             }">
          <div v-for="(item, index) in wonItems" :key="index"
               class="showcase-item bg-gray-darker/50 rounded-xl p-4 text-center transform transition-all duration-200 hover:-translate-y-1 w-full"
               :class="[
                 `rarity-${item.rarity}`,
                 { 'hidden': index >= spinCount }
               ]">
            <img :src="getSkinImagePath(item)" :alt="item.name" class="mx-auto mb-4 max-h-48 w-auto">
            <div class="item-name text-lg" :class="{ 'stattrak': item.stattrak }">
              {{ item.stattrak ? 'StatTrak™ ' : '' }}{{ item.weapon }} | {{ item.name }}
            </div>
            <div class="text-white/70">{{ item.wear }} • {{ item.rarity }}</div>
            <div class="text-yellow text-xl mt-2">${{ item.price.toFixed(2) }}</div>
          </div>
        </div>
        <div class="flex justify-center gap-4 mt-6">
          <button @click="closeShowcase" 
                  class="px-6 py-2 bg-gray-darker text-white rounded-lg hover:bg-gray-dark/70 transition-all duration-200">
            Continue
          </button>
          <button @click="sellShowcaseItems" 
                  class="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-all duration-200">
            {{ spinCount > 1 ? 'Sell All' : 'Sell' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useStore, CASE_MAPPING } from '../store'

export default {
  name: 'InventoryView',
  setup() {
    const store = useStore()
    const currentCategory = ref('skins')
    const currentSort = ref('rarity')
    const showSellAllModal = ref(false)
    const inventory = ref([])
    const isLoading = ref(true)
    const showCaseOpeningOverlay = ref(false)
    const showShowcaseOverlay = ref(false)
    const spinnerContainers = ref([])
    const spinCount = ref(1)
    const wonItems = ref([])
    const spinningSound = ref(null)
    const showcaseSound = ref(null)
    
    const categories = [
      { id: 'skins', name: 'Skins' },
      { id: 'cases', name: 'Cases' },
      { id: 'capsules', name: 'Sticker Capsules' }
    ]

    const sortOptions = [
      { id: 'rarity', name: 'Sort by Rarity' },
      { id: 'price', name: 'Sort by Price' }
    ]

    // Computed properties
    const skins = computed(() => {
      return inventory.value.filter(item => !item.is_case && !item.is_capsule)
    })

    const cases = computed(() => {
      return inventory.value.filter(item => item.is_case)
    })

    const capsules = computed(() => {
      return inventory.value.filter(item => item.is_capsule)
    })

    // Add this to the setup() function after other refs
    const expandedStacks = ref(new Set())

    const sortedSkins = computed(() => {
      const items = [...skins.value]
      const stackedItems = {}
      
      // Group items by their unique characteristics
      items.forEach(item => {
        if (item.is_sticker) {
          // Stickers are grouped by name and case type
          const stackKey = `sticker|${item.name}|${item.case_type}`
          if (!stackedItems[stackKey]) {
            stackedItems[stackKey] = {
              items: [],
              displayItem: { ...item }
            }
          }
          stackedItems[stackKey].items.push(item)
        } else {
          // Weapon skins are grouped by weapon, name, wear, and stattrak
          const stackKey = `${item.weapon}|${item.name}|${item.wear}|${item.stattrak}`
          if (!stackedItems[stackKey]) {
            stackedItems[stackKey] = {
              items: [],
              displayItem: { ...item }
            }
          }
          stackedItems[stackKey].items.push(item)
        }
      })

      // Convert to final format, expanding stacks if needed
      let result = []
      Object.entries(stackedItems).forEach(([key, stack]) => {
        if (stack.items.length > 1) {
          if (expandedStacks.value.has(key)) {
            // If stack is expanded, add all items individually
            result.push(...stack.items.map(item => ({
              ...item,
              stackKey: key,
              isExpanded: true
            })))
          } else {
            // If stack is collapsed, add as a stack
            const stackPrice = stack.items.reduce((total, item) => total + item.price, 0);
            result.push({
              ...stack.displayItem,
              isStack: true,
              stackKey: key,
              stackedItems: stack.items,
              quantity: stack.items.length,
              price: stackPrice
            })
          }
        } else {
          // Single items are added as is
          result.push({
            ...stack.items[0],
            stackKey: key
          })
        }
      })

      // Sort based on current sort type
      const rarityOrder = {
        'CONTRABAND': 6,
        'GOLD': 5,
        'RED': 4,
        'PINK': 3,
        'PURPLE': 2,
        'BLUE': 1
      }

      if (currentSort.value === 'rarity') {
        return result.sort((a, b) => rarityOrder[b.rarity] - rarityOrder[a.rarity])
      } else if (currentSort.value === 'price') {
        return result.sort((a, b) => b.price - a.price)
      }
      return result
    })

    const totalValue = computed(() => {
      // Calculate total value using the backend-provided prices
      return skins.value.reduce((total, item) => total + item.price, 0);
    });

    // Update the total value display
    watch(totalValue, (newValue) => {
      const sellAllBtn = document.getElementById('sell-all-btn');
      if (sellAllBtn) {
        sellAllBtn.textContent = `Sell All: $${newValue.toFixed(2)}`;
        sellAllBtn.dataset.totalValue = newValue.toString();
      }
    });

    // Methods
    async function fetchInventory() {
      try {
        isLoading.value = true
        const response = await fetch('/get_inventory')
        const data = await response.json()
        
        if (data.error) {
          console.error('Error:', data.error)
          return
        }

        inventory.value = data.inventory
        store.updateUserData({
          balance: data.balance,
          exp: data.exp,
          rank: data.rank,
          upgrades: data.upgrades
        })
      } catch (error) {
        console.error('Error fetching inventory:', error)
      } finally {
        isLoading.value = false
      }
    }

    function sortItems(sortType) {
      currentSort.value = sortType
    }

    function getFloatClass(float) {
      const value = parseFloat(float)
      if (value < 0.001) return 'text-yellow font-bold'
      if (value < 0.01) return 'text-pink-500 font-bold'
      if (value < 0.07) return 'text-purple-500'
      return 'text-white/50'
    }

    function getRarityColor(rarity) {
      const colors = {
        'CONTRABAND': 'bg-gradient-to-r from-amber-500 to-amber-600',
        'GOLD': 'bg-gradient-to-r from-[#FFD700] to-[#FFA500]',
        'RED': 'bg-gradient-to-r from-red-500 to-red-600',
        'PINK': 'bg-gradient-to-r from-pink-500 to-pink-600',
        'PURPLE': 'bg-gradient-to-r from-purple-500 to-purple-600',
        'BLUE': 'bg-gradient-to-r from-blue-500 to-blue-600'
      }
      return colors[rarity] || 'bg-gradient-to-r from-gray-500 to-gray-600'
    }

    function getAvailableOpenCounts(item) {
      // Get the multi_open value from store, default to 1 if not available
      const maxMultiOpen = store.state.upgrades?.multi_open || 1
      console.log('Multi-open level:', maxMultiOpen) // Debug log
      // Get the maximum number of cases we can open based on quantity and multi_open level
      const maxCount = Math.min(item.quantity, maxMultiOpen)
      // Create an array of numbers from 1 to maxCount
      const counts = Array.from({ length: maxCount }, (_, i) => i + 1)
      console.log('Available counts:', counts) // Debug log
      return counts
    }

    async function sellItem(item) {
      try {
        const response = await fetch('/sell/item', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            item: item,
            quantity: item.isStack ? item.quantity : 1
          })
        })

        const data = await response.json()
        
        if (data.error) {
          alert(data.error)
          return
        }

        // Update store with new data
        store.updateUserData({
          balance: data.balance,
          exp: data.exp,
          rank: data.rank
        })

        // Refresh inventory
        await fetchInventory()

        // Handle achievement if present
        if (data.achievement) {
          store.showAchievementPopup(data.achievement)
        }

        // Handle level up
        if (data.levelUp) {
          store.showLevelUpAnimation()
        }
      } catch (error) {
        console.error('Error selling item:', error)
        alert('Failed to sell item')
      }
    }

    async function sellAll() {
      try {
        const response = await fetch('/sell/all', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        })

        const data = await response.json()
        
        if (data.error) {
          alert(data.error)
          return
        }

        // Update store with new data
        store.updateUserData({
          balance: data.balance,
          exp: data.exp,
          rank: data.rank
        })

        // Refresh inventory
        await fetchInventory()

        // Handle achievement if present
        if (data.achievement) {
          store.showAchievementPopup(data.achievement)
        }

        // Handle level up
        if (data.levelUp) {
          store.showLevelUpAnimation()
        }

        showSellAllModal.value = false
      } catch (error) {
        console.error('Error selling all items:', error)
        alert('Failed to sell all items')
      }
    }

    // Add new methods for case opening
    async function openCase(caseType, count = 1) {
      console.log('openCase called with:', caseType, count) // Debug log
      try {
        spinCount.value = count
        showCaseOpeningOverlay.value = true
        spinnerContainers.value = []
        wonItems.value = []

        // Load case contents first
        console.log('Loading case contents...') // Debug log
        const caseContents = await loadCaseContents(caseType)
        if (!caseContents) {
          console.error('Failed to load case contents') // Debug log
          alert('Failed to load case contents')
          return
        }
        console.log('Case contents loaded:', caseContents) // Debug log

        // Start spinning sound
        if (spinningSound.value) {
          spinningSound.value.currentTime = 0
          spinningSound.value.volume = 0.5
          try {
            await spinningSound.value.play()
          } catch (error) {
            console.error('Failed to play spinning sound:', error)
          }
        }

        // Call backend to get items
        console.log('Calling backend to open case...') // Debug log
        const response = await fetch(`/open/${caseType}?count=${count}`)
        const data = await response.json()
        
        if (data.error) {
          console.error('Backend error:', data.error) // Debug log
          alert(data.error)
          return
        }
        console.log('Received items from backend:', data) // Debug log

        // Generate random items for each spinner
        for (let i = 0; i < count; i++) {
          const { items, winningPosition } = generateRandomItems(data.items[i], caseContents)
          spinnerContainers.value.push({ items, winningPosition })
        }
        console.log('Generated spinner items:', spinnerContainers.value) // Debug log

        // Store won items for showcase
        wonItems.value = data.items

        // Wait for Vue to update the DOM
        await new Promise(resolve => setTimeout(resolve, 100))

        // Calculate final positions for all spinners
        const spinnerPositions = spinnerContainers.value.map((container, index) => {
          const spinnerEl = document.getElementById(`spinner-${index}`)
          if (spinnerEl) {
            const itemWidth = 200 // Width of each item
            const spacing = 4 // Gap between items
            const containerWidth = spinnerEl.parentElement.offsetWidth
            const centerOffset = (containerWidth / 2) - (itemWidth / 2)
            const randomOffset = Math.floor(Math.random() * itemWidth) - (itemWidth / 2)
            return (container.winningPosition * (itemWidth + spacing)) - centerOffset + randomOffset
          }
          return 0
        })

        // Reset all spinners to starting position
        spinnerContainers.value.forEach((_, index) => {
          const spinnerEl = document.getElementById(`spinner-${index}`)
          if (spinnerEl) {
            spinnerEl.style.transition = 'none'
            spinnerEl.style.transform = 'translateX(0)'
            // Force reflow
            spinnerEl.offsetHeight
          }
        })

        // Start synchronized spinning animation
        requestAnimationFrame(() => {
          spinnerContainers.value.forEach((_, index) => {
            const spinnerEl = document.getElementById(`spinner-${index}`)
            if (spinnerEl) {
              spinnerEl.style.transition = 'transform 6s cubic-bezier(0.12, 0.39, 0.01, 1)'
              spinnerEl.style.transform = `translateX(-${spinnerPositions[index]}px)`
            }
          })
        })

        // Wait for animation to complete
        await new Promise(resolve => setTimeout(resolve, 6800))

        // Stop spinning sound
        let soundFadeInterval
        if (spinningSound.value) {
          soundFadeInterval = setInterval(() => {
            if (spinningSound.value && spinningSound.value.volume > 0.1) {
              spinningSound.value.volume -= 0.1
            } else {
              if (spinningSound.value) {
                spinningSound.value.pause()
              }
              clearInterval(soundFadeInterval)
            }
          }, 100)
        }

        showCaseOpeningOverlay.value = false
        showShowcase()

        // Update store with new data
        store.updateUserData({
          balance: data.balance,
          exp: data.exp,
          rank: data.rank
        })

        // Handle achievement if present
        if (data.achievement) {
          store.showAchievementPopup(data.achievement)
        }

        // Handle level up
        if (data.levelUp) {
          store.showLevelUpAnimation()
        }

        // Update case quantity
        await fetchInventory()

      } catch (error) {
        console.error('Error in openCase:', error)
        alert('Failed to open case')
      }
    }

    async function loadCaseContents(caseType) {
      try {
        const response = await fetch(`/api/data/case_contents/${caseType}`)
        const data = await response.json()
        
        if (data.error) {
          console.error('Error loading case contents:', data.error)
          return null
        }
        return data
      } catch (error) {
        console.error('Error loading case contents:', error)
        return null
      }
    }

    function generateRandomItems(actualItem, caseContents) {
      const items = []
      const totalItems = 100
      const winningPosition = 85 // Fixed position for the winning item

      // Define rarity weights
      const weights = {
        'BLUE': 74.66,
        'PURPLE': 20.08,
        'PINK': 4.10,
        'RED': 0.90,
        'GOLD': 0.26,
        'CONTRABAND': 0
      }

      // Create weighted item pools
      const itemPools = {
        'BLUE': caseContents.skins.blue || [],
        'PURPLE': caseContents.skins.purple || [],
        'PINK': caseContents.skins.pink || [],
        'RED': caseContents.skins.red || [],
        'GOLD': caseContents.skins.gold || [],
        'CONTRABAND': caseContents.skins.contraband || []
      }

      // Generate random items
      for (let i = 0; i < totalItems; i++) {
        if (i === winningPosition) {
          items.push(actualItem)
        } else {
          // Pick a random rarity based on weights
          const random = Math.random() * 100
          let cumulativeWeight = 0
          let selectedRarity = 'BLUE'
          
          for (const [rarity, weight] of Object.entries(weights)) {
            cumulativeWeight += weight
            if (random <= cumulativeWeight) {
              selectedRarity = rarity
              break
            }
          }

          // Pick a random item from the selected rarity pool
          const pool = itemPools[selectedRarity]
          if (pool.length > 0) {
            const randomItem = pool[Math.floor(Math.random() * pool.length)]
            items.push({
              ...randomItem,
              rarity: selectedRarity, // Explicitly set the rarity
              wear: ['FN', 'MW', 'FT', 'WW', 'BS'][Math.floor(Math.random() * 5)],
              stattrak: Math.random() < 0.1,
              case_type: actualItem.case_type
            })
          }
        }
      }

      return { items, winningPosition }
    }

    function showShowcase() {
      showShowcaseOverlay.value = true
      console.log('Showcase sound element:', showcaseSound.value) // Debug log
      if (showcaseSound.value) {
        console.log('Attempting to play showcase sound') // Debug log
        showcaseSound.value.currentTime = 0
        showcaseSound.value.volume = 0.5
        try {
          const playPromise = showcaseSound.value.play()
          playPromise.then(() => {
            console.log('Showcase sound started playing successfully') // Debug log
          }).catch(error => {
            console.error('Error playing showcase sound:', error) // Detailed error logging
          })
        } catch (error) {
          console.error('Failed to play showcase sound:', error)
        }
      } else {
        console.error('Showcase sound element not found') // Debug log
      }
    }

    async function closeShowcase() {
      if (showcaseSound.value) {
        // Fade out showcase sound
        let soundFadeInterval = setInterval(() => {
          if (showcaseSound.value && showcaseSound.value.volume > 0.1) {
            showcaseSound.value.volume -= 0.1
          } else {
            if (showcaseSound.value) {
              showcaseSound.value.pause()
            }
            clearInterval(soundFadeInterval)
          }
        }, 50)
      }
      showShowcaseOverlay.value = false
    }

    async function sellShowcaseItems() {
      try {
        const response = await fetch('/sell/last', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            count: spinCount.value
          })
        })

        const data = await response.json()
        
        if (data.error) {
          alert(data.error)
          return
        }

        // Update store with new data
        store.updateUserData({
          balance: data.balance,
          exp: data.exp,
          rank: data.rank
        })

        // Close showcase
        closeShowcase()

        // Refresh inventory
        await fetchInventory()

      } catch (error) {
        console.error('Error selling showcase items:', error)
        alert('Failed to sell items')
      }
    }

    function getSpinnerItemImage(item) {
      if (item.is_sticker) {
        const capsuleType = item.case_type || item.capsule_type
        return `/sticker_skins/${capsuleType}/${item.image}`
      }
      // For gold/rare items, show the rare item image
      if (item.rarity === 'GOLD' || item.rarity === 'CONTRABAND') {
        return '/cases/rare_item.png'
      }
      
      if (!item.weapon || !item.name) {
        return '/skins/placeholder.png'
      }
      return getSkinImagePath(item)
    }

    function getSkinImagePath(item) {
      if (item.is_sticker) {
        // For stickers, use the case_type to determine the folder
        const capsuleType = item.case_type || item.capsule_type
        return `/sticker_skins/${capsuleType}/${item.image}`
      }
      const casePath = CASE_MAPPING[item.case_type] || 'weapon_case_1'
      return `/skins/${casePath}/${item.image || 'placeholder.png'}`
    }

    function getCaseImagePath(item) {
      const caseType = item.type || item.case_type
      return `/cases/${CASE_MAPPING[caseType] || caseType}.png`
    }

    function getCapsuleImagePath(item) {
      const capsuleType = item.type || item.capsule_type
      return `/stickers/${capsuleType}.png`
    }

    async function openCapsule(capsuleType, count = 1) {
      console.log('openCapsule called with:', capsuleType, count)
      try {
        spinCount.value = count
        showCaseOpeningOverlay.value = true
        spinnerContainers.value = []
        wonItems.value = []

        // Load capsule contents first
        console.log('Loading capsule contents...')
        const capsuleContents = await loadCapsuleContents(capsuleType)
        if (!capsuleContents) {
          console.error('Failed to load capsule contents')
          alert('Failed to load capsule contents')
          return
        }
        console.log('Capsule contents loaded:', capsuleContents)

        // Start spinning sound
        if (spinningSound.value) {
          spinningSound.value.currentTime = 0
          spinningSound.value.volume = 0.5
          try {
            await spinningSound.value.play()
          } catch (error) {
            console.error('Failed to play spinning sound:', error)
          }
        }

        // Call backend to get items
        console.log('Calling backend to open capsule...')
        const response = await fetch(`/open_capsule/${capsuleType}?count=${count}`)
        const data = await response.json()
        
        if (data.error) {
          console.error('Backend error:', data.error)
          alert(data.error)
          return
        }
        console.log('Received items from backend:', data)

        // Generate random items for each spinner
        for (let i = 0; i < count; i++) {
          const { items, winningPosition } = generateRandomStickerItems(data.items[i], capsuleContents)
          spinnerContainers.value.push({ items, winningPosition })
        }
        console.log('Generated spinner items:', spinnerContainers.value)

        // Store won items for showcase
        wonItems.value = data.items

        // Wait for Vue to update the DOM
        await new Promise(resolve => setTimeout(resolve, 100))

        // Calculate final positions for all spinners
        const spinnerPositions = spinnerContainers.value.map((container, index) => {
          const spinnerEl = document.getElementById(`spinner-${index}`)
          if (spinnerEl) {
            const itemWidth = 200
            const spacing = 4
            const containerWidth = spinnerEl.parentElement.offsetWidth
            const centerOffset = (containerWidth / 2) - (itemWidth / 2)
            const randomOffset = Math.floor(Math.random() * itemWidth) - (itemWidth / 2)
            return (container.winningPosition * (itemWidth + spacing)) - centerOffset + randomOffset
          }
          return 0
        })

        // Reset all spinners to starting position
        spinnerContainers.value.forEach((_, index) => {
          const spinnerEl = document.getElementById(`spinner-${index}`)
          if (spinnerEl) {
            spinnerEl.style.transition = 'none'
            spinnerEl.style.transform = 'translateX(0)'
            spinnerEl.offsetHeight
          }
        })

        // Start synchronized spinning animation
        requestAnimationFrame(() => {
          spinnerContainers.value.forEach((_, index) => {
            const spinnerEl = document.getElementById(`spinner-${index}`)
            if (spinnerEl) {
              spinnerEl.style.transition = 'transform 6s cubic-bezier(0.12, 0.39, 0.01, 1)'
              spinnerEl.style.transform = `translateX(-${spinnerPositions[index]}px)`
            }
          })
        })

        // Wait for animation to complete
        await new Promise(resolve => setTimeout(resolve, 6800))

        // Stop spinning sound
        let soundFadeInterval
        if (spinningSound.value) {
          soundFadeInterval = setInterval(() => {
            if (spinningSound.value && spinningSound.value.volume > 0.1) {
              spinningSound.value.volume -= 0.1
            } else {
              if (spinningSound.value) {
                spinningSound.value.pause()
              }
              clearInterval(soundFadeInterval)
            }
          }, 100)
        }

        showCaseOpeningOverlay.value = false
        showShowcase()

        // Update store with new data
        store.updateUserData({
          balance: data.balance,
          exp: data.exp,
          rank: data.rank
        })

        // Handle achievement if present
        if (data.achievement) {
          store.showAchievementPopup(data.achievement)
        }

        // Handle level up
        if (data.levelUp) {
          store.showLevelUpAnimation()
        }

        // Update capsule quantity
        await fetchInventory()

      } catch (error) {
        console.error('Error in openCapsule:', error)
        alert('Failed to open capsule')
      }
    }

    async function loadCapsuleContents(capsuleType) {
      try {
        const response = await fetch(`/api/data/sticker_capsule_contents/${capsuleType}`)
        const data = await response.json()
        
        if (data.error) {
          console.error('Error loading capsule contents:', data.error)
          return null
        }
        return data
      } catch (error) {
        console.error('Error loading capsule contents:', error)
        return null
      }
    }

    // Add new helper function for generating random sticker items
    function generateRandomStickerItems(actualItem, capsuleContents) {
      const items = []
      const totalItems = 100
      const winningPosition = 85 // Fixed position for the winning item

      // Define rarity weights
      const weights = {
        'BLUE': 80.0,
        'PURPLE': 16.0,
        'PINK': 3.841
      }

      // Create weighted item pools
      const itemPools = {}
      for (const [rarity, stickers] of Object.entries(capsuleContents.stickers)) {
        itemPools[rarity.toUpperCase()] = stickers || []
      }

      // Generate random items
      for (let i = 0; i < totalItems; i++) {
        if (i === winningPosition) {
          // Ensure actualItem has the correct rarity field
          items.push({
            ...actualItem,
            rarity: actualItem.rarity.toUpperCase()
          })
        } else {
          // Pick a random rarity based on weights
          const random = Math.random() * 100
          let cumulativeWeight = 0
          let selectedRarity = 'BLUE'
          
          for (const [rarity, weight] of Object.entries(weights)) {
            cumulativeWeight += weight
            if (random <= cumulativeWeight && itemPools[rarity] && itemPools[rarity].length > 0) {
              selectedRarity = rarity
              break
            }
          }

          // Pick a random item from the selected rarity pool
          const pool = itemPools[selectedRarity]
          if (pool && pool.length > 0) {
            const randomItem = pool[Math.floor(Math.random() * pool.length)]
            items.push({
              ...randomItem,
              rarity: selectedRarity,
              case_type: actualItem.case_type,
              is_sticker: true
            })
          }
        }
      }

      return { items, winningPosition }
    }

    // Add this new method in setup()
    function toggleStack(stackKey) {
      if (expandedStacks.value.has(stackKey)) {
        expandedStacks.value.delete(stackKey)
      } else {
        expandedStacks.value.add(stackKey)
      }
    }

    // Add this new method in setup()
    function formatPrice(price) {
      return (price || 0).toFixed(2)
    }

    // Lifecycle hooks
    onMounted(async () => {
      await fetchInventory()
    })

    return {
      currentCategory,
      currentSort,
      showSellAllModal,
      categories,
      sortOptions,
      inventory,
      isLoading,
      skins,
      cases,
      sortedSkins,
      totalValue,
      sortItems,
      getFloatClass,
      getRarityColor,
      getAvailableOpenCounts,
      sellItem,
      sellAll,
      openCase,
      getSkinImagePath,
      getCaseImagePath,
      showCaseOpeningOverlay,
      showShowcaseOverlay,
      spinnerContainers,
      spinCount,
      wonItems,
      spinningSound,
      showcaseSound,
      closeShowcase,
      sellShowcaseItems,
      getSpinnerItemImage,
      toggleStack,
      formatPrice,
      capsules,
      getCapsuleImagePath,
      openCapsule
    }
  }
}
</script>

<style scoped>
</style> 