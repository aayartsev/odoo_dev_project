import configparser
import json
import base64
import pathlib
import subprocess

from .constants import *

class StartStringBuilder():

    def __init__(self, config):
        self.config = config
        self.args_dict = self.config["args_dict"]
        self.config["start_string"] = self.get_start_string()
    
    def get_base64_string_config(self):
        data = json.dumps(self.config).encode("utf-8")
        config_base64_data = base64.b64encode(data)
        return config_base64_data.decode()
    
    def get_start_string(self):
        # Reading of config file
        odoo_config = configparser.ConfigParser()
        odoo_config.read(os.path.join(self.config["project_dir"], PROJECT_ODOO_TEMPLATE_CONFIG_FILE_RELATIVE_PATH))
        # Build string of all addons directories
        addons_string = ",".join(
            self.config["docker_dirs_with_addons"]
        )
        odoo_config["options"]["addons_path"] = addons_string
        odoo_config["options"]["db_password"] = POSTGRES_ODOO_PASS
        odoo_config["options"]["db_user"] = POSTGRES_ODOO_USER
        odoo_config["options"]["http_port"] = ODOO_DOCKER_PORT
        odoo_config["options"]["db_port"] = POSTGRES_DOCKER_PORT

        data_dir = str(pathlib.PurePosixPath(self.config["docker_project_dir"], ".local/share/Odoo"))
        odoo_config["options"]["data_dir"] = data_dir
        self.config["odoo_config_data"] = {s:dict(odoo_config.items(s)) for s in odoo_config.sections()}
        start_python_command = f"""python3 -u -m debugpy --listen 0.0.0.0:{DEBUGGER_DOCKER_PORT} {self.config["docker_odoo_dir"]}/odoo-bin -c {self.config["docker_project_dir"]}/odoo.conf --limit-time-real 99999"""
        db_name = self.args_dict.get(D_PARAM, False)
        translate_lang = self.args_dict.get(TRANSLATE_PARAM, False)
        install_pip = self.args_dict.get(INSTALL_PIP_PARAM, False)
        start_pre_commit = self.args_dict.get(START_PRECOMMIT_PARAM, False)
        build_image = self.args_dict.get(BUILD_IMAGE_PARAM, False)
        
        if build_image:
            subprocess.run(["docker", "build", "-f", self.config["dockerfile_path"], "-t", self.config["odoo_image_name"], "."])
            exit()

        if install_pip:
            pip_install_command = f"""cd {self.config["docker_project_dir"]} && python3 -m venv {self.config["docker_venv_dir"]} && . {pathlib.PurePosixPath(self.config["docker_venv_dir"], "bin", "activate")} && wget -O odoo_requirements.txt https://raw.githubusercontent.com/odoo/odoo/{self.config["odoo_version"]}/requirements.txt && python3 -m pip install -r odoo_requirements.txt && python3 -m pip install {" ".join([req for req in self.config["requirements_txt"]])}"""
            start_string = f"""bash -c '{pip_install_command}'"""
            return start_string
        
        if start_pre_commit:
            start_string = f"""/bin/bash -c 'cd {self.config["docker_odoo_project_dir_path"]} && ls && git config --global --add safe.directory {self.config["docker_odoo_project_dir_path"]} && pre-commit run --all-files'"""
            return start_string

        if db_name:
            start_python_command +=  f" {D_PARAM} {db_name}"

        if self.args_dict.get(U_PARAM, False):
            start_python_command += f""" {I_PARAM} {self.config["init_modules"]}"""

        if self.args_dict.get(U_PARAM, False):
            start_python_command += f""" {I_PARAM} {self.config["update_modules"]}"""

        if self.args_dict.get(T_PARAM, False) or self.args_dict.get(TEST_PARAM, False):
            start_python_command += f"{TEST_COMMAND}"

        if translate_lang:
            start_python_command += f" --language {translate_lang} --load-language {translate_lang} --i18n-overwrite"

        start_main = " && ".join([
            f"""cd {self.config["docker_project_dir"]}""",
            f""". {pathlib.PurePosixPath(self.config["docker_venv_dir"],"bin", "activate")}""",
            f"""python3 {pathlib.PurePosixPath(self.config["docker_inside_app"],"main.py")} {CONFIG_BASE64_DATA} {self.get_base64_string_config()}""",
            f"""{start_python_command}""",
        ])
        start_string = f"""bash -c '{start_main}'"""
        return start_string