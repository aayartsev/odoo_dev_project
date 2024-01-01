import os
from pathlib import Path

from . import constants
from . import translations

from .inside_docker_app.logger import get_module_logger

_logger = get_module_logger(__name__)

class ProjectDirManager():

    def __init__(self, start_dir_path, args_dict, program_dir_path):
        self.start_dir_path = start_dir_path
        self.project_path = start_dir_path
        self.dir_is_project = False
        self.args_dict = args_dict
        self.init = self.args_dict.get(constants.INIT_PARAM, False)
        self.service_directory = os.path.join(self.project_path, constants.PROJECT_SERVICE_DIRECTORY)
        self.program_dir_path = program_dir_path
        self.home_config_dir = os.path.join(Path.home(), constants.CONFIG_DIR_IN_HOME_DIR)
    
    def find_project_dir_in_parents(self):
        exist_service_directory = os.path.exists(self.service_directory)
        while not exist_service_directory:
            parent_dir = os.path.abspath(os.path.join(self.project_path, os.pardir))
            if self.project_path == parent_dir:
                break
            self.project_path = parent_dir
            self.service_directory = os.path.join(self.project_path, constants.PROJECT_SERVICE_DIRECTORY)
            if self.home_config_dir == self.service_directory:
                continue
            exist_service_directory = os.path.exists(self.service_directory)

    def check_project_dir(self):
        self.find_project_dir_in_parents()
        if os.path.exists(self.service_directory):
            self.dir_is_project = True
        else:
            self.project_path = self.start_dir_path
            self.service_directory = os.path.join(self.project_path, constants.PROJECT_SERVICE_DIRECTORY)
        if not self.init and not self.dir_is_project:
            _logger.info(translations.get_translation(translations.THIS_IS_NOT_PROJECT_DIRECTORY).format(
                        PROJECT_NAME=constants.PROJECT_NAME,
                        INIT_PARAM=constants.INIT_PARAM,
                    ))
            exit()
        if self.init and not self.dir_is_project:
            self.init_project()
            if isinstance(self.init, bool):
                exit()
            return
        if self.init and self.dir_is_project:
            _logger.info(translations.get_translation(translations.ALREADY_INITED_PROJECT).format(
                        PROJECT_NAME=constants.PROJECT_NAME,
                    ))
            return
        self.rebuild_templates()


    def init_project(self):
        os.makedirs(self.service_directory)
        self.rebuild_templates()
    
    def rebuild_templates(self):
        self.rebuild_docker_compose_template()
        self.rebuild_odoo_config_file_template()
    
    def rebuild_dockerfile_template(self, debian_template_filename=constants.DOCKERFILE):
        program_dockerfile_template_path = os.path.join(
            self.program_dir_path,
            os.path.join(constants.DEV_PROJECT_DIR, "templates", debian_template_filename)
        )
        project_dockerfile_template_path = os.path.join(
            self.project_path,
            os.path.join(constants.PROJECT_SERVICE_DIRECTORY, debian_template_filename)
        )
        self.generate_project_template_files(program_dockerfile_template_path, project_dockerfile_template_path)
    
    def rebuild_docker_compose_template(self):
        program_docker_compose_template_path = os.path.join(self.program_dir_path, constants.PROGRAM_DOCKER_COMPOSE_TEMPLATE_FILE_RELATIVE_PATH)
        project_docker_compose_template_path = os.path.join(self.project_path, constants.PROJECT_DOCKER_COMPOSE_TEMPLATE_FILE_RELATIVE_PATH)
        self.generate_project_template_files(program_docker_compose_template_path, project_docker_compose_template_path)
    
    def rebuild_odoo_config_file_template(self):
        program_odoo_config_file_template_path = os.path.join(self.program_dir_path, constants.PROGRAM_ODOO_TEMPLATE_CONFIG_FILE_RELATIVE_PATH)
        project_odoo_config_file_template_path = os.path.join(self.project_path, constants.PROJECT_ODOO_TEMPLATE_CONFIG_FILE_RELATIVE_PATH)
        self.generate_project_template_files(program_odoo_config_file_template_path, project_odoo_config_file_template_path)

    def generate_project_template_files(self, program_template_file, project_template_file):
        with open(program_template_file) as f:
            lines = f.readlines()
        content = "".join(lines)
        for replace_phrase in {
                constants.MESSAGE_MARKER: translations.get_translation(translations.MESSAGE_ODOO_CONF),
            }.items():
            content = content.replace(replace_phrase[0], replace_phrase[1])
        if not os.path.exists(project_template_file):
            with open(project_template_file, 'w') as writer:
                writer.write(content)
