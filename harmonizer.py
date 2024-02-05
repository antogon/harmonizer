import argparse
import re
from music21 import chord, converter, stream, scale, pitch, note

def validate_tablature(tablature):
    valid_tablature_regex = r'[\n\w]*([a-gA-G#]{1,2}(\|[-0-9]+)+\|?\w*\n?){4,6}'
    if re.match(valid_tablature_regex, tablature):
        return True
    else:
        return False

def parse_tablature(tablature):
    if validate_tablature(tablature):
        one_line_regex = r'([a-gA-G#](\|[-0-9]+)+\|?\n)'
        parsed_notes = []
        for line_match in re.finditer(one_line_regex, tablature):
            line_breakup_match = re.match(r'[\w\n]*([a-gA-G#]{1,2})((\|[-0-9]+)+)\|?', line_match.group(0))
            starting_pitch = line_breakup_match.group(1)
            chromatic_scale = scale.ChromaticScale('g2')
            for note_match in re.finditer(r'([0-9]+)', line_breakup_match.group(2)):
                match_index = note_match.start()
                note_as_semitone_count = int(note_match.group(1))
                origin_pitch = pitch.Pitch(starting_pitch)
                adjusted_pitch = chromatic_scale.nextPitch(origin_pitch, note_as_semitone_count)
                parsed_notes.append((match_index, adjusted_pitch))
        return list(map(lambda note_tuple: note_tuple[1], sorted(parsed_notes, key=lambda note_tuple: note_tuple[0])))
    else:
        raise RuntimeError("Invalid tablature")
    
def find_nearest_note(string_tunings, first_note, harmony_pitch, prioritize_higher=False):
    chromatic_scale = scale.ChromaticScale('g2')
    for neighbor_depth in range(1, 3):
        if prioritize_higher:
            strings_to_search = list(range(-1 * neighbor_depth, 0)) + [0] + list(range(1, neighbor_depth + 1))
        else:
            strings_to_search = [0] + list(range(-1 * neighbor_depth, 0)) + list(range(1, neighbor_depth + 1))

        for search_string_ndx in strings_to_search:
            possible_note_string_ndx = first_note[0] + search_string_ndx
            if (possible_note_string_ndx == first_note[0] and possible_note_string_ndx == first_note[1]) or \
                        possible_note_string_ndx < 0 or \
                        possible_note_string_ndx > len(string_tunings) - 1:
                    continue
            for search_note_ndx in range(-4, 4):
                if search_note_ndx + first_note[1] < 0 or search_note_ndx + first_note[1] > 24:
                    continue
                possible_note_fret_ndx = first_note[1] + search_note_ndx
                possible_note_open_string_tuning = string_tunings[possible_note_string_ndx]
                possible_note = chromatic_scale.nextPitch(possible_note_open_string_tuning[1], possible_note_fret_ndx) if possible_note_fret_ndx != 0 else pitch.Pitch(possible_note_open_string_tuning[1])
                if possible_note.pitchClass == harmony_pitch.pitchClass:
                    return (possible_note_string_ndx, possible_note_fret_ndx)
    return None

