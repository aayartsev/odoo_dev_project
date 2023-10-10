import sys
import base64
import json

from parse_args import ArgumentParser
from check_virtualenv import VirtualenvChecker
from check_odoo import OdooChecker
from command_line_params import *

def get_config(args_dict):
    config_base64_data = args_dict.get(CONFIG_BASE64_DATA, "")
    config_data = json.loads(base64.b64decode(config_base64_data).decode())
    return config_data

def main():
    args_list = sys.argv[1:]
    args_dict = ArgumentParser(args_list).args_dict
    config = get_config(args_dict)
    VirtualenvChecker(config)
    OdooChecker(config)

if __name__ == "__main__":
    main()