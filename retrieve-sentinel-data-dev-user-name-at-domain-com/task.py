from minio import Minio
import glob
import os

import argparse
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--param_s3_public_bucket', action='store', type=str, required=True, dest='param_s3_public_bucket')
arg_parser.add_argument('--param_s3_public_prefix', action='store', type=str, required=True, dest='param_s3_public_prefix')
arg_parser.add_argument('--param_s3_server', action='store', type=str, required=True, dest='param_s3_server')

args = arg_parser.parse_args()
print(args)

id = args.id


param_s3_public_bucket = args.param_s3_public_bucket
param_s3_public_prefix = args.param_s3_public_prefix
param_s3_server = args.param_s3_server

conf_data_dir = '/tmp/data'


conf_data_dir = '/tmp/data'


minio_client = Minio(param_s3_server, secure=True)

for item in minio_client.list_objects(param_s3_public_bucket, prefix=f"{param_s3_public_prefix}", recursive=True):
    target_file = f"{conf_data_dir}/input/{item.object_name.removeprefix(param_s3_public_prefix)}"
    if not os.path.exists(target_file):
        print("Downloading", item.object_name)
        minio_client.fget_object(param_s3_public_bucket, item.object_name, target_file)

input_dirs = sorted(glob.glob(f"{conf_data_dir}/input/*.SAFE"))
settings_file = f"{conf_data_dir}/input/settings.txt"

import json
filename = "/tmp/input_dirs_" + id + ".json"
file_input_dirs = open(filename, "w")
file_input_dirs.write(json.dumps(input_dirs))
file_input_dirs.close()
filename = "/tmp/settings_file_" + id + ".json"
file_settings_file = open(filename, "w")
file_settings_file.write(json.dumps(settings_file))
file_settings_file.close()
