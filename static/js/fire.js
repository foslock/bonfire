// Procedural fire: bezier flame tongues + particle fill + gentle wind fluid dynamics
const Fire = (() => {
    let canvas, ctx;
    let frameCount = 0;
    let windX = 0;
    let windPhase = Math.random() * 100;

    // Particle system for fill and embers
    const POOL_SIZE = 140;
    let particles = [];
    let powderColor = null;
    let powderFrames = 0;

    // --- Noise ---
    function hash(n) {
        const s = Math.sin(n * 127.1 + 311.7) * 43758.5453;
        return s - Math.floor(s);
    }
    function smoothNoise(t) {
        const i = Math.floor(t);
        const f = t - i;
        const u = f * f * (3.0 - 2.0 * f);
        return hash(i) * (1 - u) + hash(i + 1) * u;
    }
    function fbm(t) {
        return smoothNoise(t) * 0.5
             + smoothNoise(t * 2.1 + 3.7) * 0.3
             + smoothNoise(t * 4.5 + 7.3) * 0.2;
    }

    // --- Flame tongue configs (generated once) ---
    const TONGUE_COUNT = 9;
    const tongues = Array.from({ length: TONGUE_COUNT }, (_, i) => ({
        xOffset: (Math.random() - 0.5) * 44,
        noiseOff: Math.random() * 100,
        baseH: 55 + Math.random() * 75,
        baseW: 7 + Math.random() * 9,
    }));

    function init(canvasEl) {
        canvas = canvasEl;
        ctx = canvas.getContext('2d');
        resize();
        window.addEventListener('resize', resize);
        for (let i = 0; i < POOL_SIZE; i++) {
            const p = newParticle();
            p.life = Math.random() * p.maxLife;
            particles.push(p);
        }
    }

    function resize() {
        canvas.width = canvas.parentElement.offsetWidth * window.devicePixelRatio;
        canvas.height = canvas.parentElement.offsetHeight * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    }

    function dims() {
        const w = canvas.parentElement.offsetWidth;
        const h = canvas.parentElement.offsetHeight;
        return { w, h, cx: w / 2, cy: h * 0.65 };
    }

    function newParticle() {
        const { cx, cy } = dims();
        return {
            x: cx + (Math.random() - 0.5) * 48,
            y: cy + (Math.random() - 0.5) * 8,
            vx: (Math.random() - 0.5) * 0.7,
            vy: -(Math.random() * 2.8 + 0.9),
            life: 0,
            maxLife: Math.random() * 40 + 18,
            size: Math.random() * 5 + 2,
            noiseOff: Math.random() * 500,
        };
    }

    function resetParticle(p) {
        const { cx, cy } = dims();
        p.x = cx + (Math.random() - 0.5) * 48;
        p.y = cy + (Math.random() - 0.5) * 8;
        p.vx = (Math.random() - 0.5) * 0.7;
        p.vy = -(Math.random() * 2.8 + 0.9);
        p.life = 0;
        p.maxLife = Math.random() * 40 + 18;
        p.size = Math.random() * 5 + 2;
        p.noiseOff = Math.random() * 500;
    }

    function triggerPowder(hexColor) {
        const r = parseInt(hexColor.slice(1, 3), 16);
        const g = parseInt(hexColor.slice(3, 5), 16);
        const b = parseInt(hexColor.slice(5, 7), 16);
        powderColor = { r, g, b };
        powderFrames = 60;
        for (let i = 0; i < 30; i++) {
            const p = particles.find(p => p.life > p.maxLife * 0.8);
            if (p) resetParticle(p);
        }
    }

    function drawTongues(cx, cy) {
        const t = frameCount * 0.016;

        ctx.save();
        ctx.globalCompositeOperation = 'lighter';

        for (const cfg of tongues) {
            const tx = cx + cfg.xOffset;

            // Flicker: height and width vary with fractal noise
            const hNoise = fbm(t * 1.4 + cfg.noiseOff);
            const height = cfg.baseH * (0.55 + hNoise * 0.95);
            const wNoise = smoothNoise(t * 2.2 + cfg.noiseOff + 50);
            const width = cfg.baseW * (0.75 + wNoise * 0.5);

            // Gentle lean: wind + individual turbulence
            const turb = (smoothNoise(t * 3.5 + cfg.noiseOff + 20) * 2 - 1) * 0.10;
            const lean = windX * 0.07 + turb;

            ctx.save();
            ctx.translate(tx, cy);
            ctx.rotate(lean);

            // Teardrop flame: wide at base, pointed tip upward
            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.bezierCurveTo( width,       -height * 0.30,
                                width * 0.65, -height * 0.78,
                                0,            -height);
            ctx.bezierCurveTo(-width * 0.65, -height * 0.78,
                               -width,        -height * 0.30,
                                0,             0);
            ctx.closePath();

            // Color: white-yellow base → orange → dark red tip (all luminous via 'lighter')
            const grad = ctx.createLinearGradient(0, 0, 0, -height);
            if (powderColor && powderFrames > 0) {
                const b = powderFrames / 60;
                const pr = powderColor.r, pg = powderColor.g, pb = powderColor.b;
                grad.addColorStop(0.00, `rgba(${lerp(255,pr,b)}, ${lerp(255,pg,b)}, ${lerp(200,pb,b)}, 0.90)`);
                grad.addColorStop(0.30, `rgba(${lerp(255,pr,b)}, ${lerp(190,pg,b)}, ${lerp(35,pb,b)}, 0.82)`);
                grad.addColorStop(0.60, `rgba(${lerp(240,pr,b)}, ${lerp(100,pg,b)}, ${lerp(15,pb,b)}, 0.60)`);
                grad.addColorStop(0.88, `rgba(${lerp(170,pr,b)}, ${lerp(30,pg,b)}, ${lerp(5,pb,b)}, 0.30)`);
                grad.addColorStop(1.00, `rgba(${lerp(80,pr,b)},  ${lerp(8,pg,b)},  ${lerp(0,pb,b)},  0.00)`);
            } else {
                grad.addColorStop(0.00, 'rgba(255, 255, 200, 0.90)');
                grad.addColorStop(0.30, 'rgba(255, 190,  35, 0.82)');
                grad.addColorStop(0.60, 'rgba(240, 100,  15, 0.60)');
                grad.addColorStop(0.88, 'rgba(170,  30,   5, 0.30)');
                grad.addColorStop(1.00, 'rgba( 80,   8,   0, 0.00)');
            }
            ctx.fillStyle = grad;
            ctx.fill();
            ctx.restore();
        }

        ctx.restore();
    }

    function lerp(a, b, t) { return Math.round(a + (b - a) * t); }

    function particleColor(lifeRatio) {
        // young = bright white-yellow, old = orange-red
        if (lifeRatio < 0.35) return { r: 255, g: 220, b: 90 };
        if (lifeRatio < 0.65) return { r: 255, g: 130, b: 20 };
        return { r: 200, g: 50, b: 8 };
    }

    function render() {
        frameCount++;
        windPhase += 0.005; // very slow wind evolution

        if (powderFrames > 0) powderFrames--;
        if (powderFrames === 0) powderColor = null;

        // Gentle, slowly shifting horizontal wind
        windX = (fbm(windPhase) * 2 - 1) * 1.1
              + (fbm(windPhase * 3.8 + 10) * 2 - 1) * 0.3;

        const { w, h, cx, cy } = dims();
        ctx.clearRect(0, 0, w, h);

        // Base ambient glow (normal composite)
        const glowColor = (powderColor && powderFrames > 0)
            ? `rgba(${powderColor.r}, ${powderColor.g}, ${powderColor.b}, 0.20)`
            : 'rgba(255, 130, 40, 0.20)';
        const glow = ctx.createRadialGradient(cx, cy, 6, cx, cy, 115);
        glow.addColorStop(0, glowColor);
        glow.addColorStop(1, 'transparent');
        ctx.fillStyle = glow;
        ctx.fillRect(0, 0, w, h);

        // Flame tongues (primary visual)
        drawTongues(cx, cy);

        // Particle fill — small flames between tongues, additive
        ctx.save();
        ctx.globalCompositeOperation = 'lighter';
        for (const p of particles) {
            p.life++;
            if (p.life >= p.maxLife) { resetParticle(p); continue; }

            const lifeRatio = p.life / p.maxLife;
            const heightFactor = Math.max(0, (cy - p.y) / 80);
            const nt = frameCount * 0.02 + p.noiseOff;
            const turbX = (smoothNoise(nt) * 2 - 1) * 0.35;

            p.x += p.vx + windX * heightFactor * 0.10 + turbX;
            p.y += p.vy;
            p.vy *= 0.988;
            p.vx *= 0.96;

            const alpha = Math.pow(1 - lifeRatio, 1.4) * 0.55;
            const size = p.size * (1 - lifeRatio * 0.65);
            if (alpha < 0.01 || size < 0.3) continue;

            let color = particleColor(lifeRatio);
            if (powderColor && powderFrames > 0) {
                const bl = powderFrames / 60;
                color = {
                    r: lerp(color.r, powderColor.r, bl),
                    g: lerp(color.g, powderColor.g, bl),
                    b: lerp(color.b, powderColor.b, bl),
                };
            }

            // Elongated in velocity direction for a "flame streak" look
            const angle = Math.atan2(p.vy, p.vx);
            ctx.save();
            ctx.translate(p.x, p.y);
            ctx.rotate(angle);
            ctx.beginPath();
            // semi-axis along velocity = 1.5×size, perpendicular = 0.45×size
            ctx.ellipse(0, 0, size * 1.5, size * 0.45, 0, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${color.r}, ${color.g}, ${color.b}, ${alpha})`;
            ctx.fill();
            ctx.restore();
        }
        ctx.restore();

        // Rising embers — drift with wind
        for (let i = 0; i < 10; i++) {
            const et = (frameCount * 0.42 + i * 137) % 270;
            const windDrift = windX * (et / 270) * 22;
            const ex = cx + Math.sin(et * 0.09 + i * 2.3) * 22 + windDrift;
            const ey = cy - et * 0.92;
            const ea = Math.max(0, 1 - et / 270) * 0.88;
            if (ey > 0 && ea > 0.02) {
                ctx.beginPath();
                ctx.arc(ex, ey, 1.2, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255, 195, 70, ${ea})`;
                ctx.fill();
            }
        }
    }

    return { init, render, triggerPowder };
})();
