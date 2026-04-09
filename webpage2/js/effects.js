/**
 * Cyberpunk Effects & Animations
 * Handles neon glows, scanline effects, and visual effects
 */

// Initialize effects on load
document.addEventListener('DOMContentLoaded', initializeEffects);

function initializeEffects() {
    // Initialize particle effects
    initializeParticles();
    
    // Initialize scroll reveal animations
    initializeScrollReveal();
    
    // Initialize neon flicker for text
    initializeNeonFlicker();
    
    // Add scroll listener for effects
    window.addEventListener('scroll', handleScrollEffects, { passive: true });
}

/**
 * Create animated particle background (optional subtle effect)
 */
function initializeParticles() {
    // This is kept minimal to avoid performance issues
    // The grid background already provides visual interest
}

/**
 * Scroll reveal animation for sections
 */
function initializeScrollReveal() {
    const revealElements = document.querySelectorAll(
        '.matrix-card, .protocol-card, .metric-card, .combat-card, .faq-item'
    );

    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('scroll-reveal-active');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    revealElements.forEach(element => {
        element.classList.add('scroll-reveal');
        observer.observe(element);
    });
}

/**
 * Subtle neon flicker effect for important text
 */
function initializeNeonFlicker() {
    const flickerElements = document.querySelectorAll('.glowing-text, .neon-text');
    
    flickerElements.forEach(element => {
        // Occasionally apply a subtle flicker
        if (Math.random() > 0.5) {
            element.style.animation = 'neon-flicker 0.15s ease-in-out infinite';
        }
    });
}

/**
 * Handle scroll-based visual effects
 */
function handleScrollEffects() {
    const scrollY = window.scrollY;
    
    // Parallax effect for hero section
    const heroSection = document.querySelector('.hero');
    if (heroSection && scrollY < window.innerHeight) {
        heroSection.style.transform = `translateY(${scrollY * 0.5}px)`;
    }
    
    // Optional: Add subtle glow intensity based on scroll position
    updateScrollIndicator(scrollY);
}

/**
 * Update visual indicator of scroll position
 */
function updateScrollIndicator(scrollY) {
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    const scrollPercentage = (scrollY / maxScroll) * 100;
    
    // This could be used for a progress bar or other indicator
    // Currently just for tracking
    document.documentElement.style.setProperty('--scroll-percentage', scrollPercentage);
}

/**
 * Utility: Trigger glow effect on element
 */
export function triggerGlowEffect(element) {
    element.style.animation = 'neon-pulse 2s ease-in-out';
    setTimeout(() => {
        element.style.animation = '';
    }, 2000);
}

/**
 * Utility: Add hover glow to element
 */
export function addHoverGlow(element, color = 'cyan') {
    element.addEventListener('mouseenter', () => {
        element.style.textShadow = `0 0 10px var(--color-${color})`;
    });
    
    element.addEventListener('mouseleave', () => {
        element.style.textShadow = '';
    });
}

/**
 * Create circuit pattern effect on elements
 */
export function addCircuitPattern(element) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = element.offsetWidth;
    canvas.height = element.offsetHeight;
    
    // Draw circuit pattern
    ctx.strokeStyle = 'rgba(0, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    
    // Simple grid pattern
    const gridSize = 30;
    for (let x = 0; x < canvas.width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
    }
    
    for (let y = 0; y < canvas.height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
    }
    
    return canvas.toDataURL();
}

/**
 * Data attributes for custom animations
 * Usage: <div data-animation="fade-up" data-delay="0.2s">
 */
export function initializeDataAnimations() {
    const animatedElements = document.querySelectorAll('[data-animation]');
    
    animatedElements.forEach(element => {
        const animationName = element.dataset.animation;
        const delay = element.dataset.delay || '0s';
        
        element.style.animation = `${animationName} 0.8s cubic-bezier(0.23, 1, 0.32, 1) ${delay} forwards`;
    });
}

/**
 * Initialize glitch effect on text elements
 */
export function initializeGlitchEffect() {
    const glitchElements = document.querySelectorAll('[data-glitch]');
    
    glitchElements.forEach(element => {
        const originalText = element.textContent;
        element.setAttribute('data-text', originalText);
        element.classList.add('glitch');
    });
}

/**
 * Create holographic effect background
 */
export function createHolographicBackground(element) {
    element.classList.add('holographic');
}

/**
 * Animate counter/metrics
 */
export function animateCounter(element, target, duration = 2000) {
    const startValue = 0;
    const startTime = performance.now();
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const current = Math.floor(startValue + (target - startValue) * progress);
        
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target;
        }
    }
    
    requestAnimationFrame(updateCounter);
}

/**
 * Add glow shadow to element
 */
export function addGlowShadow(element, color = 'cyan', intensity = 1) {
    const colors = {
        cyan: 'rgba(0, 255, 255, ' + (0.5 * intensity) + ')',
        pink: 'rgba(255, 0, 110, ' + (0.5 * intensity) + ')',
        green: 'rgba(0, 255, 65, ' + (0.5 * intensity) + ')'
    };
    
    element.style.boxShadow = `0 0 ${20 * intensity}px ${colors[color]}, 0 0 ${40 * intensity}px ${colors[color]}`;
}

/**
 * Pulse animation for status indicators
 */
export function startStatusPulse(element) {
    element.style.animation = 'status-pulse 1.5s ease-in-out infinite';
}

/**
 * Create animated data stream effect
 */
export function createDataStream(container) {
    const characters = '01';
    const stream = document.createElement('div');
    stream.style.cssText = `
        position: absolute;
        color: var(--color-cyan);
        opacity: 0.3;
        font-size: 12px;
        overflow: hidden;
        white-space: nowrap;
        letter-spacing: 2px;
    `;
    
    let text = '';
    for (let i = 0; i < 20; i++) {
        text += characters[Math.floor(Math.random() * characters.length)];
    }
    
    stream.textContent = text;
    container.appendChild(stream);
    
    // Animate the stream
    let y = 0;
    function animate() {
        y += 2;
        stream.style.transform = `translateY(${y}px)`;
        
        if (y < 100) {
            requestAnimationFrame(animate);
        } else {
            stream.remove();
        }
    }
    
    animate();
}

/**
 * Initialize interactive elements
 */
export function initializeInteractive() {
    // Hover effects on cards
    const hoverCards = document.querySelectorAll(
        '.matrix-card, .protocol-card, .metric-card, .combat-card'
    );
    
    hoverCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    });
}

// Export all functions for use in other scripts
window.CyberpunkEffects = {
    triggerGlowEffect,
    addHoverGlow,
    addCircuitPattern,
    initializeDataAnimations,
    initializeGlitchEffect,
    createHolographicBackground,
    animateCounter,
    addGlowShadow,
    startStatusPulse,
    createDataStream,
    initializeInteractive
};
