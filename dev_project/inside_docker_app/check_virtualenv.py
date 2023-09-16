import sys
import os
import logging
import venv

from pip._internal.operations.freeze import freeze
from pip._internal.req import parse_requirements

class VirtualenvChecker():

    def __init__(self, config):
        self.docker_venv_dir = config["docker_venv_dir"]
        self.docker_project_dir = config["docker_project_dir"]
        self.requirements_txt = config["requirements_txt"]
        self.odoo_version = config["requirements_txt"]
        self.odoo_version = config["odoo_version"]
        self.odoo_data_dir = config["odoo_config_data"]["options"]["data_dir"]
        self.check_virtual_env()

    def is_virtualenv(self):
        return sys.prefix != sys.base_prefix

    def find_file(self, start_dir, pattern):
        for root, dirs, files in os.walk(start_dir):
            for name in files:
                if name.find(pattern) >= 0:
                    return root + os.sep + name

        return None

    def set_venv(self):
        # This is the heart of this script that puts you inside the virtual environment. 
        # There is no need to undo this. When this script ends, your original path will 
        # be restored.
        os.environ['PATH'] = os.path.dirname(self.find_file(self.docker_venv_dir, 'activate')) + os.pathsep + os.environ['PATH']
        sys.path.insert(1, os.path.dirname(self.find_file(self.docker_venv_dir, 'easy_install.py')))

    def check_packages_for_install(self) -> None:
        # TODO autoinstall packages from requirements_txt if they non in already installed list of pip packages
        dict_of_packages = {}
        for line in freeze():
            dict_of_packages.update({
                line.split("==")[0]: line.split("==")[1]
            })
        for package in self.requirements_txt:
            if package not in freeze():
                os.system(f"""python3 -m pip install {package}""")
    
    def update_requirements_list(self):
        odoo_requirements_path = os.path.join(self.odoo_data_dir, "requirements.txt")
        if not os.path.exists(odoo_requirements_path):
            os.system(f"""cd {self.docker_project_dir} && wget -O {odoo_requirements_path} https://raw.githubusercontent.com/odoo/odoo/{self.odoo_version}/requirements.txt""")
        result = parse_requirements(odoo_requirements_path, session=False)
        # TODO find the way to check if i need to install package in my environment
    
    def check_virtual_env(self):
        self.update_requirements_list()
        if self.is_virtualenv():
            logging.info("Already in virtual environment.")
        else:
            if self.find_file(self.docker_venv_dir, 'activate') is None:
                logging.info("No virtual environment found. Creating one.")
                env = venv.EnvBuilder(with_pip = True)
                env.create(self.docker_venv_dir)
                self.set_venv()
            else:
                logging.info("Not in virtual environment. Virtual environment directory found.")
                self.set_venv()
        self.check_packages_for_install()