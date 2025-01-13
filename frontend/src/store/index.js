import { reactive, readonly } from 'vue'

// Case mappings from base.html
export const CASE_MAPPING = {
    'csgo': 'weapon_case_1',
    'esports': 'esports_2013',
    'bravo': 'operation_bravo_case',
    'csgo2': 'weapon_case_2',
    'esports_winter': 'esports_2013_winter',
    'winter_offensive': 'winter_offensive_case',
    'csgo3': 'weapon_case_3',
    'phoenix': 'operation_phoenix_case',
    'huntsman': 'huntsman_case',
    'breakout': 'operation_breakout_case',
    'esports_summer': 'esports_2014_summer',
    'vanguard': 'operation_vanguard_case',
    'chroma': 'chroma_case',
    'chroma_2': 'chroma_2_case',
    'falchion': 'falchion_case',
    'shadow': 'shadow_case',
    'revolution': 'revolution_case',
    'wildfire': 'operation_wildfire_case',
    'revolver': 'revolver_case',
    'gamma': 'gamma_case',
    'gamma_2': 'gamma_2_case',
    'chroma_3': 'chroma_3_case',
    'hydra': 'operation_hydra_case',
    'glove': 'glove_case',
    'spectrum': 'spectrum_case',
    'spectrum_2': 'spectrum_2_case',
    'clutch': 'clutch_case',
    'cs20': 'cs20_case',
    'danger_zone': 'danger_zone_case',
    'horizon': 'horizon_case',
    'riptide': 'operation_riptide_case',
    'shattered_web': 'shattered_web_case',
    'dreams_&_nightmares': 'dreams_&_nightmares_case',
    'fracture': 'fracture_case',
    'gallery': 'gallery_case',
    'kilowatt': 'kilowatt_case',
    'recoil': 'recoil_case',
    'snakebite': 'snakebite_case',
    'broken_fang': 'operation_broken_fang_case',
    'prisma': 'prisma_case',
    'prisma_2': 'prisma_2_case'
};

// Case rank requirements
export const CASE_RANK_REQUIREMENTS = {
    'CS:GO Weapon Case': 17,
    'eSports 2013 Case': 17,
    'Operation Bravo Case': 16,
    'CS:GO Weapon Case 2': 16,
    'eSports 2013 Winter Case': 15,
    'Winter Offensive Case': 15,
    'CS:GO Weapon Case 3': 15,
    'Operation Phoenix Case': 14,
    'Huntsman Case': 14,
    'Operation Breakout Case': 13,
    'eSports 2014 Summer Case': 13,
    'Operation Vanguard Case': 12,
    'Chroma Case': 12,
    'Chroma 2 Case': 11,
    'Falchion Case': 11,
    'Shadow Case': 11,
    'Revolution Case': 10,
    'Operation Wildfire Case': 10,
    'Dreams & Nightmares Case': 10,
    'Revolver Case': 9,
    'Gamma Case': 9,
    'Gamma 2 Case': 8,
    'Kilowatt Case': 8,
    'Horizon Case': 8,
    'Chroma 3 Case': 8,
    'Operation Hydra Case': 7,
    'Glove Case': 7,
    'Spectrum Case': 6,
    'Spectrum 2 Case': 6,
    'Clutch Case': 5,
    'CS20 Case': 5,
    'Danger Zone Case': 4,
    'Operation Riptide Case': 4,
    'Gallery Case': 3,
    'Snakebite Case': 3,
    'Fracture Case': 2,
    'Recoil Case': 1,
    'Shattered Web Case': 1,
    'Operation Broken Fang Case': 0,
    'Prisma Case': 0,
    'Prisma 2 Case': 0
}

export const RANKS = {
    0: "Silver I",
    1: "Silver II", 
    2: "Silver III",
    3: "Silver IV",
    4: "Silver Elite",
    5: "Silver Elite Master",
    6: "Gold Nova I",
    7: "Gold Nova II",
    8: "Gold Nova III",
    9: "Gold Nova Master",
    10: "Master Guardian I",
    11: "Master Guardian II",
    12: "Master Guardian Elite",
    13: "Distinguished Master Guardian",
    14: "Legendary Eagle",
    15: "Legendary Eagle Master",
    16: "Supreme Master First Class",
    17: "The Global Elite"
}

