// Main entry point — orchestrates all modules
(function () {
    let myInfo = null;
    let colors = [];
    let promptHidden = false;

    // Initialize canvases
    Sky.init(document.getElementById('sky-canvas'));
    Fire.init(document.getElementById('fire-canvas'));
    Powder.init(document.getElementById('powder-canvas'));

    // Click handler on bonfire area
    document.getElementById('bonfire-area').addEventListener('click', () => {
        if (!myInfo) return;
        BonfireWS.send({ type: 'powder_toss' });

        // Hide prompt on first click
        if (!promptHidden) {
            promptHidden = true;
            document.getElementById('prompt').classList.add('hidden');
        }
    });

    // WebSocket event handlers
    BonfireWS.on('init', (msg) => {
        myInfo = msg.you;
        colors = msg.colors || [];

        document.getElementById('my-name').textContent = myInfo.name;
        Sky.setMoonPhase(msg.moon_phase);
        Knights.setKnights(msg.users);
    });

    BonfireWS.on('user_joined', (msg) => {
        Knights.addKnight(msg);
    });

    BonfireWS.on('user_left', (msg) => {
        Knights.removeKnight(msg.id);
    });

    BonfireWS.on('powder_toss', (msg) => {
        const color = colors[msg.color_index] || '#FFD700';
        Fire.triggerPowder(color);
        Powder.trigger(color);
    });

    // Animation loop
    function animate() {
        Sky.render();
        Fire.render();
        Powder.render();
        requestAnimationFrame(animate);
    }
    animate();

    // Connect WebSocket
    BonfireWS.connect();
})();
