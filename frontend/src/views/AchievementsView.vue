<template>
  <div class="min-h-screen bg-gray-darker">
    <!-- Header -->
    <div class="relative py-12 mb-8">
      <div class="absolute inset-0 bg-gradient-to-b from-yellow/5 to-transparent"></div>
      <div class="relative max-w-7xl mx-auto px-4">
        <h1 class="text-4xl font-display font-bold text-white mb-2">Achievements</h1>
        <p class="text-white/70">Track your progress and earn rewards</p>
      </div>
    </div>

    <!-- Content -->
    <div class="max-w-7xl mx-auto px-4 pb-12">
      <!-- Summary Stats -->
      <div class="glass-panel p-6 mb-8 grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div class="text-center">
          <h3 class="text-2xl font-display text-yellow mb-1">{{ completedCount }}/{{ totalCount }}</h3>
          <p class="text-white/70 text-sm">Achievements Completed</p>
        </div>
        <div class="text-center">
          <h3 class="text-2xl font-display text-yellow mb-1">{{ completionRate }}%</h3>
          <p class="text-white/70 text-sm">Completion Rate</p>
        </div>
        <div class="text-center">
          <h3 class="text-2xl font-display text-yellow mb-1">${{ totalRewards.toLocaleString() }}</h3>
          <p class="text-white/70 text-sm">Total Rewards Earned</p>
        </div>
      </div>

      <!-- Category Filter -->
      <div class="flex flex-wrap justify-center gap-3 mb-8">
        <button 
          v-for="category in categories" 
          :key="category.id"
          class="px-4 py-2 rounded-lg font-medium transition-all duration-200"
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

      <!-- Achievements Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="achievement in filteredAchievements" 
          :key="achievement.id"
          class="glass-panel p-6 relative group transition-all duration-300"
          :class="{ 'opacity-70 grayscale': !achievement.completed }"
        >
          <!-- Lock Icon for Incomplete Achievements -->
          <div 
            v-if="!achievement.completed"
            class="absolute top-4 right-4 text-xl text-white/50"
          >
            🔒
          </div>

          <!-- Achievement Content -->
          <div class="flex items-start gap-4">
            <div 
              class="w-12 h-12 rounded-full bg-gray-dark/50 flex items-center justify-center text-2xl"
              :class="{ 'text-yellow': achievement.completed }"
            >
              {{ achievement.icon }}
            </div>
            <div class="flex-1">
              <h3 class="font-display text-lg text-yellow mb-1">{{ achievement.title }}</h3>
              <p class="text-sm text-white/70 mb-4">{{ achievement.description }}</p>

              <!-- Progress Bar -->
              <div class="h-2 bg-gray-dark rounded-full overflow-hidden mb-3">
                <div 
                  class="h-full bg-gradient-to-r from-yellow to-yellow/80 transition-all duration-300"
                  :style="{ width: `${achievement.progress}%` }"
                ></div>
              </div>

              <!-- Progress Stats -->
              <div class="flex items-end justify-between text-sm">
                <span class="text-white/50">
                  {{ achievement.current_value.toLocaleString() }}/{{ achievement.target_value.toLocaleString() }}
                </span>
                <div class="flex flex-col items-end gap-1">
                  <span class="text-emerald-400/90 bg-emerald-400/10 px-2 py-0.5 rounded flex items-center gap-1">
                    💰 ${{ achievement.reward.toLocaleString() }}
                  </span>
                  <span v-if="achievement.exp_reward" class="text-amber-400/90 bg-amber-400/10 px-2 py-0.5 rounded flex items-center gap-1">
                    ✨ {{ achievement.exp_reward.toLocaleString() }} EXP
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'AchievementsView',
  setup() {
    const achievements = ref([])
    const currentCategory = ref('all')
    const completedCount = ref(0)
    const totalCount = ref(0)
    const totalRewards = ref(0)
    const completionRate = ref(0)

    // Categories
    const categories = [
      { id: 'all', name: 'All' },
      { id: 'cases', name: 'Cases' },
      { id: 'trading', name: 'Trading' },
      { id: 'casino', name: 'Casino' },
      { id: 'clicker', name: 'Clicker' },
      { id: 'inventory', name: 'Inventory' },
      { id: 'special', name: 'Special' },
      { id: 'completed', name: 'Completed' }
    ]

    // Filter achievements based on selected category
    const filteredAchievements = computed(() => {
      if (currentCategory.value === 'all') {
        return achievements.value.filter(a => !a.completed)
      }
      if (currentCategory.value === 'completed') {
        return achievements.value.filter(a => a.completed)
      }
      return achievements.value.filter(a => 
        a.category === currentCategory.value && !a.completed
      )
    })

    // Fetch achievements data
    const fetchAchievements = async () => {
      try {
        const response = await fetch('/api/achievements')
        const data = await response.json()
        
        achievements.value = data.achievements
        completedCount.value = data.completed_count
        totalCount.value = data.total_count
        completionRate.value = data.completion_rate
        totalRewards.value = data.total_rewards
      } catch (error) {
        console.error('Error fetching achievements:', error)
      }
    }

    // Fetch data on component mount
    fetchAchievements()

    return {
      achievements,
      currentCategory,
      categories,
      filteredAchievements,
      completedCount,
      totalCount,
      completionRate,
      totalRewards
    }
  }
}
</script> 