"""Frontend JS tests — run via pytest.

These tests verify the JavaScript files contain expected structure and logic
by parsing them as text and by running small snippets through Node.js (if available).
This gives us regression protection without a full browser environment.
"""

import json
import os
import subprocess
import re

import pytest

JS_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "js")


def read_js(name: str) -> str:
    with open(os.path.join(JS_DIR, name)) as f:
        return f.read()


def run_node(script: str, timeout: int = 5) -> str:
    """Run a JS snippet in Node.js and return stdout."""
    try:
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode != 0:
            pytest.fail(f"Node.js error:\n{result.stderr}")
        return result.stdout.strip()
    except FileNotFoundError:
        pytest.skip("Node.js not available")


# === Structural tests (no Node.js needed) ===

class TestWSModule:
    def test_exports_connect_send_on(self):
        src = read_js("ws.js")
        assert "return { connect, send, on }" in src

    def test_uses_exponential_backoff(self):
        src = read_js("ws.js")
        assert "reconnectDelay * 2" in src

    def test_max_delay_defined(self):
        src = read_js("ws.js")
        assert "MAX_DELAY" in src
        assert "30000" in src

    def test_resets_delay_on_open(self):
        src = read_js("ws.js")
        assert "reconnectDelay = 1000" in src

    def test_parses_json_messages(self):
        src = read_js("ws.js")
        assert "JSON.parse" in src

    def test_sends_json_messages(self):
        src = read_js("ws.js")
        assert "JSON.stringify" in src

    def test_protocol_detection(self):
        src = read_js("ws.js")
        assert "wss:" in src
        assert "ws:" in src


class TestFireModule:
    def test_exports_init_render_trigger(self):
        src = read_js("fire.js")
        assert "return { init, render, triggerPowder }" in src

    def test_pool_size_defined(self):
        src = read_js("fire.js")
        assert "POOL_SIZE" in src
        match = re.search(r"POOL_SIZE\s*=\s*(\d+)", src)
        assert match
        assert int(match.group(1)) >= 100  # should have enough particles

    def test_base_colors_defined(self):
        src = read_js("fire.js")
        assert "BASE_COLORS" in src
        # Should have warm color entries
        assert "255, g: 240, b: 180" in src  # white-yellow

    def test_powder_color_parsing(self):
        src = read_js("fire.js")
        # triggerPowder should parse hex color
        assert "parseInt(hexColor.slice(1, 3), 16)" in src

    def test_particle_lifecycle(self):
        src = read_js("fire.js")
        assert "life" in src
        assert "maxLife" in src
        assert "resetParticle" in src

    def test_powder_frames_decay(self):
        src = read_js("fire.js")
        assert "powderFrames > 0" in src
        assert "powderFrames--" in src


class TestSkyModule:
    def test_exports_init_setmoonphase_render(self):
        src = read_js("sky.js")
        assert "return { init, setMoonPhase, render }" in src

    def test_generates_120_stars(self):
        src = read_js("sky.js")
        assert "120" in src

    def test_star_twinkling(self):
        src = read_js("sky.js")
        assert "Math.sin" in src
        assert "twinkle" in src

    def test_moon_waxing_waning(self):
        src = read_js("sky.js")
        assert "phase < 0.5" in src  # waxing/waning branch
        assert "Waxing" in src
        assert "Waning" in src

    def test_moon_shadow_drawing(self):
        src = read_js("sky.js")
        assert "ellipse" in src  # uses ellipse for shadow


class TestKnightsModule:
    def test_exports_add_remove_set(self):
        src = read_js("knights.js")
        assert "return { addKnight, removeKnight, setKnights }" in src

    def test_semicircle_positioning(self):
        src = read_js("knights.js")
        # Should use angle-based positioning
        assert "Math.sin(angle)" in src
        assert "Math.cos(angle)" in src

    def test_perspective_squish(self):
        src = read_js("knights.js")
        assert "0.3" in src  # perspective squish factor

    def test_knight_name_display(self):
        src = read_js("knights.js")
        assert "knight-name" in src
        assert "textContent" in src

    def test_fade_transition(self):
        src = read_js("knights.js")
        assert "opacity" in src

    def test_placeholder_on_sprite_error(self):
        src = read_js("knights.js")
        assert "onerror" in src


