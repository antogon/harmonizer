from harmonizer import find_nearest_note, write_harmony_tablature
from music21 import pitch

more_mess_theme_lick = '''
e|-----------------|-----------------|-8-8-10----------|-----------------|
B|-----------------|-8-8-8-10-10-10--|-----------------|-----------------|
G|-7-7-7-10-10-10--|-----------------|-----------------|-----------------|
D|-----------------|-----------------|-----------------|-----------------|
A|-----------------|-----------------|-----------------|-----------------|
E|-----------------|-----------------|-----------------|-----------------|
'''

more_mess_harmony = '''
e--------------------------10-10-10-12--12--12-----15-15-17----
B--10-10-10-13--13--13-----------------------------------------
G--------------------------------------------------------------
D--------------------------------------------------------------
A--------------------------------------------------------------
E--------------------------------------------------------------
'''

def test_find_nearest_note():
    string_tunings = [
        ('e', pitch.Pitch('E4')),
        ('B', pitch.Pitch('B3')),
        ('G', pitch.Pitch('G3')),
        ('D', pitch.Pitch('D3')),
        ('A', pitch.Pitch('A2')),
        ('E', pitch.Pitch('E2'))
    ]
    first_note = (2, 7, pitch.Pitch('D4'))
    harmony_pitch = pitch.Pitch('A5')
    # Here, we expect it to pick out the A note on the 10th fret of the B string
    # because it is the closest note _above_ the given melody line.
    assert find_nearest_note(string_tunings, first_note, harmony_pitch) == (1, 10)

def test_write_harmony_tablature():
    harmony_line = [
        pitch.Pitch('A'),
        pitch.Pitch('A'),
        pitch.Pitch('A'), 
        pitch.Pitch('C'), 
        pitch.Pitch('C'),
        pitch.Pitch('C'),
        pitch.Pitch('D'),
        pitch.Pitch('D'),
        pitch.Pitch('D'), 
        pitch.Pitch('E'),
        pitch.Pitch('E'),
        pitch.Pitch('E'), 
        pitch.Pitch('G'),
        pitch.Pitch('G'), 
        pitch.Pitch('A')
    ]
    output_string = write_harmony_tablature(more_mess_theme_lick, harmony_line)
    assert output_string == more_mess_harmony.strip()