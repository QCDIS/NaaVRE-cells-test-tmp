import os

import argparse
import json
import os
arg_parser = argparse.ArgumentParser()


arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--a', action='store', type=int, required=True, dest='a')


args = arg_parser.parse_args()
print(args)

id = args.id

a = args.a



print(a)
cmd = "vol2bird --version"

msg = os.system(cmd)  # returns the exit code in unix

a = 0.6148744804155413

file_msg = open("/tmp/msg_" + id + ".json", "w")
file_msg.write(json.dumps(msg))
file_msg.close()