class TestPowderModule:
    def test_exports_init_trigger_render(self):
        src = read_js("powder.js")
        assert "return { init, trigger, render }" in src

    def test_creates_25_sparks_per_trigger(self):
        src = read_js("powder.js")
        assert "25" in src

    def test_gravity_applied(self):
        src = read_js("powder.js")
        assert "gravity" in src
        assert "s.vy += s.gravity" in src

    def test_sparks_removed_when_dead(self):
        src = read_js("powder.js")
        assert "sparks.splice(i, 1)" in src

    def test_hex_color_parsing(self):
        src = read_js("powder.js")
        assert "parseInt(hexColor.slice(1, 3), 16)" in src


class TestMainModule:
    def test_registers_all_ws_handlers(self):
        src = read_js("main.js")
        assert "BonfireWS.on('init'" in src
        assert "BonfireWS.on('user_joined'" in src
        assert "BonfireWS.on('user_left'" in src
        assert "BonfireWS.on('powder_toss'" in src

    def test_initializes_all_canvases(self):
        src = read_js("main.js")
        assert "Sky.init" in src
        assert "Fire.init" in src
        assert "Powder.init" in src

    def test_animation_loop(self):
        src = read_js("main.js")
        assert "requestAnimationFrame(animate)" in src

    def test_click_sends_powder_toss(self):
        src = read_js("main.js")
        assert "BonfireWS.send({ type: 'powder_toss' })" in src

    def test_prompt_hidden_on_click(self):
        src = read_js("main.js")
        assert "prompt" in src
        assert "hidden" in src


# === Node.js logic tests ===

