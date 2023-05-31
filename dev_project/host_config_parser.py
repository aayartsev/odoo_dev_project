import os
import json
from configparser import ConfigParser
from .constants import *


class ConfParser():

    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.config_path = os.path.join(self.project_dir, CONFIG_FILE_NAME)
        self.env_file = os.path.join(self.project_dir, ENV_FILE_NAME)
        self.config = None
        self.parse_json_config()
        self.parse_env_file()

    def parse_json_config(self):
        with open(self.config_path) as config_file:
            self.config = json.load(config_file)
            self.config["project_dir"] = self.project_dir
    
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

