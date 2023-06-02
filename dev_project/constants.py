import os
import pathlib
import platform

DEV_PROJECT_DIR = "dev_project"
CONFIG_FILE_NAME = "config.json"
ENV_FILE_NAME = ".env"
DOCKERFILE = "Dockerfile"
DOCKER_TEMPLATE_FILE_RELATIVE_PATH = os.path.join(DEV_PROJECT_DIR, "templates", DOCKERFILE)
DOCKER_COMPOSE_TEMPLATE_FILE_RELATIVE_PATH = os.path.join(DEV_PROJECT_DIR, "templates", "docker-compose.yml")
ODOO_TEMPLATE_CONFIG_FILE_RELATIVE_PATH = os.path.join(DEV_PROJECT_DIR, "templates", "dev_odoo_docker_config_file.conf")
DB_MANAGEMENT_RELATIVE_PATH = pathlib.PurePosixPath(DEV_PROJECT_DIR, "db_management.py")
DEBUGGER_DEFAULT_PORT = "5678"
DEBUGGER_DOCKER_PORT = DEBUGGER_DEFAULT_PORT
ODOO_DEFAULT_PORT = "8069"
ODOO_DOCKER_PORT = ODOO_DEFAULT_PORT
POSTGRES_DEFAULT_PORT = "5432"
POSTGRES_DOCKER_PORT = POSTGRES_DEFAULT_PORT
DEBUGGER_UNIT_NAME = "Odoo: Remote Attach"
GITLINK_TYPE_SSH = "ssh"
GITLINK_TYPE_HTTP = "http"
GITLINK_TYPE_FILE = "local_filesystem"
TYPE_PROJECT_PROJECT = "project"
TYPE_PROJECT_MODULE = "module"
CURRENT_USER_UID = "9999"
CURRENT_USER_GID = CURRENT_USER_UID
CURRENT_USER = "odoo"
CURRENT_PASSWORD = CURRENT_USER
# If you have already used this image of postgres, you can have situation when your variables are not enabled
# https://github.com/docker-library/docs/blob/master/postgres/README.md
# Warning: the Docker specific variables will only have an effect if you start the container with a data directory that is empty; any pre-existing database will be left untouched on container startup.
# In this case you need to delete old data or use old variables
POSTGRES_ODOO_USER = CURRENT_USER
POSTGRES_ODOO_PASS = CURRENT_PASSWORD

ARCH = str(platform.machine()).lower()
if platform.system() == "Linux":
    import pwd
    if ARCH == "x86_64":
        ARCH = "amd64"
    CURRENT_USER_UID = os.getuid()
    CURRENT_USER_GID = os.getgid()
    CURRENT_USER = pwd.getpwuid(os.getuid())[0]

DOCKER_COMPOSE_VERSION_DATA = {
    "1.25.0": {
        "file_version": "3.3",
        "no_log_prefix": False,
    },
    "default": {
        "file_version": "3.8",
        "no_log_prefix": True,
    },
}

DOCKER_WORKING_MESSAGE = "Server Version"
GIT_WORKING_MESSAGE = "git version"
