// Powder toss visual effect
const Powder = (() => {
    let canvas, ctx;
    let sparks = [];

    function init(canvasEl) {
        canvas = canvasEl;
        ctx = canvas.getContext('2d');
        resize();
        window.addEventListener('resize', resize);
    }

    function resize() {
        canvas.width = canvas.offsetWidth * window.devicePixelRatio;
        canvas.height = canvas.offsetHeight * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    }

    function trigger(hexColor) {
        const r = parseInt(hexColor.slice(1, 3), 16);
        const g = parseInt(hexColor.slice(3, 5), 16);
        const b = parseInt(hexColor.slice(5, 7), 16);

        const w = canvas.offsetWidth;
        const h = canvas.offsetHeight;
        const startX = w / 2;
        const startY = h * 0.8;     // from user's "hands" at bottom
        const targetX = w / 2;
        const targetY = h * 0.42;   // toward the bonfire

        // Create arc of sparks
        for (let i = 0; i < 25; i++) {
            sparks.push({
                x: startX + (Math.random() - 0.5) * 40,
                y: startY,
                vx: (targetX - startX) / 30 + (Math.random() - 0.5) * 3,
                vy: (targetY - startY) / 30 - Math.random() * 4,
                gravity: 0.15,
                r, g, b,
                life: 0,
                maxLife: 30 + Math.random() * 20,
                size: Math.random() * 3 + 1.5,
            });
        }
    }

    function render() {
        const w = canvas.offsetWidth;
        const h = canvas.offsetHeight;
        ctx.clearRect(0, 0, w, h);

        for (let i = sparks.length - 1; i >= 0; i--) {
            const s = sparks[i];
            s.life++;
            s.x += s.vx;
            s.y += s.vy;
            s.vy += s.gravity;
            s.vx *= 0.98;

            const alpha = 1 - (s.life / s.maxLife);
            if (alpha <= 0) {
                sparks.splice(i, 1);
                continue;
            }

            ctx.beginPath();
            ctx.arc(s.x, s.y, s.size * alpha, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${s.r}, ${s.g}, ${s.b}, ${alpha})`;
            ctx.fill();

            // Glow trail
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.size * alpha * 2, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${s.r}, ${s.g}, ${s.b}, ${alpha * 0.2})`;
            ctx.fill();
        }
    }

    return { init, trigger, render };
})();
