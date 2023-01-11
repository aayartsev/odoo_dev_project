1. clone repo
2. copy its content to folder odoo_dev_project-16
3. check in `win_env_path.ps1` or in `lin_mac_docker_env.sh` variable `PROJECT_DIR_NAME`
4. Fill variables in this files with your context
5. enable on your system start scripts
6. use it with this [demo project](https://github.com/aayartsev/odoo_demo_project)
7. create docker image with command
for windows
```
docker build -f F:\projects\odoo_dev_project-16\Dockerfile -t odoo-x86 .
```
for linux of mac(for m1 you can set name of image odoo-arm, do not forget change name in `docker-compose.yml`)
```
docker build -f $HOME/projects/odoo_dev_project-16/Dockerfile -t odoo-x86 .
```
8. try to use it)