# ELAN_make_subtitles

This script uses the [MoviePy](https://zulko.github.io/moviepy/) module to create video clips (with subtitles) from ELAN annotations. The output is an `.mp4` file with the same name as the original video file but `_subtitles_N` added to the end (where "N" is the chronological position of the clip in the `.eaf` file, in case of several clips generated from the same original file).

In order to use it, you need the `.py` file on your computer, located in the same file as your `.eaf` files and their associated video files. By creating a new tier with the name "make_subtitles_...", where "..." represents a unique identifier for the video file associated with the tier, the script finds the annotations and outputs video files. NB: The video file identifier has to distinguish it from any other associated video files. For example, if you have an `.eaf` file with two associated videos (`video1.mp4` and `video2.mp4`), you can create an ELAN tier with the name "make_subtitles_1", and the script then uses `video1.mp4` as the associated video file.

You run the script by entering
```
python3 ELAN_make_subtitles.py
```
or
```
python ELAN_make_subtitles.py
```
and `.mp4` video files (with subtitles, if text is added to ELAN annotation cells) are generated and saved to the directory.

For example, in the [Swedish Sign Language Corpus](https://www.ling.su.se/teckenspr%C3%A5ksresurser/teckenspr%C3%A5kskorpusar/svensk-teckenspr%C3%A5kskorpus) file `SSLC01_003.eaf`, there are two associated video files. They are distinguished by containing the signer id number of the two signers ("S001" and "S002"). Thus, we can create a tier called "make_subtitles_S002" that will be associated with the video on the right in the image below, through the identifier "S002".

![ELAN](https://github.com/borstell/ELAN_make_subtitles/blob/master/Example_SSLC_ELAN.png)

In the above image, the stretch of signing is rather long, and thus there is an added "//" in the middle of the annotation cell text. The script will automatically split all texts at "//" and put separate subtitle timings at even split points. Longer text without "//" will get an automatic line break in the subtitle text.

By adding more arguments in the command line input, you can choose to create clips from another tier, as long as the tiername is of the type "tiername_...", where "..." represents a unique video file identifier. It is also possible to make the output video files slower (or, faster) by adding an argument specifying the speed in % of the original. For example
```
python3 ELAN_make_subtitles.py 60
```
makes the output file 60% of the speed of the original video file. The generated output file below (converted to `.gif`).

![Example](https://github.com/borstell/ELAN_make_subtitles/blob/master/Example_SSLC.gif)
