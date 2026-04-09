/**
 * Main JavaScript - Navigation, Interactivity, and Core Functionality
 * Cyberpunk Landing Page
 */

document.addEventListener('DOMContentLoaded', initializePage);

// ============================================================================
// INITIALIZATION
// ============================================================================

function initializePage() {
    setupNavigation();
    setupSmoothScroll();
    setupScrollSpy();
    setupFAQInteractions();
    setupButtonInteractions();
    setupHoverEffects();
}

// ============================================================================
// NAVIGATION
// ============================================================================

/**
 * Setup navigation menu behavior
 */
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const navMenu = document.querySelector('.nav-menu');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            link.classList.add('active');
            
            // Close menu if on mobile
            if (window.innerWidth < 768) {
                navMenu?.classList.remove('active');
            }
        });
    });
    
    // Highlight current section on load
    updateScrollSpy();
}

/**
 * Smooth scroll to sections
 */
function setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            const href = anchor.getAttribute('href');
            
            // Skip if it's just a hash
            if (href === '#') return;
            
            e.preventDefault();
            
            const target = document.querySelector(href);
            if (target) {
                const offsetTop = target.offsetTop - 100; // Account for sticky nav
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// ============================================================================
// SCROLL SPY
// ============================================================================

/**
 * Setup scroll spy to highlight current section in nav
 */
function setupScrollSpy() {
    window.addEventListener('scroll', updateScrollSpy, { passive: true });
}

/**
 * Update scroll spy highlighting
 */
function updateScrollSpy() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');
    
    let currentSection = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop - 150;
        if (window.scrollY >= sectionTop) {
            currentSection = section.getAttribute('id');
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href').substring(1);
        if (href === currentSection) {
            link.classList.add('active');
        }
    });
}

// ============================================================================
// FAQ INTERACTIONS
// ============================================================================

/**
 * Setup FAQ accordion interactions
 */
function setupFAQInteractions() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        
        if (question) {
            question.addEventListener('click', () => {
                // Toggle current item
                item.classList.toggle('active');
                
                // Close other items
                faqItems.forEach(other => {
                    if (other !== item) {
                        other.classList.remove('active');
                    }
                });
            });
        }
    });
}

// ============================================================================
// BUTTON & CTA INTERACTIONS
// ============================================================================

/**
 * Setup button interactions and effects
 */
function setupButtonInteractions() {
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        // Add ripple effect on click
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                background: currentColor;
                border-radius: 50%;
                left: ${x}px;
                top: ${y}px;
                opacity: 0.5;
                animation: ripple 0.6s ease-out;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
}

// ============================================================================
// HOVER EFFECTS
// ============================================================================

/**
 * Setup hover effects for interactive elements
 */
function setupHoverEffects() {
    // Cards hover effect
    const interactiveCards = document.querySelectorAll(
        '.matrix-card, .protocol-card, .metric-card, .combat-card, .faq-item'
    );
    
    interactiveCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    });
    
    // Neon glow on hover for text
    const glowElements = document.querySelectorAll('.neon-hover');
    glowElements.forEach(element => {
        element.addEventListener('mouseenter', addNeonGlow);
        element.addEventListener('mouseleave', removeNeonGlow);
    });
}

/**
 * Add neon glow effect
 */
function addNeonGlow(e) {
    const element = e.target;
    element.style.color = 'var(--color-cyan)';
    element.style.textShadow = 'var(--text-glow-cyan)';
}

/**
 * Remove neon glow effect
 */
function removeNeonGlow(e) {
    const element = e.target;
    element.style.color = 'var(--color-text)';
    element.style.textShadow = 'none';
}

// ============================================================================
// ANIMATION UTILITIES
// ============================================================================

/**
 * Trigger glow animation on element
 */
export function triggerGlowAnimation(element, duration = 2000) {
    element.style.animation = `neon-pulse ${duration}ms ease-in-out`;
    setTimeout(() => {
        element.style.animation = '';
    }, duration);
}

/**
 * Trigger bounce animation
 */
