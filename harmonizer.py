import argparse
from music21 import chord, converter, stream

parser=argparse.ArgumentParser(description="sample argument parser")
parser.add_argument("numberOfSteps", type=int, help="number of semitones (+/-) to harmonize")
parser.add_argument("outputFile", type=str, help="output file name")
args=parser.parse_args()

scale = converter.parse("tinynotation: 4/4 e b e e- e- e f# e e- c# e- c# a f# f# e e- c# b b c# b")
key = scale.analyze('key')

print("Analyzed key: ", key.tonic.name, key.mode)
print("Notes given: ", scale.pitches)
print("Notes in scale: ", key.pitches)

harmony_pitches = []

for pitch in scale.pitches:
    harmony_pitches.append(key.nextPitch(pitch, stepSize=args.numberOfSteps))

print("Notes in harmony: ", harmony_pitches)

harmonized_line = []

for given_pitch, harmony_pitch in list(zip(scale.pitches, harmony_pitches)):
    print("Given pitch: ", given_pitch, "Harmony pitch: ", harmony_pitch)
    c = chord.Chord([given_pitch, harmony_pitch])
    harmonized_line.append(c)

output_score = stream.Score(stream.Part(stream.Measure(harmonized_line)))
output_score.show('text')
output_score.write('midi', args.outputFile)