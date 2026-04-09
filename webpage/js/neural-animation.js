// Neural Network Animation System
// Handles pathway animations, node interactions, and scroll effects

class NeuralNetwork {
    constructor() {
        this.svgs = document.querySelectorAll('.neural-dino-svg');
        this.pathways = document.querySelectorAll('.neural-path');
        this.nodes = document.querySelectorAll('.neural-node');
        this.cards = document.querySelectorAll('.pathway-card');
        this.timelineNodes = document.querySelectorAll('.timeline-node');
        this.init();
    }

    init() {
        this.createGradients();
        this.setupPathwayAnimations();
        this.setupCardInteractions();
        this.setupScrollAnimations();
    }

    createGradients() {
        // Create SVG gradients for neural pathways
        const svgs = document.querySelectorAll('.neural-dino-svg, .energy-divider svg');
        
        svgs.forEach((svg) => {
            // Check if gradients already exist
            if (svg.querySelector('#pathGradient')) return;
            
            const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
            
            // Path gradient
            const pathGradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
            pathGradient.setAttribute('id', 'pathGradient');
            pathGradient.setAttribute('x1', '0%');
            pathGradient.setAttribute('y1', '0%');
            pathGradient.setAttribute('x2', '100%');
            pathGradient.setAttribute('y2', '100%');
            
            const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
            stop1.setAttribute('offset', '0%');
            stop1.setAttribute('stop-color', 'rgba(0, 217, 255, 0.3)');
            
            const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
            stop2.setAttribute('offset', '50%');
            stop2.setAttribute('stop-color', 'rgba(0, 217, 255, 0.8)');
            
            const stop3 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
            stop3.setAttribute('offset', '100%');
            stop3.setAttribute('stop-color', 'rgba(107, 46, 255, 0.3)');
            
            pathGradient.appendChild(stop1);
            pathGradient.appendChild(stop2);
            pathGradient.appendChild(stop3);
            
            defs.appendChild(pathGradient);
            
            // Energy gradient
            const energyGradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
            energyGradient.setAttribute('id', 'energyGradient');
            energyGradient.setAttribute('x1', '0%');
            energyGradient.setAttribute('y1', '50%');
            energyGradient.setAttribute('x2', '100%');
            energyGradient.setAttribute('y2', '50%');
            
            const estop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
            estop1.setAttribute('offset', '0%');
            estop1.setAttribute('stop-color', 'rgba(0, 217, 255, 0)');
            
            const estop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
            estop2.setAttribute('offset', '50%');
            estop2.setAttribute('stop-color', 'rgba(0, 217, 255, 0.8)');
            
            const estop3 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
            estop3.setAttribute('offset', '100%');
            estop3.setAttribute('stop-color', 'rgba(0, 217, 255, 0)');
            
            energyGradient.appendChild(estop1);
            energyGradient.appendChild(estop2);
            energyGradient.appendChild(estop3);
            
            defs.appendChild(energyGradient);
            svg.insertBefore(defs, svg.firstChild);
        });
    }

    setupPathwayAnimations() {
        // Stagger pathway animations for a cascading effect
        this.pathways.forEach((pathway, index) => {
            const duration = 3 + (Math.random() * 2);
            pathway.style.animationDuration = duration + 's';
            pathway.style.animationDelay = (index * 0.2) + 's';
        });
    }

    setupCardInteractions() {
        this.cards.forEach((card) => {
            card.addEventListener('mouseenter', () => {
                this.activateCard(card);
            });
            
            card.addEventListener('mouseleave', () => {
                this.deactivateCard(card);
            });
        });
    }

    activateCard(card) {
        const ports = card.querySelectorAll('.port');
        const signalBar = card.querySelector('.signal-bar');
        
        ports.forEach((port, index) => {
            port.style.animation = 'none';
            setTimeout(() => {
                port.style.animation = '';
            }, 10);
        });
        
        if (signalBar) {
            signalBar.style.animationDuration = '0.8s';
        }
    }

    deactivateCard(card) {
        const signalBar = card.querySelector('.signal-bar');
        if (signalBar) {
            signalBar.style.animationDuration = '2s';
        }
    }

    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    this.animateElement(entry.target);
                }
            });
        }, observerOptions);

        // Observe timeline nodes
        this.timelineNodes.forEach((node) => {
            observer.observe(node);
        });

        // Observe cards
        this.cards.forEach((card) => {
            observer.observe(card);
        });

        // Observe integration nodes
        document.querySelectorAll('.integration-node').forEach((node) => {
            observer.observe(node);
        });
    }

    animateElement(element) {
        if (element.classList.contains('timeline-node')) {
            element.classList.add('active');
        }
    }
}

// Initialize neural network system when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new NeuralNetwork();
    
    // Smooth scroll to sections
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
