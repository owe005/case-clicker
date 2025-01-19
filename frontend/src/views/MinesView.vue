<template>
  <div class="min-h-screen bg-gray-darker">
    <!-- Add audio element -->
    <audio ref="backgroundMusic" src="/awolnation_menu.mp3" preload="auto" loop></audio>
    <!-- Header -->
    <div class="relative py-12 mb-8">
      <div class="absolute inset-0 bg-gradient-to-b from-yellow/5 to-transparent"></div>
      <div class="relative max-w-7xl mx-auto px-4">
        <h1 class="text-4xl font-display font-bold text-white mb-2">Mines</h1>
        <p class="text-white/70">Find the diamonds, avoid the mines!</p>
        <!-- Add volume controls -->
        <div class="flex gap-4 mt-4">
          <button 
            class="px-4 py-2 rounded-lg bg-gray-dark/50 text-white/70 hover:bg-gray-darker hover:text-white transition-all duration-200 flex items-center gap-2"
            @click="toggleMusic"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path v-if="!isMusicMuted" fill-rule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM14.657 2.929a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 7.071 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.984 5.984 0 01-1.757 4.243 1 1 0 01-1.415-1.415A3.984 3.984 0 0013 10a3.983 3.983 0 00-1.172-2.828 1 1 0 010-1.415z" clip-rule="evenodd" />
              <path v-else fill-rule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM12.293 7.293a1 1 0 011.414 1.414L10.414 12l3.293 3.293a1 1 0 01-1.414 1.414L9 13.414l-3.293 3.293a1 1 0 01-1.414-1.414L7.586 12 4.293 8.707a1 1 0 011.414-1.414L9 10.586l3.293-3.293z" clip-rule="evenodd" />
            </svg>
            {{ isMusicMuted ? 'Unmute Music' : 'Mute Music' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Game Area -->
    <div class="max-w-7xl mx-auto px-4 pb-12">
      <!-- Game Notification -->
      <div v-if="notification" class="mb-8">
        <div :class="[
          'text-center p-4 rounded-lg font-bold text-lg',
          notification.type === 'success' ? 'bg-green-600 text-white' : '',
          notification.type === 'error' ? 'bg-red-600 text-white' : ''
        ]">
          {{ notification.message }}
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Game Controls -->
        <div class="lg:col-span-1">
          <div class="bg-gray-dark/50 rounded-xl p-6">
            <!-- Game Settings -->
            <div class="mb-6">
              <h2 class="text-xl font-display text-white mb-4">Game Settings</h2>
              
              <!-- Grid Size -->
              <div class="mb-4">
                <label class="block text-white/70 mb-2">Grid Size</label>
                <select 
                  v-model="gridSize" 
                  class="w-full bg-gray-darker border border-gray-700 text-white rounded px-3 py-2"
                  :disabled="gameActive"
                >
                  <option v-for="size in [4,5,6,7,8]" :key="size" :value="size">
                    {{ size }}x{{ size }}
                  </option>
                </select>
              </div>
              
              <!-- Number of Mines -->
              <div class="mb-4">
                <label class="block text-white/70 mb-2">Number of Mines</label>
                <select 
                  v-model="numMines" 
                  class="w-full bg-gray-darker border border-gray-700 text-white rounded px-3 py-2"
                  :disabled="gameActive"
                >
                  <option 
                    v-for="n in maxMines" 
                    :key="n" 
                    :value="n"
                  >
                    {{ n }} {{ n === 1 ? 'Mine' : 'Mines' }}
                  </option>
                </select>
              </div>
              
              <!-- Bet Amount -->
              <div class="mb-4">
                <label class="block text-white/70 mb-2">Bet Amount</label>
                <div class="flex gap-2">
                  <input 
                    v-model="betAmount" 
                    type="number" 
                    min="0.01" 
                    step="0.01"
                    class="flex-1 bg-gray-darker border border-gray-700 text-white rounded px-3 py-2"
                    :disabled="gameActive"
                  >
                  <button 
                    @click="betAmount = Math.max(0.01, betAmount / 2)" 
                    class="px-3 py-2 bg-gray-700 text-white rounded hover:bg-gray-600"
                    :disabled="gameActive"
                  >
                    ½
                  </button>
                  <button 
                    @click="betAmount = betAmount * 2" 
                    class="px-3 py-2 bg-gray-700 text-white rounded hover:bg-gray-600"
                    :disabled="gameActive"
                  >
                    2×
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Game Stats -->
            <div class="mb-6">
              <h2 class="text-xl font-display text-white mb-4">Game Stats</h2>
              <div class="grid grid-cols-2 gap-4">
                <div class="bg-gray-darker rounded-lg p-4">
                  <div class="text-white/70 text-sm mb-1">Multiplier</div>
                  <div class="text-white text-xl font-bold">{{ currentMultiplier }}×</div>
                </div>
                <div class="bg-gray-darker rounded-lg p-4">
                  <div class="text-white/70 text-sm mb-1">Potential Win</div>
                  <div class="text-white text-xl font-bold">${{ formatNumber(potentialWin) }}</div>
                </div>
              </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="grid grid-cols-2 gap-4">
              <button 
                v-if="!gameActive"
                @click="startGame" 
                class="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-500 font-bold"
                :disabled="!canStart"
              >
                Start Game
              </button>
              <button 
                v-else
                @click="cashOut" 
                class="w-full px-6 py-3 bg-yellow text-gray-900 rounded-lg hover:bg-yellow/90 font-bold"
                :disabled="!canCashOut"
              >
                Cash Out
              </button>
            </div>
          </div>
        </div>
        
        <!-- Game Grid -->
        <div class="lg:col-span-2">
          <div class="bg-gray-dark/50 rounded-xl p-6">
            <div class="grid gap-1" :style="gridStyle">
              <button 
                v-for="(tile, index) in tiles" 
                :key="index"
                @click="revealTile(index)"
                class="w-full aspect-square rounded-lg text-3xl font-bold transition-all duration-200 flex items-center justify-center"
                :class="getTileClass(tile)"
                :disabled="!gameActive || tile.revealed"
              >
                <template v-if="tile.revealed || gameOver">
                  <span v-if="tile.isMine">💣</span>
                  <span v-else>💎</span>
                </template>
                <span v-else>?</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import confetti from 'canvas-confetti'

export default {
  name: 'MinesView',
  setup() {
    // Game settings
    const gridSize = ref(5)
    const numMines = ref(3)
    const betAmount = ref(1.00)
    
    // Game state
    const gameActive = ref(false)
    const gameOver = ref(false)
    const currentMultiplier = ref(1.0)
    const potentialWin = ref(0)
    const tiles = ref([])
    const notification = ref(null)
    const audioContext = ref(null)
    const diamondSoundBuffer = ref(null)
    const mineSoundBuffer = ref(null)
    const winSoundBuffer = ref(null)
    const basePitch = 0.25 // Start at 25% pitch (75% lower)
    const pitchIncrement = 0.01 // 1% increase per diamond
    const revealedCount = ref(0)
    
    // Audio state
    const backgroundMusic = ref(null)
    const isMusicMuted = ref(false)
    const previousMusicVolume = ref(0.1) // Store previous music volume
    const audioInitialized = ref(false)
    const NORMAL_VOLUME = 0.1  // 10% volume
    const LOWERED_VOLUME = 0.02 // 2% volume when effects play
    const VOLUME_RESTORE_DELAY = 500 // 500ms delay before restoring volume

    // Function to temporarily lower background music volume
    const lowerBackgroundMusic = () => {
      if (backgroundMusic.value && !isMusicMuted.value) {
        backgroundMusic.value.volume = LOWERED_VOLUME
      }
    }

    // Function to restore background music volume
    const restoreBackgroundMusic = () => {
      if (backgroundMusic.value && !isMusicMuted.value) {
        backgroundMusic.value.volume = NORMAL_VOLUME
      }
    }

    // Initialize audio context and load sounds
    const initAudio = async () => {
      try {
        audioContext.value = new (window.AudioContext || window.webkitAudioContext)()
        
        // Load diamond sound
        const diamondResponse = await fetch('/effect.wav')
        const diamondBuffer = await diamondResponse.arrayBuffer()
        diamondSoundBuffer.value = await audioContext.value.decodeAudioData(diamondBuffer)
        
        // Load mine sound
        const mineResponse = await fetch('/mine.wav')
        const mineBuffer = await mineResponse.arrayBuffer()
        mineSoundBuffer.value = await audioContext.value.decodeAudioData(mineBuffer)
        
        // Load win sound
        const winResponse = await fetch('/win.wav')
        const winBuffer = await winResponse.arrayBuffer()
        winSoundBuffer.value = await audioContext.value.decodeAudioData(winBuffer)
      } catch (error) {
        console.error('Error loading sounds:', error)
      }
    }

    // Play sound with pitch
    const playDiamondSound = () => {
      if (!audioContext.value || !diamondSoundBuffer.value) return
      
      lowerBackgroundMusic()
      
      const source = audioContext.value.createBufferSource()
      source.buffer = diamondSoundBuffer.value
      
      // Calculate current pitch
      const currentPitch = basePitch + (revealedCount.value * pitchIncrement)
      source.playbackRate.value = currentPitch
      
      source.connect(audioContext.value.destination)
      source.start(0)
      
      // Restore volume after effect
      setTimeout(restoreBackgroundMusic, VOLUME_RESTORE_DELAY)
    }
    
    // Play mine sound
    const playMineSound = () => {
      if (!audioContext.value || !mineSoundBuffer.value) return
      
      lowerBackgroundMusic()
      
      const source = audioContext.value.createBufferSource()
      source.buffer = mineSoundBuffer.value
      source.connect(audioContext.value.destination)
      source.start(0)
      
      // Restore volume after effect
      setTimeout(restoreBackgroundMusic, VOLUME_RESTORE_DELAY)
    }
    
    // Play win sound
    const playWinSound = () => {
      if (!audioContext.value || !winSoundBuffer.value) return
      
      lowerBackgroundMusic()
      
      const source = audioContext.value.createBufferSource()
      source.buffer = winSoundBuffer.value
      source.connect(audioContext.value.destination)
      source.start(0)
      
      // Restore volume after effect
      setTimeout(restoreBackgroundMusic, VOLUME_RESTORE_DELAY)
    }

    // Function to initialize audio
    const initializeAudio = () => {
      if (!audioInitialized.value) {
        // Initialize effect sounds first
        const sounds = [diamondSoundBuffer.value, mineSoundBuffer.value, winSoundBuffer.value].filter(Boolean)
        Promise.all(sounds.map(sound => {
          if (!sound) return Promise.resolve()
          sound.volume = 0
          return sound.play().then(() => {
            sound.pause()
            sound.volume = 1
          }).catch(error => {
            console.log('Audio initialization failed:', error)
          })
        })).then(() => {
          audioInitialized.value = true
          // Initialize and start background music
          if (backgroundMusic.value) {
            backgroundMusic.value.load()
            backgroundMusic.value.volume = isMusicMuted.value ? 0 : NORMAL_VOLUME
            backgroundMusic.value.loop = true  // Ensure looping is enabled
            backgroundMusic.value.play().catch(error => {
              console.log('Error playing background music:', error)
            })
          }
        })
      } else if (backgroundMusic.value && backgroundMusic.value.paused) {
        // If audio is initialized but background music is paused, try to start it
        backgroundMusic.value.volume = isMusicMuted.value ? 0 : NORMAL_VOLUME
        backgroundMusic.value.loop = true
        backgroundMusic.value.play().catch(error => {
          console.log('Error playing background music:', error)
        })
      }
    }

    // Function to toggle music
    const toggleMusic = () => {
      if (backgroundMusic.value) {
        if (isMusicMuted.value) {
          // Unmute - restore previous volume
          backgroundMusic.value.volume = NORMAL_VOLUME
          isMusicMuted.value = false
        } else {
          // Mute - store current volume and set to 0
          previousMusicVolume.value = backgroundMusic.value.volume
          backgroundMusic.value.volume = 0
          isMusicMuted.value = true
        }
      }
    }

    // Add click handler to initialize audio and ensure background music plays
    const handleClick = () => {
      initializeAudio()
    }
    
    // Show notification
    const showNotification = (message, type = 'success') => {
      notification.value = { message, type }
    }
    
    // Computed properties
    const maxMines = computed(() => (gridSize.value * gridSize.value) - 1)
    
    const gridStyle = computed(() => ({
      'grid-template-columns': `repeat(${gridSize.value}, minmax(0, 1fr))`
    }))
    
    const canStart = computed(() => {
      return betAmount.value > 0 && numMines.value > 0 && numMines.value <= maxMines.value
    })
    
    const canCashOut = computed(() => {
      return gameActive.value && !gameOver.value && tiles.value.some(tile => tile.revealed)
    })
    
    // Initialize tiles
    const initializeTiles = () => {
      tiles.value = Array(gridSize.value * gridSize.value).fill(null).map(() => ({
        revealed: false,
        isMine: false
      }))
    }
    
    // Start new game
    const startGame = async () => {
      try {
        // Initialize audio context if not already done
        if (!audioContext.value) {
          await initializeAudio()
        }
        
        const response = await axios.post('/api/mines/start', {
          grid_size: parseInt(gridSize.value),
          num_mines: parseInt(numMines.value),
          bet_amount: parseFloat(betAmount.value)
        })
        
        if (response.data.success) {
          gameActive.value = true
          gameOver.value = false
          currentMultiplier.value = response.data.multiplier
          potentialWin.value = response.data.potential_win
          revealedCount.value = 0
          initializeTiles()
        }
      } catch (error) {
        console.error('Error starting game:', error)
        showNotification(error.response?.data?.error || 'Failed to start game', 'error')
      }
    }
    
    // Play win sound and show confetti
    const celebrateWin = () => {
      playWinSound()
      
      // Fire confetti from both sides
      const count = 200
      const defaults = {
        origin: { y: 0.7 },
        spread: 80,
        startVelocity: 30,
        ticks: 300
      }

      function fire(particleRatio, opts) {
        confetti({
          ...defaults,
          ...opts,
          particleCount: Math.floor(count * particleRatio)
        })
      }

      fire(0.25, {
        spread: 26,
        startVelocity: 55,
        origin: { x: 0.2 }
      })
      fire(0.25, {
        spread: 26,
        startVelocity: 55,
        origin: { x: 0.8 }
      })
      fire(0.2, {
        spread: 60,
        origin: { x: 0.3 }
      })
      fire(0.2, {
        spread: 60,
        origin: { x: 0.7 }
      })
      fire(0.1, {
        spread: 100,
        decay: 0.91,
        origin: { x: 0.5 }
      })
    }
    
    // Reveal tile
    const revealTile = async (index) => {
      if (!gameActive.value || tiles.value[index].revealed) return
      
      const x = Math.floor(index / gridSize.value)
      const y = index % gridSize.value
      
      try {
        const response = await axios.post('/api/mines/reveal', { x, y })
        
        // Update tile state
        tiles.value[index].revealed = true
        tiles.value[index].isMine = response.data.hit_mine
        
        // Play appropriate sound
        if (response.data.hit_mine) {
          playMineSound()
        } else {
          revealedCount.value++
          playDiamondSound()
        }
        
        if (response.data.status === 'continue') {
          currentMultiplier.value = response.data.multiplier
          potentialWin.value = response.data.potential_win
        } else if (response.data.status === 'game_over' || response.data.status === 'win') {
          gameOver.value = true
          gameActive.value = false
          
          // Reveal all mines
          const grid = response.data.grid
          grid.forEach((row, i) => {
            row.forEach((isMine, j) => {
              if (isMine) {
                const idx = i * gridSize.value + j
                tiles.value[idx].isMine = true
                tiles.value[idx].revealed = true
              }
            })
          })
          
          if (response.data.status === 'win') {
            celebrateWin()
            const winAmount = response.data.potential_win || response.data.win_amount || 0
            showNotification(`Congratulations! You won $${formatNumber(winAmount)}!`, 'success')
          } else {
            showNotification('Game Over! You hit a mine!', 'error')
          }
        }
      } catch (error) {
        console.error('Error revealing tile:', error)
        showNotification(error.response?.data?.error || 'Failed to reveal tile', 'error')
      }
    }
    
    // Cash out
    const cashOut = async () => {
      try {
        const response = await axios.post('/api/mines/cashout')
        
        if (response.data.status === 'cash_out') {
          gameActive.value = false
          gameOver.value = true
          
          // Reveal all mines
          const grid = response.data.grid
          grid.forEach((row, i) => {
            row.forEach((isMine, j) => {
              if (isMine) {
                const idx = i * gridSize.value + j
                tiles.value[idx].isMine = true
                tiles.value[idx].revealed = true
              }
            })
          })
          
          celebrateWin()
          showNotification(`Congratulations! You won $${formatNumber(response.data.win_amount)}!`, 'success')
        }
      } catch (error) {
        console.error('Error cashing out:', error)
        showNotification(error.response?.data?.error || 'Failed to cash out', 'error')
      }
    }
    
    // Utility functions
    const formatNumber = (num) => {
      if (num >= 1000000) {
        return `${(num / 1000000).toFixed(2)}M`
      }
      if (num >= 1000) {
        return `${(num / 1000).toFixed(2)}K`
      }
      return Number(num).toFixed(2)
    }
    
    const getTileClass = (tile) => {
      if (!tile.revealed) {
        return 'bg-gray-700 hover:bg-gray-600 text-white'
      }
      if (tile.isMine) {
        return 'bg-red-600 text-white'
      }
      return 'bg-green-600 text-white'
    }
    
    // Initialize game
    initializeTiles()
    
    // Watch for grid size changes
    watch(gridSize, () => {
      initializeTiles()
    })

    // Initialize component
    onMounted(async () => {
      try {
        // Get background music element reference
        backgroundMusic.value = document.querySelector('audio[ref="backgroundMusic"]')

        // Initialize audio
        initializeAudio()
        await initAudio() // Initialize game sounds

        // Add click event listeners to initialize audio
        document.addEventListener('click', handleClick)
        document.addEventListener('touchstart', handleClick)
      } catch (error) {
        console.error('Error in onMounted:', error)
      }
    })

    // Cleanup on unmount
    onUnmounted(() => {
      // Remove event listeners
      document.removeEventListener('click', handleClick)
      document.removeEventListener('touchstart', handleClick)

      // Stop background music
      if (backgroundMusic.value) {
        backgroundMusic.value.pause()
        backgroundMusic.value.currentTime = 0
      }
    })
    
    return {
      // State
      gridSize,
      numMines,
      betAmount,
      gameActive,
      gameOver,
      currentMultiplier,
      potentialWin,
      tiles,
      notification,
      audioContext,
      diamondSoundBuffer,
      mineSoundBuffer,
      winSoundBuffer,
      basePitch,
      pitchIncrement,
      revealedCount,
      
      // Audio state
      backgroundMusic,
      isMusicMuted,
      previousMusicVolume,
      audioInitialized,
      
      // Computed
      maxMines,
      gridStyle,
      canStart,
      canCashOut,
      
      // Methods
      startGame,
      revealTile,
      cashOut,
      formatNumber,
      getTileClass,
      initializeAudio,
      toggleMusic,
      handleClick
    }
  }
}
</script>

<style scoped>
.aspect-square {
  aspect-ratio: 1;
}
</style> 