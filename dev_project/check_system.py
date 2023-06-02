import subprocess
import logging

from .constants import *

class SystemChecker():

    def __init__(self, config):
        self.config = config
        if self.config["check_system"]:
            self.check_git()
            self.check_docker()
        self.check_docker_compose()
    
    def check_git(self):
        process_result = subprocess.run(["git",  "--version"], capture_output=True)
        output_string = process_result.stdout.decode("utf-8")
        if GIT_WORKING_MESSAGE not in output_string:
            logging.error(f"""Did you installed git?""")
            exit()

    def check_docker(self):
        process_result = subprocess.run(["docker",  "info"], capture_output=True)
        output_string = process_result.stdout.decode("utf-8")
        if DOCKER_WORKING_MESSAGE not in output_string:
            logging.error(f"""Cannot connect to the Docker daemon. Is the docker daemon running?""")
            exit()

    def check_docker_compose(self):
        process_result = subprocess.run(["docker-compose",  "version"], capture_output=True)
        output_string = process_result.stdout.decode("utf-8")
        docker_compose_version = "default"
        if platform.system() == "Linux":
            try:
                docker_compose_version = output_string.split("\n")[0].split(" ")[2].strip(",")
            except BaseException:
                logging.warning(f"""We can not detect docker-compose versions, we will use default settings""")
        self.config["compose_file_version"] = DOCKER_COMPOSE_VERSION_DATA[docker_compose_version]["file_version"]
        self.config["no_log_prefix"] = DOCKER_COMPOSE_VERSION_DATA[docker_compose_version]["no_log_prefix"]
