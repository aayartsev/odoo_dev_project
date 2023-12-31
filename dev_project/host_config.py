import os
import pathlib
import json
import subprocess

from . import constants
from . import translations
from .handle_odoo_project_git_link import HandleOdooProjectGitLink

from .inside_docker_app.logger import get_module_logger

_logger = get_module_logger(__name__)

class Config():

    def __init__(self, pd_manager, arguments, program_dir, user_env):
        
        self.pd_manager = pd_manager
        self.program_dir = program_dir
        self.arguments = arguments
        self.config_dict = None
        self.repo_odpm_json = None
        self.config_json_loaded = False
        self.project_dir = self.pd_manager.project_path
        self.config_home_dir = self.pd_manager.home_config_dir
        self.user_env = user_env
        if self.pd_manager.init and isinstance(self.pd_manager.init, str):
            self.clone_project()
        # check current config.json file
        self.config_json_content = None
        self.check_for_config()
        # init user settings from json file
        self.get_user_settings_json()
        self.get_user_settings()
        self.init_modules = self.config_dict.get("init_modules", False)
        self.update_modules = self.config_dict.get("update_modules", False)
        self.beautify_module_list()
        self.db_creation_data = self.config_dict.get("db_creation_data", {})
        self.update_git_repos = self.config_dict.get("update_git_repos", False)
        self.clean_git_repos = self.config_dict.get("clean_git_repos", False)
        self.check_system = self.config_dict.get("check_system", False)
        self.db_manager_password = self.config_dict.get("db_manager_password", "admin")
        self.dev_mode = self.config_dict.get("dev_mode", False)
        self.developing_project = self.config_dict.get("developing_project", False)
        self.pre_commit_map_files = self.config_dict.get("pre_commit_map_files", [])

        # prepare developing project
        self.developing_project = self.handle_git_link(self.developing_project)
        self.odoo_project_dir_path = self.developing_project.project_path
        # init project settings from odpm.json
        self.get_project_odpm_json()
        self.get_odpm_settings()
        self.odoo_version = self.config_dict.get("odoo_version", 0.0)
        self.python_version = self.config_dict.get("python_version", constants.DEFAULT_PYTHON_VERSION)
        self.debian_version = self.config_dict.get("debian_version", constants.DEFAULT_DEBIAN_VERSION)
        self.debian_name = constants.DEBIAN_NAMES.get(self.debian_version)
        self.dependencies = self.config_dict.get("dependencies", [])
        self.requirements_txt = self.config_dict.get("requirements_txt", [])
        if constants.DEBUGPY not in self.requirements_txt:
            self.requirements_txt.append(constants.DEBUGPY)
        
        # prepare dockerfile template
        self.dockerfile_template_name = f"""debian_{self.debian_version}_dockerfile"""
        self.project_dockerfile_template_path = os.path.join(
            self.pd_manager.project_path,
            os.path.join(constants.PROJECT_SERVICE_DIRECTORY, self.dockerfile_template_name)
        )
        if not os.path.exists(self.project_dockerfile_template_path):
            self.pd_manager.rebuild_dockerfile_template(debian_template_filename=self.dockerfile_template_name)

        # prepare list of mapped dirs for  third party modules from which our project depends on
        self.dependencies_dirs = []
        # prepare list of mapped dirs for building config file for debugger usage
        self.debugger_path_mappings = []

        # set processor architecture
        self.arch = self.config_dict.get("arch", constants.ARCH)
        if self.arch == "auto":
            self.arch = constants.ARCH
        
        self.odoo_image_name = f"""odoo-{self.arch}-python-{self.python_version}-debian-{self.debian_version}"""
        self.docker_project_dir = str(pathlib.PurePosixPath("/home", constants.CURRENT_USER))
        self.docker_dev_project_dir = str(pathlib.PurePosixPath(self.docker_project_dir, constants.DEV_PROJECT_DIR))
        self.docker_inside_app = str(pathlib.PurePosixPath(self.docker_dev_project_dir, "inside_docker_app"))
        self.docker_odoo_dir = str(pathlib.PurePosixPath(self.docker_project_dir, "odoo"))
        
        # prepare of mapped dirs for odoo addons
        self.docker_dirs_with_addons = []
        self.docker_extra_addons = str(pathlib.PurePosixPath(self.docker_project_dir, "extra-addons"))
        self.docker_odoo_project_dir_path = str(pathlib.PurePosixPath(self.docker_extra_addons, self.developing_project.project_data.name))
        self.docker_dirs_with_addons.append(str(pathlib.PurePosixPath(self.docker_odoo_dir, "addons")))
        self.docker_dirs_with_addons.append(str(pathlib.PurePosixPath(self.docker_odoo_dir, "odoo", "addons")))
        self.docker_dirs_with_addons.append(self.docker_odoo_project_dir_path)

        self.docker_path_odoo_conf = str(pathlib.PurePosixPath(self.docker_project_dir, "odoo.conf"))
        self.docker_venv_dir = str(pathlib.PurePosixPath(self.docker_project_dir, "venv"))
        
        self.docker_backups_dir = str(pathlib.PurePosixPath(self.docker_project_dir, "backups"))
        self.docker_temp_tests_dir = str(pathlib.PurePosixPath("/tmp", "odoo_tests"))
        self.venv_dir = os.path.join(self.project_dir, "venv")
        self.docker_home = os.path.join(self.project_dir, "docker_home")
        self.dependencies_dir = os.path.join(self.project_dir, "dependencies")
        self.odoo_tests_dir = os.path.join(self.project_dir, "odoo_tests")
        self.compose_file_version = constants.DOCKER_COMPOSE_DEFAULT_FILE_VERSION
        self.odoo_config_data = {}

        # list of dirs and files which symlinks must be inside of project dir
        self.list_for_symlinks = [
            self.user_env.backups,
            self.user_env.odoo_src_dir,
            self.odoo_project_dir_path,
        ]

        if os.path.exists(self.repo_odpm_json):
            self.list_for_symlinks.append(self.repo_odpm_json)

    def clone_project(self):
        dev_project=self.handle_git_link(self.pd_manager.init)
        if constants.BRANCH_PARAM in self.arguments and isinstance(constants.BRANCH_PARAM, str):
            branch = self.arguments[constants.BRANCH_PARAM]
            subprocess.run(["git", "stash"], capture_output=False)
            subprocess.run(["git", "pull"], capture_output=False)
            subprocess.run(["git", "checkout", branch], capture_output=False)

    def get_project_odpm_json(self):
        self.repo_odpm_json = os.path.join(self.developing_project.project_path, constants.PROJECT_CONFIG_FILE_NAME)
        self.project_odpm_json = os.path.join(self.project_dir, constants.PROJECT_CONFIG_FILE_NAME)
        if not os.path.exists(self.repo_odpm_json) and not os.path.exists(self.project_odpm_json):
            default_odpm_json_content = self.create_default_odpm_json_content()
            with open(self.project_odpm_json, "w", encoding="utf-8") as odpm_json_file:
                json.dump(default_odpm_json_content, odpm_json_file, ensure_ascii=False, indent=4)
    
    def get_user_settings_json(self):
        self.user_settings_json = os.path.join(self.project_dir, constants.USER_CONFIG_FILE_NAME)
        if not os.path.exists(self.user_settings_json):
            default_user_settings_json_content = self.create_default_user_setting_json_content()
            with open(self.user_settings_json, "w", encoding="utf-8") as user_settings_json_file:
                json.dump(default_user_settings_json_content, user_settings_json_file, ensure_ascii=False, indent=4)

    def create_default_odpm_json_content(self):
        if self.config_json_content:
            return {
                "python_version": self.config_json_content.get("python_version", constants.DEFAULT_PYTHON_VERSION),
                "debian_version": self.config_json_content.get("debian_version", constants.DEFAULT_DEBIAN_VERSION),
                "odoo_version": self.config_json_content.get("odoo_version", 0.0),
                "dependencies": self.config_json_content.get("dependencies", []),
                "requirements_txt":self.config_json_content.get("requirements_txt", []),
            }
        available_versions = [int(float(version)) for version in constants.ODOO_VERSION_DEFAULT_ENV]
        available_versions_str = ", ".join([str(float(version)) for version in available_versions])
        user_odoo_version = input(translations.get_translation(translations.SET_ODOO_VERSION).format(
                    ODOO_LATEST_VERSION=constants.ODOO_LATEST_VERSION,
                    AVAILABEL_ODOO_VERSIONS_ARE = available_versions_str,
                ))
        if not user_odoo_version:
            user_odoo_version = constants.ODOO_LATEST_VERSION


        _logger.info(translations.get_translation(translations.YOU_SELECT_ODOO_VERSION).format(
                SELECTED_ODOO_VERSION=user_odoo_version,
            ))
        default_odpm_json_content = {
            "python_version": constants.ODOO_VERSION_DEFAULT_ENV[user_odoo_version]["python_version"],
            "debian_version": constants.ODOO_VERSION_DEFAULT_ENV[user_odoo_version]["debian_version"],
            "odoo_version": user_odoo_version,
            "dependencies":[
            ],
            "requirements_txt":[
            ]
        }
        return default_odpm_json_content

    def get_user_settings(self):
        if os.path.exists(self.user_settings_json):
            with open(self.user_settings_json) as user_settings_file:
                user_settings_dict = json.load(user_settings_file)
                self.config_dict = user_settings_dict
    
    def get_odpm_settings(self):
        if os.path.exists(self.project_odpm_json):
            with open(self.project_odpm_json) as project_odpm_file:
                project_odpm_dict = json.load(project_odpm_file)
                self.config_dict.update(project_odpm_dict)
        elif os.path.exists(self.repo_odpm_json):
            with open(self.repo_odpm_json) as repo_odpm_json:
                repo_odpm_json = json.load(repo_odpm_json)
                self.config_dict.update(repo_odpm_json)

    def check_for_config(self):
        self.config_json_path = os.path.join(self.project_dir, constants.CONFIG_FILE_NAME)
        self.config_deprecated_json_path = os.path.join(self.project_dir, "config_deprecated.json")
        if os.path.exists(self.config_json_path):
            with open(self.config_json_path) as config_file:
                self.config_json_content = json.load(config_file)
            os.rename(self.config_json_path, self.config_deprecated_json_path)
            _logger.warning(translations.get_translation(translations.CONFIG_JSON_IS_DEPRECATED).format(
                    CONFIG_FILE_NAME=constants.CONFIG_FILE_NAME,
                ))

    
    def beautify_module_list(self):
        for module_list in [self.init_modules, self.update_modules]:
            if isinstance(module_list, list):
                module_list = ",".join(module_list)
            if isinstance(module_list, str):
                module_list = module_list.split(",")
                module_list = [module.strip() for module in module_list]
                module_list = ",".join(module_list)
    
    def create_default_user_setting_json_content(self):
        if self.config_json_content:
            return {
                "init_modules": self.config_json_content.get("init_modules", ""),
                "update_modules": self.config_json_content.get("update_modules", ""),
                "db_creation_data":{
                    "db_lang": self.config_json_content.get("db_creation_data", {}).get("db_lang", "en_US"),
                    "db_country_code": self.config_json_content.get("db_creation_data", {}).get("db_country_code", None),
                    "create_demo": self.config_json_content.get("db_creation_data", {}).get("create_demo", True),
                    "db_default_admin_login": self.config_json_content.get("db_creation_data", {}).get("db_default_admin_login", "admin"),
                    "db_default_admin_password": self.config_json_content.get("db_creation_data", {}).get("db_default_admin_password", "admin"),
                },
                "update_git_repos": self.config_json_content.get("update_git_repos", False),
                "clean_git_repos": self.config_json_content.get("clean_git_repos", False),
                "check_system": self.config_json_content.get("check_system", True),
                "db_manager_password": self.config_json_content.get("db_manager_password", "1"),
                "dev_mode": self.config_json_content.get("dev_mode", False),
                "developing_project": self.config_json_content.get("developing_project", self.pd_manager.init),
                "pre_commit_map_files": self.config_json_content.get("pre_commit_map_files", []),
            }
        user_settings_content = {
            "init_modules":"",
            "update_modules":"",
            "db_creation_data":{
                "db_lang": "en_US",
                "db_country_code": None,
                "create_demo": True,
                "db_default_admin_login": "admin",
                "db_default_admin_password": "admin"
            },
            "update_git_repos": False,
            "clean_git_repos": False,
            "check_system": True,
            "db_manager_password":"1",
            "dev_mode": False,
            "developing_project": self.pd_manager.init,
            "pre_commit_map_files":[
            ]
        }
        return user_settings_content


    
    def handle_git_link(self, gitlink):
        odoo_project = HandleOdooProjectGitLink(gitlink, self)
        odoo_project.build_project()
        return odoo_project

    def config_to_json(self):
        config = {}
        config["docker_odoo_dir"] = self.docker_odoo_dir
        config["odoo_config_data"] = self.odoo_config_data
        config["docker_path_odoo_conf"] = self.docker_path_odoo_conf
        config["arguments"] = self.arguments
        config["db_creation_data"] = self.db_creation_data
        config["db_manager_password"] = self.db_manager_password
        config["docker_venv_dir"] = self.docker_venv_dir
        config["docker_project_dir"] = self.docker_project_dir
        config["requirements_txt"] = self.requirements_txt
        config["odoo_version"] = self.odoo_version
        config["python_version"] = self.python_version
        config["arch"] = self.arch
        return json.dumps(config).encode("utf-8")
            


