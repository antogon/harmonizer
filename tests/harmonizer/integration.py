from harmonizer import harmonize, parse_tablature

more_mess_theme_lick = '''
e|-----------------|-----------------|-----------------|-----------------|
B|-----------------|-----------------|-----------------|-----------------|
G|-----------------|---------5-5-7---|-----------------|-----------------|
D|-------------5-5-|-5-7-7-7---------|-----------------|-----------------|
A|-5-5-5-8-8-8-----|-----------------|-----------------|-----------------|
E|-----------------|-----------------|-----------------|-----------------|
'''

def test_harmonizes_happy_path():
    pitches = parse_tablature(more_mess_theme_lick)
    (key, harmony_line, _harmonized_line) = harmonize(pitches, 4)
    assert key.tonic.name == "D"
    assert key.mode == "minor"
    assert list(map(lambda pitch: pitch.name, harmony_line)) == \
        ['A', 'A', 'A', 'C', 'C', 'C', 'D', 'D', 'D', 'E', 'E', 'E', 'G', 'G', 'A']