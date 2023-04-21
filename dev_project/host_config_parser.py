import os
import json
from .constants import *


class ConfParser():

    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.config_path = os.path.join(self.project_dir, CONFIG_FILE_NAME)
        self.config = None
        self.parse_json_config()

    def parse_json_config(self):
        with open(self.config_path) as config_file:
            self.config = json.load(config_file)
            self.config["project_dir"] = self.project_dir