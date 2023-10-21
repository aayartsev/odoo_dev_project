import os
import pathlib
import json

from . import constants
from .translations import *
from .handle_odoo_project_git_link import HandleOdooProjectGitLink

from .inside_docker_app.logger import get_module_logger

_logger = get_module_logger(__name__)

class Config():

    def __init__(self, pd_manager, arguments, program_dir, env):
        
        self.pd_manager = pd_manager
        self.program_dir = program_dir
        self.arguments = arguments
        self.config_file = None
        self.project_dir = self.pd_manager.project_path
        self.config_path = os.path.join(self.pd_manager.project_path, constants.CONFIG_FILE_NAME)
        self.config_home_dir = self.pd_manager.home_config_dir
        self.env = env

        self.parse_json_config()
        self.init_modules = self.config_file_dict.get("init_modules", False)
        self.update_modules = self.config_file_dict.get("update_modules", False)
        for module_list in [self.init_modules, self.update_modules]:
            if isinstance(module_list, list):
                module_list = ",".join(module_list)
            if isinstance(module_list, str):
                module_list = module_list.split(",")
                module_list = [module.strip() for module in module_list]
                module_list = ",".join(module_list)
        
        self.db_creation_data = self.config_file_dict.get("db_creation_data", {})
        self.odoo_version = self.config_file_dict.get("odoo_version", 0.0)
        self.update_git_repos = self.config_file_dict.get("update_git_repos", False)
        self.clean_git_repos = self.config_file_dict.get("clean_git_repos", False)
        self.check_system = self.config_file_dict.get("check_system", False)
        self.db_manager_password = self.config_file_dict.get("db_manager_password", "admin")
        self.dev_mode = self.config_file_dict.get("dev_mode", False)
        self.developing_project = self.config_file_dict.get("developing_project", False)
        self.pre_commit_map_files = self.config_file_dict.get("pre_commit_map_files", [])
        self.dependencies = self.config_file_dict.get("dependencies", [])
        self.requirements_txt = self.config_file_dict.get("requirements_txt", [])

        self.dependencies_dirs = []
        self.docker_dirs_with_addons = []
        self.debugger_path_mappings = []
        self.odoo_image_name = f"""odoo-{constants.ARCH}"""
        self.docker_project_dir = str(pathlib.PurePosixPath("/home", constants.CURRENT_USER))
        self.docker_dev_project_dir = str(pathlib.PurePosixPath(self.docker_project_dir, constants.DEV_PROJECT_DIR))
        self.docker_inside_app = str(pathlib.PurePosixPath(self.docker_dev_project_dir, "inside_docker_app"))
        self.docker_odoo_dir = str(pathlib.PurePosixPath(self.docker_project_dir, "odoo"))
        self.docker_dirs_with_addons.append(str(pathlib.PurePosixPath(self.docker_odoo_dir, "addons")))
        self.docker_dirs_with_addons.append(str(pathlib.PurePosixPath(self.docker_odoo_dir, "odoo", "addons")))
        self.docker_path_odoo_conf = str(pathlib.PurePosixPath(self.docker_project_dir, "odoo.conf"))
        self.docker_venv_dir = str(pathlib.PurePosixPath(self.docker_project_dir, "venv"))
        self.docker_extra_addons = str(pathlib.PurePosixPath(self.docker_project_dir, "extra-addons"))
        self.docker_backups_dir = str(pathlib.PurePosixPath(self.docker_project_dir, "backups"))
        self.venv_dir = os.path.join(self.project_dir, "venv")
        self.docker_home = os.path.join(self.project_dir, "docker_home")
        self.dependencies_dir = os.path.join(self.project_dir, "dependencies")
        self.compose_file_version = constants.DOCKER_COMPOSE_DEFAULT_FILE_VERSION
        self.odoo_config_data = {}

        self.developing_project = self.handle_git_link(self.developing_project)
        self.odoo_project_dir_path = self.developing_project.project_path
        self.docker_odoo_project_dir_path = str(pathlib.PurePosixPath(self.docker_extra_addons, self.developing_project.project_data.name))
        self.docker_dirs_with_addons.append(self.docker_odoo_project_dir_path)
    
    def parse_json_config(self):
        try:
            with open(self.config_path) as config_file:
                self.config_file_dict = json.load(config_file)
        except BaseException:
            _logger.error(get_translation(CHECK_CONFIG_FILE).format(
                CONFIG_FILE_NAME=constants.CONFIG_FILE_NAME,
            ))
            exit()
    
    def handle_git_link(self, gitlink):
        odoo_project = HandleOdooProjectGitLink(gitlink, self)
        return odoo_project

    def config_to_json(self):
        config = {}
        config["docker_odoo_dir"] = self.docker_odoo_dir
        config["odoo_config_data"] = self.odoo_config_data
        config["docker_path_odoo_conf"] = self.docker_path_odoo_conf
        config["arguments"] = self.arguments
        config["db_creation_data"] = self.db_creation_data
        config["db_manager_password"] = self.db_manager_password
        config["docker_venv_dir"] = self.docker_venv_dir
        config["docker_project_dir"] = self.docker_project_dir
        config["requirements_txt"] = self.requirements_txt
        config["odoo_version"] = self.odoo_version
        return json.dumps(config).encode("utf-8")
            


