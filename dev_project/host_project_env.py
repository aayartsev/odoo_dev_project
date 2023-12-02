import os
import subprocess
import json
import shutil
import platform
from configparser import ConfigParser

import pathlib
from pathlib import Path

from .handle_odoo_project_git_link import HandleOdooProjectGitLink
from . import constants
from . import translations

from .inside_docker_app.logger import get_module_logger

_logger = get_module_logger(__name__)

class CreateProjectEnvironment():

    def __init__(self, config):
        self.config = config
        self.user_env = self.config.user_env
        self.config.project_env = self

    def handle_git_link(self, gitlink):
        odoo_project = HandleOdooProjectGitLink(gitlink, self.config)
        odoo_project.build_project()
        return odoo_project

    def map_folders(self):
        self.mapped_folders = [
            (self.user_env.odoo_src_dir, self.config.docker_odoo_dir),
            (self.config.venv_dir, self.config.docker_venv_dir),
            (self.config.odoo_tests_dir, self.config.docker_temp_tests_dir),
            (os.path.join(self.config.program_dir, constants.DEV_PROJECT_DIR), self.config.docker_dev_project_dir),
            (self.user_env.backups, self.config.docker_backups_dir),
            (os.path.join(self.config.docker_home, ".local"), str(pathlib.PurePosixPath(self.config.docker_project_dir, ".local"))),
            (os.path.join(self.config.docker_home, ".cache"), str(pathlib.PurePosixPath(self.config.docker_project_dir, ".cache"))),
            (self.config.developing_project.project_path, self.config.docker_odoo_project_dir_path),
        ]
        for dependency_path in self.config.dependencies:
            dependency_project = self.handle_git_link(dependency_path)
            docker_dependency_project_path = str(pathlib.PurePosixPath(self.config.docker_extra_addons, dependency_project.inside_docker_path))
            self.config.dependencies_dirs.append(dependency_project.project_path)
            docker_dir_with_addons = docker_dependency_project_path
            if dependency_project.project_type == constants.TYPE_PROJECT_MODULE:
                docker_dir_with_addons = str(pathlib.PurePosixPath(docker_dir_with_addons, os.pardir))
            self.config.docker_dirs_with_addons.append(docker_dir_with_addons)
            self.mapped_folders.append(
                (dependency_project.project_path, docker_dependency_project_path)
            )
        
        for pre_commit_file in self.config.pre_commit_map_files:
            real_file_place = os.path.join(self.config.odoo_project_dir_path,pre_commit_file)
            if os.path.exists(real_file_place):
                full_path_pre_commit_file = os.path.join(self.config.project_dir,pre_commit_file)
                if not os.path.exists(full_path_pre_commit_file):
                    shutil.copy(real_file_place, full_path_pre_commit_file)
                self.mapped_folders.append((
                    full_path_pre_commit_file, 
                    str(pathlib.PurePosixPath(self.config.docker_odoo_project_dir_path,pre_commit_file))
                ))
            else:
                
                _logger.warning(translations.get_translation(translations.PRE_COMMIT_FILE_WAS_NOT_FOUND).format(
                    PRE_COMMIT_FILE=pre_commit_file,
                    ODOO_PROJECT_DIR_PATH=self.config.odoo_project_dir_path,
                ))
        
    
    def generate_dockerfile(self):
        dockerfile_template_path = os.path.join(self.config.project_dir, constants.PROJECT_DOCKER_TEMPLATE_FILE_RELATIVE_PATH)
        with open(dockerfile_template_path) as f:
            lines = f.readlines()
        content = "".join(lines).format(
            PROCESSOR_ARCH=constants.ARCH,
            CURRENT_USER_UID=constants.CURRENT_USER_UID,
            CURRENT_USER_GID=constants.CURRENT_USER_GID,
            CURRENT_USER=constants.CURRENT_USER,
            CURRENT_PASSWORD=constants.CURRENT_PASSWORD,
            PYTHON_VERSION=self.config.python_version,
            DEBIAN_NAME=self.config.debian_name,

        )
        content = content.replace(translations.get_translation(translations.MESSAGE_ODOO_CONF), translations.get_translation(translations.DO_NOT_CHANGE_FILE))
        dockerfile_path = os.path.join(self.config.project_dir, constants.DOCKERFILE)
        self.config.dockerfile_path = dockerfile_path
        with open(dockerfile_path, 'w') as writer:
            writer.write(content)
    
    def generate_config_file(self):
        config_file_template_path = os.path.join(self.config.project_dir, constants.PROJECT_ODOO_TEMPLATE_CONFIG_FILE_RELATIVE_PATH)
        with open(config_file_template_path) as f:
            lines = f.readlines()
        content = "".join(lines)
        for replace_phrase in {constants.DO_NOT_CHANGE_PARAM: translations.get_translation(translations.DO_NOT_CHANGE_PARAM),
            constants.ADMIN_PASSWD_MESSAGE: translations.get_translation(translations.ADMIN_PASSWD_MESSAGE),
            constants.MESSAGE_MARKER: translations.get_translation(translations.MESSAGE_ODOO_CONF)}.items():
            content = content.replace(replace_phrase[0], replace_phrase[1])
        odoo_config_file_path = os.path.join(self.config.project_dir, constants.ODOO_CONF_NAME)
        if not os.path.exists(odoo_config_file_path):
            with open(odoo_config_file_path, 'w') as writer:
                writer.write(content)
    
    def generate_docker_compose_file(self):
        docker_compose_template_path = os.path.join(self.config.project_dir, constants.PROJECT_DOCKER_COMPOSE_TEMPLATE_FILE_RELATIVE_PATH)
        with open(docker_compose_template_path) as f:
            lines = f.readlines()
        
        mapped_volumes = "\n"
        for mapped_volume in self.mapped_folders:
            mapped_volumes += " " * 6 + f"- {mapped_volume[0]}:{mapped_volume[1]}\n"
            if not os.path.exists(mapped_volume[0]):
                path = Path(mapped_volume[0])
                path.mkdir(parents=True)

        content = "".join(lines).format(
            ODOO_IMAGE=self.config.odoo_image_name,
            MAPPED_VOLUMES=mapped_volumes,
            DEBUGGER_PORT=self.user_env.debugger_port or constants.DEBUGGER_DEFAULT_PORT,
            ODOO_PORT=self.user_env.odoo_port or constants.ODOO_DEFAULT_PORT,
            POSTGRES_PORT=self.user_env.postgres_port or constants.POSTGRES_DEFAULT_PORT,
            START_STRING=self.config.start_string,
            CURRENT_USER=constants.CURRENT_USER,
            CURRENT_PASSWORD=constants.CURRENT_PASSWORD,
            POSTGRES_ODOO_USER=constants.POSTGRES_ODOO_USER,
            POSTGRES_ODOO_PASS=constants.POSTGRES_ODOO_PASS,
            ODOO_DOCKER_PORT=constants.ODOO_DOCKER_PORT,
            DEBUGGER_DOCKER_PORT=constants.DEBUGGER_DOCKER_PORT,
            POSTGRES_DOCKER_PORT=constants.POSTGRES_DOCKER_PORT,
            COMPOSE_FILE_VERSION=self.config.compose_file_version
        )
        content = content.replace(translations.get_translation(translations.MESSAGE_ODOO_CONF), translations.get_translation(translations.DO_NOT_CHANGE_FILE))
        dockerfile_path = os.path.join(self.config.project_dir, "docker-compose.yml")
        with open(dockerfile_path, 'w') as writer:
            writer.write(content)
    
    def delete_old_links(self, dir_to_clean, current_links):
        os.chdir(dir_to_clean)
        for item in os.listdir():
            if os.path.islink(item) and not item in current_links:
                os.unlink(item)
    
    def create_new_links(self, dir_to_create, current_links):
        for dep_for_link in current_links:
            dep_dir_name = os.path.basename(dep_for_link)
            try:
                os.symlink(dep_for_link, os.path.join(dir_to_create, dep_dir_name))
            except FileExistsError:
                pass
    
    def checkout_dependencies(self):
        list_for_checkout = [self.user_env.odoo_src_dir]
        list_for_checkout.extend(self.config.dependencies_dirs)
        for source_dir in list_for_checkout:
            os.chdir(source_dir)
            current_branch_bytes = subprocess.run(["git", "branch", "--show-current"], capture_output=True)
            current_branch_string = current_branch_bytes.stdout.decode("utf-8").strip()
            try:
                current_branch_float = float(current_branch_string)
            except:
                current_branch_float = 0.0
            if current_branch_float and current_branch_string != self.config.odoo_version:
                subprocess.run(["git", "stash"], capture_output=True)
                subprocess.run(["git", "checkout", self.config.odoo_version], capture_output=True)
            if self.config.clean_git_repos:
                subprocess.run(["git", "stash"], capture_output=True)
                subprocess.run(["git", "checkout", self.config.odoo_version], capture_output=True)
            if self.config.update_git_repos:
                subprocess.run(["git", "pull"], capture_output=True)
    
    def get_list_of_mapped_sources(self):
        list_of_mapped_links = []
        list_for_links = [
            self.user_env.odoo_src_dir,
            self.config.odoo_project_dir_path,
        ]
        
        for linking_dir in list_for_links:
            dir_name_to_link = os.path.basename(linking_dir)
            for mapped_folder in self.mapped_folders:
                mapped_dir_name = os.path.basename(mapped_folder[1])
                if dir_name_to_link == mapped_dir_name:
                    list_of_mapped_links.append(
                        (os.path.join(self.config.project_dir, dir_name_to_link),mapped_folder[1])
                    )
        for linking_dir in self.config.dependencies_dirs:
            dir_name_to_link = os.path.basename(linking_dir)
            for mapped_folder in self.mapped_folders:
                mapped_dir_name = os.path.basename(mapped_folder[1])
                if dir_name_to_link == mapped_dir_name:
                    list_of_mapped_links.append(
                        (os.path.join(self.config.dependencies_dir, dir_name_to_link), mapped_folder[1])
                    )
        return list_of_mapped_links

    
    def update_links(self):
        list_for_links = [
            self.user_env.backups,
            self.user_env.odoo_src_dir,
            self.config.odoo_project_dir_path
        ]
        
        if not os.path.exists(self.config.dependencies_dir) and self.config.dependencies_dirs:
            os.mkdir(self.config.dependencies_dir)
        self.delete_old_links(self.config.project_dir, list_for_links)
        self.create_new_links(self.config.project_dir, list_for_links)
        if self.config.dependencies_dirs:
            self.delete_old_links(self.config.dependencies_dir, self.config.dependencies_dirs)
            self.create_new_links(self.config.dependencies_dir, self.config.dependencies_dirs)
    
    def update_vscode_debugger_launcher(self):
        if not os.path.exists(os.path.join(self.config.project_dir, ".vscode")):
            os.mkdir(os.path.join(self.config.project_dir, ".vscode"))
        launch_json = os.path.join(self.config.project_dir, ".vscode", "launch.json")
        if not os.path.exists(launch_json):
            content = {
                "configurations": []
            }
        else:
            with open(launch_json, "r") as open_file:
                content = json.load(open_file)
        debugger_unit_exists = False
        list_of_mapped_sources = self.get_list_of_mapped_sources()
        for dir_with_sources in list_of_mapped_sources:
            self.config.debugger_path_mappings.append({
                "localRoot": dir_with_sources[0], 
                "remoteRoot": dir_with_sources[1],
            })
        port = self.user_env.debugger_port or constants.DEBUGGER_DEFAULT_PORT
        odoo_debugger_uint = {
            "name": constants.DEBUGGER_UNIT_NAME,
            "type": "python",
            "request": "attach",
            "port": int(port),
            "host": "localhost",
            "pathMappings": self.config.debugger_path_mappings,
        }
        for index, debugger_unit in enumerate(content["configurations"]):
            if debugger_unit["name"] == constants.DEBUGGER_UNIT_NAME:
                content["configurations"][index] = odoo_debugger_uint
                debugger_unit_exists = True
        if not debugger_unit_exists:
            list_of_mapped_sources = self.get_list_of_mapped_sources()
            content["configurations"].append({
                "name": constants.DEBUGGER_UNIT_NAME,
                "type": "python",
                "request": "attach",
                "port": self.user_env.debugger_port or constants.DEBUGGER_DEFAULT_PORT,
                "host": "localhost",
                "pathMappings": self.config.debugger_path_mappings,
            })
        with open(launch_json, "w") as outfile:
            json.dump(content, outfile, indent=4)
    
    def clone_odoo(self):
        odoo_crc_project = HandleOdooProjectGitLink(constants.ODOO_GIT_LINK, self.config)
        odoo_crc_project.project_path = self.config.user_env.odoo_src_dir
        odoo_crc_project.get_dir_to_clone()
        odoo_crc_project.force_clone_repo()
    
    def build_image(self):
        os.chdir(self.config.project_dir)
        # i need to create .dockerignore file (because it tries to send docker context)
        subprocess.run(["docker", "build", "-f", self.config.dockerfile_path, "-t", self.config.odoo_image_name, "."])