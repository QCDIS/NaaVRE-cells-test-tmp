import glob
import os
import pathlib

import argparse
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--S3_done', action='store', type=str, required=True, dest='S3_done')


args = arg_parser.parse_args()
print(args)

id = args.id

S3_done = args.S3_done.replace('"','')


conf_local_path_retiled = os.path.join( pathlib.Path('/tmp/data').as_posix(), 'retiled')


conf_local_path_retiled = os.path.join( pathlib.Path('/tmp/data').as_posix(), 'retiled')

S3_done 

tiles = []
tile_folders = glob.glob(os.path.join(conf_local_path_retiled, 'tile_*_*'))

for folder in tile_folders:
    folder_name = os.path.basename(folder)
    tiles.append(folder_name)  # Append only the folder name
print(tiles)

import json
filename = "/tmp/tiles_" + id + ".json"
file_tiles = open(filename, "w")
file_tiles.write(json.dumps(tiles))
file_tiles.close()
