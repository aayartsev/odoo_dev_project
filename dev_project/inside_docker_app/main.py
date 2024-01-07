import sys
import base64
import json

from parse_args import args
from check_virtualenv import VirtualenvChecker
from check_odoo import OdooChecker

def get_config(args):
    config_data = json.loads(base64.b64decode(args.config_base64_data).decode())
    return config_data

def main():
    config = get_config(args)
    VirtualenvChecker(config)
    OdooChecker(config)

if __name__ == "__main__":
    main()