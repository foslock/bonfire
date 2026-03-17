// Knight sprite positioning and management
const Knights = (() => {
    const container = () => document.getElementById('knights-container');
    let knightElements = {};  // id -> DOM element

    // Placeholder silhouette SVG for when sprites don't exist
    function placeholderSrc(spriteId) {
        // Try the real sprite first; the onerror handler swaps to a placeholder
        return `/static/sprites/knight_${spriteId}.png`;
    }

    function createKnightElement(user) {
        const el = document.createElement('div');
        el.className = 'knight';
        el.dataset.userId = user.id;

        const img = document.createElement('img');
        img.src = placeholderSrc(user.sprite_id);
        img.alt = user.name;
        img.onerror = function() {
            // Replace with a placeholder silhouette
            this.style.display = 'none';
            const placeholder = document.createElement('div');
            placeholder.style.cssText = `
                width: 80px; height: 120px;
                background: linear-gradient(to bottom, #2a2520, #1a1815);
                border-radius: 30px 30px 10px 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.5);
                opacity: 0.7;
            `;
            this.parentElement.insertBefore(placeholder, this);
        };

        const name = document.createElement('div');
        name.className = 'knight-name';
        name.textContent = user.name;

        el.appendChild(img);
        el.appendChild(name);
        return el;
    }

    function positionKnights() {
        const ids = Object.keys(knightElements);
        const n = ids.length;
        if (n === 0) return;

        const vw = window.innerWidth;
        const vh = window.innerHeight;
        const centerX = vw / 2;
        // Place arc center at fire/ground level so knights sit on the ground
        const centerY = vh * 0.64;
        const radius = Math.min(vw * 0.30, 300);

        for (let i = 0; i < n; i++) {
            const angle = (-60 + (120 / (n + 1)) * (i + 1)) * (Math.PI / 180);
            const x = centerX + Math.sin(angle) * radius;
            // Perspective squish: behind-fire knights are higher on screen
            const y = centerY - Math.cos(angle) * radius * 0.35;
            const scale = 1.0 - Math.abs(angle) * 0.12;

            const el = knightElements[ids[i]];
            el.style.left = `${x}px`;
            el.style.top = `${y}px`;
            // Anchor bottom of element at y so feet touch the ground
            el.style.transform = `translate(-50%, -100%) scale(${scale})`;
        }
    }

    function addKnight(user) {
        if (knightElements[user.id]) return;
        const el = createKnightElement(user);
        el.style.opacity = '0';
        container().appendChild(el);
        knightElements[user.id] = el;
        positionKnights();
        // Fade in
        requestAnimationFrame(() => {
            el.style.opacity = '1';
        });
    }

    function removeKnight(userId) {
        const el = knightElements[userId];
        if (!el) return;
        el.style.opacity = '0';
        setTimeout(() => {
            el.remove();
            delete knightElements[userId];
            positionKnights();
        }, 500);
    }

    function setKnights(users) {
        // Clear existing
        for (const id of Object.keys(knightElements)) {
            knightElements[id].remove();
        }
        knightElements = {};

        for (const user of users) {
            const el = createKnightElement(user);
            container().appendChild(el);
            knightElements[user.id] = el;
        }
        positionKnights();
    }

    window.addEventListener('resize', positionKnights);

    return { addKnight, removeKnight, setKnights };
})();
