// Sky renderer: stars + moon
const Sky = (() => {
    let canvas, ctx;
    let stars = [];
    let moonPhase = 0.5;
    let frameCount = 0;

    function init(canvasEl) {
        canvas = canvasEl;
        ctx = canvas.getContext('2d');
        resize();
        window.addEventListener('resize', resize);
        generateStars();
    }

    function resize() {
        canvas.width = canvas.offsetWidth * window.devicePixelRatio;
        canvas.height = canvas.offsetHeight * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    }

    function generateStars() {
        stars = [];
        for (let i = 0; i < 120; i++) {
            stars.push({
                x: Math.random(),
                y: Math.random(),
                size: Math.random() * 2 + 0.5,
                speed: Math.random() * 0.02 + 0.005,
                phase: Math.random() * Math.PI * 2,
                brightness: Math.random() * 0.5 + 0.5,
            });
        }
    }

    function setMoonPhase(phase) {
        moonPhase = phase;
    }

    function drawMoon(w, h) {
        const moonX = w * 0.8;
        const moonY = h * 0.15;
        const radius = Math.min(w, h) * 0.08;

        // Glow
        const glow = ctx.createRadialGradient(moonX, moonY, radius * 0.5, moonX, moonY, radius * 3);
        glow.addColorStop(0, 'rgba(200, 210, 230, 0.08)');
        glow.addColorStop(1, 'transparent');
        ctx.fillStyle = glow;
        ctx.fillRect(moonX - radius * 3, moonY - radius * 3, radius * 6, radius * 6);

        // Moon body
        ctx.save();
        ctx.beginPath();
        ctx.arc(moonX, moonY, radius, 0, Math.PI * 2);
        ctx.fillStyle = '#d4d0c8';
        ctx.fill();

        // Shadow overlay based on phase
        ctx.clip();
        const phase = moonPhase;
        const shadowX = Math.cos(phase * Math.PI * 2) * radius;

        ctx.beginPath();
        // Draw shadow using two arcs
        if (phase < 0.5) {
            // Waxing: shadow on the left
            ctx.arc(moonX, moonY, radius, -Math.PI / 2, Math.PI / 2, false);
            ctx.ellipse(moonX, moonY, Math.abs(shadowX), radius, 0, Math.PI / 2, -Math.PI / 2, shadowX > 0);
        } else {
            // Waning: shadow on the right
            ctx.arc(moonX, moonY, radius, Math.PI / 2, -Math.PI / 2, false);
            ctx.ellipse(moonX, moonY, Math.abs(shadowX), radius, 0, -Math.PI / 2, Math.PI / 2, shadowX < 0);
        }
        ctx.closePath();
        ctx.fillStyle = '#0c0c14';
        ctx.fill();

        ctx.restore();
    }

    function render() {
        frameCount++;
        const w = canvas.offsetWidth;
        const h = canvas.offsetHeight;

        // Sky gradient
        const grad = ctx.createLinearGradient(0, 0, 0, h);
        grad.addColorStop(0, '#05050d');
        grad.addColorStop(0.6, '#0a0a18');
        grad.addColorStop(1, '#0f0e15');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, w, h);

        // Stars
        for (const star of stars) {
            const twinkle = Math.sin(frameCount * star.speed + star.phase) * 0.3 + 0.7;
            const alpha = star.brightness * twinkle;
            ctx.beginPath();
            ctx.arc(star.x * w, star.y * h, star.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(220, 225, 240, ${alpha})`;
            ctx.fill();
        }

        // Moon
        drawMoon(w, h);
    }

    return { init, setMoonPhase, render };
})();
