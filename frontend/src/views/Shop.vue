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
      <div v-if="currentCategory === 'cases'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <div v-for="item in cases" :key="item.id" class="group">
          <div class="relative bg-gray-dark/50 rounded-xl p-6 transition-all duration-300 hover:bg-gray-dark/70">
            <!-- Hover Glow Effect -->
            <div class="absolute inset-0 bg-gradient-to-r from-yellow/0 via-yellow/10 to-yellow/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl"></div>
            
            <!-- Content -->
            <div class="relative">
              <!-- Image -->
              <div class="aspect-square mb-4 p-4">
                <img :src="item.image" :alt="item.name" class="w-full h-full object-contain">
              </div>
              
              <!-- Info -->
              <div class="space-y-2">
                <h3 class="font-display text-white group-hover:text-yellow transition-colors duration-200">{{ item.name }}</h3>
                <div class="flex items-center justify-between">
                  <span class="text-yellow font-medium">${{ item.price.toFixed(2) }}</span>
                  <button class="px-4 py-1.5 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200">
                    Buy Now
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Featured Skins -->
      <div v-if="currentCategory === 'skins'" class="space-y-6">
        <!-- Featured Section -->
        <div class="bg-gray-dark/50 rounded-xl p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-display text-white">Featured Skins</h2>
            <div class="text-sm text-white/50">
              Refreshes in: <span class="text-yellow">59:59</span>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <div v-for="skin in featuredSkins" :key="skin.id" class="group">
              <div class="relative bg-gray-darker rounded-lg p-4 transition-all duration-300 hover:bg-gray-dark/70">
                <!-- Rarity Indicator -->
                <div class="absolute inset-x-0 top-0 h-1 rounded-t-lg" :class="skin.rarityColor"></div>
                
                <!-- Content -->
                <div class="relative pt-2">
                  <!-- Image -->
                  <div class="aspect-square mb-4">
                    <img :src="skin.image" :alt="skin.name" class="w-full h-full object-contain">
                  </div>
                  
                  <!-- Info -->
                  <div class="space-y-2">
                    <h3 class="font-display text-sm text-white truncate" :class="{ 'text-yellow': skin.statTrak }">
                      {{ skin.statTrak ? 'StatTrak™ ' : '' }}{{ skin.name }}
                    </h3>
                    <div class="flex items-center gap-2 text-xs text-white/50">
                      <span>{{ skin.wear }}</span>
                      <span>•</span>
                      <span>Float: {{ skin.float }}</span>
                    </div>
                    <div class="flex items-center justify-between pt-2">
                      <span class="text-yellow font-medium">${{ skin.price.toFixed(2) }}</span>
                      <button class="px-3 py-1 bg-yellow/10 hover:bg-yellow/20 text-yellow text-sm rounded transition-all duration-200">
                        Purchase
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Market Section -->
        <div class="bg-gray-dark/50 rounded-xl p-6">
          <h2 class="text-xl font-display text-white mb-6">Community Market</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <!-- Market items would go here -->
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'ShopView',
  setup() {
    const currentCategory = ref('cases')
    
    const categories = [
      { id: 'cases', name: 'Cases' },
      { id: 'skins', name: 'Skins' },
      { id: 'stickers', name: 'Sticker Capsules' },
      { id: 'collections', name: 'Collections' },
      { id: 'souvenir', name: 'Souvenir Packages' }
    ]

    // Dummy data for demonstration
    const cases = [
      {
        id: 1,
        name: 'CS2 Case',
        price: 2.49,
        image: '/cases/cs2_case.png'
      },
      {
        id: 2,
        name: 'Revolution Case',
        price: 1.99,
        image: '/cases/revolution_case.png'
      },
      {
        id: 3,
        name: 'Recoil Case',
        price: 2.99,
        image: '/cases/recoil_case.png'
      },
      // Add more cases as needed
    ]

    const featuredSkins = [
      {
        id: 1,
        name: 'AK-47 | Asiimov',
        wear: 'Factory New',
        float: '0.01234567',
        price: 149.99,
        image: '/skins/ak47_asiimov.png',
        statTrak: true,
        rarityColor: 'bg-gradient-to-r from-pink-500 to-pink-600'
      },
      {
        id: 2,
        name: 'M4A4 | Neo-Noir',
        wear: 'Minimal Wear',
        float: '0.08234567',
        price: 89.99,
        image: '/skins/m4a4_neo_noir.png',
        statTrak: false,
        rarityColor: 'bg-gradient-to-r from-purple-500 to-purple-600'
      },
      // Add more skins as needed
    ]

    return {
      currentCategory,
      categories,
      cases,
      featuredSkins
    }
  }
}
</script> 