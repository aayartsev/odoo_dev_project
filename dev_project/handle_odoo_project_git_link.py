import re
import os
import subprocess
import shutil
import pathlib
from dataclasses import dataclass
from typing import Literal

from . import constants

@dataclass
class OdooProjectData(object):
    server:str
    author:str
    name:str

class HandleOdooProjectGitLink():

    def __init__(self, gitlink:str, path_to_ssh_key: str, odoo_projects_dir: str):
        self.gitlink = gitlink
        self.path_to_ssh_key = path_to_ssh_key
        self.odoo_projects_dir = odoo_projects_dir
        self.dir_to_clone = ""
        self.project_type = None
        self.ssh_regex = r"git@[a-z.]*:"
        self.link_type = self.get_git_link_type()
        self.project_data = self.parse_link_by_type()
        self.project_path = self.get_project_path()
    
    def build_project(self) -> None:
        if self.link_type in [constants.GITLINK_TYPE_HTTP, constants.GITLINK_TYPE_SSH]:
            self.get_dir_to_clone()
            self.check_project()
        self.get_project_type()
        self.inside_docker_path = self.project_data.name
        if self.project_type == constants.TYPE_PROJECT_MODULE:
            self.inside_docker_path = str(pathlib.PurePosixPath(self.inside_docker_path, self.project_data.name))

    def get_git_link_type(self) -> Literal["http"] | Literal["ssh"] | Literal["local_filesystem"]:
        git_link_type = constants.GITLINK_TYPE_FILE
        if "file://" in self.gitlink:
            git_link_type = constants.GITLINK_TYPE_FILE
        if "http" in self.gitlink:
            git_link_type = constants.GITLINK_TYPE_HTTP
        ssh_pattern = re.findall(self.ssh_regex, self.gitlink)
        if ssh_pattern:
            git_link_type = constants.GITLINK_TYPE_SSH
        return git_link_type
    
    def parse_link_by_type(self) -> OdooProjectData:
        return getattr(self, f"parse_{self.link_type}")()

    def get_project_type(self) -> None:
        self.project_type = constants.TYPE_PROJECT_PROJECT
        if os.path.exists(os.path.join(self.project_path, "__manifest__.py")):
            self.project_type = constants.TYPE_PROJECT_MODULE

    def parse_local_filesystem(self) -> OdooProjectData:
        local_path = self.gitlink.replace("file://","")
        if local_path[-1] == "/":
            local_path = local_path[:-1]

        project_name = os.path.basename(local_path)
        return OdooProjectData(
            server="",
            author="",
            name=project_name,
        )


    def parse_http(self) -> OdooProjectData:
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
    
    def parse_ssh(self) -> OdooProjectData:
        server = self.gitlink.split(":")[0].split("@")[1]
        author = self.gitlink.split(":")[1].split("/")[0]
        project_name = self.gitlink.split(":")[1].split("/")[1].replace(".git", "")
        return OdooProjectData(
            server=server,
            author=author,
            name=project_name,
        )
    
    def get_project_path(self) -> str:
        if self.link_type in [constants.GITLINK_TYPE_HTTP, constants.GITLINK_TYPE_SSH]:
            return os.path.abspath(os.path.join(
                self.odoo_projects_dir,
                self.project_data.server,
                self.project_data.author,
                self.project_data.name,
            ))
        local_path = self.gitlink.replace("file://","")
        if self.link_type in [constants.GITLINK_TYPE_FILE]:
            if local_path[-1] == "/":
                local_path = local_path[:-1]
        return local_path

    def get_dir_to_clone(self) -> None:
        self.dir_to_clone = pathlib.Path(self.project_path).parent.absolute()

    def check_project(self) -> None:
        state = False
        if os.path.exists(self.project_path):
            if os.path.exists(os.path.join(self.project_path, ".git")):
                os.chdir(self.project_path)
                state = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True)
        if not state or b"true" not in state.stdout:
            self.force_clone_repo()
    
    def force_clone_repo(self) -> None:
        try:
            shutil.rmtree(self.project_path)
        except FileNotFoundError:
            pass 
        if not os.path.exists(self.dir_to_clone):
            os.makedirs(self.dir_to_clone)
        os.chdir(self.dir_to_clone)
        self.clone_repo()
    
    def clone_repo(self) -> None:
        if not self.path_to_ssh_key:
            subprocess.run(["git", "clone", self.gitlink])
        else:
            subprocess.call(f'git clone {self.gitlink} --config core.sshCommand="ssh -i {self.path_to_ssh_key}"', shell=True)