from harmonizer import harmonize
from music21 import converter

def test_harmonize_happy_path():
    input_score = converter.parse("tinynotation: 4/4 d f g a c d")
    print(list(input_score.pitches))
    (key, harmony_line, _harmonized_line) = harmonize(list(input_score.pitches), 4)
    assert key.tonic.name == "D"
    assert key.mode == "minor"
    assert list(map(lambda pitch: pitch.name, harmony_line)) == ['A', 'C', 'D', 'E', 'G', 'A']