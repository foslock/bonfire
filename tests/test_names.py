import re

from bonfire.names import ADJECTIVES, PROPER_NOUNS, generate_knight_name


def test_proper_nouns_not_empty():
    assert len(PROPER_NOUNS) >= 10


def test_adjectives_not_empty():
    assert len(ADJECTIVES) >= 10


def test_no_duplicate_proper_nouns():
    assert len(PROPER_NOUNS) == len(set(PROPER_NOUNS))


def test_no_duplicate_adjectives():
    assert len(ADJECTIVES) == len(set(ADJECTIVES))


def test_generate_knight_name_format():
    name = generate_knight_name()
    # Should match "Noun the Adjective"
    assert re.match(r"^[A-Z][a-z]+ the [A-Z][a-z]+$", name), f"Unexpected format: {name}"


def test_generate_knight_name_uses_known_words():
    name = generate_knight_name()
    parts = name.split(" the ")
    assert len(parts) == 2
    noun, adj = parts
    assert noun in PROPER_NOUNS
    assert adj in ADJECTIVES


def test_generate_knight_name_randomness():
    """Generate many names and verify we get at least some variety."""
    names = {generate_knight_name() for _ in range(50)}
    # With 50x50=2500 combinations and 50 draws, extremely unlikely to get <5 unique
    assert len(names) >= 5
