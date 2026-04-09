/**
 * Metrics.js - Animated counter functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    setupMetricCounters();
});

/**
 * Setup animated counters for metrics section
 */
function setupMetricCounters() {
    const metricNumbers = document.querySelectorAll('.metric-number');
    
    if (metricNumbers.length === 0) return;

    // Create observer for metrics section
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.counted) {
                // Mark as counted to avoid re-counting
                entry.target.dataset.counted = 'true';
                
                const targetValue = parseInt(entry.target.getAttribute('data-target'), 10);
                animateCounter(entry.target, targetValue);
            }
        });
    }, observerOptions);

    metricNumbers.forEach(el => {
        observer.observe(el);
    });
}

/**
 * Animate a counter from 0 to target value
 */
function animateCounter(element, targetValue) {
    const duration = 2000; // 2 seconds
    const startTime = Date.now();
    const startValue = 0;
    
    function update() {
        const currentTime = Date.now();
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function (ease-out-cubic)
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        
        let currentValue;
        
        // Handle special cases
        if (targetValue === 1200) {
            // Counter for tests (count up to 1200)
            currentValue = Math.floor(easeProgress * targetValue);
        } else if (targetValue === 93.7) {
            // Coverage percentage
            currentValue = (easeProgress * targetValue).toFixed(1);
        } else if (targetValue === 83.9) {
            // Mutation score
            currentValue = (easeProgress * targetValue).toFixed(1);
        } else if (targetValue === 1250) {
            // Performance multiplier
            currentValue = Math.floor(easeProgress * targetValue);
        } else {
            currentValue = Math.floor(easeProgress * targetValue);
        }
        
        element.textContent = currentValue;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            // Set final value
            if (targetValue === 93.7 || targetValue === 83.9) {
                element.textContent = targetValue.toFixed(1);
            } else {
                element.textContent = targetValue;
            }
        }
    }
    
    update();
}

/**
 * Alternative counter animation with different approach (if needed)
 */
function animateCounterLinear(element, targetValue, duration = 2000) {
    const startValue = 0;
    const startTime = Date.now();
    
    const increment = setInterval(function() {
        const now = Date.now();
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentValue = Math.floor(progress * (targetValue - startValue) + startValue);
        element.textContent = currentValue;
        
        if (progress >= 1) {
            clearInterval(increment);
            element.textContent = targetValue;
        }
    }, 50);
}
