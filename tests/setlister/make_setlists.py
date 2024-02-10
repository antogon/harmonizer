from setlister import generate_possible_setlist, check_setlist
from uuid import uuid4

songs_csv = '''
song_name,artist_name,key,tempo,beat_style,start_with,end_with
Favorite Cup,Don Carlos,Dm,88,Rockers,Yes,No
Heavy Metal,Don Felder,Bm,88,Metal,No,No
In Another Life,Irie Love,G#,96,One Drop,No,Yes
'''

def test_generates_possible_setlist():
    songs_by_id = {}
    song_ids_to_start_with = []
    song_ids_to_end_with = []
    for row in songs_csv.strip().split('\n')[1:]:
        song_id = str(uuid4())
        song = dict(zip(songs_csv.strip().split('\n')[0].split(','), row.split(',')))
        songs_by_id[song_id] = song
        if song['start_with'] == 'Yes':
            song_ids_to_start_with.append(song_id)
        if song['end_with'] == 'Yes':
            song_ids_to_end_with.append(song_id)
    possible_setlist = generate_possible_setlist(3, [], song_ids_to_end_with, song_ids_to_start_with, songs_by_id)
    assert len(possible_setlist) == 3
    assert possible_setlist[0] in song_ids_to_start_with
    assert possible_setlist[2] in song_ids_to_end_with
    assert possible_setlist[1] not in song_ids_to_start_with + song_ids_to_end_with

def test_checks_setlists_happy_path():
    possible_setlist = ['1', '2', '3']
    songs_keys_by_id = {
        '1': 'Dm',
        '2': 'Bm',
        '3': 'G#'
    }
    songs_beat_styles_by_id = {
        '1': 'Rockers',
        '2': 'Metal',
        '3': 'One Drop'
    }
    assert check_setlist(possible_setlist, songs_keys_by_id, songs_beat_styles_by_id) == True

def test_checks_setlists_repeating_keys():
    possible_setlist = ['1', '2', '3']
    songs_keys_by_id = {
        '1': 'Dm',
        '2': 'Dm',
        '3': 'G#'
    }
    songs_beat_styles_by_id = {
        '1': 'Rockers',
        '2': 'Metal',
        '3': 'One Drop'
    }
    assert check_setlist(possible_setlist, songs_keys_by_id, songs_beat_styles_by_id) == False

def test_checks_setlists_repeating_beats():
    possible_setlist = ['1', '2', '3']
    songs_keys_by_id = {
        '1': 'Dm',
        '2': 'Bm',
        '3': 'G#'
    }
    songs_beat_styles_by_id = {
        '1': 'Rockers',
        '2': 'Rockers',
        '3': 'One Drop'
    }
    assert check_setlist(possible_setlist, songs_keys_by_id, songs_beat_styles_by_id) == False