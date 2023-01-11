FROM python:3.7.12-bullseye  
  
# Переменные проекта
ARG USER_UID=9999  
ARG USER_GID=$USER_UID  

ARG USER_NAME=odoo
ARG PASSWORD=odoo
ARG WORKSPACE_FOLDER=odoo_project
# Если используете, например, макбук на M1 посатавьте arm64
ARG PROCESSOR_ARCH=amd64
  
# Подготавливаем внутреннего пользователя
RUN groupadd --gid $USER_GID $USER_NAME \  
    && useradd --uid $USER_UID --gid $USER_GID -m $USER_NAME -p $(openssl passwd -crypt $PASSWORD) \
    && apt-get update \  
    && apt-get install -y sudo \  
    && echo $USER_NAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USER_NAME \  
    && chmod 0440 /etc/sudoers.d/$USER_NAME\
    && mkdir /home/$USER_NAME/.ssh\  
    && chown ${USER_NAME}:${USER_NAME} /home/$USER_NAME/.ssh\   
    && mkdir -p /home/${USER_NAME}/.vscode-server\  
    && chown -R ${USER_NAME}:${USER_NAME} /home/${USER_NAME}/.vscode-server\  
    && apt-get -y install git postgresql-client node-less npm ssh  \  
    && python3 -m pip install pre-commit
 
# устанавливаем все необходимые зависимости 
RUN apt-get -y install libxml2-dev libxslt1-dev libldap2-dev\  
        libsasl2-dev libtiff5-dev libjpeg62-turbo-dev libopenjp2-7-dev\  
        zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev\  
        libharfbuzz-dev libfribidi-dev libxcb1-dev libpq-dev\
        openssl build-essential libssl-dev libxrender-dev \
        git-core libx11-dev libxext-dev libfontconfig1-dev libfreetype6-dev fontconfig\
        xvfb libfontconfig python3-virtualenv virtualenv
# Скачиваем и устанавливаем wkhtmltopdf который будет рендерить PDF файлы как нам нужно, 
# пакет из официальных репозиториев не рендерит заголовки и подвалы
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.bullseye_${PROCESSOR_ARCH}.deb \
    && apt-get install -y ./wkhtmltox_0.12.6.1-2.bullseye_${PROCESSOR_ARCH}.deb

USER $USER_NAME
