from laserfarm import DataProcessing
import os
import pathlib
import shutil

import argparse
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--tiles', action='store', type=str, required=True, dest='tiles')


args = arg_parser.parse_args()
print(args)

id = args.id

import json
tiles = json.loads(args.tiles)


conf_local_path_targets = os.path.join( pathlib.Path('/tmp/data').as_posix(), 'targets')

conf_feature_name = 'perc_95_normalized_height'

conf_tile_mesh_size = '10.'

conf_min_x = '-113107.81'

conf_max_x = '398892.19'

conf_min_y = '214783.87'

conf_max_y = '726783.87'

conf_n_tiles_side = '512'

conf_local_path_retiled = os.path.join( pathlib.Path('/tmp/data').as_posix(), 'retiled')

conf_attribute = 'raw_classification'

conf_filter_type = 'select_equal'

conf_apply_filter_value = '1'

conf_validate_precision = '0.001'


conf_local_path_targets = os.path.join( pathlib.Path('/tmp/data').as_posix(), 'targets')
conf_feature_name = 'perc_95_normalized_height'
conf_tile_mesh_size = '10.'
conf_min_x = '-113107.81'
conf_max_x = '398892.19'
conf_min_y = '214783.87'
conf_max_y = '726783.87'
conf_n_tiles_side = '512'
conf_local_path_retiled = os.path.join( pathlib.Path('/tmp/data').as_posix(), 'retiled')
conf_attribute = 'raw_classification'
conf_filter_type= 'select_equal'
conf_apply_filter_value = '1'
conf_validate_precision = '0.001'

for t in tiles:
    local_path_targets = os.path.join(conf_local_path_targets, t)
    features = [conf_feature_name]

    tile_mesh_size = float(conf_tile_mesh_size)

    grid_feature = {
        'min_x': float(conf_min_x),
        'max_x': float(conf_max_x),
        'min_y': float(conf_min_y),
        'max_y': float(conf_max_y),
        'n_tiles_side': int(conf_n_tiles_side)
    }

    feature_extraction_input = {
        'setup_local_fs': {
            'input_folder': conf_local_path_retiled,
            'output_folder': local_path_targets
        },
        'load': {'attributes': [conf_attribute]},
        'normalize': 1,
        'apply_filter': {
            'filter_type': conf_filter_type, 
            'attribute': conf_attribute,
            'value': [int(conf_apply_filter_value)]#ground surface (2), water (9), buildings (6), artificial objects (26), vegetation (?), and unclassified (1)
        },
        'generate_targets': {
            'tile_mesh_size' : tile_mesh_size,
            'validate' : True,
            'validate_precision': float(conf_validate_precision),
            **grid_feature
        },
        'extract_features': {
            'feature_names': features,
            'volume_type': 'cell',
            'volume_size': tile_mesh_size
        },
        'export_targets': {
            'attributes': features,
            'multi_band_files': False
        },
    }
    idx = (t.split('_')[1:])

    processing = DataProcessing(t, tile_index=idx,label=t).config(feature_extraction_input)
    processing.run()
    target_file = os.path.join(local_path_targets, conf_feature_name,t+'.ply')  
    target_folder = os.path.join(conf_local_path_targets, conf_feature_name)
    os.makedirs(target_folder, exist_ok=True)
    shutil.move(target_file, target_folder)
    
S5_done = 'True'

import json
filename = "/tmp/S5_done_" + id + ".json"
file_S5_done = open(filename, "w")
file_S5_done.write(json.dumps(S5_done))
file_S5_done.close()
