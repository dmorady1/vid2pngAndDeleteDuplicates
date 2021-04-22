# Table of Contents

1.  [Description](#org5fe6834)
2.  [Requirements](#org0c6d865)
3.  [examples](#org35ea0c1)

<a id="org5fe6834"></a>

# Description

Creates pictures of a video file and delete duplicate in these pictures.

Can also be used for pictures
only with option `-w` make sure to use the `-P` option to give the correct path to your files.

Default value for `Threshold` for similarity is `95`. (100 would mean exact the same pictures)

Threshold can be changed with `-t` option.

<a id="org0c6d865"></a>

# Requirements
- findimagedupes (https://github.com/jhnc/findimagedupes)
- python
- ffmpeg
    
<a id="org35ea0c1"></a>

# examples

with video

    python vid2pngAndDeleteDuplicates.py -p myVideo.mp4

without video

    python vid2pngAndDeleteDuplicates -w -P PATH_OF_PICTURES

with threshold

    python vid2pngAndDeleteDuplicates.py -p myVideo.mp4 -t 90

help function
```
usage: ./vid2pngAndDeleteDuplicates.py [-h] [-p PATH_OF_VIDEO] [-P PATH_OF_PICTURES] [-w] [-s] [--dry] [-t THRESHOLD]

optional arguments:
  -h, --help            show this help message and exit
  -p PATH_OF_VIDEO, --path PATH_OF_VIDEO
  -P PATH_OF_PICTURES, --path_of_pictures PATH_OF_PICTURES
  -w, --without_video
  -s, --stop_remove_file
                        not delete Dup file: dups.txt (default: False)
  --dry                 dry run (without deleting) (default: False)
  -t THRESHOLD, --threshold THRESHOLD
                        threshold image similarity (100 means if exact the same) (default: 95)
 ```
