<template>
  <div class="min-h-screen bg-gray-darker">
    <!-- Header -->
    <div class="relative py-12 mb-8">
      <div class="absolute inset-0 bg-gradient-to-b from-yellow/5 to-transparent"></div>
      <div class="relative max-w-7xl mx-auto px-4">
        <h1 class="text-4xl font-display font-bold text-white mb-2">Upgrades</h1>
        <p class="text-white/70">Enhance your clicking power</p>
      </div>
    </div>

    <!-- Upgrades Grid -->
    <div class="max-w-7xl mx-auto px-4 pb-12">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <!-- Base Click Value -->
        <div 
          class="bg-gray-dark/50 rounded-xl p-6 relative group hover:bg-gray-dark/70 transition-all duration-300"
          :class="{ 'border-2 border-yellow shadow-[0_0_15px_rgba(255,215,0,0.2)]': upgrades.click_value >= maxLevels.click_value }"
        >
          <div v-if="upgrades.click_value >= maxLevels.click_value" 
               class="absolute -top-3 -right-3 bg-gradient-to-r from-yellow to-yellow/80 text-gray-darker px-3 py-1 rounded-full text-sm font-bold transform rotate-12">
            Max Level
          </div>
          <h3 class="text-lg font-display text-white mb-4">Base Click Value</h3>
          <div class="space-y-2 mb-6">
            <p class="text-yellow">Level: {{ upgrades.click_value }}</p>
            <p class="text-white/70">Current: ${{ (0.01 * (1.5 ** (upgrades.click_value - 1))).toFixed(3) }} per click</p>
            <p v-if="upgrades.click_value < maxLevels.click_value" class="text-white/50">
              Cost: ${{ (100 * (2 ** (upgrades.click_value - 1))).toFixed(2) }}
            </p>
          </div>
          <button 
            v-if="upgrades.click_value < maxLevels.click_value"
            @click="purchaseUpgrade('click_value')"
            class="w-full px-4 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200"
            :class="{ 'opacity-50 cursor-not-allowed': !canAfford('click_value') }"
          >
            {{ canAfford('click_value') ? 'Upgrade' : 'Too Expensive' }}
          </button>
        </div>

        <!-- Maximum Multiplier -->
        <div 
          class="bg-gray-dark/50 rounded-xl p-6 relative group hover:bg-gray-dark/70 transition-all duration-300"
          :class="{ 'border-2 border-yellow shadow-[0_0_15px_rgba(255,215,0,0.2)]': upgrades.max_multiplier >= maxLevels.max_multiplier }"
        >
          <div v-if="upgrades.max_multiplier >= maxLevels.max_multiplier" 
               class="absolute -top-3 -right-3 bg-gradient-to-r from-yellow to-yellow/80 text-gray-darker px-3 py-1 rounded-full text-sm font-bold transform rotate-12">
            Max Level
          </div>
          <h3 class="text-lg font-display text-white mb-4">Maximum Multiplier</h3>
          <div class="space-y-2 mb-6">
            <p class="text-yellow">Level: {{ upgrades.max_multiplier }}</p>
            <p class="text-white/70">Current: {{ (1.5 + (0.5 * (upgrades.max_multiplier - 1))).toFixed(1) }}x max</p>
            <p v-if="upgrades.max_multiplier < maxLevels.max_multiplier" class="text-white/50">
              Cost: ${{ (250 * (2 ** (upgrades.max_multiplier - 1))).toFixed(2) }}
            </p>
          </div>
          <button 
            v-if="upgrades.max_multiplier < maxLevels.max_multiplier"
            @click="purchaseUpgrade('max_multiplier')"
            class="w-full px-4 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200"
            :class="{ 'opacity-50 cursor-not-allowed': !canAfford('max_multiplier') }"
          >
            {{ canAfford('max_multiplier') ? 'Upgrade' : 'Too Expensive' }}
          </button>
        </div>

        <!-- Auto Clicker -->
        <div 
          class="bg-gray-dark/50 rounded-xl p-6 relative group hover:bg-gray-dark/70 transition-all duration-300"
          :class="[
            { 'border-2 border-yellow shadow-[0_0_15px_rgba(255,215,0,0.2)]': upgrades.auto_clicker >= maxLevels.auto_clicker },
            { 'opacity-75': upgrades.auto_clicker === 0 }
          ]"
        >
          <div v-if="upgrades.auto_clicker >= maxLevels.auto_clicker" 
               class="absolute -top-3 -right-3 bg-gradient-to-r from-yellow to-yellow/80 text-gray-darker px-3 py-1 rounded-full text-sm font-bold transform rotate-12">
            Max Level
          </div>
          <h3 class="text-lg font-display text-white mb-4">Auto Clicker</h3>
          <div class="space-y-2 mb-6">
            <p class="text-yellow">Level: {{ upgrades.auto_clicker }}</p>
            <p class="text-white/70">
              <span v-if="upgrades.auto_clicker === 0">Not Unlocked</span>
              <span v-else-if="upgrades.auto_clicker <= 9">1 click every {{ 11 - upgrades.auto_clicker }} seconds</span>
              <span v-else>{{ upgrades.auto_clicker - 8 }} clicks per second</span>
            </p>
            <p v-if="upgrades.auto_clicker < maxLevels.auto_clicker" class="text-white/50">
              Cost: ${{ (upgrades.auto_clicker === 0 ? 500 : 50 * (1.8 ** (upgrades.auto_clicker - 1))).toFixed(2) }}
            </p>
          </div>
          <button 
            v-if="upgrades.auto_clicker < maxLevels.auto_clicker"
            @click="purchaseUpgrade('auto_clicker')"
            class="w-full px-4 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200"
            :class="{ 'opacity-50 cursor-not-allowed': !canAfford('auto_clicker') }"
          >
            {{ upgrades.auto_clicker === 0 ? 'Unlock Auto Clicker' : canAfford('auto_clicker') ? 'Upgrade' : 'Too Expensive' }}
          </button>
        </div>

        <!-- Combo Speed -->
        <div 
          class="bg-gray-dark/50 rounded-xl p-6 relative group hover:bg-gray-dark/70 transition-all duration-300"
          :class="{ 'border-2 border-yellow shadow-[0_0_15px_rgba(255,215,0,0.2)]': upgrades.combo_speed >= maxLevels.combo_speed }"
        >
          <div v-if="upgrades.combo_speed >= maxLevels.combo_speed" 
               class="absolute -top-3 -right-3 bg-gradient-to-r from-yellow to-yellow/80 text-gray-darker px-3 py-1 rounded-full text-sm font-bold transform rotate-12">
            Max Level
          </div>
          <h3 class="text-lg font-display text-white mb-4">Combo Speed</h3>
          <div class="space-y-2 mb-6">
            <p class="text-yellow">Level: {{ upgrades.combo_speed }}</p>
            <p class="text-white/70">Current: Multiplier increases every {{ 21 - upgrades.combo_speed }} clicks</p>
            <p v-if="upgrades.combo_speed < maxLevels.combo_speed" class="text-white/50">
              Cost: ${{ (150 * (2 ** (upgrades.combo_speed - 1))).toFixed(2) }}
            </p>
          </div>
          <button 
            v-if="upgrades.combo_speed < maxLevels.combo_speed"
            @click="purchaseUpgrade('combo_speed')"
            class="w-full px-4 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200"
            :class="{ 'opacity-50 cursor-not-allowed': !canAfford('combo_speed') }"
          >
            {{ canAfford('combo_speed') ? 'Upgrade' : 'Too Expensive' }}
          </button>
        </div>

        <!-- Critical Strike -->
        <div 
          class="bg-gray-dark/50 rounded-xl p-6 relative group hover:bg-gray-dark/70 transition-all duration-300"
          :class="[
            { 'border-2 border-yellow shadow-[0_0_15px_rgba(255,215,0,0.2)]': upgrades.critical_strike >= maxLevels.critical_strike },
            { 'opacity-75': upgrades.critical_strike === 0 }
          ]"
        >
          <div v-if="upgrades.critical_strike >= maxLevels.critical_strike" 
               class="absolute -top-3 -right-3 bg-gradient-to-r from-yellow to-yellow/80 text-gray-darker px-3 py-1 rounded-full text-sm font-bold transform rotate-12">
            Max Level
          </div>
          <h3 class="text-lg font-display text-white mb-4">Critical Strike</h3>
          <div class="space-y-2 mb-6">
            <p class="text-yellow">Level: {{ upgrades.critical_strike }}</p>
            <p class="text-white/70">
              <span v-if="upgrades.critical_strike === 0">Not Unlocked</span>
              <span v-else>{{ upgrades.critical_strike }}% chance for 4x multiplier</span>
            </p>
            <p v-if="upgrades.critical_strike < maxLevels.critical_strike" class="text-white/50">
              Cost: ${{ (upgrades.critical_strike === 0 ? 1000 : 200 * (2 ** (upgrades.critical_strike - 1))).toFixed(2) }}
            </p>
          </div>
          <button 
            v-if="upgrades.critical_strike < maxLevels.critical_strike"
            @click="purchaseUpgrade('critical_strike')"
            class="w-full px-4 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200"
            :class="{ 'opacity-50 cursor-not-allowed': !canAfford('critical_strike') }"
          >
            {{ upgrades.critical_strike === 0 ? 'Unlock Critical Strike' : canAfford('critical_strike') ? 'Upgrade' : 'Too Expensive' }}
          </button>
        </div>

        <!-- Progress Per Click -->
        <div 
          class="bg-gray-dark/50 rounded-xl p-6 relative group hover:bg-gray-dark/70 transition-all duration-300"
          :class="{ 'border-2 border-yellow shadow-[0_0_15px_rgba(255,215,0,0.2)]': upgrades.progress_per_click >= maxLevels.progress_per_click }"
        >
          <div v-if="upgrades.progress_per_click >= maxLevels.progress_per_click" 
               class="absolute -top-3 -right-3 bg-gradient-to-r from-yellow to-yellow/80 text-gray-darker px-3 py-1 rounded-full text-sm font-bold transform rotate-12">
            Max Level
          </div>
          <h3 class="text-lg font-display text-white mb-4">Progress Per Click</h3>
          <div class="space-y-2 mb-6">
            <p class="text-yellow">Level: {{ upgrades.progress_per_click }}/{{ maxLevels.progress_per_click }}</p>
            <p class="text-white/70">Current: {{ upgrades.progress_per_click }}% per click</p>
            <p v-if="upgrades.progress_per_click < maxLevels.progress_per_click" class="text-white/50">
              Cost: ${{ (150 * (2 ** (upgrades.progress_per_click - 1))).toFixed(2) }}
            </p>
          </div>
          <button 
            v-if="upgrades.progress_per_click < maxLevels.progress_per_click"
            @click="purchaseUpgrade('progress_per_click')"
            class="w-full px-4 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200"
            :class="{ 'opacity-50 cursor-not-allowed': !canAfford('progress_per_click') }"
          >
            {{ canAfford('progress_per_click') ? 'Upgrade' : 'Too Expensive' }}
          </button>
        </div>

        <!-- Case Quality -->
        <div 
          class="bg-gray-dark/50 rounded-xl p-6 relative group hover:bg-gray-dark/70 transition-all duration-300"
          :class="{ 'border-2 border-yellow shadow-[0_0_15px_rgba(255,215,0,0.2)]': upgrades.case_quality >= maxLevels.case_quality }"
        >
          <div v-if="upgrades.case_quality >= maxLevels.case_quality" 
               class="absolute -top-3 -right-3 bg-gradient-to-r from-yellow to-yellow/80 text-gray-darker px-3 py-1 rounded-full text-sm font-bold transform rotate-12">
            Max Level
          </div>
          <h3 class="text-lg font-display text-white mb-4">Case Quality</h3>
          <div class="space-y-2 mb-6">
            <p class="text-yellow">Level: {{ upgrades.case_quality }}/{{ maxLevels.case_quality }}</p>
            <p class="text-white/70">Current: {{ getCaseQualityRange(upgrades.case_quality) }}</p>
            <p v-if="upgrades.case_quality < maxLevels.case_quality" class="text-white/50">
              Cost: ${{ (500 * (2 ** (upgrades.case_quality - 1))).toFixed(2) }}
            </p>
          </div>
          <button 
            v-if="upgrades.case_quality < maxLevels.case_quality"
            @click="purchaseUpgrade('case_quality')"
            class="w-full px-4 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200"
            :class="{ 'opacity-50 cursor-not-allowed': !canAfford('case_quality') }"
          >
            {{ canAfford('case_quality') ? 'Upgrade' : 'Too Expensive' }}
          </button>
        </div>

        <!-- Multi Open -->
        <div 
          class="bg-gray-dark/50 rounded-xl p-6 relative group hover:bg-gray-dark/70 transition-all duration-300"
          :class="{ 'border-2 border-yellow shadow-[0_0_15px_rgba(255,215,0,0.2)]': upgrades.multi_open >= maxLevels.multi_open }"
        >
          <div v-if="upgrades.multi_open >= maxLevels.multi_open" 
               class="absolute -top-3 -right-3 bg-gradient-to-r from-yellow to-yellow/80 text-gray-darker px-3 py-1 rounded-full text-sm font-bold transform rotate-12">
            Max Level
          </div>
          <h3 class="text-lg font-display text-white mb-4">Multi Open</h3>
          <div class="space-y-2 mb-6">
            <p class="text-yellow">Level: {{ upgrades.multi_open }}/{{ maxLevels.multi_open }}</p>
            <p class="text-white/70">
              Current: Can open {{ upgrades.multi_open === 1 ? '1 case' : `up to ${upgrades.multi_open} cases` }} at once
            </p>
            <p v-if="upgrades.multi_open < maxLevels.multi_open" class="text-white/50">
              Cost: ${{ (300 * (2 ** (upgrades.multi_open - 1))).toFixed(2) }}
            </p>
          </div>
          <button 
            v-if="upgrades.multi_open < maxLevels.multi_open"
            @click="purchaseUpgrade('multi_open')"
            class="w-full px-4 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200"
            :class="{ 'opacity-50 cursor-not-allowed': !canAfford('multi_open') }"
          >
            {{ canAfford('multi_open') ? 'Upgrade' : 'Too Expensive' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'UpgradesView',
  setup() {
    const upgrades = ref({
      click_value: 1,
      max_multiplier: 1,
      auto_clicker: 0,
      combo_speed: 1,
      critical_strike: 0,
      progress_per_click: 1,
      case_quality: 1,
      multi_open: 1
    })

    const maxLevels = {
      click_value: 999999,
      max_multiplier: 999999,
      auto_clicker: 999999,
      combo_speed: 999999,
      critical_strike: 999999,
      progress_per_click: 10,
      case_quality: 5,
      multi_open: 5
    }

    const balance = ref(0)

    const loadUpgrades = async () => {
      try {
        const response = await fetch('/get_upgrades')
        const data = await response.json()
        upgrades.value = data
      } catch (error) {
        console.error('Error loading upgrades:', error)
      }
    }

    const loadUserData = async () => {
      try {
        const response = await fetch('/api/get_user_data')
        const data = await response.json()
        balance.value = data.balance
      } catch (error) {
        console.error('Error loading user data:', error)
      }
    }

    const getCost = (type) => {
      const costs = {
        click_value: 100 * (2 ** (upgrades.value[type] - 1)),
        max_multiplier: 250 * (2 ** (upgrades.value[type] - 1)),
        auto_clicker: upgrades.value[type] === 0 ? 500 : 50 * (1.8 ** (upgrades.value[type] - 1)),
        combo_speed: 150 * (2 ** (upgrades.value[type] - 1)),
        critical_strike: upgrades.value[type] === 0 ? 1000 : 200 * (2 ** (upgrades.value[type] - 1)),
        progress_per_click: 150 * (2 ** (upgrades.value[type] - 1)),
        case_quality: 500 * (2 ** (upgrades.value[type] - 1)),
        multi_open: 300 * (2 ** (upgrades.value[type] - 1))
      }
      return costs[type]
    }

    const canAfford = (type) => {
      return balance.value >= getCost(type)
    }

    const getCaseQualityRange = (level) => {
      const ranges = {
        1: '0-2 USD cases',
        2: '0-5 USD cases',
        3: '0-10 USD cases',
        4: '0-15 USD cases',
        5: '0-20 USD cases'
      }
      return ranges[level]
    }

    const purchaseUpgrade = async (type) => {
      if (!canAfford(type)) return

      try {
        const response = await fetch('/purchase_upgrade', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ upgrade_type: type })
        })

        const data = await response.json()

        if (data.error) {
          console.error(data.error)
          return
        }

        // Update balance and upgrades
        balance.value = data.balance
        upgrades.value = data.upgrades

        // Dispatch custom event with new upgrade values
        window.dispatchEvent(new CustomEvent('upgradesPurchased', {
          detail: data.upgrades
        }))
      } catch (error) {
        console.error('Error purchasing upgrade:', error)
      }
    }

    // Load initial data
    onMounted(() => {
      loadUpgrades()
      loadUserData()
    })

    return {
      upgrades,
      maxLevels,
      balance,
      canAfford,
      getCaseQualityRange,
      purchaseUpgrade
    }
  }
}
</script> 