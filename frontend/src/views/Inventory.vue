<template>
  <div class="min-h-screen bg-gray-darker">
    <!-- Inventory Header -->
    <div class="relative py-12 mb-8">
      <div class="absolute inset-0 bg-gradient-to-b from-yellow/5 to-transparent"></div>
      <div class="relative max-w-7xl mx-auto px-4">
        <h1 class="text-4xl font-display font-bold text-white mb-2">Inventory</h1>
        <p class="text-white/70">Manage your skins, cases, and items</p>
      </div>
    </div>

    <!-- Inventory Content -->
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
            class="px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-500 rounded-lg transition-all duration-200 font-medium"
            @click="showSellAllModal = true"
          >
            Sell All: ${{ totalValue.toFixed(2) }}
          </button>
        </div>

        <!-- Skins Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <div v-for="item in sortedSkins" :key="item.id" class="group">
            <div class="relative bg-gray-dark/50 rounded-xl p-4 transition-all duration-300 hover:bg-gray-dark/70">
              <!-- Rarity Indicator -->
              <div class="absolute inset-x-0 top-0 h-1 rounded-t-xl" :class="item.rarityColor"></div>
              
              <!-- Content -->
              <div class="relative pt-2">
                <!-- Image -->
                <div class="aspect-square mb-4">
                  <img :src="item.image" :alt="item.name" class="w-full h-full object-contain">
                </div>
                
                <!-- Info -->
                <div class="space-y-2">
                  <h3 class="font-display text-sm text-white truncate" :class="{ 'text-yellow': item.statTrak }">
                    {{ item.statTrak ? 'StatTrak™ ' : '' }}{{ item.name }}
                  </h3>
                  <div class="flex items-center gap-2 text-xs text-white/50">
                    <span>{{ item.wear }}</span>
                    <span>•</span>
                    <span class="font-mono" :class="getFloatClass(item.float)">
                      Float: {{ item.float }}
                    </span>
                  </div>
                  <div class="flex items-center justify-between pt-2">
                    <span class="text-yellow font-medium">${{ item.price.toFixed(2) }}</span>
                    <button 
                      class="px-3 py-1 bg-red-500/10 hover:bg-red-500/20 text-red-500 text-sm rounded transition-all duration-200"
                      @click="sellItem(item)"
                    >
                      Sell
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Cases Section -->
      <div v-if="currentCategory === 'cases'" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div v-for="item in cases" :key="item.id" class="group">
            <div class="relative bg-gray-dark/50 rounded-xl p-6 transition-all duration-300 hover:bg-gray-dark/70">
              <!-- Content -->
              <div class="flex gap-6">
                <!-- Image -->
                <div class="w-40 h-40 flex-shrink-0">
                  <img :src="item.image" :alt="item.name" class="w-full h-full object-contain">
                </div>
                
                <!-- Info -->
                <div class="flex-1 flex flex-col">
                  <h3 class="font-display text-lg text-white mb-2">{{ item.name }}</h3>
                  <p class="text-white/70 mb-4">Quantity: {{ item.quantity }}</p>
                  
                  <!-- Open Buttons -->
                  <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-auto">
                    <button 
                      v-for="count in getAvailableOpenCounts(item)"
                      :key="count"
                      class="px-3 py-1.5 bg-yellow/10 hover:bg-yellow/20 text-yellow text-sm rounded transition-all duration-200"
                      @click="openCase(item, count)"
                    >
                      Open {{ count }}x
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- No Cases Message -->
          <div v-if="cases.length === 0" class="col-span-full">
            <div class="bg-gray-dark/50 rounded-xl p-8 text-center">
              <h3 class="text-xl font-display text-white mb-4">No Cases Found</h3>
              <p class="text-white/70 mb-6">You don't have any cases in your inventory.</p>
              <router-link 
                to="/shop" 
                class="inline-block px-6 py-3 bg-yellow text-gray-darker rounded-lg font-medium transition-all duration-200 hover:bg-yellow/90"
              >
                Buy Cases
              </router-link>
            </div>
          </div>
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
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'InventoryView',
  setup() {
    const currentCategory = ref('skins')
    const currentSort = ref('rarity')
    const showSellAllModal = ref(false)
    
    const categories = [
      { id: 'skins', name: 'Skins' },
      { id: 'cases', name: 'Cases' }
    ]

    const sortOptions = [
      { id: 'rarity', name: 'Sort by Rarity' },
      { id: 'price', name: 'Sort by Price' }
    ]

    // Dummy data for demonstration
    const skins = ref([
      {
        id: 1,
        name: 'AK-47 | Asiimov',
        wear: 'Factory New',
        float: '0.00234567',
        price: 149.99,
        image: '/skins/ak47_asiimov.png',
        statTrak: true,
        rarityColor: 'bg-gradient-to-r from-pink-500 to-pink-600',
        rarity: 'COVERT'
      },
      {
        id: 2,
        name: 'M4A4 | Neo-Noir',
        wear: 'Minimal Wear',
        float: '0.08234567',
        price: 89.99,
        image: '/skins/m4a4_neo_noir.png',
        statTrak: false,
        rarityColor: 'bg-gradient-to-r from-purple-500 to-purple-600',
        rarity: 'CLASSIFIED'
      }
    ])

    const cases = ref([
      {
        id: 1,
        name: 'CS2 Case',
        quantity: 5,
        image: '/cases/cs2_case.png'
      },
      {
        id: 2,
        name: 'Revolution Case',
        quantity: 3,
        image: '/cases/revolution_case.png'
      }
    ])

    const sortedSkins = computed(() => {
      const items = [...skins.value]
      const rarityOrder = {
        'CONTRABAND': 6,
        'COVERT': 5,
        'CLASSIFIED': 4,
        'RESTRICTED': 3,
        'MIL-SPEC': 2,
        'CONSUMER': 1
      }

      if (currentSort.value === 'rarity') {
        return items.sort((a, b) => rarityOrder[b.rarity] - rarityOrder[a.rarity])
      } else if (currentSort.value === 'price') {
        return items.sort((a, b) => b.price - a.price)
      }
      return items
    })

    const totalValue = computed(() => {
      return skins.value.reduce((total, item) => total + item.price, 0)
    })

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

    function getAvailableOpenCounts(item) {
      const maxCount = Math.min(item.quantity, 5)
      return Array.from({ length: maxCount }, (_, i) => i + 1)
    }

    function sellItem(item) {
      // Implement sell functionality
      console.log('Selling item:', item)
    }

    function sellAll() {
      // Implement sell all functionality
      console.log('Selling all items')
      showSellAllModal.value = false
    }

    function openCase(item, count) {
      // Implement case opening functionality
      console.log('Opening case:', item, 'count:', count)
    }

    return {
      currentCategory,
      currentSort,
      showSellAllModal,
      categories,
      sortOptions,
      skins,
      cases,
      sortedSkins,
      totalValue,
      sortItems,
      getFloatClass,
      getAvailableOpenCounts,
      sellItem,
      sellAll,
      openCase
    }
  }
}
</script> 