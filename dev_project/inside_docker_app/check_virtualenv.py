import sys
import os
import venv

from pip._internal.operations.freeze import freeze
from pip._internal.req import parse_requirements
from pip._internal.req.constructors import install_req_from_req_string
from pip._internal.network.session import PipSession

from logger import get_module_logger

_logger = get_module_logger(__name__)

class VirtualenvChecker():

    def __init__(self, config):
        self.docker_venv_dir = config.get("docker_venv_dir", False)
        self.docker_project_dir = config["docker_project_dir"]
        self.requirements_txt = config.get("requirements_txt", [])
        self.odoo_version = config.get("odoo_version", 0.0)
        self.odoo_data_dir = config["odoo_config_data"]["options"]["data_dir"]
        self.odoo_requirements_path = os.path.join(config["docker_odoo_dir"], "requirements.txt")
        self.python_version = config["python_version"]
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
        # finding venv/bin dir
        venv_bin_dir = os.path.dirname(self.find_file(self.docker_venv_dir, "activate"))
        # defining path to the venv`s dirs
        venv_lib_path = os.path.join(self.docker_venv_dir,"lib",f"python{self.python_version}","site-packages")
        # update PATH environment variable
        os.environ['PATH'] = venv_bin_dir + os.pathsep + os.environ["PATH"]
        # inserting path to the venv`s dirs in system path
        sys.path.insert(1, venv_lib_path)

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
        os.system(f"""python3 -m pip install -r {self.odoo_requirements_path}""")
        # TODO find the way to check if i need to install package in my environment
    
    def check_virtual_env(self):
        if self.is_virtualenv():
            _logger.info("Already in virtual environment.")
        else:
            if self.find_file(self.docker_venv_dir, 'activate') is None:
                _logger.info("No virtual environment found. Creating one.")
                env = venv.EnvBuilder(with_pip = True)
                env.create(self.docker_venv_dir)
                self.set_venv()
                self.update_requirements_list()
            else:
                _logger.info("Not in virtual environment. Virtual environment directory found.")
                self.set_venv()
        
        self.check_packages_for_install()