
import argparse
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--a', action='store', type=int, required=True, dest='a')

arg_parser.add_argument('--count', action='store', type=int, required=True, dest='count')


args = arg_parser.parse_args()
print(args)

id = args.id

a = args.a
count = args.count



some_list = range(count, a+1)

msg = '1'
a = 0.5514231387311931

import json
filename = "/tmp/msg_" + id + ".json"
file_msg = open(filename, "w")
file_msg.write(json.dumps(msg))
file_msg.close()
