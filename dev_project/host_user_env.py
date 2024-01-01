import os
import platform
from configparser import ConfigParser

from pathlib import Path

from . import constants
from . import translations

from .inside_docker_app.logger import get_module_logger

_logger = get_module_logger(__name__)

class CreateUserEnvironment():

    def __init__(self, pd_manager):
        self.pd_manager = pd_manager
        self.config_home_dir = self.pd_manager.home_config_dir
        self.env_file = self.get_env_file_path()
        self.parse_env_file()
    
    def get_env_file_path(self):
        local_env_file = os.path.join(self.pd_manager.project_path, constants.ENV_FILE_NAME)
        if os.path.exists(local_env_file):
            return local_env_file
        if not os.path.exists(self.config_home_dir):
            os.makedirs(self.config_home_dir)
        # TODO we need to write method that will create default .env file
        local_env_file = os.path.join(self.config_home_dir, constants.ENV_FILE_NAME)
        if not os.path.exists(local_env_file):
            self.create_env_file(local_env_file)
        return local_env_file

    def parse_env_file(self):
        parser = ConfigParser()
        with open(self.env_file) as stream:
            parser.read_string("[env]\n" + stream.read())
        self.backups = parser["env"]["BACKUP_DIR"]
        self.odoo_src_dir = parser["env"]["ODOO_SRC_DIR"]
        self.odoo_projects_dir = parser["env"]["ODOO_PROJECTS_DIR"]
        self.debugger_port = parser["env"].get("DEBUGGER_PORT", constants.DEBUGGER_DEFAULT_PORT)
        self.odoo_port = parser["env"].get("ODOO_PORT", constants.ODOO_DEFAULT_PORT)
        self.postgres_port = parser["env"].get("POSTGRES_PORT", constants.POSTGRES_DEFAULT_PORT)
        path_to_ssh_key = parser["env"].get("PATH_TO_SSH_KEY", False)
        if isinstance(path_to_ssh_key, str) and platform.system() == "Windows":
            path_to_ssh_key = path_to_ssh_key.replace("\\","\\\\")
        self.path_to_ssh_key = path_to_ssh_key
    
    def create_env_file(self, local_env_file):
        odoo_src_dir = self.get_from_user_odoo_src_dir()
        
        odoo_projects_src_dir = self.get_from_user_odoo_projects_src_dir()
        backup_dir = self.get_from_user_backup_dir()
        path_to_ssh_key = self.get_from_user_path_to_ssh_key()
        odoo_port = self.get_from_user_odoo_port()
        postgres_port = self.get_from_user_postgres_port()
        debugger_port = self.get_from_user_debugger_port()
        new_env_data = {
            "BACKUP_DIR": backup_dir,
            "ODOO_SRC_DIR": odoo_src_dir,
            "ODOO_PROJECTS_DIR": odoo_projects_src_dir,
            "PATH_TO_SSH_KEY": path_to_ssh_key,
            "ODOO_PORT": odoo_port,
            "POSTGRES_PORT": postgres_port,
            "DEBUGGER_PORT": debugger_port,
        }
        with open(local_env_file, 'w') as env_file:
            for key_name, value in new_env_data.items():
                string = f"{key_name}={value}\n"
                env_file.write(string)

        
    def get_from_user_odoo_src_dir(self):
        default_odoo_src_dir = os.path.join(Path.home(), "odoo")
        user_dir = input(translations.get_translation(translations.SET_ODOO_SRC_DIR).format(
                    DEFAULT_ODOO_SRC_DIR=default_odoo_src_dir,
                ))
        if not user_dir:
            user_dir = default_odoo_src_dir
        _logger.info(translations.get_translation(translations.YOU_SELECT_ODOO_DIR).format(
                SELECTED_ODOO_DIR=user_dir,
            ))
        return user_dir
    
    def get_from_user_odoo_projects_src_dir(self):
        default_odoo_projects_src_dir = os.path.join(Path.home(), "odoo_projects")
        user_dir = input(translations.get_translation(translations.SET_ODOO_PROJECTS_SRC_DIR).format(
                    DEFAULT_ODOO_PROJECTS_SRC_DIR=default_odoo_projects_src_dir,
                ))
        if not user_dir:
            user_dir = default_odoo_projects_src_dir
        _logger.info(translations.get_translation(translations.YOU_SELECT_ODOO_PROJECTS_DIR).format(
                SELECTED_ODOO_PROJECTS_DIR=user_dir,
            ))
        return user_dir

    def get_from_user_backup_dir(self):
        default_backup_dir = os.path.join(Path.home(), "odoo_backups")
        user_dir = input(translations.get_translation(translations.SET_ODOO_BACKUP_DIR).format(
                    DEFAULT_ODOO_BACKUP_DIR=default_backup_dir,
                ))
        if not user_dir:
            user_dir = default_backup_dir
        _logger.info(translations.get_translation(translations.YOU_SELECT_ODOO_BACKUPS_DIR).format(
                SELECTED_ODOO_BACKUPS_DIR=user_dir,
            ))
        return user_dir
    
    def get_from_user_path_to_ssh_key(self):
        ssh_path = input(translations.get_translation(translations.SET_SSH_KEY_PATH))
        ssh_path_name = ssh_path
        if not ssh_path:
            ssh_path_name = translations.get_translation(translations.NOTHING_SSH_PATH_NAME)
        _logger.info(translations.get_translation(translations.YOU_SELECT_SSH_KEY_PATH).format(
                SELECTED_SSH_KEY_PATH=ssh_path_name,
            ))
        return ssh_path
    
    def get_from_user_odoo_port(self):
        default_port = constants.ODOO_DEFAULT_PORT
        port = input(translations.get_translation(translations.SET_ODOO_PORT).format(
                    DEFAULT_ODOO_PORT=default_port,
                ))
        if not port:
            port = default_port
        _logger.info(translations.get_translation(translations.YOU_SELECT_ODOO_PORT).format(
                SELECTED_ODOO_PORT=default_port,
            ))
        return port
    
    def get_from_user_postgres_port(self):
        default_port = constants.POSTGRES_DEFAULT_PORT
        port = input(translations.get_translation(translations.SET_POSTGRES_PORT).format(
                    DEFAULT_POSTGRES_PORT=default_port,
                ))
        if not port:
            port = default_port
        _logger.info(translations.get_translation(translations.YOU_SELECT_POSTGRES_PORT).format(
                SELECTED_POSTGRES_PORT=default_port,
            ))
        return port

    def get_from_user_debugger_port(self):
        default_port = constants.DEBUGGER_DEFAULT_PORT
        port = input(translations.get_translation(translations.SET_DEBUGGER_PORT).format(
                    DEFAULT_DEBUGGER_PORT=default_port,
                ))
        if not port:
            port = default_port
        _logger.info(translations.get_translation(translations.YOU_SELECT_DEBUGGER_PORT).format(
                SELECTED_DEBUGGER_PORT=default_port,
            ))
        return port
