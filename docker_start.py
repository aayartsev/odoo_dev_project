#!/bin/python3
import os
import sys
import subprocess

from dev_project.host_config_parser import ConfParser
from dev_project.host_env import CreateEnvironment
from dev_project.parse_args import ArgumentParser
from dev_project.host_start_string_builder import StartStringBuilder

current_dir_path = os.path.dirname(os.path.abspath(__file__))
args_list = sys.argv[1:]
args_dict = ArgumentParser(args_list).args_dict
build_image = args_dict.get("--build_image", False)
config = ConfParser(current_dir_path).config
environment = CreateEnvironment(config)
environment.update_config()
environment.generate_dockerfile()
if build_image:
    subprocess.run(["docker", "build", "-f", config["dockerfile_path"], "-t", config["odoo_image_name"], "."])
    exit()
environment.generate_docker_compose_file()
environment.checkout_dependencies()
environment.update_links()
environment.update_vscode_debugger_launcher()

os.environ["START_STRING"] = StartStringBuilder(config, args_dict).get_start_string()
os.chdir(config["project_dir"])

try:
    subprocess.run(["docker-compose", "up", "--no-log-prefix"])
except KeyboardInterrupt:
    print("Control+C pressed")
    sys.exit()