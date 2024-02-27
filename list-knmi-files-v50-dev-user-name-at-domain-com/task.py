import math
import requests
import sys

import argparse
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--init_complete', action='store', type=str, required=True, dest='init_complete')

arg_parser.add_argument('--param_api_key', action='store', type=str, required=True, dest='param_api_key')
arg_parser.add_argument('--param_concurrency', action='store', type=int, required=True, dest='param_concurrency')
arg_parser.add_argument('--param_end_date', action='store', type=str, required=True, dest='param_end_date')
arg_parser.add_argument('--param_radar', action='store', type=str, required=True, dest='param_radar')
arg_parser.add_argument('--param_start_date', action='store', type=str, required=True, dest='param_start_date')

args = arg_parser.parse_args()
print(args)

id = args.id

init_complete = args.init_complete.replace('"','')

param_api_key = args.param_api_key
param_concurrency = args.param_concurrency
param_end_date = args.param_end_date
param_radar = args.param_radar
param_start_date = args.param_start_date

conf_radars = {'herwijnen' :  ['radar_volume_full_herwijnen',1.0,'https://api.dataplatform.knmi.nl/open-data/v1/datasets/radar_volume_full_herwijnen/versions/1.0/files','NL/HRW'],'denhelder' :  ['radar_volume_full_denhelder',2.0,'https://api.dataplatform.knmi.nl/open-data/v1/datasets/radar_volume_denhelder/versions/2.0/files','NL/DHL']}

conf_interval = 60 # minutes, HH:00


conf_radars = {'herwijnen' :  ['radar_volume_full_herwijnen',1.0,'https://api.dataplatform.knmi.nl/open-data/v1/datasets/radar_volume_full_herwijnen/versions/1.0/files','NL/HRW'],'denhelder' :  ['radar_volume_full_denhelder',2.0,'https://api.dataplatform.knmi.nl/open-data/v1/datasets/radar_volume_denhelder/versions/2.0/files','NL/DHL']}
conf_interval = 60 # minutes, HH:00

def rewrite_list_nested(in_list,concurrency):
    out_list = []
    in_list_len = len(in_list)
    worker_chunk_size = math.floor(in_list_len / concurrency)
    leftovers = in_list_len%param_concurrency
    while in_list:
        leftover = 0
        if leftovers:
            leftover = 1
            leftovers -= leftover
        out_list.append(in_list[:worker_chunk_size+leftover])
        in_list = in_list[worker_chunk_size+leftover:]
    return out_list
init_complete = init_complete.replace("'","")
init_complete = init_complete.replace('"','')
if init_complete == "Yes":
    print("Workflow configuration succesfull")
else:
    print("Workflow configuration was not complete, exitting")
    sys.exit(1)
start_ts = param_start_date
end_ts = param_end_date
datasetName, datasetVersion, api_url, _ = conf_radars.get(param_radar)
params = {'datasetName' : datasetName,
          'datasetVersion' : datasetVersion,
          'maxKeys' : 10,
          'sorting' : "asc",
          'orderBy' : "created",
          'begin' : start_ts,
          'end' : end_ts,
         }
dataset_files = []
while True:
    list_files_response = requests.get(url = api_url,
                            headers={"Authorization": param_api_key},
                            params = params)
    list_files = list_files_response.json()
    dset_files = list_files.get("files")
    dset_files = [list(dset_file.values()) for dset_file in dset_files]
    dataset_files += dset_files
    nextPageToken = list_files.get("nextPageToken")
    if not nextPageToken:
        break
    else:
        params.update({'nextPageToken' : nextPageToken})

filtered_list = []
interval_list = list(range(0,60,conf_interval))
for dataset_file in dataset_files:
    minute = int(dataset_file[0].split('_')[-1].split('.')[0][-2:])
    if minute in interval_list:
        filtered_list.append(dataset_file)

dataset_files = filtered_list
print(f"Found {len(dataset_files)} files")
print(dataset_files)

dataset_files = rewrite_list_nested(dataset_files,param_concurrency)


import json
filename = "/tmp/dataset_files_" + id + ".json"
file_dataset_files = open(filename, "w")
file_dataset_files.write(json.dumps(dataset_files))
file_dataset_files.close()
