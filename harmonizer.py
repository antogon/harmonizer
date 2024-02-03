import argparse
from music21 import chord, converter, stream

def harmonize(tinynotation_notes, number_of_steps):
    scale = converter.parse(tinynotation_notes)
    key = scale.analyze('key')

    harmony_pitches = []

    for pitch in scale.pitches:
        harmony_pitches.append(key.nextPitch(pitch, stepSize=number_of_steps))

    harmonized_line = []

    for given_pitch, harmony_pitch in list(zip(scale.pitches, harmony_pitches)):
        c = chord.Chord([given_pitch, harmony_pitch])
        harmonized_line.append(c)

    return (key, harmony_pitches, harmonized_line)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="sample argument parser")
    parser.add_argument("lineToHarmonize", type=str, help="notes in line to harmonize")
    parser.add_argument("numberOfSteps", type=int, help="number of semitones (+/-) to harmonize")
    parser.add_argument("outputFile", type=str, help="output file name")
    args = parser.parse_args()

    (key, harmony_pitches, harmonized_line) = harmonize(args.lineToHarmonize, args.numberOfSteps)

    print("Analyzed key: ", key.tonic.name, key.mode)
    print("Notes in scale: ", key.pitches)
    print("Notes in harmony: ", harmony_pitches)

    output_score = stream.Score(stream.Part(stream.Measure(harmonized_line)))
    output_score.show('text')
    output_score.write('midi', args.outputFile)