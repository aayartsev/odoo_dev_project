SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $SCRIPT_DIR/lin_mac_docker_env.sh

cd $ODOO_PATH
git stash
git checkout $ODOO_VERSION

cd $PROJECT_DIR_PATH

export START_PRE_COMMIT_STRING="/bin/bash -c 'cd $DOCKER_ODOO_PROJECT_DIR_PATH && ls && pre-commit run --all-files'"

export START_STRING=$START_PRE_COMMIT_STRING
var2="docker-compose up"
eval "$var2"
