#!/usr/bin/env python3

import os
import subprocess
import re
import argparse
import time

# REQUIRES findimagedupes

dupsFile = "dups.txt"

parser = argparse.ArgumentParser(prog="./vid2pngAndDeleteDuplicates.py")

parser.add_argument("-p", "--path", metavar="pathOfVid", type=str, default=None)
parser.add_argument("-P", "--path_of_pictures", type=str, default="pictures")
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

print("path to vid:", config.path)
print("keep dupes file:", config.stop_remove_file)
print("DryRun:", config.dry)
print("Threshhold:", config.threshold)
print("without_video:", config.without_video)

picture_path = config.path_of_pictures

count = 1
while os.path.isdir(picture_path):
    count += 1
    picture_path = "pictures" + str(count)
print("Picture path is:", picture_path)
subprocess.run(f"mkdir {picture_path}", shell=True)

count = len(next(os.walk(picture_path))[2])

if not config.without_video:
    print("start ffmpeg")
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
    f'findimagedupes -t {config.threshold} -R "{picture_path}" > "{dupsFile}"',
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

    if config.dry:
        print(smallerFiles + similarFiles)

    if not config.dry:
        list(map(os.remove, smallerFiles + similarFiles))
        print("Removed: ", len(smallerFiles + similarFiles))


with open(dupsFile, "r") as fp:
    for cnt, line in enumerate(fp):
        matches = re.findall("(?:(.*?(?:jpg|jpeg|png|gif))[\s]{0,1})+?", line)
        delete_all_but_largest_and_newest(matches)

new_count = len(next(os.walk(picture_path))[2])
print(f"{count - new_count} images were removed from {count}")

if not config.stop_remove_file:
    os.remove(dupsFile)
