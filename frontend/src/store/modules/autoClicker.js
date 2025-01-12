// Auto clicker state and functionality
import { ref } from 'vue'

const autoClickerInterval = ref(null)
const isAutoClickerActive = ref(false)

// Create a custom event for floating text
const AUTO_CLICK_EVENT = 'autoClickerText'

export const autoClicker = {
    state: {
        isActive: isAutoClickerActive,
        interval: autoClickerInterval
    },

    startAutoClicker(store, level) {
        // Clear any existing interval
        if (autoClickerInterval.value) {
            clearInterval(autoClickerInterval.value)
            autoClickerInterval.value = null
        }
        
        // If level is greater than 0, start new interval
        if (level > 0) {
            let interval
            
            if (level <= 9) {
                interval = (11 - level) * 1000 // Convert seconds to milliseconds
            } else {
                const clicksPerSecond = level - 8
                interval = 1000 / clicksPerSecond
            }
            
            isAutoClickerActive.value = true
            autoClickerInterval.value = setInterval(async () => {
                try {
                    // Ensure store and required state properties exist
                    if (!store?.state?.upgrades?.critical_strike || !store?.state?.clicker?.baseClickValue) {
                        console.warn('Store state not fully initialized yet')
                        return
                    }

                    // Calculate critical strike chance
                    const criticalChance = store.state.upgrades.critical_strike / 100
                    let isCritical = false
                    
                    if (criticalChance > 0) {
                        const roll = Math.random()
                        if (roll < criticalChance) {
                            isCritical = true
                        }
                    }

                    // Calculate value for floating text
                    const baseValue = store.state.clicker.baseClickValue || 0.01
                    const value = baseValue * (isCritical ? 4 : 1)

                    // Emit custom event for floating text
                    const event = new CustomEvent(AUTO_CLICK_EVENT, {
                        detail: {
                            value,
                            isCritical
                        }
                    })
                    window.dispatchEvent(event)

                    // Simulate auto click with potential crit
                    await store.handleBatchMoneyClicks(
                        isCritical ? 0 : 1, // normal clicks
                        isCritical ? 1 : 0, // critical clicks
                        isCritical ? 0 : 1, // auto normal clicks
                        isCritical ? 1 : 0  // auto critical clicks
                    )
                } catch (error) {
                    console.warn('Error in auto clicker:', error)
                }
            }, interval)
        } else {
            isAutoClickerActive.value = false
        }
    },

    stopAutoClicker() {
        if (autoClickerInterval.value) {
            clearInterval(autoClickerInterval.value)
            autoClickerInterval.value = null
        }
        isAutoClickerActive.value = false
    }
} 