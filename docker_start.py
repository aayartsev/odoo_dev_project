#!/bin/python3
import os
import sys
import logging

from dev_project.host_config_parser import ConfParser
from dev_project.check_system import SystemChecker
from dev_project.host_env import CreateEnvironment
from dev_project.inside_docker_app.parse_args import ArgumentParser
from dev_project.host_start_string_builder import StartStringBuilder

def main():
    current_dir_path = os.path.dirname(os.path.abspath(__file__))
    args_list = sys.argv[1:]
    args_dict = ArgumentParser(args_list).args_dict
    config = ConfParser(
        current_dir_path,
        args_dict
    ).config
    SystemChecker(config)
    environment = CreateEnvironment(config)
    environment.update_config()
    environment.generate_dockerfile()
    environment.generate_config_file()
    StartStringBuilder(config)
    environment.generate_docker_compose_file()
    environment.checkout_dependencies()
    environment.update_links()
    environment.update_vscode_debugger_launcher()

    os.chdir(config["project_dir"])

    try:
        if config["no_log_prefix"]:
            os.system(f"""docker-compose up --no-log-prefix --abort-on-container-exit""")
        else:
            os.system(f"""docker-compose up --abort-on-container-exit""")
    except KeyboardInterrupt:
        logging.info("Control+C pressed")
        sys.exit()

if __name__ == "__main__":
    main()
