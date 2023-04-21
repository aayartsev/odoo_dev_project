import re
import os
import subprocess
import shutil
from dataclasses import dataclass

@dataclass
class OdooProjectData(object):
    server:str
    author:str
    name:str

class HandleOdooProjectGitLink():

    def __init__(self, gitlink, config):
        self.gitlink = gitlink
        self.config = config
        self.ssh_regex = r"git@[a-z.]*:"
        self.link_type = self.get_git_link_type()
        self.project_data = self.parse_link_by_type()
        self.project_path = self.get_project_path()
        self.dir_to_clone = self.get_dir_to_clone()
        self.check_project()
        
    def get_git_link_type(self):
        if "http" in self.gitlink:
            return "http"
        ssh_pattern = re.findall(self.ssh_regex, self.gitlink)
        if ssh_pattern:
            return "ssh"
    
    def parse_link_by_type(self):
        return getattr(self, f"parse_{self.link_type}")()

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
        return os.path.abspath(os.path.join(
            self.config["odoo_projects_dir"],
            self.project_data.server,
            self.project_data.author,
            self.project_data.name,
        ))
    
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
        os.chdir(self.dir_to_clone)
        subprocess.run(["git", "clone", self.gitlink])