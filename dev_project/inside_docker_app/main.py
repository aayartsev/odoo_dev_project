import base64
import json

from parse_args import args
from check_virtualenv import VirtualenvChecker
from check_odoo import OdooChecker

def main():
    config = json.loads(base64.b64decode(args.config_base64_data).decode())
    VirtualenvChecker(config)
    OdooChecker(config)

if __name__ == "__main__":
    main()