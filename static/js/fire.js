// Procedural fire particle system
const Fire = (() => {
    let canvas, ctx;
    const POOL_SIZE = 180;
    let particles = [];
    let powderColor = null;
    let powderFrames = 0;
    let frameCount = 0;

    // Base fire colors (warm palette)
    const BASE_COLORS = [
        { r: 255, g: 240, b: 180 },  // white-yellow center
        { r: 255, g: 200, b: 60 },   // yellow
        { r: 255, g: 140, b: 30 },   // orange
        { r: 220, g: 80, b: 20 },    // red-orange
        { r: 150, g: 30, b: 10 },    // dark red
    ];

    function init(canvasEl) {
        canvas = canvasEl;
        ctx = canvas.getContext('2d');
        resize();
        window.addEventListener('resize', resize);

        // Pre-fill particle pool
        for (let i = 0; i < POOL_SIZE; i++) {
            particles.push(createParticle());
        }
    }

    function resize() {
        canvas.width = canvas.parentElement.offsetWidth * window.devicePixelRatio;
        canvas.height = canvas.parentElement.offsetHeight * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    }

    function createParticle() {
        const w = canvas.parentElement.offsetWidth;
        const h = canvas.parentElement.offsetHeight;
        const centerX = w / 2;
        const baseY = h * 0.65;

        return {
            x: centerX + (Math.random() - 0.5) * 60,
            y: baseY + (Math.random() - 0.5) * 10,
            vx: (Math.random() - 0.5) * 1.0,
            vy: -(Math.random() * 2.5 + 1.5),
            life: 0,
            maxLife: Math.random() * 40 + 30,
            size: Math.random() * 6 + 3,
            active: true,
        };
    }

    function resetParticle(p) {
        const w = canvas.parentElement.offsetWidth;
        const h = canvas.parentElement.offsetHeight;
        const centerX = w / 2;
        const baseY = h * 0.65;

        p.x = centerX + (Math.random() - 0.5) * 60;
        p.y = baseY + (Math.random() - 0.5) * 10;
        p.vx = (Math.random() - 0.5) * 1.0;
        p.vy = -(Math.random() * 2.5 + 1.5);
        p.life = 0;
        p.maxLife = Math.random() * 40 + 30;
        p.size = Math.random() * 6 + 3;
        p.active = true;
    }

    function getColor(lifeRatio) {
        // If powder effect active, blend with powder color
        if (powderColor && powderFrames > 0) {
            const blend = powderFrames / 60;
            const idx = Math.min(Math.floor(lifeRatio * (BASE_COLORS.length - 1)), BASE_COLORS.length - 1);
            const base = BASE_COLORS[idx];
            const r = Math.round(base.r * (1 - blend) + powderColor.r * blend);
            const g = Math.round(base.g * (1 - blend) + powderColor.g * blend);
            const b = Math.round(base.b * (1 - blend) + powderColor.b * blend);
            return { r, g, b };
        }

        const idx = Math.min(Math.floor(lifeRatio * (BASE_COLORS.length - 1)), BASE_COLORS.length - 1);
        return BASE_COLORS[idx];
    }

    function triggerPowder(hexColor) {
        // Parse hex color
        const r = parseInt(hexColor.slice(1, 3), 16);
        const g = parseInt(hexColor.slice(3, 5), 16);
        const b = parseInt(hexColor.slice(5, 7), 16);
        powderColor = { r, g, b };
        powderFrames = 60;

        // Burst of extra particles
        for (let i = 0; i < 30; i++) {
            const p = particles.find(p => !p.active || p.life > p.maxLife * 0.8);
            if (p) resetParticle(p);
        }
    }

    function render() {
        frameCount++;
        if (powderFrames > 0) powderFrames--;
        if (powderFrames === 0) powderColor = null;

        const w = canvas.parentElement.offsetWidth;
        const h = canvas.parentElement.offsetHeight;
        ctx.clearRect(0, 0, w, h);

        // Ambient glow at fire base
        const centerX = w / 2;
        const baseY = h * 0.65;
        const glowColor = powderColor
            ? `rgba(${powderColor.r}, ${powderColor.g}, ${powderColor.b}, 0.15)`
            : 'rgba(255, 150, 50, 0.15)';
        const glow = ctx.createRadialGradient(centerX, baseY, 10, centerX, baseY, 100);
        glow.addColorStop(0, glowColor);
        glow.addColorStop(1, 'transparent');
        ctx.fillStyle = glow;
        ctx.fillRect(0, 0, w, h);

        for (const p of particles) {
            p.life++;
            if (p.life >= p.maxLife) {
                resetParticle(p);
            }

            p.x += p.vx + Math.sin(frameCount * 0.1 + p.x * 0.01) * 0.3;
            p.y += p.vy;
            p.vy *= 0.99;

            const lifeRatio = p.life / p.maxLife;
            const color = getColor(lifeRatio);
            const alpha = 1 - lifeRatio;
            const size = p.size * (1 - lifeRatio * 0.6);

            ctx.beginPath();
            ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${color.r}, ${color.g}, ${color.b}, ${alpha * 0.8})`;
            ctx.fill();
        }

        // Rising embers (sparse, high)
        for (let i = 0; i < 5; i++) {
            const t = (frameCount * 0.5 + i * 137) % 200;
            const emberX = centerX + Math.sin(t * 0.1 + i) * 40;
            const emberY = baseY - t * 1.2;
            const emberAlpha = Math.max(0, 1 - t / 200) * 0.6;
            if (emberY > 0 && emberAlpha > 0) {
                ctx.beginPath();
                ctx.arc(emberX, emberY, 1.5, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255, 180, 50, ${emberAlpha})`;
                ctx.fill();
            }
        }
    }

    return { init, render, triggerPowder };
})();