def write_harmony_tablature(original_tablature, harmony_pitches):
    if validate_tablature(original_tablature):
        one_line_regex = r'([a-gA-G#](\|[-0-9]+)+\|?\n)'
        # First, we find the position and pitch of the first note in the original tablature.
        # While we do this, we'll also store the tunings of each string to make it
        # easier to write tablature in the same tuning back out later.
        first_note = None
        first_note_lowest_index = None
        string_tunings = []
        string_ndx = 0
        notes_in_melody_by_tab_column_ndx = []
        for line_match in re.finditer(one_line_regex, original_tablature):
            line_breakup_match = re.match(r'[\w\n]*([a-gA-G#]{1,2})((\|[-0-9]+)+)\|?', line_match.group(0))
            pitch_of_open_string = line_breakup_match.group(1)
            string_tunings.append((line_breakup_match.group(1), pitch_of_open_string))
            chromatic_scale = scale.ChromaticScale('g2')
            for note_match in re.finditer(r'([0-9]+)', line_breakup_match.group(2)):
                match_index = note_match.start()
                note_as_semitone_count = int(note_match.group(1))
                origin_pitch = pitch.Pitch(pitch_of_open_string)
                adjusted_pitch = chromatic_scale.nextPitch(origin_pitch, note_as_semitone_count)
                notes_in_melody_by_tab_column_ndx.append((match_index, note_as_semitone_count, adjusted_pitch))
                if first_note_lowest_index is None or match_index < first_note_lowest_index:
                    first_note_lowest_index = match_index
                    first_note = (string_ndx, note_as_semitone_count, adjusted_pitch)
            string_ndx += 1
        notes_in_melody_by_tab_column_ndx = sorted(notes_in_melody_by_tab_column_ndx, key=lambda note_tuple: note_tuple[0])
        # Now that we have the position and pitch of the first note, we can use it as the origin
        # for our first nearest-neighbor search as we attempt to fret the harmony pitches.
        last_note = first_note
        fretted_harmony = []
        distance_traveled_from_first_fret = 0
        for harmony_pitch in harmony_pitches:
            nearest_note = find_nearest_note(string_tunings, last_note, harmony_pitch, prioritize_higher=distance_traveled_from_first_fret > 3)
            if nearest_note is not None:
                distance_traveled_from_first_fret = abs(nearest_note[1] - first_note[1])
                fretted_harmony.append(nearest_note)
                last_note = nearest_note
            else:
                print("Could not find a fretting for the harmony pitch", harmony_pitch.name, "in the neighborhood of", last_note)
                raise RuntimeError("Could not find a fretting for the harmony pitch")
        # Now that we have our harmony line ready, let's write it out in tablature format
        # using our melody line as a template, but putting the harmony notes in place
        # of the melody notes.
        tablature_lines = list(map(lambda tuning: tuning[0], string_tunings))
        length_of_tablature = notes_in_melody_by_tab_column_ndx[-1][0] + 5
        harmony_ndx = 0
        for col_ndx in range(length_of_tablature):
            note_to_write = fretted_harmony[harmony_ndx] if harmony_ndx < len(fretted_harmony) else None
            note_in_melody = next((n for n in notes_in_melody_by_tab_column_ndx if n[0] == col_ndx), None)
            if note_in_melody is not None and note_to_write is not None:
                for s_ndx in range(len(tablature_lines)):
                    line = tablature_lines[s_ndx]
                    if s_ndx == note_to_write[0] and col_ndx == note_in_melody[0]:
                        line += str(note_to_write[1])
                        harmony_ndx += 1
                        tablature_lines[s_ndx] = line
                    else:
                        line += ('-') * len(str(note_to_write[1]))
                        tablature_lines[s_ndx] = line
            else:
                for s_ndx in range(len(tablature_lines)):
                    line = tablature_lines[s_ndx]
                    line += '-'
                    tablature_lines[s_ndx] = line
        return "\n".join(tablature_lines)
    else:
        raise RuntimeError("Invalid tablature")

def harmonize(input_line, number_of_steps):
    notes = list(map(lambda p: note.Note(p), input_line))
    input_score = stream.Stream(notes)
    key = input_score.analyze('key')

    harmony_pitches = []

    for input_pitch in input_line:
        harmony_pitches.append(key.nextPitch(input_pitch, stepSize=number_of_steps))

    harmonized_line = []

    for given_pitch, harmony_pitch in list(zip(input_line, harmony_pitches)):
        c = chord.Chord([given_pitch, harmony_pitch])
        harmonized_line.append(c)

    return (key, harmony_pitches, harmonized_line)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Harmonize a line of notes.")
    parser.add_argument("--line", required=False, type=str, help="notes in tinynotation format of line to harmonize")
    parser.add_argument("--file", required=False, type=str, help="name of file containing guitar tablature to harmonize")
    parser.add_argument("numberOfSteps", type=int, help="number of semitones (+/-) to harmonize")
    parser.add_argument("--output", required=False, type=str, help="output file name")
    args = parser.parse_args()

    if args.line is None and args.file is None:
        parser.error("Either --line or --file must be specified")

    if args.line is not None and args.file is not None:
        parser.error("Specify either --line or --file, not both")

    if args.line is not None:
        input_score = converter.parse(args.line)
        (key, harmony_pitches, harmonized_line) = harmonize(list(input_score.pitches), args.numberOfSteps)
    elif args.file is not None:
        with open(args.file) as f:
            data = f.read()
        input_pitches = parse_tablature(data)
        (key, harmony_pitches, harmonized_line) = harmonize(input_pitches, args.numberOfSteps)

    print("Analyzed key: ", key.tonic.name, key.mode)
    print("Notes in scale: ", list(map(lambda pitch: pitch.name, key.pitches)))
    print("Notes in harmony: ", list(map(lambda pitch: pitch.name, harmony_pitches)))
    print(" ")
    
    notes_in_harmonized_line = list(map(lambda c: str(list(map(lambda p: p.name, c.pitches))), harmonized_line))
    print("Harmonized line:\n", "\n".join(notes_in_harmonized_line), sep='')
    print(" ")

    if args.file is not None:
        print("Possible tablature:")
        print(write_harmony_tablature(data, harmony_pitches))

    output_score = stream.Score(stream.Part(stream.Measure(harmonized_line)))
    if args.output is not None:
        output_score.write('midi', args.output)