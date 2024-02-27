from webdav3 import client as wc
import os
import pathlib

import argparse
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--param_webdav_endpoint', action='store', type=str, required=True, dest='param_webdav_endpoint')
arg_parser.add_argument('--param_webdav_password', action='store', type=str, required=True, dest='param_webdav_password')
arg_parser.add_argument('--param_webdav_user', action='store', type=str, required=True, dest='param_webdav_user')

args = arg_parser.parse_args()
print(args)

id = args.id


param_webdav_endpoint = args.param_webdav_endpoint
param_webdav_password = args.param_webdav_password
param_webdav_user = args.param_webdav_user

conf_webdav_user_path = f'/vl-vol2bird/{os.environ.get("JUPYTERHUB_USER")}'

conf_webdav_output_pvol = f'/vl-vol2bird/{os.environ.get("JUPYTERHUB_USER")}'+'/pvol' # F'string formatting is breaking the analyser. Concating Str by addition works

conf_webdav_output_vp = f'/vl-vol2bird/{os.environ.get("JUPYTERHUB_USER")}'+'/vp'

conf_local_root = "/tmp/data"

conf_local_knmi = "/tmp/data/knmi"

conf_local_odim = "/tmp/data/odim"

conf_local_vp = "/tmp/data/vp"

conf_local_conf = "/tmp/data/conf"

conf_local_radar_db = "/tmp/data/conf/OPERA_RADARS_DB.json"

conf_webdav_radar_db = '/vl-vol2bird/common_data/conf/OPERA_RADARS_DB.json'


conf_webdav_user_path = f'/vl-vol2bird/{os.environ.get("JUPYTERHUB_USER")}'
conf_webdav_output_pvol =  f'/vl-vol2bird/{os.environ.get("JUPYTERHUB_USER")}'+'/pvol' # F'string formatting is breaking the analyser. Concating Str by addition works
conf_webdav_output_vp =  f'/vl-vol2bird/{os.environ.get("JUPYTERHUB_USER")}'+'/vp'
conf_local_root = "/tmp/data"
conf_local_knmi = "/tmp/data/knmi"
conf_local_odim = "/tmp/data/odim"
conf_local_vp = "/tmp/data/vp"
conf_local_conf = "/tmp/data/conf"
conf_local_radar_db = "/tmp/data/conf/OPERA_RADARS_DB.json"
conf_webdav_radar_db = '/vl-vol2bird/common_data/conf/OPERA_RADARS_DB.json'
options = {
 'webdav_hostname': param_webdav_endpoint,
 'webdav_login':    param_webdav_user,
 'webdav_password': param_webdav_password
}
client = wc.Client(options)
for webdav_dir in [conf_webdav_user_path,conf_webdav_output_pvol,conf_webdav_output_vp]:
    if not client.check(webdav_dir):
        client.mkdir(webdav_dir)

for local_dir in [conf_local_root,conf_local_knmi,conf_local_odim,conf_local_vp, conf_local_conf]:
    local_dir = pathlib.Path(local_dir)
    if not local_dir.exists():
        local_dir.mkdir(parents=True,exist_ok=True)
if not pathlib.Path(conf_local_radar_db).exists():
    print(f"{conf_local_radar_db} not found, downloading")
    client.download_sync(remote_path = conf_webdav_radar_db, local_path = conf_local_radar_db)
    
init_complete = "Yes" # Cant sent bool
print("Finished initialization")

import json
filename = "/tmp/init_complete_" + id + ".json"
file_init_complete = open(filename, "w")
file_init_complete.write(json.dumps(init_complete))
file_init_complete.close()
