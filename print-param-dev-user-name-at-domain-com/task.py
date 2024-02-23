
import argparse
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--hostname', action='store', type=str, required=True, dest='hostname')

arg_parser.add_argument('--mode', action='store', type=str, required=True, dest='mode')

arg_parser.add_argument('--num', action='store', type=int, required=True, dest='num')

arg_parser.add_argument('--output', action='store', type=str, required=True, dest='output')

arg_parser.add_argument('--password', action='store', type=str, required=True, dest='password')

arg_parser.add_argument('--remote', action='store', type=str, required=True, dest='remote')

arg_parser.add_argument('--username', action='store', type=str, required=True, dest='username')


args = arg_parser.parse_args()
print(args)

id = args.id

hostname = args.hostname.replace('"','')
mode = args.mode.replace('"','')
num = args.num
output = args.output.replace('"','')
password = args.password.replace('"','')
remote = args.remote.replace('"','')
username = args.username.replace('"','')



print(hostname)
print(username)
print(password)
print(remote)
print(num)
print(mode)
print(output)

