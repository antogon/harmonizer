import argparse
import re
from music21 import chord, converter, stream, scale, pitch, note

def parse_tablature(tablature):
    valid_tablature_regex = r'[\n\w]*([a-gA-G#]{1,2}(\|[-0-9]+)+\|?\w*\n?){4,6}'
    if re.match(valid_tablature_regex, tablature):
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

    output_score = stream.Score(stream.Part(stream.Measure(harmonized_line)))
    output_score.show('text')
    if args.output is not None:
        output_score.write('midi', args.output)