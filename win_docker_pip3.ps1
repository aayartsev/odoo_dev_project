#Requires -RunAsAdministrator
# Описанные тут пути относятся к файловой системе контейнера, т.к. все действия выполняются внутри него"
$path = $MyInvocation.MyCommand.Path | split-path -parent
& $path\win_env_path.ps1

Write-Host "env:PROJECT_DIR_PATH: $env:PROJECT_DIR_PATH"


$BASH_COMMAND="cd $env:DOCKER_PROJECT_DIR && virtualenv --python=python3 $env:DOCKER_VENV_DIR && . $env:DOCKER_VENV_DIR/bin/activate && wget -O odoo_requirements.txt https://raw.githubusercontent.com/odoo/odoo/$env:ODOO_VERSION/requirements.txt && python3 -m pip install -r odoo_requirements.txt && python3 -m pip install -r $env:DOCKER_PROJECT_DIR/requirements.txt"
$START_STRING="bash -c '$BASH_COMMAND' "

[Environment]::SetEnvironmentVariable("START_STRING", $START_STRING)
Write-Host $env:START_STRING
docker-compose up
