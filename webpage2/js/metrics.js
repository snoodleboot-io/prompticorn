/**
 * Metrics Animation & Counter System
 * Handles animated counters for system metrics
 */

document.addEventListener('DOMContentLoaded', initializeMetrics);

function initializeMetrics() {
    // Observe metrics cards for animation trigger
    const metricsSection = document.querySelector('.metrics-grid');
    
    if (metricsSection) {
        const observerOptions = {
            threshold: 0.3,
            rootMargin: '0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateMetrics();
                    observer.unobserve(metricsSection);
                }
            });
        }, observerOptions);
        
        observer.observe(metricsSection);
    }
}

/**
 * Animate all metric values when visible
 */
function animateMetrics() {
    const metricValues = document.querySelectorAll('.metric-value');
    
    metricValues.forEach(metric => {
        const target = parseInt(metric.dataset.target, 10);
        const duration = 2000; // 2 seconds
        
        animateCounterValue(metric, target, duration);
    });
}

/**
 * Animate a single counter value
 */
function animateCounterValue(element, targetValue, duration = 2000) {
    const startTime = performance.now();
    const startValue = 0;
    const isSuffixed = element.textContent.includes('%') || element.textContent.includes('min');
    const suffix = element.textContent.match(/[a-z%]+/i)?.[0] || '';
    
    function updateValue(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function (easeOutQuad)
        const easedProgress = 1 - Math.pow(1 - progress, 2);
        
        // Calculate current value
        const currentValue = Math.floor(startValue + (targetValue - startValue) * easedProgress);
        
        // Update display
        element.textContent = currentValue + suffix;
        
        // Continue animation if not finished
        if (progress < 1) {
            requestAnimationFrame(updateValue);
        } else {
            element.textContent = targetValue + suffix;
        }
    }
    
    requestAnimationFrame(updateValue);
}

/**
 * Create progress bar animation
 */
export function animateProgressBar(progressElement, targetPercentage, duration = 2000) {
    const startTime = performance.now();
    const fill = progressElement.querySelector('.metric-fill');
    
    if (!fill) return;
    
    function updateProgress(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function
        const easedProgress = 1 - Math.pow(1 - progress, 2);
        
        const currentWidth = targetPercentage * easedProgress;
        fill.style.width = currentWidth + '%';
        
        if (progress < 1) {
            requestAnimationFrame(updateProgress);
        }
    }
    
    requestAnimationFrame(updateProgress);
}

/**
 * Create pulse effect on metric cards
 */
export function pulseMetricCard(cardElement) {
    cardElement.style.animation = 'pulse-glow 2s ease-in-out infinite';
}

/**
 * System status display helper
 */
export class MetricsSystem {
    constructor() {
        this.metrics = {};
        this.isAnimating = false;
    }
    
    /**
     * Register a metric to be displayed
     */
    registerMetric(name, initialValue, maxValue, unit = '') {
        this.metrics[name] = {
            value: initialValue,
            maxValue: maxValue,
            unit: unit,
            element: null
        };
    }
    
    /**
     * Update metric value
     */
    updateMetric(name, newValue) {
        if (this.metrics[name]) {
            this.metrics[name].value = newValue;
        }
    }
    
    /**
     * Get metric data
     */
    getMetric(name) {
        return this.metrics[name];
    }
    
