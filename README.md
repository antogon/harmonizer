# Harmonizer

A small tool to accept notes (with a guitar bias) and output harmony lines in the
given number of steps up.

## How to run

To pass in tinynotation:

```
python harmonizer.py --line "tinynotation: 4/4 d f g a c d" 4 --output output.midi
```

To pass in a file:

```
python harmonizer.py --file tablature.txt 4 --output output.midi
```