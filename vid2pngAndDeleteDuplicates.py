#!/usr/bin/env python3

import os
import re
import subprocess
import argparse
import time
import shutil
import tempfile


# REQUIRES findimagedupes, ffmpeg


def does_executable_exist(executable_name):
    if shutil.which(executable_name) is None:
        print(f"Seems like you did not install {executable_name}")
        print(f"Please make sure to install {executable_name}")
        exit()


does_executable_exist("findimagedupes")
does_executable_exist("ffmpeg")


parser = argparse.ArgumentParser(
    prog="./vid2pngAndDeleteDuplicates.py",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument("-p", "--path", metavar="PATH_OF_VIDEO", type=str, default=None)
parser.add_argument("-P", "--path_of_pictures", type=str, default=None)
parser.add_argument("-w", "--without_video", action="store_true")
parser.add_argument(
    "-s",
    "--stop_remove_file",
    action="store_true",
    help="not delete Dup file: dups.txt",
)
parser.add_argument("--dry", action="store_true", help="dry run (without deleting)")
parser.add_argument(
    "-t",
    "--threshold",
    type=int,
    default=95,
    help="threshold image similarity (100 means if exact the same)",
)
config = parser.parse_args()

if config.path is None and not config.without_video:
    print("Error: Please provide path using the -p option")
    exit()

if config.without_video and config.path_of_pictures is None:
    print(
        "Yo used -w option, so without_video with this option you have to give the path of the pictures"
    )
    print("Error: Please provide path of pictures the -P option")
    exit()

tmp_dir = tempfile.mkdtemp()
dups_file = os.path.join(tmp_dir, "dups.txt")
print("tmpfile", dups_file)

print("path to vid:", config.path)
print("keep dupes file:", config.stop_remove_file)
print("DryRun:", config.dry)
print("Threshhold:", config.threshold)
print("without_video:", config.without_video)

picture_path = ""
if config.path is not None:
    picture_path = os.path.join(os.path.dirname(config.path), "pictures")

if config.path_of_pictures is not None:
    if not os.path.isdir(config.path_of_pictures):
        print(
            "the path of the pictures directory does not exist, it will be created for you"
        )
        os.makedirs(config.path_of_pictures)
    print("using path:", config.path_of_pictures)
    print("If you want to change use: -P PathToPictures ")
    picture_path = config.path_of_pictures

if not config.without_video and config.path_of_pictures is None:
    count = 1
    while os.path.isdir(picture_path):
        count += 1
        picture_path = os.path.join(
            os.path.dirname(config.path), "pictures" + str(count)
        )
    print("Picture path is:", picture_path)
    os.makedirs(picture_path)

count = len(next(os.walk(picture_path))[2])

if not config.without_video:
    print("start ffmpeg")
    if config.path is not None and not os.path.isfile(config.path):
        print(f"File does not exist with path: {config.path}")
        exit()

    if config.path is not None:
        p = subprocess.Popen(
            f"ffmpeg -nostdin -loglevel error -threads 1 -skip_frame nokey -i {config.path}  -vsync 0 -r 30 -f image2 {picture_path}/%02d.png",
            shell=True,
        )

        prev_count = count - 1
        while prev_count != count:
            prev_count = int(count)
            time.sleep(2)
            count = len(next(os.walk(picture_path))[2])
            print(f"No of pictures {count}\r", end="", flush=True)
        print()
        p.communicate()

print("start findimagedupes")
subprocess.run(
    f'findimagedupes -t {config.threshold} -R "{picture_path}" > "{dups_file}"',
    shell=True,
)

print("start deletion")


def delete_all_but_largest_and_newest(filepaths):
    maxSize = max(map(lambda x: os.stat(x).st_size, filepaths))

    smallerFiles = [
        filepath for filepath in filepaths if os.stat(filepath).st_size < maxSize
    ]

    similarFiles = [
        filepath for filepath in filepaths if os.stat(filepath).st_size == maxSize
    ]

    newestFile = max(similarFiles, key=lambda x: os.stat(x).st_mtime)

    similarFiles.remove(newestFile)

    if not config.dry:
        list(map(os.remove, smallerFiles + similarFiles))

    return len(smallerFiles + similarFiles)


del_count = 0
with open(dups_file, "r") as fp:
    for line in fp:
        matches = re.findall("(?:(.*?(?:jpg|jpeg|png|gif))[\s]{0,1})+?", line)
        del_count += delete_all_but_largest_and_newest(matches)


print(f"{del_count} images were removed from {count}")

if config.stop_remove_file:
    shutil.move(dups_file, os.getcwd() + "/" + "dups.txt")
shutil.rmtree(tmp_dir)
