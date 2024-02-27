from pathlib import Path
import math
import requests

import argparse
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--dataset_files', action='store', type=str, required=True, dest='dataset_files')

arg_parser.add_argument('--param_api_key', action='store', type=str, required=True, dest='param_api_key')
arg_parser.add_argument('--param_concurrency', action='store', type=int, required=True, dest='param_concurrency')
arg_parser.add_argument('--param_radar', action='store', type=str, required=True, dest='param_radar')

args = arg_parser.parse_args()
print(args)

id = args.id

import json
dataset_files = json.loads(args.dataset_files)

param_api_key = args.param_api_key
param_concurrency = args.param_concurrency
param_radar = args.param_radar

conf_radars = {'herwijnen' :  ['radar_volume_full_herwijnen',1.0,'https://api.dataplatform.knmi.nl/open-data/v1/datasets/radar_volume_full_herwijnen/versions/1.0/files','NL/HRW'],'denhelder' :  ['radar_volume_full_denhelder',2.0,'https://api.dataplatform.knmi.nl/open-data/v1/datasets/radar_volume_denhelder/versions/2.0/files','NL/DHL']}

conf_local_knmi = "/tmp/data/knmi"


conf_radars = {'herwijnen' :  ['radar_volume_full_herwijnen',1.0,'https://api.dataplatform.knmi.nl/open-data/v1/datasets/radar_volume_full_herwijnen/versions/1.0/files','NL/HRW'],'denhelder' :  ['radar_volume_full_denhelder',2.0,'https://api.dataplatform.knmi.nl/open-data/v1/datasets/radar_volume_denhelder/versions/2.0/files','NL/DHL']}
conf_local_knmi = "/tmp/data/knmi"
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
check_list = []
for dataset_file in dataset_files:
    if isinstance(dataset_file,list):
        check_list += dataset_file
    else:
        check_list.append(dataset_file)
dataset_files = check_list   
n_files = len(dataset_files)      
print(f"Starting download of {n_files} files.")
_, _, api_url, radar_code = conf_radars.get(param_radar)
knmi_pvol_paths = []
idx = 1
for dataset_file in dataset_files:
    filename = dataset_file[0]
    fname_parts = filename.split('_')
    fname_date_part = fname_parts[-1].split('.')[0]
    year = fname_date_part[0:4]
    month = fname_date_part[4:6]
    day = fname_date_part[6:8]
    p = Path(f"{conf_local_knmi}/{radar_code}/{year}/{month}/{day}/{filename}")
    knmi_pvol_paths.append('{}'.format(str(p)))
    
    if not p.exists():
        print(f"Downloading file {idx}/{n_files}")
        endpoint = f"{api_url}/{filename}/url"
        get_file_response = requests.get(endpoint, headers={"Authorization": param_api_key})
        download_url = get_file_response.json().get("temporaryDownloadUrl")
        dataset_file_response = requests.get(download_url)
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(dataset_file_response.content)
    else:
        print(f"{p} already exists, skipping")
    idx += 1

knmi_pvol_paths = rewrite_list_nested(knmi_pvol_paths,param_concurrency)
print(knmi_pvol_paths)
print("Finished downloading files")

import json
filename = "/tmp/knmi_pvol_paths_" + id + ".json"
file_knmi_pvol_paths = open(filename, "w")
file_knmi_pvol_paths.write(json.dumps(knmi_pvol_paths))
file_knmi_pvol_paths.close()
