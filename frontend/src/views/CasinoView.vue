<template>
  <div class="min-h-screen bg-gray-darker">
    <!-- Header -->
    <div class="relative py-12 mb-8">
      <div class="absolute inset-0 bg-gradient-to-b from-yellow/5 to-transparent"></div>
      <div class="relative max-w-7xl mx-auto px-4">
        <h1 class="text-4xl font-display font-bold text-white mb-2">Casino</h1>
        <p class="text-white/70">Try your luck with various casino games</p>
      </div>
    </div>

    <!-- Casino Games Grid -->
    <div class="max-w-7xl mx-auto px-4 pb-12">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Blackjack -->
        <div class="group h-full">
          <div class="bg-gray-dark/50 rounded-xl overflow-hidden transition-all duration-300 hover:bg-gray-dark/70 hover:transform hover:-translate-y-1 hover:shadow-xl h-full flex flex-col">
            <!-- Game Preview -->
            <div class="aspect-video w-full bg-gray-darker/50 overflow-hidden flex items-center justify-center">
              <img 
                src="/casino/blackjack.png" 
                alt="Blackjack"
                class="w-auto h-auto max-w-full max-h-full object-contain transition-transform duration-300 group-hover:scale-105"
              >
            </div>
            <!-- Game Info -->
            <div class="p-6 flex flex-col flex-grow">
              <h2 class="text-xl font-display text-white mb-2">Blackjack</h2>
              <p class="text-white/70 mb-6 flex-grow">Classic casino blackjack - try to beat the dealer to 21!</p>
              <router-link 
                to="/blackjack"
                class="block w-full px-4 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200 text-center mt-auto"
              >
                Play Now
              </router-link>
            </div>
          </div>
        </div>

        <!-- Jackpot -->
        <div class="group h-full">
          <div class="bg-gray-dark/50 rounded-xl overflow-hidden transition-all duration-300 hover:bg-gray-dark/70 hover:transform hover:-translate-y-1 hover:shadow-xl h-full flex flex-col">
            <div class="aspect-video w-full bg-gray-darker/50 overflow-hidden flex items-center justify-center">
              <img 
                src="/casino/jackpot.png" 
                alt="Jackpot"
                class="w-auto h-auto max-w-full max-h-full object-contain transition-transform duration-300 group-hover:scale-105"
              >
            </div>
            <div class="p-6 flex flex-col flex-grow">
              <h2 class="text-xl font-display text-white mb-2">Jackpot</h2>
              <p class="text-white/70 mb-6 flex-grow">Bet your skins against other players for a chance to win big!</p>
              <router-link 
                to="/jackpot"
                class="block w-full px-4 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200 text-center mt-auto"
              >
                Play Now
              </router-link>
            </div>
          </div>
        </div>

        <!-- Crash -->
        <div class="group h-full">
          <div class="bg-gray-dark/50 rounded-xl overflow-hidden transition-all duration-300 hover:bg-gray-dark/70 hover:transform hover:-translate-y-1 hover:shadow-xl h-full flex flex-col">
            <div class="aspect-video w-full bg-gray-darker/50 overflow-hidden flex items-center justify-center">
              <img 
                src="/casino/crash.png" 
                alt="Crash"
                class="w-auto h-auto max-w-full max-h-full object-contain transition-transform duration-300 group-hover:scale-105"
              >
            </div>
            <div class="p-6 flex flex-col flex-grow">
              <h2 class="text-xl font-display text-white mb-2">Crash</h2>
              <p class="text-white/70 mb-6 flex-grow">Watch the multiplier grow and cash out before it crashes!</p>
              <router-link 
                to="/crash"
                class="block w-full px-4 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200 text-center mt-auto"
              >
                Play Now
              </router-link>
            </div>
          </div>
        </div>

        <!-- Upgrade -->
        <div class="group h-full">
          <div class="bg-gray-dark/50 rounded-xl overflow-hidden transition-all duration-300 hover:bg-gray-dark/70 hover:transform hover:-translate-y-1 hover:shadow-xl h-full flex flex-col">
            <div class="aspect-video w-full bg-gray-darker/50 overflow-hidden flex items-center justify-center">
              <img 
                src="/casino/upgrade.png" 
                alt="Upgrade"
                class="w-auto h-auto max-w-full max-h-full object-contain transition-transform duration-300 group-hover:scale-105"
              >
            </div>
            <div class="p-6 flex flex-col flex-grow">
              <h2 class="text-xl font-display text-white mb-2">Upgrade</h2>
              <p class="text-white/70 mb-6 flex-grow">Try to upgrade your skins to more valuable ones!</p>
              <router-link 
                to="/upgrade"
                class="block w-full px-4 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200 text-center mt-auto"
              >
                Play Now
              </router-link>
            </div>
          </div>
        </div>

        <!-- Coinflip -->
        <div class="group h-full">
          <div class="bg-gray-dark/50 rounded-xl overflow-hidden transition-all duration-300 hover:bg-gray-dark/70 hover:transform hover:-translate-y-1 hover:shadow-xl h-full flex flex-col">
            <div class="aspect-video w-full bg-gray-darker/50 overflow-hidden flex items-center justify-center">
              <img 
                src="/casino/coinflip.png" 
                alt="Coinflip"
                class="w-auto h-auto max-w-full max-h-full object-contain transition-transform duration-300 group-hover:scale-105"
              >
            </div>
            <div class="p-6 flex flex-col flex-grow">
              <h2 class="text-xl font-display text-white mb-2">Coinflip</h2>
              <p class="text-white/70 mb-6 flex-grow">50/50 chance to double your bet!</p>
              <router-link 
                to="/coinflip"
                class="block w-full px-4 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200 text-center mt-auto"
              >
                Play Now
              </router-link>
            </div>
          </div>
        </div>

        <!-- Roulette -->
        <div class="group h-full">
          <div class="bg-gray-dark/50 rounded-xl overflow-hidden transition-all duration-300 hover:bg-gray-dark/70 hover:transform hover:-translate-y-1 hover:shadow-xl h-full flex flex-col">
            <div class="aspect-video w-full bg-gray-darker/50 overflow-hidden flex items-center justify-center">
              <img 
                src="/casino/roulette.png" 
                alt="Roulette"
                class="w-auto h-auto max-w-full max-h-full object-contain transition-transform duration-300 group-hover:scale-105"
              >
            </div>
            <div class="p-6 flex flex-col flex-grow">
              <h2 class="text-xl font-display text-white mb-2">Roulette</h2>
              <p class="text-white/70 mb-6 flex-grow">Classic casino roulette with CS:GO skins!</p>
              <router-link 
                to="/roulette"
                class="block w-full px-4 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200 text-center mt-auto"
              >
                Play Now
              </router-link>
            </div>
          </div>
        </div>

        <!-- Mines -->
        <div class="group h-full">
          <div class="bg-gray-dark/50 rounded-xl overflow-hidden transition-all duration-300 hover:bg-gray-dark/70 hover:transform hover:-translate-y-1 hover:shadow-xl h-full flex flex-col">
            <div class="aspect-video w-full bg-gray-darker/50 overflow-hidden flex items-center justify-center">
              <img 
                src="/casino/mines.png" 
                alt="Mines"
                class="w-auto h-auto max-w-full max-h-full object-contain transition-transform duration-300 group-hover:scale-105"
              >
            </div>
            <div class="p-6 flex flex-col flex-grow">
              <h2 class="text-xl font-display text-white mb-2">Mines</h2>
              <p class="text-white/70 mb-6 flex-grow">Find the diamonds, avoid the mines!</p>
              <router-link 
                to="/mines"
                class="block w-full px-4 py-2 bg-yellow/10 hover:bg-yellow/20 text-yellow rounded-lg transition-all duration-200 text-center mt-auto"
              >
                Play Now
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Game Modal -->
    <div 
      v-if="showGameModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      @click.self="showGameModal = false"
    >
      <div class="bg-gray-dark rounded-xl p-8 max-w-4xl w-full mx-4">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-display text-white">{{ currentGame.title }}</h2>
          <button 
            @click="showGameModal = false"
            class="text-white/50 hover:text-white transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Game Content -->
        <div class="min-h-[400px] bg-gray-darker/50 rounded-lg p-6">
          <div class="text-center text-white/70">
            Game content for {{ currentGame.title }} will be implemented here
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'CasinoView',
  setup() {
    const showGameModal = ref(false)
    const currentGame = ref({
      title: '',
      type: ''
    })

    const games = {
      blackjack: { title: 'Blackjack' },
      jackpot: { title: 'Jackpot' },
      crash: { title: 'Crash' },
      upgrade: { title: 'Upgrade' },
      coinflip: { title: 'Coinflip' },
      roulette: { title: 'Roulette' }
    }

    const playGame = (type) => {
      currentGame.value = {
        title: games[type].title,
        type
      }
      showGameModal.value = true
    }

    return {
      showGameModal,
      currentGame,
      playGame
    }
  }
}
</script>

<style scoped>
.shadow-xl {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}
</style> 