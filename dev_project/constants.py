import os
import pathlib

DEV_PROJECT_DIR = "dev_project"
CONFIG_FILE_NAME = "config.json"
DOCKER_TEMPLATE_FILE_RELATIVE_PATH = os.path.join(DEV_PROJECT_DIR, "templates", "Dockerfile")
DOCKER_COMPOSE_TEMPLATE_FILE_RELATIVE_PATH = os.path.join(DEV_PROJECT_DIR, "templates", "docker-compose.yml")
ODOO_TEMPLATE_CONFIG_FILE_RELATIVE_PATH = os.path.join(DEV_PROJECT_DIR, "templates", "dev_odoo_docker_config_file.conf")
DB_MANAGEMENT_RELATIVE_PATH = pathlib.PurePosixPath(DEV_PROJECT_DIR, "db_management.py")
DEBUGGER_DEFAULT_PORT = 5678
DEBUGGER_UNIT_NAME = "Odoo: Remote Attach"
DOCKERFILE = "Dockerfile"
GITLINK_TYPE_SSH = "ssh"
GITLINK_TYPE_HTTP = "http"
GITLINK_TYPE_FILE = "local_filesystem"
TYPE_PROJECT_PROJECT = "project"
TYPE_PROJECT_MODULE = "module"