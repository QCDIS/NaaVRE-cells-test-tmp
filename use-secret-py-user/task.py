
import argparse
import json
import os
arg_parser = argparse.ArgumentParser()

  secret_xyz = os.getenv('secret_xyz')

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--param_xyz', action='store', type=int, required=True, dest='param_xyz')

args = arg_parser.parse_args()
print(args)

id = args.id


param_xyz = args.param_xyz


print(param_xyz, secret_xyz)

