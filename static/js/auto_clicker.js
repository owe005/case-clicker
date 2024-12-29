// Global state
let autoClickerInterval = null;
let baseClickValue = 0.01;
let criticalStrikeLevel = 0;

// Function to perform auto click
async function performAutoClick() {
    try {
        // Calculate critical strike
        let isCritical = false;
        const criticalChance = criticalStrikeLevel / 100;
        
        if (criticalChance > 0) {
            const roll = Math.random();
            if (roll < criticalChance) {
                isCritical = true;
            }
        }

        const response = await fetch('/click', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                amount: 1.0, // Auto clicks always use base multiplier
                critical: isCritical,
                auto: true // Flag to indicate this is an auto click
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            console.error(data.error);
            return;
        }
        
        // Update balance display if it exists
        const balanceElement = document.getElementById('balance');
        if (balanceElement) {
            balanceElement.textContent = data.balance.toFixed(2);
        }
        
        // Update rank progress if provided and elements exist
        if (data.rank !== undefined) {
            const rankInfo = document.querySelector('.current-rank');
            const expInfo = document.querySelector('.exp-info');
            const progressFill = document.querySelector('.progress-fill');
            
            if (rankInfo) rankInfo.textContent = data.rankName;
            
            if (expInfo && progressFill) {
                if (data.nextRankExp) {
                    expInfo.textContent = `${data.exp}/${data.nextRankExp} EXP`;
                    progressFill.style.width = `${(data.exp / data.nextRankExp) * 100}%`;
                } else {
                    expInfo.textContent = 'MAX RANK';
                    progressFill.style.width = '100%';
                }
            }
        }
    } catch (error) {
        console.error('Error in auto click:', error);
    }
}

// Function to start/update auto clicker
function startAutoClicker(level) {
    // Clear any existing interval
    if (autoClickerInterval) {
        clearInterval(autoClickerInterval);
        autoClickerInterval = null;
    }
    
    // If level is greater than 0, start new interval
    if (level > 0) {
        let interval;
        
        if (level <= 9) {
            interval = (11 - level) * 1000; // Convert seconds to milliseconds
        } else {
            const clicksPerSecond = level - 8;
            interval = 1000 / clicksPerSecond;
        }
        
        autoClickerInterval = setInterval(performAutoClick, interval);
    }
}

// Initialize auto clicker on page load
async function initializeAutoClicker() {
    try {
        const response = await fetch('/get_upgrades');
        const data = await response.json();
        
        if (data) {
            baseClickValue = 0.01 * (1.5 ** (data.click_value - 1));
            criticalStrikeLevel = data.critical_strike || 0;
            startAutoClicker(data.auto_clicker || 0);
        }
    } catch (error) {
        console.error('Error initializing auto clicker:', error);
    }
}

// Listen for upgrade purchases
window.addEventListener('upgradesPurchased', function(e) {
    const upgrades = e.detail;
    baseClickValue = 0.01 * (1.5 ** (upgrades.click_value - 1));
    criticalStrikeLevel = upgrades.critical_strike || 0;
    startAutoClicker(upgrades.auto_clicker);
});

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeAutoClicker); 