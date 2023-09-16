import subprocess
import logging
import platform

if platform.system() == "Linux":
    import pwd
    import grp

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
            logging.error("Did you install git?")
            exit()
    
    def get_groups(self, user):
        gids = [g.gr_gid for g in grp.getgrall() if user in g.gr_mem]
        gid = pwd.getpwnam(user).pw_gid
        gids.append(grp.getgrgid(gid).gr_gid)
        return [grp.getgrgid(gid).gr_name for gid in gids]

    def check_docker(self):
        if platform.system() == "Linux":
            groups = self.get_groups(CURRENT_USER)
            if LINUX_DOCKER_GROUPNAME not in groups:
                logging.error(
                    f"""You need to add your user {CURRENT_USER} to group {LINUX_DOCKER_GROUPNAME}"""
                    f"""run this command as root or sudo:  usermod -a -G {LINUX_DOCKER_GROUPNAME} {CURRENT_USER}"""
                    f"""then reboot your computer"""
                )
                exit()
        process_result = subprocess.run(["docker",  "info"], capture_output=True)
        output_string = process_result.stdout.decode("utf-8")
        if DOCKER_WORKING_MESSAGE not in output_string:
            logging.error("Cannot connect to the Docker daemon. Is the docker daemon running?")
            exit()

    def check_docker_compose(self):
        self.config["no_log_prefix"] = True
        process_result = subprocess.run(["docker-compose",  "version"], capture_output=True)
        output_string = process_result.stdout.decode("utf-8")
        output_string = output_string.lower().replace("-"," ")
        if DOCKER_COMPOSE_WORKING_MESSAGE not in output_string:
            logging.error("Cannot get docker-compose info, did you install it?")
            exit()
        up_help_result = subprocess.run(["docker-compose",  "up", "--help"], capture_output=True)
        up_help_string = up_help_result.stdout.decode("utf-8")
        output_string = output_string.lower().replace("-"," ")
        if NO_LOG_PREFIX not in up_help_string:
            self.config["no_log_prefix"] = False
        self.config["compose_file_version"] = DOCKER_COMPOSE_DEFAULT_FILE_VERSION
    
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
