import configparser
import json
import base64
import pathlib

from .constants import *

class StartStringBuilder():

    def __init__(self, config, args_dict):
        self.config = config
        self.args_dict = args_dict
    
    def get_start_string(self):
        # Reading of config file
        odoo_config = configparser.ConfigParser()
        odoo_config.read(os.path.join(self.config["project_dir"], ODOO_TEMPLATE_CONFIG_FILE_RELATIVE_PATH))
        # Build string of all addons directories
        addons_string = ",".join(
            self.config["docker_dirs_with_addons"]
        )
        odoo_config["options"]["addons_path"] = addons_string
        my_config_parser_dict = {s:dict(odoo_config.items(s)) for s in odoo_config.sections()}

        data = json.dumps(my_config_parser_dict).encode("utf-8")
        config_base64_data = base64.b64encode(data)
        db_management_params = {
            "--db-lang": self.config["db_creation_data"]["db_lang"],
            "--db-country_code": self.config["db_creation_data"]["db_country_code"],
            "--default_password": self.config["db_creation_data"]["db_default_admin_password"],
            "--default_login": self.config["db_creation_data"]["db_default_admin_login"],
            "--create_demo": self.config["db_creation_data"]["create_demo"],
            "--config_base64_data": config_base64_data.decode(),
            "--odoo_dir": self.config["docker_odoo_dir"],
            "-c": self.config["docker_path_odoo_conf"],
        }
        db_management_start_string=f"""python3 {pathlib.PurePosixPath(self.config["docker_project_dir"], DB_MANAGEMENT_RELATIVE_PATH)}"""
        for param, param_value in db_management_params.items():
            db_management_start_string += f" {param} {param_value}"
        start_python_command = f"""python3 -u -m debugpy --listen 0.0.0.0:5678 {self.config["docker_odoo_dir"]}/odoo-bin -c {self.config["docker_project_dir"]}/odoo.conf --limit-time-real 99999"""
        test_command = " --test-enable --stop-after-init"

        db_name = self.args_dict.get("-d", False)
        restore_db_filepath = self.args_dict.get("--db-restore", False)
        drop_db_name = self.args_dict.get("--db-drop", False)
        translate_lang = self.args_dict.get("--translate", False)
        install_pip = self.args_dict.get("--pip_install", False)
        get_dbs_list = self.args_dict.get("--get_dbs_list", False)
        start_pre_commit = self.args_dict.get("--start_precommit", False)

        if install_pip:
            pip_install_command = f"""cd {self.config["docker_project_dir"]} && python3 -m venv {self.config["docker_venv_dir"]} && . {pathlib.PurePosixPath(self.config["docker_venv_dir"], "bin", "activate")} && wget -O odoo_requirements.txt https://raw.githubusercontent.com/odoo/odoo/{self.config["odoo_version"]}/requirements.txt && python3 -m pip install -r odoo_requirements.txt && python3 -m pip install {" ".join([req for req in self.config["requirements_txt"]])}"""
            start_string = f"""bash -c '{pip_install_command}'"""
            return start_string
        
        if start_pre_commit:
            start_string = f"""/bin/bash -c 'cd {self.config["docker_odoo_project_dir_path"]} && ls && pre-commit run --all-files'"""
            return start_string

        if db_name:
            db_management_start_string +=  f" -d {db_name}"
            start_python_command +=  f" -d {db_name}"

        if get_dbs_list:
            db_management_start_string +=  f" --get_dbs_list"

        if restore_db_filepath:
            db_management_start_string += f" --db-restore {restore_db_filepath}"

        if drop_db_name:
            db_management_start_string += f" --db-drop {drop_db_name}"

        if self.args_dict.get("-i", False):
            start_python_command += f""" -i {self.config["init_modules"]}"""

        if self.args_dict.get("-u", False):
            start_python_command += f""" -u {self.config["update_modules"]}"""

        if self.args_dict.get("-t", False) or self.args_dict.get("--test", False):
            start_python_command += f"{test_command}"

        if translate_lang:
            start_python_command += f" --language {translate_lang} --load-language {translate_lang} --i18n-overwrite"
            
        start_string = f"""bash -c ' cd {self.config["docker_project_dir"]} && source {pathlib.PurePosixPath(self.config["docker_venv_dir"], "bin", "activate")} && {db_management_start_string} && {start_python_command}'"""
        return start_string