import argparse
import csv
from uuid import uuid4
from random import randint, sample
from prettytable import PrettyTable

def generate_possible_setlist(setlist_length, songs_ids_already_used, song_ids_to_end_with, song_ids_to_start_with, songs_by_id):
    if setlist_length < 2:
        raise RuntimeError("Setlist length must be at least 2")
    possible_setlist = []
    possible_song_ids_to_start_with = [id for id in song_ids_to_start_with if id not in songs_ids_already_used]
    if len(possible_song_ids_to_start_with) == 0:
        raise RuntimeError("No songs to start with are left!")
    possible_ndx = randint(0, len(possible_song_ids_to_start_with) - 1)
    song_id_to_start_with = possible_song_ids_to_start_with[possible_ndx]

    possible_song_ids_to_end_with = [id for id in song_ids_to_end_with if id not in songs_ids_already_used + [song_id_to_start_with]]
    if len(possible_song_ids_to_end_with) == 0:
        raise RuntimeError("No songs to end with are left!")
    possible_ndx = randint(0, len(possible_song_ids_to_end_with) - 1)
    song_id_to_end_with = possible_song_ids_to_end_with[possible_ndx]

    possible_setlist.append(song_id_to_start_with)

    song_ids_to_sample = [id for id in songs_by_id.keys() if id not in songs_ids_already_used + [song_id_to_start_with, song_id_to_end_with]]
    songs_ids_in_the_middle = sample(song_ids_to_sample, setlist_length - 2)
    for song_id in songs_ids_in_the_middle:
        possible_setlist.append(song_id)

    possible_setlist.append(song_id_to_end_with)
    return possible_setlist

def check_setlist(setlist_song_ids, songs_keys_by_id, songs_beat_styles_by_id):
    for ndx in range(len(setlist_song_ids) - 1):
        song_id = setlist_song_ids[ndx]
        next_song_id = setlist_song_ids[ndx + 1]
        if song_id not in songs_keys_by_id or next_song_id not in songs_keys_by_id:
            raise RuntimeError("Song ID not found in songs_keys_by_id")
        if song_id not in songs_beat_styles_by_id or next_song_id not in songs_beat_styles_by_id:
            raise RuntimeError("Song ID not found in songs_beat_styles_by_id")
        if songs_keys_by_id[song_id] == songs_keys_by_id[next_song_id]:
            return False
        if songs_beat_styles_by_id[song_id] == songs_beat_styles_by_id[next_song_id]:
            return False
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create a setlist with songs that don't repeat keys or beat styles.")
    parser.add_argument("file", type=str, help="file containing CSV of songs to consider for setlists (song_name, artist_name, key, tempo, beat_style, end_with, start_with)")
    parser.add_argument("numberOfSets", type=int, help="number of setlists to create")
    parser.add_argument("--output", required=False, type=str, help="output file name")
    args = parser.parse_args()

    songs_by_id = {}
    songs_keys_by_id = {}
    songs_beat_styles_by_id = {}
    song_ids_to_start_with = []
    song_ids_to_end_with = []

    with open(args.file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            song_id = uuid4()
            songs_by_id[song_id] = row
            songs_keys_by_id[song_id] = row['key']
            songs_beat_styles_by_id[song_id] = row['beat_style']
            song_ids_to_start_with.append(song_id) if row['start_with'] in ['true', 'True', 't', 'Yes', 'yes', 'y'] else None
            song_ids_to_end_with.append(song_id) if row['end_with'] in ['true', 'True', 't', 'Yes', 'yes', 'y'] else None

    if args.numberOfSets > 1:
        songs_per_setlist = len(songs_by_id) // args.numberOfSets
        song_count_leftover = len(songs_by_id) % args.numberOfSets
        song_count_per_setlist = ([songs_per_setlist] * (args.numberOfSets - 1)) + [song_count_leftover] if song_count_leftover > 0 else [songs_per_setlist] * args.numberOfSets
    else:
        song_count_per_setlist = [len(songs_by_id)]
        
    songs_ids_already_used = []
    setlists = []
    for setlist_ndx in range(args.numberOfSets):
        is_setlist_valid = False
        setlist_length = song_count_per_setlist[setlist_ndx]
        while not is_setlist_valid:
            possible_setlist = generate_possible_setlist(setlist_length, songs_ids_already_used, song_ids_to_end_with, song_ids_to_start_with, songs_by_id)
            is_setlist_valid = check_setlist(possible_setlist, songs_keys_by_id, songs_beat_styles_by_id)
        setlists.append(possible_setlist)
        songs_ids_already_used += possible_setlist

    output_headers = ["Song Name", "Artist Name", "Key", "Tempo", "Beat Style", "End With", "Start With"]

    for ndx, setlist in enumerate(setlists):
        print("Setlist", ndx + 1)
        t = PrettyTable(output_headers)
        for song_id in setlist:
            t.add_row([songs_by_id[song_id]['song_name'], songs_by_id[song_id]['artist_name'], songs_by_id[song_id]['key'], songs_by_id[song_id]['tempo'], songs_by_id[song_id]['beat_style'], songs_by_id[song_id]['end_with'], songs_by_id[song_id]['start_with']])
        t.align = 'l'
        print(t)
        print("") if ndx != len(setlists) - 1 else None

    if args.output is not None:
        print("")
        with open(args.output, 'w') as f:
            f.write(",".join(output_headers) + "\n")
            for setlist in setlists:
                for song_id in setlist:
                    song = songs_by_id[song_id]
                    f.write(",".join([song['song_name'], song['artist_name'], song['key'], song['tempo'], song['beat_style'], song['end_with'], song['start_with']]) + "\n")
                f.write(",".join(["--"]*7) + "\n")
        print(f"Setlists written to {args.output}")