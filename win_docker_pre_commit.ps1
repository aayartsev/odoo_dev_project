#Requires -RunAsAdministrator
# Описанные тут пути относятся к файловой системе контейнера, т.к. все действия выполняются внутри него"
$path = $MyInvocation.MyCommand.Path | split-path -parent
& $path\win_env_path.ps1

Write-Host $env:DOCKER_ODOO_PROJECT_DIR_PATH

$START_STRING="/bin/bash -c 'cd $env:DOCKER_ODOO_PROJECT_DIR_PATH && pre-commit run --all-files'"

[Environment]::SetEnvironmentVariable("START_STRING", $START_STRING)
Write-Host $env:START_STRING
docker-compose up
