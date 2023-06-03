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
        self.check_file_system()
    
    def check_git(self):
        process_result = subprocess.run(["git",  "--version"], capture_output=True)
        output_string = process_result.stdout.decode("utf-8")
        if GIT_WORKING_MESSAGE not in output_string:
            logging.error("Did you installed git?")
            exit()

    def check_docker(self):
        process_result = subprocess.run(["docker",  "info"], capture_output=True)
        output_string = process_result.stdout.decode("utf-8")
        if DOCKER_WORKING_MESSAGE not in output_string:
            logging.error("Cannot connect to the Docker daemon. Is the docker daemon running?")
            exit()

    def check_docker_compose(self):
        process_result = subprocess.run(["docker-compose",  "version"], capture_output=True)
        output_string = process_result.stdout.decode("utf-8")
        output_string = output_string.lower().replace("-"," ")
        if DOCKER_COMPOSE_WORKING_MESSAGE not in output_string:
            logging.error("Cannot get docker-compose info, did you install it?")
            exit()
        docker_compose_version = "default"
        try:
            docker_compose_version = output_string.split("\n")[0].split(" ")[3].strip(",").strip("v")
        except BaseException:
                logging.warning(
                    "We can not detect docker-compose versions, we will use default settings. "
                    "If your system is not starting you can change param 'version:' in file "
                    "./dev_project/templates/docker-compose.yml manualy. Try to start command "
                    "'docker-compose  config' and read carefully"
                )
        self.config["compose_file_version"] = DOCKER_COMPOSE_VERSION_DATA[docker_compose_version]["file_version"]
        self.config["no_log_prefix"] = DOCKER_COMPOSE_VERSION_DATA[docker_compose_version]["no_log_prefix"]
    
    def check_file_system(self):
        for dir_path in [
            self.config["backups"]["local_dir"],
            self.config["odoo_projects_dir"],
        ]:
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path)
                except BaseException:
                    logging.error(f"Cannot create dir, {dir_path}, please check it")
                    exit()
        
        
        os.chdir(self.config["odoo_src_dir"])
        odoo_src_state_bytes = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True)
        odoo_src_state_string = odoo_src_state_bytes.stdout.decode("utf-8")
        if not "true" in odoo_src_state_string:
            logging.error(
                f"""Your odoo src directory {self.config["odoo_src_dir"]} is not git repository."""
                "Please fix it, or delete and clone its repo again: "
                "git clone https://github.com/odoo/odoo.git"    
            )
            exit()
