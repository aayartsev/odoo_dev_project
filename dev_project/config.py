import os
import pathlib

from . import constants

class Config():

    def __init__(self):
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
        developing_project = self.handle_git_link(self.developing_project)
        self.odoo_project_dir_path = developing_project.project_path
        self.docker_odoo_project_dir_path = str(pathlib.PurePosixPath(self.docker_extra_addons, developing_project.project_data.name))
        self.docker_dirs_with_addons.append(self.docker_odoo_project_dir_path)

