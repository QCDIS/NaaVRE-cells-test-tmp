import glob
import os
import pathlib

import argparse
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--S2_done', action='store', type=str, required=True, dest='S2_done')


args = arg_parser.parse_args()
print(args)

id = args.id

S2_done = args.S2_done.replace('"','')


conf_local_path_split = os.path.join( pathlib.Path('/tmp/data').as_posix(), 'split')


conf_local_path_split = os.path.join( pathlib.Path('/tmp/data').as_posix(), 'split')

S2_done 

split_laz_folder = glob.glob(os.path.join(conf_local_path_split, '*.LAZ'))
split_laz_files = []
print("File names ending with .LAZ:")
for file_path in split_laz_folder:
    split_laz_files.append(os.path.basename(file_path))

print(split_laz_files)
S21_done = 'True'

import json
filename = "/tmp/split_laz_files_" + id + ".json"
file_split_laz_files = open(filename, "w")
file_split_laz_files.write(json.dumps(split_laz_files))
file_split_laz_files.close()
