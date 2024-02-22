
import argparse
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--param_a', action='store', type=str, required=True, dest='param_a')
arg_parser.add_argument('--param_b', action='store', type=str, required=True, dest='param_b')
arg_parser.add_argument('--param_c', action='store', type=str, required=True, dest='param_c')
arg_parser.add_argument('--param_d', action='store', type=str, required=True, dest='param_d')
arg_parser.add_argument('--param_e', action='store', type=str, required=True, dest='param_e')

args = arg_parser.parse_args()
print(args)

id = args.id


param_a = args.param_a
param_b = args.param_b
param_c = args.param_c
param_d = args.param_d
param_e = args.param_e

conf_z = 'config'


conf_z = 'config'
print(param_a, param_b, param_c, param_d, param_e, conf_z)

