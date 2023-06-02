import os
import subprocess
import json
import shutil
import logging
import pathlib
import platform
from pathlib import Path

from .handle_odoo_project_git_link import HandleOdooProjectGitLink
from .constants import *

class CreateEnvironment():

    def __init__(self, config):
        self.config = config
    
    def handle_git_link(self, gitlink):
        odoo_project = HandleOdooProjectGitLink(gitlink, self.config)
        return odoo_project

    def update_config(self):
        self.config["dependencies_dirs"] = []
        self.config["docker_dirs_with_addons"] = []
        self.config["debugger_path_mappings"] = []
        self.config["odoo_image_name"] = f"""odoo-{ARCH}"""
        self.config["venv_dir"] = os.path.join(self.config["project_dir"], "venv")
        self.config["docker_home"] = os.path.join(self.config["project_dir"], "docker_home")
        self.config["docker_project_dir"] = str(pathlib.PurePosixPath("/home", CURRENT_USER))
        self.config["docker_odoo_dir"] = str(pathlib.PurePosixPath(self.config["docker_project_dir"], "odoo"))
        self.config["docker_dirs_with_addons"].append(str(pathlib.PurePosixPath(self.config["docker_odoo_dir"], "addons")))
        self.config["docker_dirs_with_addons"].append(str(pathlib.PurePosixPath(self.config["docker_odoo_dir"], "odoo", "addons")))
        self.config["docker_path_odoo_conf"] = str(pathlib.PurePosixPath(self.config["docker_project_dir"], "odoo.conf"))
        self.config["docker_venv_dir"] = str(pathlib.PurePosixPath(self.config["docker_project_dir"], "venv"))
        self.config["docker_extra_addons"] = str(pathlib.PurePosixPath(self.config["docker_project_dir"], "extra-addons"))
        developing_project = self.handle_git_link(self.config.get("developing_project"))
        self.config["odoo_project_dir_path"] = developing_project.project_path
        #TODO create check for odoo project if its type is module
        self.config["docker_odoo_project_dir_path"] = str(pathlib.PurePosixPath(self.config["docker_extra_addons"], developing_project.project_data.name))
        self.config["docker_dirs_with_addons"].append(self.config["docker_odoo_project_dir_path"])
        self.config["docker_backups_dir"] = str(pathlib.PurePosixPath(self.config["docker_project_dir"], "backups"))
        self.config["dependencies_dir"] = os.path.join(self.config["project_dir"], "dependencies")

        

        self.mapped_folders = [
            (self.config["odoo_src_dir"], self.config["docker_odoo_dir"]),
            (self.config["venv_dir"], self.config["docker_venv_dir"]),
            (os.path.join(self.config["project_dir"], DEV_PROJECT_DIR), str(pathlib.PurePosixPath(self.config["docker_project_dir"], DEV_PROJECT_DIR))),
            (self.config.get("backups", {}).get("local_dir", ""), self.config["docker_backups_dir"]),
            (os.path.join(self.config["docker_home"], ".local"), str(pathlib.PurePosixPath(self.config["docker_project_dir"], ".local"))),
            (os.path.join(self.config["docker_home"], ".cache"), str(pathlib.PurePosixPath(self.config["docker_project_dir"], ".cache"))),
            (developing_project.project_path, self.config["docker_odoo_project_dir_path"]),
        ]
        for dependency_path in self.config["dependencies"]:
            dependency_project = self.handle_git_link(dependency_path)
            docker_dependency_project_path = dependency_project.docker_dependency_project_path
            self.config["dependencies_dirs"].append(dependency_project.project_path)
            docker_dir_with_addons = docker_dependency_project_path
            if dependency_project.project_type == TYPE_PROJECT_MODULE:
                docker_dir_with_addons = str(pathlib.PurePosixPath(docker_dir_with_addons, os.pardir))
            self.config["docker_dirs_with_addons"].append(docker_dir_with_addons)
            self.mapped_folders.append(
                (dependency_project.project_path, docker_dependency_project_path)
            )
        
        for pre_commit_file in self.config["pre_commit_map_files"]:
            real_file_place = os.path.join(self.config["odoo_project_dir_path"],pre_commit_file)
            if os.path.exists(real_file_place):
                full_path_pre_commit_file = os.path.join(self.config["project_dir"],pre_commit_file)
                if not os.path.exists(full_path_pre_commit_file):
                    shutil.copy(real_file_place, full_path_pre_commit_file)
                self.mapped_folders.append((
                    full_path_pre_commit_file, 
                    str(pathlib.PurePosixPath(self.config["docker_odoo_project_dir_path"],pre_commit_file))
                ))
            else:
                logging.warning(f"""Pre-commit file {pre_commit_file} was not found at {self.config["odoo_project_dir_path"]}""")
        
    
    def generate_dockerfile(self):
        dockerfile_template_path = os.path.join(self.config["project_dir"], DOCKER_TEMPLATE_FILE_RELATIVE_PATH)
        with open(dockerfile_template_path) as f:
            lines = f.readlines()
        content = "".join(lines).format(
            PROCESSOR_ARCH=ARCH,
            CURRENT_USER_UID=CURRENT_USER_UID,
            CURRENT_USER_GID=CURRENT_USER_GID,
            CURRENT_USER=CURRENT_USER,
            CURRENT_PASSWORD=CURRENT_PASSWORD,

        )
        dockerfile_path = os.path.join(self.config["project_dir"], DOCKERFILE)
        self.config["dockerfile_path"] = dockerfile_path
        with open(dockerfile_path, 'w') as writer:
            writer.write(content)
    
    def generate_docker_compose_file(self):
        docker_compose_template_path = os.path.join(self.config["project_dir"], DOCKER_COMPOSE_TEMPLATE_FILE_RELATIVE_PATH)
        with open(docker_compose_template_path) as f:
            lines = f.readlines()
        
        mapped_volumes = "\n"
        for mapped_volume in self.mapped_folders:
            mapped_volumes += " " * 6 + f"- {mapped_volume[0]}:{mapped_volume[1]}\n"
            if not os.path.exists(mapped_volume[0]):
                path = Path(mapped_volume[0])
                path.mkdir(parents=True)

        content = "".join(lines).format(
            ODOO_IMAGE=self.config["odoo_image_name"],
            MAPPED_VOLUMES=mapped_volumes,
            DEBUGGER_PORT=self.config.get("debugger_port", DEBUGGER_DEFAULT_PORT),
            ODOO_PORT=self.config.get("odoo_port", ODOO_DEFAULT_PORT),
            POSTGRES_PORT=self.config.get("postgres_port", POSTGRES_DEFAULT_PORT),
            START_STRING=self.config["start_string"],
            CURRENT_USER=CURRENT_USER,
            CURRENT_PASSWORD=CURRENT_PASSWORD,
            POSTGRES_ODOO_USER=POSTGRES_ODOO_USER,
            POSTGRES_ODOO_PASS=POSTGRES_ODOO_PASS,
            ODOO_DOCKER_PORT=ODOO_DOCKER_PORT,
            DEBUGGER_DOCKER_PORT=DEBUGGER_DOCKER_PORT,
            POSTGRES_DOCKER_PORT=POSTGRES_DOCKER_PORT,
            COMPOSE_FILE_VERSION=self.config["compose_file_version"]
        )
        dockerfile_path = os.path.join(self.config["project_dir"], "docker-compose.yml")
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
        list_for_checkout = [self.config.get("odoo_src_dir")]
        list_for_checkout.extend(self.config["dependencies_dirs"])
        for source_dir in list_for_checkout:
            os.chdir(source_dir)
            current_branch_bytes = subprocess.run(["git", "branch", "--show-current"], capture_output=True)
            current_branch_string = current_branch_bytes.decode("utf-8")
            try:
                current_branch_float = float(current_branch_bytes)
            except:
                current_branch_float = 0.0
            if current_branch_float and current_branch_string != self.config["odoo_version"]:
                subprocess.run(["git", "stash"], capture_output=True)
                subprocess.run(["git", "checkout", self.config["odoo_version"]], capture_output=True)
            if self.config.get("clean_git_repos", True):
                subprocess.run(["git", "stash"], capture_output=True)
                subprocess.run(["git", "checkout", self.config["odoo_version"]], capture_output=True)
            if self.config["update_git_repos"]:
                subprocess.run(["git", "pull"], capture_output=True)
    
    def get_list_of_mapped_sources(self):
        list_of_mapped_links = []
        list_for_links = [
            self.config.get("odoo_src_dir"),
            self.config.get("odoo_project_dir_path")
        ]
        
        for linking_dir in list_for_links:
            dir_name_to_link = os.path.basename(linking_dir)
            for mapped_folder in self.mapped_folders:
                mapped_dir_name = os.path.basename(mapped_folder[1])
                if dir_name_to_link == mapped_dir_name:
                    list_of_mapped_links.append(
                        (os.path.join(self.config["project_dir"], dir_name_to_link),mapped_folder[1])
                    )
        for linking_dir in self.config["dependencies_dirs"]:
            dir_name_to_link = os.path.basename(linking_dir)
            for mapped_folder in self.mapped_folders:
                mapped_dir_name = os.path.basename(mapped_folder[1])
                if dir_name_to_link == mapped_dir_name:
                    list_of_mapped_links.append(
                        (os.path.join(self.config["dependencies_dir"], dir_name_to_link), mapped_folder[1])
                    )
        return list_of_mapped_links

    
    def update_links(self):
        list_for_links = [
            self.config.get("backups", {}).get("local_dir", ""),
            self.config.get("odoo_src_dir"),
            self.config.get("odoo_project_dir_path")
        ]
        
        if not os.path.exists(self.config["dependencies_dir"]) and self.config["dependencies_dirs"]:
            os.mkdir(self.config["dependencies_dir"])
        self.delete_old_links(self.config["project_dir"], list_for_links)
        self.create_new_links(self.config["project_dir"], list_for_links)
        if self.config["dependencies_dirs"]:
            self.delete_old_links(self.config["dependencies_dir"], self.config["dependencies_dirs"])
            self.create_new_links(self.config["dependencies_dir"], self.config["dependencies_dirs"])
    
    def update_vscode_debugger_launcher(self):
        if not os.path.exists(os.path.join(self.config["project_dir"], ".vscode")):
            os.mkdir(os.path.join(self.config["project_dir"], ".vscode"))
        launch_json = os.path.join(self.config["project_dir"], ".vscode", "launch.json")
        if not os.path.exists(launch_json):
            content = {
                "configurations": []
            }

        else:
            with open(launch_json, "r") as open_file:
                content = json.load(open_file)
        # TODO compare old pathMapping records and current debugger_path_mappings
        # and delete not used folders and add new
        debugger_unit_exists = False
        for debugger_unit in content["configurations"]:
            if debugger_unit["name"] == DEBUGGER_UNIT_NAME:
                debugger_unit_exists = True
        if not debugger_unit_exists:
            list_of_mapped_sources = self.get_list_of_mapped_sources()
            for dir_with_sources in list_of_mapped_sources:
                self.config["debugger_path_mappings"].append({
                    "localRoot": dir_with_sources[0], 
                    "remoteRoot": dir_with_sources[1],
                })
            content["configurations"].append({
                "name": DEBUGGER_UNIT_NAME,
                "type": "python",
                "request": "attach",
                "port": self.config.get("debugger_port", DEBUGGER_DEFAULT_PORT),
                "host": "localhost",
                "pathMappings": self.config["debugger_path_mappings"],
            })
            with open(launch_json, "w") as outfile:
                json.dump(content, outfile, indent=4)