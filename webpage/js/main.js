/**
 * Main.js - Smooth scrolling, animations, and interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    setupSmoothScroll();
    
    // Animate elements on scroll
    setupIntersectionObserver();
    
    // Add active state to nav links
    setupNavigation();
});

/**
 * Setup smooth scrolling for anchor links
 */
function setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const offset = 80; // Account for fixed navbar
                const targetPosition = target.offsetTop - offset;
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Setup intersection observer for scroll animations
 */
function setupIntersectionObserver() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateElement(entry.target);
            }
        });
    }, observerOptions);

    // Observe all cards, sections, and animated elements
    const elementsToObserve = document.querySelectorAll(
        '.problem-card, .benefit-card, .matters-card, .metric-card, ' +
        '.builder-card, .faq-item, .proof-stat'
    );

    elementsToObserve.forEach(el => {
        observer.observe(el);
    });
}

/**
 * Animate element on scroll
 */
function animateElement(element) {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    
    // Trigger animation
    setTimeout(() => {
        element.style.transition = 'all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)';
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    }, 50);
}

/**
 * Setup navigation active state
 */
function setupNavigation() {
    window.addEventListener('scroll', updateNavigation);
    updateNavigation();
}

function updateNavigation() {
    const scrollPosition = window.scrollY;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        
        // Skip GitHub links
        if (!href || href.startsWith('http') || href === '#') {
            return;
        }
        
        const section = document.querySelector(href);
        
        if (section) {
            const sectionTop = section.offsetTop - 100;
            const sectionBottom = sectionTop + section.offsetHeight;
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                link.style.color = 'var(--color-accent-primary)';
            } else {
                link.style.color = 'var(--color-text-secondary)';
            }
        }
    });
}

/**
 * Setup staggered animations for hero
 */
function setupHeroAnimation() {
    const heroText = document.querySelector('.hero-text');
    const heroVisual = document.querySelector('.hero-visual');
    
    if (heroText) {
        heroText.style.opacity = '0';
        heroText.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            heroText.style.transition = 'all 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)';
            heroText.style.opacity = '1';
            heroText.style.transform = 'translateX(0)';
        }, 100);
    }
    
    if (heroVisual) {
        heroVisual.style.opacity = '0';
        heroVisual.style.transform = 'translateX(20px)';
        
        setTimeout(() => {
            heroVisual.style.transition = 'all 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)';
            heroVisual.style.opacity = '1';
            heroVisual.style.transform = 'translateX(0)';
        }, 200);
    }
}

// Run hero animation on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupHeroAnimation);
} else {
    setupHeroAnimation();
}

/**
 * Scroll indicator (optional enhancement)
 */
function updateScrollProgress() {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollPercent = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    
    // Could add a progress bar if desired
    document.documentElement.style.setProperty('--scroll-progress', scrollPercent + '%');
}

window.addEventListener('scroll', updateScrollProgress);
