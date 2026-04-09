// Combat Systems Animation
// Tactical HUD effects and weapon readiness animations

class CombatSystem {
    constructor() {
        this.weaponCards = document.querySelectorAll('.weapon-card');
        this.targetingBoxes = document.querySelectorAll('.targeting-box');
        this.init();
    }

    init() {
        this.setupWeaponInteractions();
        this.setupTargetingEffects();
        this.startCombatPulse();
    }

    setupWeaponInteractions() {
        this.weaponCards.forEach((card, index) => {
            card.addEventListener('mouseenter', () => {
                this.activateWeapon(card, index);
            });
            
            card.addEventListener('mouseleave', () => {
                this.deactivateWeapon(card);
            });
        });
    }

    activateWeapon(card, index) {
        // Highlight the weapon on hover
        card.style.boxShadow = `
            0 0 30px rgba(0, 255, 0, 0.5),
            0 0 60px rgba(0, 255, 255, 0.3),
            inset 0 0 20px rgba(0, 255, 0, 0.1)
        `;
        
        // Trigger charge effect
        const chargeLevel = card.querySelector('.charge-level');
        if (chargeLevel) {
            chargeLevel.style.animationDuration = '0.5s';
        }
    }

    deactivateWeapon(card) {
        const chargeLevel = card.querySelector('.charge-level');
        if (chargeLevel) {
            chargeLevel.style.animationDuration = '3s';
        }
    }

    setupTargetingEffects() {
        this.targetingBoxes.forEach((box) => {
            const crosshair = box.querySelector('.crosshair');
            if (crosshair) {
                box.addEventListener('mouseenter', () => {
                    crosshair.style.animation = 'crosshair-spin 1s linear infinite';
                });
                
                box.addEventListener('mouseleave', () => {
                    crosshair.style.animation = 'none';
                });
            }
        });
    }

    startCombatPulse() {
        // Add CSS animation for crosshair spin
        if (!document.querySelector('#combat-styles')) {
            const style = document.createElement('style');
            style.id = 'combat-styles';
            style.textContent = `
                @keyframes crosshair-spin {
                    0% { transform: translate(-50%, -50%) rotate(0deg); }
                    100% { transform: translate(-50%, -50%) rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
    }
}

// Initialize combat system
document.addEventListener('DOMContentLoaded', () => {
    new CombatSystem();
    
    // Smooth scroll for navigation
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
});
