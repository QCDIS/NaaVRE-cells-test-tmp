from laserfarm import GeotiffWriter
import os
import pathlib

import argparse
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--S5_done', action='store', type=str, required=True, dest='S5_done')

arg_parser.add_argument('--param_hostname', action='store', type=str, required=True, dest='param_hostname')
arg_parser.add_argument('--param_password', action='store', type=str, required=True, dest='param_password')
arg_parser.add_argument('--param_username', action='store', type=str, required=True, dest='param_username')

args = arg_parser.parse_args()
print(args)

id = args.id

S5_done = args.S5_done.replace('"','')

param_hostname = args.param_hostname
param_password = args.param_password
param_username = args.param_username

conf_local_path_targets = os.path.join( pathlib.Path('/tmp/data').as_posix(), 'targets')

conf_local_path_geotiff = os.path.join( pathlib.Path('/tmp/data').as_posix(), 'geotiff')

conf_remote_path_geotiffs = pathlib.Path('/webdav/vl-laserfarm/' +  '' + '/geotiffs')

conf_feature_name = 'perc_95_normalized_height'

conf_wd_opts = { 'webdav_hostname': param_hostname, 'webdav_login': param_username, 'webdav_password': param_password}


conf_local_path_targets = os.path.join( pathlib.Path('/tmp/data').as_posix(), 'targets')
conf_local_path_geotiff = os.path.join( pathlib.Path('/tmp/data').as_posix(), 'geotiff')
conf_remote_path_geotiffs = pathlib.Path('/webdav/vl-laserfarm/' +  '' + '/geotiffs')
conf_feature_name = 'perc_95_normalized_height'
conf_wd_opts = { 'webdav_hostname': param_hostname, 'webdav_login': param_username, 'webdav_password': param_password}

S5_done

geotiff_export_input = {
    'setup_local_fs': {
        'input_folder': conf_local_path_targets,
         'output_folder': conf_local_path_geotiff
        },
    'parse_point_cloud': {},
    'data_split': {'xSub': 1, 'ySub': 1},
    'create_subregion_geotiffs': {'output_handle': 'geotiff'},
    'pushremote': conf_remote_path_geotiffs.as_posix(),
}

writer = GeotiffWriter(input_dir=conf_feature_name, bands=conf_feature_name, label=conf_feature_name).config(geotiff_export_input).setup_webdav_client(conf_wd_opts)
writer.run()

remote_path_geotiffs = str(conf_remote_path_geotiffs)
S6_done = 'True'

import json
filename = "/tmp/S6_done_" + id + ".json"
file_S6_done = open(filename, "w")
file_S6_done.write(json.dumps(S6_done))
file_S6_done.close()
