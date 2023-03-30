#!/usr/bin/env bash
export ODOO_VERSION=16.0
export GIT_SERVER_NAME="github.com"
export GIT_PROJECT_AUTHOR="aayartsev"
export GIT_PROJECT_NAME="odoo_demo_project"
export PROJECT_DIR_NAME="odoo_dev_project-16"
export ODOO_PATH="$HOME/odoo"
export PROJECT_DIR_PATH="$HOME/projects/$PROJECT_DIR_NAME"
export OODOO_PROJECT_DIR_PATH="$HOME/odoo_projects/$GIT_SERVER_NAME/$GIT_PROJECT_AUTHOR/$GIT_PROJECT_NAME"
export DOCKER_HOME="$PROJECT_DIR_PATH/docker_home"

# Описанные тут пути относятся к файловой системе контейнера, т.к. все действия выполняются внутри него"

export DOCKER_PROJECT_DIR="/home/odoo"
export DOCKER_ODOO_DIR="$DOCKER_PROJECT_DIR/odoo"
export DOCKER_VENV_DIR="$DOCKER_PROJECT_DIR/venv"
export DOCKER_ODOO_PROJECT_DIR_PATH="$DOCKER_PROJECT_DIR/extra-addons/$GIT_PROJECT_NAME"

