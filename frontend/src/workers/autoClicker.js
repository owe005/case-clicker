let clickInterval = null;
let msPerClick = 1000;

self.onmessage = function(e) {
    const { type, level } = e.data;
    
    if (type === 'start') {
        // Clear any existing interval
        if (clickInterval) {
            clearInterval(clickInterval);
        }

        // Calculate clicks per second
        const clicksPerSecond = level <= 9 ? level * 0.1 : level - 9;
        msPerClick = 1000 / clicksPerSecond;

        // Start interval
        clickInterval = setInterval(() => {
            self.postMessage({ type: 'click' });
        }, msPerClick);
    } 
    else if (type === 'stop') {
        if (clickInterval) {
            clearInterval(clickInterval);
            clickInterval = null;
        }
    }
}; 