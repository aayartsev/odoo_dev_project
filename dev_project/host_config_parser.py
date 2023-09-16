import os
import json
import logging
from configparser import ConfigParser
from pathlib import Path

from .constants import *



class ConfParser():

    def __init__(self, project_dir, args_dict):
        self.project_dir = project_dir
        self.config_path = os.path.join(self.project_dir, CONFIG_FILE_NAME)
        self.config = None
        self.parse_json_config()
        self.env_file = self.get_env_file_path()
        self.parse_env_file()
        self.config["args_dict"] = args_dict

    def parse_json_config(self):
        try:
            with open(self.config_path) as config_file:
                self.config = json.load(config_file)
                self.config["project_dir"] = self.project_dir
        except BaseException:
            logging.error("Check your 'config.json' file, we can not parse it.")
            exit()

    
    def get_env_file_path(self):
        local_env_file = os.path.join(self.project_dir, ENV_FILE_NAME)
        if os.path.exists(local_env_file):
            return local_env_file
        self.config["config_home_dir"] = os.path.join(Path.home(), CONFIG_DIR_IN_HOME_DIR)
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

