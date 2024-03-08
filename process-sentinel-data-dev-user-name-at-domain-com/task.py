import acolite as ac
import os

import argparse
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--input_dirs', action='store', type=str, required=True, dest='input_dirs')

arg_parser.add_argument('--settings_file', action='store', type=str, required=True, dest='settings_file')


args = arg_parser.parse_args()
print(args)

id = args.id

import json
input_dirs = json.loads(args.input_dirs)
settings_file = args.settings_file.replace('"','')


conf_data_dir = '/tmp/data'


conf_data_dir = '/tmp/data'


output_dirs = []

for input_dir in input_dirs:
    dir_basename = os.path.basename(input_dir).removesuffix('.SAFE')
    output_dir = f"{conf_data_dir}/acolite-output/{dir_basename}"
    ac.acolite.acolite_run(settings_file, inputfile=input_dir, output=output_dir)
    output_dirs.append(output_dir)

import json
filename = "/tmp/output_dirs_" + id + ".json"
file_output_dirs = open(filename, "w")
file_output_dirs.write(json.dumps(output_dirs))
file_output_dirs.close()
