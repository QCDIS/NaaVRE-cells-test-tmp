
import argparse
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--list_of_paths', action='store', type=str, required=True, dest='list_of_paths')


args = arg_parser.parse_args()
print(args)

id = args.id

import json
list_of_paths = json.loads(args.list_of_paths)




for l in list_of_paths:
    print(l)
a = 0.12582577920891624

