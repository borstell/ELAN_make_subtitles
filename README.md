# ELAN_make_subtitles
Creates (subtitled) video clips from ELAN annotations

This script uses the MoviePy module to create video clips (with subtitles) from ELAN annotations. The output is an `.mp4` file with the same name as the original video file but `_subtitles_N` added to the end (where "N" is the chronological position of the clip in the `.eaf` file, in case of several clips generated from the same original file).

In order to use it, you need the `.py` file on your computer, located in the same file as your `.eaf` files and their associated video files. By creating a new tier with the name "make_subtitles_...", where "..." represents a unique identifier for the video file associated with the tier, the script finds the annotations and outputs video files. NB: The video file identifier has to distinguish it from any other associated video files. For example, if you have an `.eaf` file with two associated videos (`video1.mp4` and `video2.mp4`), you can create an ELAN tier with the name "make_subtitles_1", and the script then uses `video1.mp4` as the associated video file.

You run the script by entering
```
python3 ELAN_make_subtitles.py
```
or
```
python ELAN_make_subtitles.py
```
and `.mp4` video files (with subtitles, if text is added to ELAN annotation cells)