export const RANK_EXP = {
    0: 10,     // Silver I to Silver II
    1: 50,     // Silver II to Silver III  
    2: 100,    // Silver III to Silver IV
    3: 200,    // Silver IV to Silver Elite
    4: 500,    // Silver Elite to Silver Elite Master
    5: 1000,   // Silver Elite Master to Gold Nova I
    6: 2000,   // Gold Nova I to Gold Nova II
    7: 5000,   // Gold Nova II to Gold Nova III
    8: 10000,  // Gold Nova III to Gold Nova Master
    9: 20000,  // Gold Nova Master to Master Guardian I
    10: 50000, // Master Guardian I to Master Guardian II
    11: 75000, // Master Guardian II to Master Guardian Elite
    12: 100000,// Master Guardian Elite to Distinguished Master Guardian
    13: 150000,// Distinguished Master Guardian to Legendary Eagle
    14: 250000,// Legendary Eagle to Legendary Eagle Master
    15: 500000,// Legendary Eagle Master to Supreme Master First Class
    16: 1000000 // Supreme Master First Class to The Global Elite
}

// Create a reactive state
const state = reactive({
    rank: 0,
    exp: 0,
    balance: 1000,
    inventory: [],
    lastUpdate: Date.now(),
    isLoading: false,
    error: null,
    currentTab: 'money',
    currentView: 'clicker',
    upgrades: {
        click_value: 1,
        max_multiplier: 1,
        auto_clicker: 0,
        combo_speed: 1,
        critical_strike: 0,
        progress_per_click: 7,
        case_quality: 1,
        multi_open: 1
    },
    clicker: {
        currentMultiplier: 1.0,
        comboClickCount: 0,
        clicksToCombo: 20,
        maxMultiplier: 2.0,
        baseClickValue: 0.01,
        caseProgress: 0,
        lastProgress: 0,
        autoClickerInterval: null,
        multiplier: 1,
        isProcessingClick: false,
        pendingClicks: 0
    },
    autoClickQueue: {
        normal: 0,
        critical: 0
    },
    isProcessingAutoClicks: false,
    lastAutoClickProcess: 0,
    autoClickerWorker: null,
    autoClickerTabId: null,
    pingInterval: null
})

