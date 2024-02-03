from harmonizer import harmonize

def test_harmonize_happy_path():
    (key, harmony_line, _harmonized_line) = harmonize("tinynotation: 4/4 d f g a c d", 4)
    assert key.tonic.name == "D"
    assert key.mode == "minor"
    assert list(map(lambda pitch: pitch.name, harmony_line)) == ['A', 'C', 'D', 'E', 'G', 'A']