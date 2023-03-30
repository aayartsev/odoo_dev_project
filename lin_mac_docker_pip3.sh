SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $SCRIPT_DIR/lin_mac_docker_env.sh

cd $PROJECT_DIR_PATH

PIP_INSTALL_COMMAND="cd ${DOCKER_PROJECT_DIR} && python3 -m venv ${DOCKER_VENV_DIR} && . ${DOCKER_VENV_DIR}/bin/activate && wget -O odoo_requirements.txt https://raw.githubusercontent.com/odoo/odoo/$ODOO_VERSION/requirements.txt && python3 -m pip install -r odoo_requirements.txt && python3 -m pip install -r ${DOCKER_PROJECT_DIR}/requirements.txt"

export START_STRING="bash -c '${PIP_INSTALL_COMMAND}'"
echo $START_STRING

var="docker-compose up --no-log-prefix"
eval "$var"