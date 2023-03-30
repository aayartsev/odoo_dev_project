1. clone repo
2. copy its content to folder odoo_dev_project-16
3. check in `win_env_path.ps1` or in `lin_mac_docker_env.sh` variable `PROJECT_DIR_NAME`
4. Fill variables in this files with your context
5. enable on your system start scripts
6. use it with this [demo project](https://github.com/aayartsev/odoo_demo_project)
7. create docker image with command:
for windows
```
docker build -f F:\projects\odoo_dev_project-16\Dockerfile -t odoo-x86 .
```
for linux of mac(for m1 you can set name of image odoo-arm, do not forget change name in `docker-compose.yml`)
```
docker build -f $HOME/projects/odoo_dev_project-16/Dockerfile -t odoo-arm .
```
8. then install all python packages: 

for windows
```
F:\projects\odoo_dev_project-16\win_docker_pip3.ps1
```
for linux of mac
```
$HOME/projects/odoo_dev_project-16/lin_mac_docker_pip3.sh
```
you can add packages for your project in `requirements.txt` file

8. then you can start odoo: 

for windows
```
F:\projects\odoo_dev_project-16\win_docker_start.ps1 -d demo -i -u -r
```
for linux of mac
```
$HOME/projects/odoo_dev_project-16/lin_mac_docker_start.sh -d demo -i -u -r
```
in this case script will start odoo create database with name demo with demo data adn install and update modules that are written in this script. -r will add Russian language and update translation from your modules

9. If you want to start pre-commit, start script 

for windows
```
F:\projects\odoo_dev_project-16\win_docker_pre_commit.ps1
```
for linux of mac
```
$HOME/projects/odoo_dev_project-16/lin_mac_docker_start.sh
```
First of all you need to copy all pre-commit config files where your set rules for checking code and add them to `volumes` in `docker-compose.yml` because files of our project always have executable permissions inside of docker container. And you need disable this checks. In current situations this job is done and you can check differs between files from this project and files from [demo project](https://github.com/aayartsev/odoo_demo_project).

10. try to work
