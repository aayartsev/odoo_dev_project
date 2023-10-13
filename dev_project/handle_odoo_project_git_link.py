import re
import os
import subprocess
import shutil
import pathlib
from dataclasses import dataclass
from .constants import *


@dataclass
class OdooProjectData(object):
    server:str
    author:str
    name:str

class HandleOdooProjectGitLink():

    def __init__(self, gitlink, config):
        self.gitlink = gitlink
        self.config = config
        self.project_type = None
        self.ssh_regex = r"git@[a-z.]*:"
        self.link_type = self.get_git_link_type()
        self.project_data = self.parse_link_by_type()
        self.project_path = self.get_project_path()
        if self.link_type in [GITLINK_TYPE_HTTP, GITLINK_TYPE_SSH]:
            self.dir_to_clone = self.get_dir_to_clone()
            self.check_project()
        self.get_project_type()
        inside_docker_path = self.project_data.name
        if self.project_type == TYPE_PROJECT_MODULE:
            inside_docker_path = str(pathlib.PurePosixPath(inside_docker_path, self.project_data.name))
        self.docker_dependency_project_path = str(
            pathlib.PurePosixPath(self.config.docker_extra_addons, inside_docker_path))
        
    def get_git_link_type(self):
        if "file://" in self.gitlink:
            return GITLINK_TYPE_FILE
        if "http" in self.gitlink:
            return GITLINK_TYPE_HTTP
        ssh_pattern = re.findall(self.ssh_regex, self.gitlink)
        if ssh_pattern:
            return GITLINK_TYPE_SSH
    
    def parse_link_by_type(self):
        return getattr(self, f"parse_{self.link_type}")()

    def get_project_type(self):
        self.project_type = TYPE_PROJECT_PROJECT
        if os.path.exists(os.path.join(self.project_path, "__manifest__.py")):
            self.project_type = TYPE_PROJECT_MODULE

    def parse_local_filesystem(self):
        local_path = self.gitlink.replace("file://","")
        if local_path[-1] == "/":
            local_path = local_path[:-1]

        project_name = os.path.basename(local_path)
        return OdooProjectData(
            server="",
            author="",
            name=project_name,
        )


    def parse_http(self):
        server = self.gitlink.split("/")[2]
        if ":" in server:
            server = server.split(":")[0]
        author = self.gitlink.split("/")[3]
        project_name = self.gitlink.split("/")[4].replace(".git", "")
        return OdooProjectData(
            server=server,
            author=author,
            name=project_name,
        )
    
    def parse_ssh(self):
        server = self.gitlink.split(":")[0].split("@")[1]
        author = self.gitlink.split(":")[1].split("/")[0]
        project_name = self.gitlink.split(":")[1].split("/")[1].replace(".git", "")
        return OdooProjectData(
            server=server,
            author=author,
            name=project_name,
        )
    
    def get_project_path(self):
        if self.link_type in [GITLINK_TYPE_HTTP, GITLINK_TYPE_SSH]:
            return os.path.abspath(os.path.join(
                self.config.env.odoo_projects_dir,
                self.project_data.server,
                self.project_data.author,
                self.project_data.name,
            ))
        if self.link_type in [GITLINK_TYPE_FILE]:
            local_path = self.gitlink.replace("file://","")
            if local_path[-1] == "/":
                local_path = local_path[:-1]
            return local_path

    def get_dir_to_clone(self):
        return os.path.abspath(os.path.join(
            self.project_path,
            ".."
        ))

    def check_project(self):
        state = False
        if os.path.exists(self.project_path):
            if os.path.exists(os.path.join(self.project_path, ".git")):
                os.chdir(self.project_path)
                state = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True)
        if not state or b"true" not in state.stdout:
            try:
                shutil.rmtree(self.project_path)
            except FileNotFoundError:
                pass 
            self.clone_repo()
    
    def clone_repo(self):
        if not os.path.exists(self.dir_to_clone):
            os.makedirs(self.dir_to_clone)
        os.chdir(self.dir_to_clone)
        path_to_ssh_key = self.config.get("path_to_ssh_key", False)
        if not path_to_ssh_key:
            subprocess.run(["git", "clone", self.gitlink])
        else:
            subprocess.call(f'git clone {self.gitlink} --config core.sshCommand="ssh -i {path_to_ssh_key}"', shell=True)