# Harmonizer

A (poorly named) collection of helpful tools for music composition and live
performance.

## How to use the harmonizer

To pass in tinynotation:

```
python harmonizer.py --line "tinynotation: 4/4 d f g a c d" 4 --output output.midi
```

To pass in a file:

```
python harmonizer.py --file tablature.txt 4 --output output.midi
```

## How to use the setlist maker

This tool takes a list of songs your band can play and generates setlists that:

- don't repeat key
- don't repeat beat style
- don't repeat any songs in the list

```
python setlister.py setlists/setlist.csv 1
```

using an input CSV that has columns: `song_name`, `artist_name`, `key`, `tempo`, `beat_style`, `start_with`, `end_with`

Most of the columns listed above are self-explanatory.  `start_with` and `end_with` are booleans that indicate whether or
not the setlist should be able to start or end with those songs -- a song can be listed as both a possibility for ending
and starting if desired.