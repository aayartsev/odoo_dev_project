#Requires -RunAsAdministrator
[Environment]::SetEnvironmentVariable("ODOO_VERSION", "16.0")
[Environment]::SetEnvironmentVariable("GIT_SERVER_NAME", "github.com")
[Environment]::SetEnvironmentVariable("GIT_PROJECT_AUTHOR", "aayartsev")
[Environment]::SetEnvironmentVariable("GIT_PROJECT_NAME", "odoo_demo_project")
[Environment]::SetEnvironmentVariable("ODOO_PATH", ("$env:userprofile\Documents\odoo"))
[Environment]::SetEnvironmentVariable("PROJECT_DIR_NAME", "odoo_dev_project-16")
[Environment]::SetEnvironmentVariable("PROJECT_DIR_PATH", ("$env:userprofile\Documents\projects\$env:PROJECT_DIR_NAME"))
[Environment]::SetEnvironmentVariable("OODOO_PROJECT_DIR_PATH", ("$env:userprofile\Documents\odoo_projects\$env:GIT_SERVER_NAME\$env:GIT_PROJECT_AUTHOR\$env:GIT_PROJECT_NAME"))
# Описанные тут пути относятся к файловой системе контейнера, т.к. все действия выполняются внутри него"
[Environment]::SetEnvironmentVariable("DOCKER_PROJECT_DIR", "/home/odoo")
[Environment]::SetEnvironmentVariable("DOCKER_ODOO_DIR", "$env:DOCKER_PROJECT_DIR/odoo")
[Environment]::SetEnvironmentVariable("DOCKER_VENV_DIR", "$env:DOCKER_PROJECT_DIR/venv")
[Environment]::SetEnvironmentVariable("DOCKER_ODOO_PROJECT_DIR_PATH", "$env:DOCKER_PROJECT_DIR/extra-addons/$env:GIT_PROJECT_NAME")