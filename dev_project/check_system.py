import subprocess
import platform
import json
import os

if platform.system() == "Linux":
    import pwd
    import grp

from . import constants
from . import translations

from .inside_docker_app.logger import get_module_logger

_logger = get_module_logger(__name__)

class SystemChecker():

    def __init__(self, config):
        self.config = config
        if self.config.check_system:
            self.check_git()
            self.check_docker()
            self.check_docker_compose()
        self.check_file_system()
    
    def check_git(self):
        process_result = subprocess.run(["git",  "--version"], capture_output=True)
        output_string = process_result.stdout.decode("utf-8")
        if constants.GIT_WORKING_MESSAGE not in output_string:
            _logger.error(translations.get_translation(translations.IS_GIT_INSTALLED))
            exit()
    
    def get_groups(self, user):
        gids = [g.gr_gid for g in grp.getgrall() if user in g.gr_mem]
        gid = pwd.getpwnam(user).pw_gid
        gids.append(grp.getgrgid(gid).gr_gid)
        return [grp.getgrgid(gid).gr_name for gid in gids]

    def check_docker(self):
        if platform.system() == "Linux":
            groups = self.get_groups(constants.CURRENT_USER)
            if constants.LINUX_DOCKER_GROUPNAME not in groups:
                _logger.error(translations.get_translation(translations.USER_NOT_IN_DOCKER_GROUP).format(
                        CURRENT_USER=constants.CURRENT_USER,
                        LINUX_DOCKER_GROUPNAME=constants.LINUX_DOCKER_GROUPNAME,
                    )
                )
                exit()
        process_result = subprocess.run(["docker",  "info"], capture_output=True)
        output_string = process_result.stdout.decode("utf-8")
        if constants.DOCKER_WORKING_MESSAGE not in output_string:
            _logger.error(translations.get_translation(translations.CAN_NOT_CONNECT_DOCKER))
            exit()
        
        process_result = subprocess.run(["docker",  "images", "--format", "'{{json .}}'"], capture_output=True)
        output_string = process_result.stdout.decode("utf-8")
        result_list = []
        for record in output_string.split("\n"):
            if record:
                new_record = json.loads(record.replace("'", ""))
                if self.config.odoo_image_name == new_record["Repository"]:
                    result_list.append(new_record)
        if not result_list:
            self.config.env.build_image()

    def check_docker_compose(self):
        self.config.no_log_prefix = True
        process_result = subprocess.run(["docker-compose",  "version"], capture_output=True)
        output_string = process_result.stdout.decode("utf-8")
        output_string = output_string.lower().replace("-"," ")
        if constants.DOCKER_COMPOSE_WORKING_MESSAGE not in output_string:
            _logger.error(translations.get_translation(translations.CAN_NOT_GET_DOCKER_COMPOSE_INFO))
            exit()
        up_help_result = subprocess.run(["docker-compose",  "up", "--help"], capture_output=True)
        up_help_string = up_help_result.stdout.decode("utf-8")
        output_string = output_string.lower().replace("-"," ")
        if constants.NO_LOG_PREFIX not in up_help_string:
            self.config.no_log_prefix = False
    
    def check_file_system(self):
        for dir_path in [
            self.config.user_env.backups,
            self.config.user_env.odoo_projects_dir,
        ]:
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path)
                except BaseException:
                    _logger.error(translations.get_translation(translations.CAN_NOT_CREATE_DIR).format(
                        dir_path=dir_path,
                    ))
                    exit()
        
        
        os.chdir(self.config.user_env.odoo_src_dir)
        odoo_src_state_bytes = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True)
        odoo_src_state_string = odoo_src_state_bytes.stdout.decode("utf-8")
        if not "true" in odoo_src_state_string:
            clone_odoo = input(translations.get_translation(translations.DO_YOU_WANT_CLONE_ODOO))
            if clone_odoo and clone_odoo.lower() == "y":
                self.config.env.clone_odoo()
            else:
                _logger.error(translations.get_translation(translations.CHECK_ODOO_REPO).format(
                    odoo_src_dir= self.config.env.odoo_src_dir
                ))
                exit()
