#!/bin/python3
import os
import sys
import subprocess

from dev_project.host_config_parser import ConfParser
from dev_project.check_system import SystemChecker
from dev_project.host_env import CreateEnvironment
from dev_project.parse_args import ArgumentParser
from dev_project.host_start_string_builder import StartStringBuilder

current_dir_path = os.path.dirname(os.path.abspath(__file__))
args_list = sys.argv[1:]
args_dict = ArgumentParser(args_list).args_dict
config = ConfParser(current_dir_path).config
SystemChecker(config)
environment = CreateEnvironment(config)
environment.update_config()
environment.generate_dockerfile()
StartStringBuilder(config, args_dict)mc
environment.generate_docker_compose_file()
environment.checkout_dependencies()
environment.update_links()
environment.update_vscode_debugger_launcher()

os.chdir(config["project_dir"])

try:
    if config["no_log_prefix"]:
        subprocess.run(["docker-compose", "up", "--no-log-prefix"])
    else:
        subprocess.run(["docker-compose", "up"])
except KeyboardInterrupt:
    print("Control+C pressed")
    sys.exit()