export function triggerBounce(element, duration = 600) {
    element.style.animation = `bounce ${duration}ms cubic-bezier(0.68, -0.55, 0.265, 1.55)`;
    setTimeout(() => {
        element.style.animation = '';
    }, duration);
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Detect if element is in viewport
 */
export function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.bottom >= 0
    );
}

/**
 * Get random element from array
 */
export function getRandomElement(array) {
    return array[Math.floor(Math.random() * array.length)];
}

/**
 * Debounce function for performance
 */
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function for scroll events
 */
export function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ============================================================================
// RESPONSIVE BEHAVIOR
// ============================================================================

/**
 * Handle responsive behavior
 */
function handleResponsive() {
    const width = window.innerWidth;
    
    // Adjust navigation for mobile
    if (width < 768) {
        // Mobile-specific adjustments
    } else {
        // Desktop-specific adjustments
    }
}

window.addEventListener('resize', debounce(handleResponsive, 250));

// ============================================================================
// PERFORMANCE MONITORING
// ============================================================================

/**
 * Log performance metrics
 */
function logPerformanceMetrics() {
    if (window.performance && window.performance.timing) {
        const timing = window.performance.timing;
        const loadTime = timing.loadEventEnd - timing.navigationStart;
        console.log(`Page load time: ${loadTime}ms`);
    }
}

// Call on page load
window.addEventListener('load', logPerformanceMetrics);

// ============================================================================
// ACCESSIBILITY
// ============================================================================

/**
 * Keyboard navigation support
 */
document.addEventListener('keydown', (e) => {
    // Escape key to close any open modals or menus
    if (e.key === 'Escape') {
        const activeModals = document.querySelectorAll('.modal.active');
        activeModals.forEach(modal => {
            modal.classList.remove('active');
        });
    }
    
    // Tab navigation for scroll spy
    if (e.key === 'Tab') {
        updateScrollSpy();
    }
});

// ============================================================================
// EASTER EGGS & FUN STUFF
// ============================================================================

/**
 * Konami code easter egg
 */
const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
let konamiIndex = 0;

document.addEventListener('keydown', (e) => {
    if (e.key === konamiCode[konamiIndex]) {
        konamiIndex++;
        if (konamiIndex === konamiCode.length) {
            triggerKonamiEasterEgg();
            konamiIndex = 0;
        }
    } else {
        konamiIndex = 0;
    }
});

function triggerKonamiEasterEgg() {
    console.log('%c🦖 SYSTEM BREACH DETECTED 🦖', 'color: #00ff41; font-size: 20px; font-weight: bold; text-shadow: 0 0 10px #00ff41;');
    console.log('%cNEURAL PATHWAYS SYNCHRONIZED', 'color: #00ffff; font-size: 14px; font-weight: bold;');
    console.log('%cWELCOME TO THE UNIFIED PROMPT NETWORK', 'color: #ff006e; font-size: 14px; font-weight: bold;');
    
    // Visual effect
    const html = document.documentElement;
    html.style.filter = 'hue-rotate(360deg)';
    setTimeout(() => {
        html.style.filter = 'none';
    }, 1000);
}

// ============================================================================
// ANALYTICS & TRACKING (Optional)
// ============================================================================

/**
 * Track user interactions (optional - remove if privacy-focused)
 */
function trackInteraction(eventName, eventData = {}) {
    // Send to analytics service if configured
    // Example: window.gtag?.('event', eventName, eventData);
    console.debug('Interaction tracked:', eventName, eventData);
}

// Track section views
document.querySelectorAll('section[id]').forEach(section => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                trackInteraction('section_view', {
                    section: entry.target.id
                });
            }
        });
    });
    observer.observe(section);
});

// ============================================================================
// EXPORT FOR MODULAR USE
// ============================================================================

// Make utilities available globally if needed
window.PageUtils = {
    triggerGlowAnimation,
    triggerBounce,
    isInViewport,
    getRandomElement,
    debounce,
    throttle,
    trackInteraction,
    setupNavigation,
    updateScrollSpy
};