    /**
     * Render metrics to DOM
     */
    renderMetrics(containerSelector) {
        const container = document.querySelector(containerSelector);
        if (!container) return;
        
        const html = Object.entries(this.metrics).map(([name, metric]) => `
            <div class="metric-card">
                <div class="metric-label">${name.toUpperCase()}</div>
                <div class="metric-value">${metric.value}${metric.unit}</div>
                <div class="metric-bar">
                    <div class="metric-fill" style="width: ${(metric.value / metric.maxValue) * 100}%;"></div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }
    
    /**
     * Animate all metrics to their target values
     */
    animateAll(duration = 2000) {
        if (this.isAnimating) return;
        
        this.isAnimating = true;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function (easeOutQuad)
            const easedProgress = 1 - Math.pow(1 - progress, 2);
            
            Object.entries(this.metrics).forEach(([name, metric]) => {
                const currentValue = Math.floor(metric.value * easedProgress);
                const valueElement = document.querySelector(`[data-metric="${name}"]`);
                
                if (valueElement) {
                    valueElement.textContent = currentValue + metric.unit;
                }
            });
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                this.isAnimating = false;
            }
        };
        
        requestAnimationFrame(animate);
    }
}

/**
 * Real-time metrics dashboard
 */
export class MetricsDashboard {
    constructor(containerSelector) {
        this.container = document.querySelector(containerSelector);
        this.metrics = new Map();
        this.updateInterval = null;
    }
    
    /**
     * Add metric to dashboard
     */
    addMetric(name, options = {}) {
        this.metrics.set(name, {
            value: options.value || 0,
            maxValue: options.maxValue || 100,
            label: options.label || name,
            unit: options.unit || '',
            color: options.color || 'cyan'
        });
    }
    
    /**
     * Update metric value with animation
     */
    updateMetricValue(name, newValue, duration = 1000) {
        const metric = this.metrics.get(name);
        if (!metric) return;
        
        const oldValue = metric.value;
        metric.value = newValue;
        
        const startTime = performance.now();
        const element = this.container?.querySelector(`[data-metric-name="${name}"] .metric-value`);
        
        if (element) {
            const animate = (currentTime) => {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const easedProgress = 1 - Math.pow(1 - progress, 2);
                const currentValue = Math.floor(oldValue + (newValue - oldValue) * easedProgress);
                
                element.textContent = currentValue + metric.unit;
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                }
            };
            
            requestAnimationFrame(animate);
        }
    }
    
    /**
     * Render dashboard
     */
    render() {
        if (!this.container) return;
        
        let html = '<div class="metrics-dashboard">';
        
        this.metrics.forEach((metric, name) => {
            const percentage = (metric.value / metric.maxValue) * 100;
            html += `
                <div class="metric-card" data-metric-name="${name}">
                    <div class="metric-label">${metric.label}</div>
                    <div class="metric-value">${metric.value}${metric.unit}</div>
                    <div class="metric-bar">
                        <div class="metric-fill" style="width: ${percentage}%;"></div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        this.container.innerHTML = html;
    }
    
    /**
     * Start real-time updates
     */
    startUpdates(callback, interval = 3000) {
        this.updateInterval = setInterval(() => {
            callback(this);
            this.render();
        }, interval);
    }
    
    /**
     * Stop real-time updates
     */
    stopUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
}

/**
 * Custom metric animations
 */
export const MetricAnimations = {
    /**
     * Pulse animation
     */
    pulse: (element, color = 'cyan', duration = 1500) => {
        element.style.animation = `neon-pulse ${duration}ms ease-in-out infinite`;
    },
    
    /**
     * Glow animation
     */
    glow: (element, intensity = 1) => {
        const colors = {
            cyan: `0 0 ${20 * intensity}px rgba(0, 255, 255, 0.8)`,
            pink: `0 0 ${20 * intensity}px rgba(255, 0, 110, 0.8)`,
            green: `0 0 ${20 * intensity}px rgba(0, 255, 65, 0.8)`
        };
        element.style.boxShadow = colors.cyan;
    },
    
    /**
     * Flip animation
     */
    flip: (element, duration = 600) => {
        element.style.animation = `flip ${duration}ms cubic-bezier(0.23, 1, 0.32, 1)`;
    },
    
    /**
     * Slide animation
     */
    slide: (element, direction = 'left', distance = 20, duration = 500) => {
        const transform = direction === 'left' ? `translateX(-${distance}px)` : `translateX(${distance}px)`;
        element.style.animation = `slide ${duration}ms cubic-bezier(0.23, 1, 0.32, 1)`;
    }
};

// Export classes for use in other scripts
window.MetricsSystem = MetricsSystem;
window.MetricsDashboard = MetricsDashboard;
window.MetricAnimations = MetricAnimations;
