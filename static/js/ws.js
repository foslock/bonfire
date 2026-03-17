// WebSocket client with exponential backoff reconnect
const BonfireWS = (() => {
    let ws = null;
    let handlers = {};
    let reconnectDelay = 1000;
    const MAX_DELAY = 30000;

    function connect() {
        const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
        ws = new WebSocket(`${proto}//${location.host}/ws`);

        ws.onopen = () => {
            reconnectDelay = 1000;
        };

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                const fn = handlers[msg.type];
                if (fn) fn(msg);
            } catch (e) {
                console.error('WS message parse error:', e);
            }
        };

        ws.onclose = () => {
            setTimeout(() => {
                reconnectDelay = Math.min(reconnectDelay * 2, MAX_DELAY);
                connect();
            }, reconnectDelay);
        };

        ws.onerror = () => {
            ws.close();
        };
    }

    function send(msg) {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(msg));
        }
    }

    function on(type, fn) {
        handlers[type] = fn;
    }

    return { connect, send, on };
})();
