import os
import json
from configparser import ConfigParser

from .constants import *
from .translations import *

from .inside_docker_app.logger import get_module_logger

_logger = get_module_logger(__name__)


class ConfParser():

    def __init__(self, pd_manager, args_dict, program_dir):
        self.pd_manager = pd_manager
        self.config_path = os.path.join(pd_manager.project_path, CONFIG_FILE_NAME)
        self.program_dir = program_dir
        self.config = None
        self.parse_json_config()
        self.env_file = self.get_env_file_path()
        self.parse_env_file()
        self.config["args_dict"] = args_dict

    def parse_json_config(self):
        try:
            with open(self.config_path) as config_file:
                self.config = json.load(config_file)
                self.config["project_dir"] = self.pd_manager.project_path
                self.config["program_dir"] = self.program_dir
        except BaseException:
            _logger.error(get_translation(CHECK_CONFIG_FILE).format(
                CONFIG_FILE_NAME=CONFIG_FILE_NAME,
            ))
            exit()

    
    def get_env_file_path(self):
        local_env_file = os.path.join(self.pd_manager.project_path, ENV_FILE_NAME)
        if os.path.exists(local_env_file):
            return local_env_file
        self.config["config_home_dir"] = self.pd_manager.home_config_dir
        if not os.path.exists(self.config["config_home_dir"]):
            os.makedirs(self.config["config_home_dir"])
        # TODO we need to write method that will create default .env file
        local_env_file = os.path.join(self.config["config_home_dir"], ENV_FILE_NAME)
        return local_env_file

        
    
    def parse_env_file(self):
        parser = ConfigParser()
        with open(self.env_file) as stream:
            parser.read_string("[env]\n" + stream.read())
        self.config["backups"] = {
            "local_dir": parser["env"]["BACKUP_DIR"],
        }
        self.config["odoo_src_dir"] = parser["env"]["ODOO_SRC_DIR"]
        self.config["odoo_projects_dir"] = parser["env"]["ODOO_PROJECTS_DIR"]
        self.config["debugger_port"] = parser["env"].get("DEBUGGER_PORT", DEBUGGER_DEFAULT_PORT)
        self.config["odoo_port"] = parser["env"].get("ODOO_PORT", ODOO_DEFAULT_PORT)
        self.config["postgres_port"] = parser["env"].get("POSTGRES_PORT", POSTGRES_DEFAULT_PORT)
        path_to_ssh_key = parser["env"].get("PATH_TO_SSH_KEY", False)
        if path_to_ssh_key and platform.system() == "Windows":
            path_to_ssh_key = path_to_ssh_key.replace("\\","\\\\")
        self.config["path_to_ssh_key"] = path_to_ssh_key