// Methods to update state
const methods = {
    updateUserData(data) {
        if (!data) return

        state.rank = data.rank ?? state.rank
        state.exp = data.exp ?? state.exp
        state.balance = data.balance !== undefined ? Number(data.balance) : state.balance
        state.inventory = data.inventory ?? state.inventory
        state.lastUpdate = Date.now()
        state.error = null
        
        // Update upgrades if provided
        if (data.upgrades) {
            state.upgrades = {
                ...state.upgrades,
                ...data.upgrades
            }
            
            // Update clicker state based on upgrades
            state.clicker.maxMultiplier = 1.5 + (0.5 * (data.upgrades.max_multiplier - 1))
            state.clicker.clicksToCombo = Math.max(1, 21 - data.upgrades.combo_speed)
            state.clicker.baseClickValue = 0.01 * (1.5 ** (data.upgrades.click_value - 1))

            // Update auto clicker if level changed
            if (data.upgrades.auto_clicker !== undefined) {
                this.startAutoClicker(data.upgrades.auto_clicker)
            }
        }

        // Update case progress if provided
        if (data.case_progress !== undefined) {
            state.clicker.caseProgress = data.case_progress
            state.clicker.lastProgress = data.case_progress
        }
    },
    
    async fetchUserData() {
        if (state.isLoading) return
        
        try {
            state.isLoading = true
            const response = await fetch('/api/get_user_data')
            if (!response.ok) throw new Error('Failed to fetch user data')
            
            const data = await response.json()
            this.updateUserData(data)
        } catch (error) {
            console.error('Error fetching user data:', error)
            state.error = error.message
        } finally {
            state.isLoading = false
        }
    },

    async getCaseContents(caseType) {
        try {
            const response = await fetch(`/api/data/case_contents/${caseType}`)
            if (!response.ok) throw new Error('Failed to fetch case contents')
            
            const data = await response.json()
            return data
        } catch (error) {
            console.error('Error fetching case contents:', error)
            return null
        }
    },

    // Add clicker methods
    async handleMoneyClick(isCritical = false) {
        try {
            const response = await fetch('/click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    multiplier: state.clicker.currentMultiplier,
                    is_crit: isCritical
                })
            })

            const data = await response.json()
            if (data.error) throw new Error(data.error)

            // Update state with response data
            this.updateUserData(data)

            return data
        } catch (error) {
            console.error('Error processing click:', error)
            state.error = error.message
            return null
        }
    },

    async handleCaseClick() {
        if (state.clicker.isProcessingClick) return

        state.clicker.pendingClicks++
        state.clicker.isProcessingClick = true

        try {
            const response = await fetch('/case_click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    current_progress: state.clicker.lastProgress
                })
            })

            const data = await response.json()
            if (data.error) throw new Error(data.error)

            // Update progress
            state.clicker.lastProgress = data.progress
            state.clicker.caseProgress = data.progress
            state.clicker.pendingClicks--

            return data
        } catch (error) {
            console.error('Error processing case click:', error)
            state.error = error.message
            return null
        } finally {
            state.clicker.isProcessingClick = false
        }
    },

    async handleBatchCaseClicks(clickCount) {
        try {
            const response = await fetch('/api/batch_case_click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    click_count: clickCount,
                    current_progress: state.clicker.lastProgress
                })
            })

            if (!response.ok) {
                throw new Error('Network response was not ok')
            }

            const data = await response.json()
            if (data.error) throw new Error(data.error)

            // Update progress
            state.clicker.lastProgress = data.progress
            state.clicker.caseProgress = data.progress
            state.clicker.pendingClicks = 0

            return data
        } catch (error) {
            console.error('Error in batch case clicks:', error)
            return null
        }
    },

    async handleChestReward(amount) {
        try {
            const response = await fetch('/chest_reward', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ amount })
            })

            const data = await response.json()
            if (data.error) throw new Error(data.error)

            // Update balance
            state.balance = data.balance

            return data
        } catch (error) {
            console.error('Error processing chest reward:', error)
            state.error = error.message
            return null
        }
    },

    // Clicker state management
    updateClickerMultiplier() {
        state.clicker.comboClickCount++
        
        if (state.clicker.comboClickCount >= state.clicker.clicksToCombo) {
            state.clicker.comboClickCount = 0
            state.clicker.currentMultiplier = Math.min(
                parseFloat((state.clicker.currentMultiplier + 0.1).toFixed(1)),
                state.clicker.maxMultiplier
            )
        }
    },

    resetClickerMultiplier() {
        state.clicker.currentMultiplier = 1.0
        state.clicker.comboClickCount = 0
    },

    async handleBatchMoneyClicks(normalClicks, criticalClicks, autoNormalClicks = 0, autoCriticalClicks = 0) {
        try {
            const response = await fetch('/api/batch_click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    normal_clicks: normalClicks,
                    critical_clicks: criticalClicks,
                    auto_normal_clicks: autoNormalClicks,
                    auto_critical_clicks: autoCriticalClicks
                })
            })
            
            const data = await response.json()
            
            if (data.error) {
                console.error('Error:', data.error)
                return null
            }
            
            // Update store state with new balance
            state.balance = parseFloat(data.balance)
            
            return data
        } catch (error) {
            console.error('Error in handleBatchMoneyClicks:', error)
            return null
        }
    },

    // Auto clicker methods
    queueAutoClick(isCritical) {
        // Don't queue clicks if we're not on the money tab or not in clicker view
        if (state.currentTab !== 'money' || state.currentView !== 'clicker') return

        // Add to queue
        if (isCritical) {
            state.autoClickQueue.critical++
        } else {
            state.autoClickQueue.normal++
        }

        // Process clicks if we have enough queued or enough time has passed
        const now = Date.now()
        const timeSinceLastProcess = now - state.lastAutoClickProcess
        const totalQueuedClicks = state.autoClickQueue.normal + state.autoClickQueue.critical

        if (totalQueuedClicks >= 10 || timeSinceLastProcess >= 1000) {
            this.processAutoClicks()
        }
    },

    startAutoClicker(level) {
        // Clear any existing worker
        this.stopAutoClicker()

        // Only start if we're on the money tab and in clicker view
        if (state.currentTab !== 'money' || state.currentView !== 'clicker') return

        // Check if another tab is already running the auto clicker
        const now = Date.now()
        const lastPing = parseInt(localStorage.getItem('autoClickerLastPing') || '0')
        const currentTab = localStorage.getItem('autoClickerTab')
        
        // If last ping is more than 2 seconds old or no tab is registered,
        // we can take over
        if (now - lastPing > 2000 || !currentTab) {
            // Register this tab as the auto clicker owner
            const tabId = Math.random().toString(36).substring(7)
            localStorage.setItem('autoClickerTab', tabId)
            localStorage.setItem('autoClickerLastPing', now.toString())
            state.autoClickerTabId = tabId

            // Start ping interval to maintain ownership
            if (state.pingInterval) clearInterval(state.pingInterval)
            state.pingInterval = setInterval(() => {
                if (state.autoClickerTabId === localStorage.getItem('autoClickerTab')) {
                    localStorage.setItem('autoClickerLastPing', Date.now().toString())
                } else {
                    // Another tab took over, stop our worker
                    this.stopAutoClicker()
                }
            }, 1000)

            // Create new worker
            state.autoClickerWorker = new Worker(new URL('../workers/autoClicker.js', import.meta.url))

            // Set up message handler
            state.autoClickerWorker.onmessage = (e) => {
                if (e.data.type === 'click') {
                    // Double check we're still on money tab and in clicker view
                    // and we still own the auto clicker
                    if (state.currentTab === 'money' && 
                        state.currentView === 'clicker' && 
                        state.autoClickerTabId === localStorage.getItem('autoClickerTab')) {
                        const criticalChance = state.upgrades.critical_strike / 100
                        const isCritical = Math.random() < criticalChance

                        this.queueAutoClick(isCritical)

                        // Dispatch event for floating text
                        window.dispatchEvent(new CustomEvent('autoClickerText', {
                            detail: {
                                value: state.clicker.baseClickValue * (isCritical ? 4 : 1),
                                isCritical
                            }
                        }))
                    }
                }
            }

            // Start the worker
            state.autoClickerWorker.postMessage({ type: 'start', level })
        }
    },

    stopAutoClicker() {
        if (state.autoClickerWorker) {
            state.autoClickerWorker.postMessage({ type: 'stop' })
            state.autoClickerWorker.terminate()
            state.autoClickerWorker = null
        }
        if (state.pingInterval) {
            clearInterval(state.pingInterval)
            state.pingInterval = null
        }
        if (state.autoClickerTabId === localStorage.getItem('autoClickerTab')) {
            localStorage.removeItem('autoClickerTab')
            localStorage.removeItem('autoClickerLastPing')
        }
        state.autoClickerTabId = null
    },

    async processAutoClicks() {
        if (state.isProcessingAutoClicks || 
            (state.autoClickQueue.normal === 0 && state.autoClickQueue.critical === 0)) {
            return
        }

        state.isProcessingAutoClicks = true
        
        try {
            const response = await fetch('/api/batch_click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    normal_clicks: 0,
                    critical_clicks: 0,
                    auto_normal_clicks: state.autoClickQueue.normal,
                    auto_critical_clicks: state.autoClickQueue.critical
                })
            })

            const data = await response.json()
            if (data.error) throw new Error(data.error)

            // Update balance only
            state.balance = parseFloat(data.balance)
            
            // Clear queues
            state.autoClickQueue.normal = 0
            state.autoClickQueue.critical = 0
            state.lastAutoClickProcess = Date.now()
        } catch (error) {
            console.error('Error processing auto clicks:', error)
        } finally {
            state.isProcessingAutoClicks = false
        }
    },

    updateCurrentTab(tab) {
        state.currentTab = tab
        // Restart auto clicker if needed
        if (tab === 'money' && state.upgrades.auto_clicker > 0) {
            this.startAutoClicker(state.upgrades.auto_clicker)
        } else {
            this.stopAutoClicker()
        }
    },

    // Add method to handle view changes
    updateCurrentView(view) {
        state.currentView = view
        // Stop auto clicker if we leave the clicker view
        if (view !== 'clicker') {
            this.stopAutoClicker()
        } else if (state.currentTab === 'money' && state.upgrades.auto_clicker > 0) {
            // Restart auto clicker if we return to clicker view on money tab
            this.startAutoClicker(state.upgrades.auto_clicker)
        }
    }
}

// Export store with cleanup method
export const useStore = () => ({
    state: readonly(state),
    ...methods,
    cleanup: () => methods.stopAutoClicker()
})

// Initialize auto clicker when store is created
methods.fetchUserData().then(() => {
    if (state.upgrades.auto_clicker > 0) {
        methods.startAutoClicker(state.upgrades.auto_clicker)
    }
}) 