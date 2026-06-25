// static/js/particles.js
// Soft Abstract Data Mesh (Hugging Face / Databricks Style)
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('particles');
    if(!canvas) return;
    const ctx = canvas.getContext('2d');
    
    let width, height;
    let particles = [];
    
    // Config
    const config = {
        count: Math.min(window.innerWidth / 15, 80),
        distance: 150,
        color: getComputedStyle(document.body).getPropertyValue('--border-light').trim() || '#e2e8f0',
        nodeColor: getComputedStyle(document.body).getPropertyValue('--accent-indigo').trim() || '#4f46e5',
        mouseRadius: 200
    };
    
    let mouse = { x: -1000, y: -1000 };
    
    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }
    
    window.addEventListener('resize', resize);
    window.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });
    window.addEventListener('mouseout', () => {
        mouse.x = -1000;
        mouse.y = -1000;
    });
    
    class Particle {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * 0.5;
            this.vy = (Math.random() - 0.5) * 0.5;
            this.baseRadius = Math.random() * 2 + 1;
            this.radius = this.baseRadius;
        }
        
        update() {
            this.x += this.vx;
            this.y += this.vy;
            
            if (this.x < 0 || this.x > width) this.vx *= -1;
            if (this.y < 0 || this.y > height) this.vy *= -1;
            
            // Soft repel from mouse
            let dx = mouse.x - this.x;
            let dy = mouse.y - this.y;
            let dist = Math.sqrt(dx * dx + dy * dy);
            
            if (dist < config.mouseRadius) {
                const force = (config.mouseRadius - dist) / config.mouseRadius;
                this.x -= (dx / dist) * force * 1.5;
                this.y -= (dy / dist) * force * 1.5;
                this.radius = this.baseRadius + (force * 3);
            } else {
                this.radius = this.baseRadius;
            }
        }
        
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = config.nodeColor;
            ctx.globalAlpha = 0.3;
            ctx.fill();
            ctx.globalAlpha = 1.0;
        }
    }
    
    function init() {
        resize();
        particles = [];
        for (let i = 0; i < config.count; i++) {
            particles.push(new Particle());
        }
    }
    
    function animate() {
        ctx.clearRect(0, 0, width, height);
        
        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();
            
            for (let j = i + 1; j < particles.length; j++) {
                let dx = particles[i].x - particles[j].x;
                let dy = particles[i].y - particles[j].y;
                let dist = Math.sqrt(dx * dx + dy * dy);
                
                if (dist < config.distance) {
                    ctx.beginPath();
                    ctx.strokeStyle = config.color;
                    ctx.globalAlpha = 1 - (dist / config.distance);
                    ctx.lineWidth = 1;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                    ctx.globalAlpha = 1.0;
                }
            }
        }
        requestAnimationFrame(animate);
    }
    
    setTimeout(() => {
        config.color = getComputedStyle(document.body).getPropertyValue('--border-light').trim();
        config.nodeColor = getComputedStyle(document.body).getPropertyValue('--text-muted').trim();
        init();
        animate();
    }, 100);
});