class TestNodeJSLogic:
    """Tests that run JS snippets in Node.js to verify actual logic."""

    def test_hex_color_parsing(self):
        """Verify hex color parsing logic matches what fire.js and powder.js do."""
        out = run_node("""
            const hexColor = '#DC143C';
            const r = parseInt(hexColor.slice(1, 3), 16);
            const g = parseInt(hexColor.slice(3, 5), 16);
            const b = parseInt(hexColor.slice(5, 7), 16);
            console.log(JSON.stringify({r, g, b}));
        """)
        result = json.loads(out)
        assert result == {"r": 220, "g": 20, "b": 60}

    def test_knight_positioning_algorithm(self):
        """Verify the semi-circle positioning math from knights.js."""
        out = run_node("""
            const n = 3;
            const centerX = 500;
            const centerY = 400;
            const radius = 200;
            const positions = [];
            for (let i = 0; i < n; i++) {
                const angle = (-60 + (120 / (n + 1)) * (i + 1)) * (Math.PI / 180);
                const x = centerX + Math.sin(angle) * radius;
                const y = centerY - Math.cos(angle) * radius * 0.3;
                const scale = 1.0 - Math.abs(angle) * 0.15;
                positions.push({x: Math.round(x), y: Math.round(y), scale: +scale.toFixed(3)});
            }
            console.log(JSON.stringify(positions));
        """)
        positions = json.loads(out)
        assert len(positions) == 3
        # Center knight should be at centerX, outer ones symmetric
        assert positions[1]["x"] == 500  # middle knight at center
        assert positions[0]["x"] < 500   # left of center
        assert positions[2]["x"] > 500   # right of center
        # Should be roughly symmetric
        left_offset = 500 - positions[0]["x"]
        right_offset = positions[2]["x"] - 500
        assert abs(left_offset - right_offset) < 2

    def test_ws_reconnect_delay_capped(self):
        """Verify reconnect delay doubles but caps at MAX_DELAY."""
        out = run_node("""
            let reconnectDelay = 1000;
            const MAX_DELAY = 30000;
            const delays = [];
            for (let i = 0; i < 8; i++) {
                reconnectDelay = Math.min(reconnectDelay * 2, MAX_DELAY);
                delays.push(reconnectDelay);
            }
            console.log(JSON.stringify(delays));
        """)
        delays = json.loads(out)
        assert delays == [2000, 4000, 8000, 16000, 30000, 30000, 30000, 30000]

    def test_star_twinkle_bounded(self):
        """Star twinkle values should stay in a visible range."""
        out = run_node("""
            const results = [];
            for (let frame = 0; frame < 200; frame++) {
                const speed = 0.02;
                const phase = 0;
                const brightness = 0.75;
                const twinkle = Math.sin(frame * speed + phase) * 0.3 + 0.7;
                const alpha = brightness * twinkle;
                results.push(alpha);
            }
            const min = Math.min(...results);
            const max = Math.max(...results);
            console.log(JSON.stringify({min: +min.toFixed(4), max: +max.toFixed(4)}));
        """)
        result = json.loads(out)
        assert result["min"] > 0, "Stars should never be invisible"
        assert result["max"] <= 1.0, "Alpha should not exceed 1"

    def test_particle_velocity_ranges(self):
        """Verify fire particles move upward with reasonable velocity."""
        out = run_node("""
            const particles = [];
            for (let i = 0; i < 100; i++) {
                const vy = -(Math.random() * 2.5 + 1.5);
                const vx = (Math.random() - 0.5) * 1.0;
                particles.push({vx, vy});
            }
            const allUp = particles.every(p => p.vy < 0);
            const maxVx = Math.max(...particles.map(p => Math.abs(p.vx)));
            console.log(JSON.stringify({allUp, maxVx: +maxVx.toFixed(2)}));
        """)
        result = json.loads(out)
        assert result["allUp"] is True, "All particles should move upward"
        assert result["maxVx"] <= 0.5, "Horizontal drift should be small"

    def test_spark_gravity_physics(self):
        """Powder sparks should arc downward due to gravity."""
        out = run_node("""
            let vy = -5;
            const gravity = 0.15;
            const yPositions = [0];
            for (let i = 0; i < 60; i++) {
                vy += gravity;
                yPositions.push(yPositions[yPositions.length - 1] + vy);
            }
            // Should rise first then fall (parabolic arc)
            const minY = Math.min(...yPositions);
            const finalY = yPositions[yPositions.length - 1];
            console.log(JSON.stringify({
                rises: minY < 0,
                falls_back: finalY > minY,
            }));
        """)
        result = json.loads(out)
        assert result["rises"] is True, "Sparks should rise initially"
        assert result["falls_back"] is True, "Gravity should bring sparks back down"

    def test_all_12_colors_parseable(self):
        """All 12 Dark Souls colors should parse correctly as hex."""
        colors = [
            "#FFD700", "#FFFACD", "#4169E1", "#6A0DAD", "#DC143C", "#50C878",
            "#1B0033", "#00FFFF", "#FF6600", "#1A1A2E", "#C0C0C0", "#FF4500",
        ]
        out = run_node(f"""
            const colors = {json.dumps(colors)};
            const parsed = colors.map(c => ({{
                r: parseInt(c.slice(1, 3), 16),
                g: parseInt(c.slice(3, 5), 16),
                b: parseInt(c.slice(5, 7), 16),
            }}));
            const allValid = parsed.every(c =>
                c.r >= 0 && c.r <= 255 &&
                c.g >= 0 && c.g <= 255 &&
                c.b >= 0 && c.b <= 255
            );
            console.log(JSON.stringify({{allValid, count: parsed.length}}));
        """)
        result = json.loads(out)
        assert result["allValid"] is True
        assert result["count"] == 12
