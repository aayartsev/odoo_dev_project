import re
import os
import subprocess
import shutil
import pathlib
from dataclasses import dataclass
from typing import Literal

from . import constants

HTTP_MARKER = "http"
SSH_MARKER = "git"
FILE_SYSTEM_MARKER = "file://"

@dataclass
class OdooProjectData(object):
    server:str
    author:str
    name:str
    commit: str
    branch: str

class HandleOdooProjectLink():

    def __init__(self, project_string:str, path_to_ssh_key: str, odoo_projects_dir: str):
        self.is_true =True
        if not project_string:
            self.is_true = False
        self.project_string = project_string
        self.project_link = ""
        self.gitlink = ""
        self.commit = ""
        self.branch = ""
        self.path_to_ssh_key = path_to_ssh_key
        self.odoo_projects_dir = odoo_projects_dir
        self.dir_to_clone = ""
        self.project_type = None
        self.ssh_regex = r"git@[a-z.]*:"
        self.parse_project_string()
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

    def parse_project_string(self) -> None:
        project_data = self.project_string.split(" ")
        index_of_link = 0
        for marker in [HTTP_MARKER, SSH_MARKER, FILE_SYSTEM_MARKER]:
            for i in range(len(project_data)):
                if marker in project_data[i]:
                    self.project_link = project_data[i]
                    index_of_link = i
        for git_marker in [HTTP_MARKER, SSH_MARKER]:
            if git_marker in self.project_link:
                self.gitlink = self.project_link
        if index_of_link == 1 and len(project_data) > 2:
            self.branch = project_data[2]
        if index_of_link == 1 and len(project_data) > 3:
            self.commit = project_data[3]
        if index_of_link == 0 and len(project_data) > 1:
            self.branch = project_data[1]
        if index_of_link == 0 and len(project_data) > 2:
            self.commit = project_data[2]

    def get_git_link_type(self) -> Literal["http"] | Literal["ssh"] | Literal["local_filesystem"]:
        project_link_type = constants.GITLINK_TYPE_FILE
        if "file://" in self.project_link:
            project_link_type = constants.GITLINK_TYPE_FILE
        if "http" in self.project_link:
            project_link_type = constants.GITLINK_TYPE_HTTP
        ssh_pattern = re.findall(self.ssh_regex, self.project_link)
        if ssh_pattern:
            project_link_type = constants.GITLINK_TYPE_SSH
        return project_link_type
    
    def parse_link_by_type(self) -> OdooProjectData:
        return getattr(self, f"parse_{self.link_type}")()

    def get_project_type(self) -> None:
        self.project_type = constants.TYPE_PROJECT_PROJECT
        if os.path.exists(os.path.join(self.project_path, "__manifest__.py")):
            self.project_type = constants.TYPE_PROJECT_MODULE

    def parse_local_filesystem(self) -> OdooProjectData:
        local_path = self.project_link.replace("file://","")
        if local_path:
            if local_path[-1] == "/":
                local_path = local_path[:-1]

            project_name = os.path.basename(local_path)
            return OdooProjectData(
                server="",
                author="",
                name=project_name,
                commit=self.commit,
                branch=self.branch,
            )
        else:
            return OdooProjectData(
                server="",
                author="",
                name="",
                commit=self.commit,
                branch=self.branch,
            )


    def parse_http(self) -> OdooProjectData:
        server = self.project_link.split("/")[2]
        if ":" in server:
            server = server.split(":")[0]
        author = self.project_link.split("/")[3]
        project_name = self.project_link.split("/")[4].replace(".git", "")
        
        return OdooProjectData(
            server=server,
            author=author,
            name=project_name,
            commit=self.commit,
            branch=self.branch,
        )
    
    def parse_ssh(self) -> OdooProjectData:
        server = self.project_link.split(":")[0].split("@")[1]
        author = self.project_link.split(":")[1].split("/")[0]
        project_name = self.project_link.split(":")[1].split("/")[1].replace(".git", "")
        return OdooProjectData(
            server=server,
            author=author,
            name=project_name,
            commit=self.commit,
            branch=self.branch,
        )
    
    def get_project_path(self) -> str:
        if self.link_type in [constants.GITLINK_TYPE_HTTP, constants.GITLINK_TYPE_SSH]:
            return os.path.abspath(os.path.join(
                self.odoo_projects_dir,
                self.project_data.server,
                self.project_data.author,
                self.project_data.name,
            ))
        local_path = self.project_link.replace("file://","")
        if local_path:
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

    def __bool__(self):
        return self.is_true