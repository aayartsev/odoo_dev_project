import logging

from .constants import *
from .translations import *

from .inside_docker_app.logger import get_module_logger

_logger = get_module_logger(__name__)

class ProjectDirManager():

    def __init__(self, project_path, args_dict, program_dir_path):
        self.project_path = project_path
        self.dir_is_project = False
        self.args_dict = args_dict
        self.init = self.args_dict.get(INIT_PARAM, False)
        self.service_directory = os.path.join(self.project_path, PROJECT_SERVICE_DIRECTORY)
        self.program_dir_path = program_dir_path

    def check_project_dir(self):
        
        if os.path.exists(self.service_directory):
            self.dir_is_project = True
        if not self.init and not self.dir_is_project:
            _logger.info(get_translation(THIS_IS_NOT_PROJECT_DIRECTORY).format(
                        PROJECT_NAME=PROJECT_NAME,
                        INIT_PARAM=INIT_PARAM,
                    ))
        if self.init and not self.dir_is_project:
            self.init_project()
        if self.init and self.dir_is_project:
            _logger.info(get_translation(ALREADY_INITED_PROJECT).format(
                        PROJECT_NAME=PROJECT_NAME,
                    ))
            exit()
        self.rebuild_templates()


    def init_project(self):
        os.makedirs(self.service_directory)
        self.rebuild_templates()
    
    def rebuild_templates(self):
        program_dockerfile_template_path = os.path.join(self.program_dir_path, PROGRAM_DOCKER_TEMPLATE_FILE_RELATIVE_PATH)
        project_dockerfile_template_path = os.path.join(self.project_path, PROJECT_DOCKER_TEMPLATE_FILE_RELATIVE_PATH)
        self.generate_project_template_files(program_dockerfile_template_path, project_dockerfile_template_path)
        program_docker_compose_template_path = os.path.join(self.program_dir_path, PROGRAM_DOCKER_COMPOSE_TEMPLATE_FILE_RELATIVE_PATH)
        project_docker_compose_template_path = os.path.join(self.project_path, PROJECT_DOCKER_COMPOSE_TEMPLATE_FILE_RELATIVE_PATH)
        self.generate_project_template_files(program_docker_compose_template_path, project_docker_compose_template_path)
        program_odoo_config_file_template_path = os.path.join(self.program_dir_path, PROGRAM_ODOO_TEMPLATE_CONFIG_FILE_RELATIVE_PATH)
        progect_odoo_config_file_template_path = os.path.join(self.project_path, PROJECT_ODOO_TEMPLATE_CONFIG_FILE_RELATIVE_PATH)
        self.generate_project_template_files(program_odoo_config_file_template_path, progect_odoo_config_file_template_path)

    def generate_project_template_files(self, program_template_file, project_template_file):

        with open(program_template_file) as f:
            lines = f.readlines()
        content = "".join(lines)
        for replace_phrase in {
                "#MESSAGE#": get_translation(MESSAGE_ODOO_CONF),
            }.items():
            content = content.replace(replace_phrase[0], replace_phrase[1])
        if not os.path.exists(project_template_file):
            with open(project_template_file, 'w') as writer:
                writer.write(content)
