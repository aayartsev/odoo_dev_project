import locale

USER_NOT_IN_DOCKER_GROUP = """You need to add your user {CURRENT_USER} to group {LINUX_DOCKER_GROUPNAME}"""
"""run this command as root or sudo:  usermod -a -G {LINUX_DOCKER_GROUPNAME} {CURRENT_USER}"""
"""then reboot your computer"""
IS_GIT_INSTALLED = "Did you install git?"
CAN_NOT_CONNECT_DOCKER = "Cannot connect to the Docker daemon. Is the docker daemon running?"
CAN_NOT_GET_DOCKER_COMPOSE_INFO = "Cannot get docker-compose info, did you install it?"
CAN_NOT_CREATE_DIR = "Cannot create dir, {dir_path}, please check it"                
CHECK_ODOO_REPO = """Your odoo src directory {odoo_src_dir} is not git repository."""
"Please fix it, or delete and clone its repo again: "
"git clone https://github.com/odoo/odoo.git"
MESSAGE_ODOO_CONF = "If you want drop this file to default values, just delete it"
DO_NOT_CHANGE_PARAM = "Do not change this param, it is generating automatically"
DO_NOT_CHANGE_FILE = "Do not change this file, its content is generating automatically"
ADMIN_PASSWD_MESSAGE = """Do not change, it will get from "db_manager_password" param from config.json file"""
THIS_IS_NOT_PROJECT_DIRECTORY = """This is not {PROJECT_NAME} directory. If you want to init new project use "{PROJECT_NAME} {INIT_PARAM}" command"""
ALREADY_INITED_PROJECT = """This dir is already {PROJECT_NAME} project"""
CHECK_CONFIG_FILE = """Check your '{CONFIG_FILE_NAME}' file, we can not parse it."""
PRE_COMMIT_FILE_WAS_NOT_FOUND = """Pre-commit file {PRE_COMMIT_FILE} was not found at {ODOO_PROJECT_DIR_PATH}"""
SET_ODOO_SRC_DIR = """Set odoo sources directory, You can leave default {DEFAULT_ODOO_SRC_DIR} or write your own. Press 'Enter' to leave default value:"""
SET_ODOO_PROJECTS_SRC_DIR = """Set other odoo projects sources directory, You can leave default {DEFAULT_ODOO_PROJECTS_SRC_DIR} or write your own. Press 'Enter' to leave default value:"""
SET_ODOO_BACKUP_DIR = """Set directory for odoo creating/restoring backups, You can leave default {DEFAULT_ODOO_BACKUP_DIR} or write your own. Press 'Enter' to leave default value:"""
SET_SSH_KEY_PATH = """Set path to your SSH key for GitHub. How to create it you can read here: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent. Press 'Enter' leave empty value, in this case system will try to use default system ssh key for GitHub:\n"""
SET_ODOO_PORT = "Set odoo port which it will listen. You can leave default {DEFAULT_ODOO_PORT} or write your own. Press 'Enter' to leave default value:\n"
SET_POSTGRES_PORT = "Set PostgreSQL database server port which it will listen. You can leave default {DEFAULT_POSTGRES_PORT} or write your own. Press 'Enter' to leave default value:\n"
SET_DEBUGGER_PORT = "Set debugger port which it will listen. You can leave default {DEFAULT_DEBUGGER_PORT} or write your own. Press 'Enter' to leave default value:\n"
YOU_SELECT_ODOO_DIR = "You select this odoo sources dir: {SELECTED_ODOO_DIR}\n"
YOU_SELECT_ODOO_PROJECTS_DIR = "You select this other odoo projects sources dir: {SELECTED_ODOO_PROJECTS_DIR}\n"
YOU_SELECT_ODOO_BACKUPS_DIR = "You select this odoo backups dir: {SELECTED_ODOO_BACKUPS_DIR}\n"
NOTHING_SSH_PATH_NAME = "You did not selected any path to ssh key"
YOU_SELECT_SSH_KEY_PATH = "You select this ssh path key: {SELECTED_SSH_KEY_PATH}\n"
YOU_SELECT_ODOO_PORT = "You select this port for which odoo will listen: {SELECTED_ODOO_PORT}\n"
YOU_SELECT_POSTGRES_PORT = "You select this port for which PostgreSQL database server will listen: {SELECTED_POSTGRES_PORT}\n"
YOU_SELECT_DEBUGGER_PORT = "You select this port for which Python Debugger will listen: {SELECTED_DEBUGGER_PORT}\n"
DO_YOU_WANT_CLONE_ODOO = "Do you want to clone odoo? y/n\n"
CONFIG_JSON_IS_DEPRECATED = """ "config.json" is deprecated. Please read documentation"""

translations = {
    USER_NOT_IN_DOCKER_GROUP: {
        "ru_RU": """Вам необходимо добавить пользователя {CURRENT_USER} в группу {LINUX_DOCKER_GROUPNAME}\n"""
                 """запустите следующую команду от имени root или с помощью sudo:  usermod -a -G {LINUX_DOCKER_GROUPNAME} {CURRENT_USER}\n"""
                 """Затем перезапустите ваш компьютер""",
    },
    IS_GIT_INSTALLED:{
        "ru_RU": "Вы установили git?"
    },
    CAN_NOT_CONNECT_DOCKER: {
        "ru_RU": "Не удалось выполнить подключение к службе Docker. Проверьте запущена ли она."
    },
    CAN_NOT_GET_DOCKER_COMPOSE_INFO: {
        "ru_RU": "Не удалось получить информацию о Docker Compose. Проверьте установлен ли он."
    },
    CAN_NOT_CREATE_DIR: {
        "ru_RU": "Не удалось создать каталог, {dir_path}, пожалуйста проверьте его."
    },
    CHECK_ODOO_REPO: {
        "ru_RU": "Указанный вами каталог с исходными текстами odoo {odoo_src_dir} "
                 "не является git репозиторием или репозиторий поврежден"
                 "Пожалуйста исправьте повреждения или клонируйте репозиторий заново: "
                 "git clone https://github.com/odoo/odoo.git"
    },
    MESSAGE_ODOO_CONF: {
        "ru_RU": "Если вы хотите сбросить настройки этого файла в параметры по умолчанию, просто удалите его."
    },
    DO_NOT_CHANGE_PARAM:{
        "ru_RU": "Не изменяйте данный параметр, его значение генерируется автоматически"
    },
    DO_NOT_CHANGE_FILE: {
        "ru_RU": "Не изменяйте данный файл, его содержимое генерируется автоматически"
    },
    ADMIN_PASSWD_MESSAGE:{
        "ru_RU": """Не изменяйте данный параметр, его значение будет взято из"""
                 """ параметра "db_manager_password" файла конфигурации config.json"""
    },
    THIS_IS_NOT_PROJECT_DIRECTORY: {
        "ru_RU": "Данный каталог не является odpm проектом. Если вы хотите создать"
                 " новый проект, используйте команду '{PROJECT_NAME} {INIT_PARAM}'. "
    },
    ALREADY_INITED_PROJECT: {
        "ru_RU": """Данный каталог уже является {PROJECT_NAME} проектом"""
    },
    CHECK_CONFIG_FILE: {
        "ru_RU": """Проверьте ваш конфигурационный файл '{CONFIG_FILE_NAME}', его не возможно прочитать."""
    },
    PRE_COMMIT_FILE_WAS_NOT_FOUND: {
        "ru_RU": """Pre-commit файл {PRE_COMMIT_FILE} не был найден в каталоге {ODOO_PROJECT_DIR_PATH}"""
    },
    SET_ODOO_SRC_DIR: {
        "ru_RU": "Укажите каталог хранения исходных текстов odoo, Вы можете оставить "
                 "значение по умолчанию {DEFAULT_ODOO_SRC_DIR} или написать ваше собственное. "
                 "Нажмите 'Enter' чтобы оставить значение по умолчанию:\n"
    },
    SET_ODOO_PROJECTS_SRC_DIR: {
        "ru_RU": "Укажите каталог хранения исходных текстов других проектов odoo, Вы можете оставить "
                 "значение по умолчанию {DEFAULT_ODOO_PROJECTS_SRC_DIR} или написать ваше собственное. "
                 "Нажмите 'Enter' чтобы оставить значение по умолчанию:\n"
    },
    SET_ODOO_BACKUP_DIR:{
        "ru_RU": "Укажите каталог создания/восстановления бэкапов odoo, Вы можете оставить "
                 "значение по умолчанию {DEFAULT_ODOO_BACKUP_DIR} или написать ваше собственное. "
                 "Нажмите 'Enter' чтобы оставить значение по умолчанию:\n"
    },
    SET_SSH_KEY_PATH: {
        "ru_RU": "Укажите путь к SSH ключу для GitHub. Как его создать, вы можете прочитать здесь:"
                 " https://docs.github.com/en/authentication/connecting-to-github-with-ssh/"
                 "generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent. Вы можете оставить значение"
                 " пустым, нажав 'Enter'. Программа попытается использовать системный ssh ключ для GitHub:\n"
    },
    SET_ODOO_PORT: {
        "ru_RU": "Укажите порт, который будет слушать odoo. Можете оставить значение по умолчанию"
                 " {DEFAULT_ODOO_PORT} или укажите свой собственный. "
                 "Нажмите 'Enter' чтобы оставить значение по умолчанию:\n"
    },
    SET_POSTGRES_PORT: {
        "ru_RU": "Укажите порт, который будет слушать сервер PostgreSQL. Можете оставить значение по умолчанию"
                 " {DEFAULT_POSTGRES_PORT} или укажите свой собственный. "
                 "Нажмите 'Enter' чтобы оставить значение по умолчанию:\n"
    },
    SET_DEBUGGER_PORT: {
        "ru_RU": "Укажите порт, который будет слушать сервер Отладчик. Можете оставить значение по умолчанию"
                 " {DEFAULT_DEBUGGER_PORT} или укажите свой собственный. "
                 "Нажмите 'Enter' чтобы оставить значение по умолчанию:\n"
    },
    YOU_SELECT_ODOO_DIR:{
        "ru_RU": "Вы выбрали следующий каталог для хранения исходных текстов odoo: {SELECTED_ODOO_DIR}\n"
    },
    YOU_SELECT_ODOO_PROJECTS_DIR:{
        "ru_RU": "Вы выбрали следующий каталог для хранения исходных текстов других odoo проектов: {SELECTED_ODOO_PROJECTS_DIR}\n",
    },
    YOU_SELECT_ODOO_BACKUPS_DIR:{
        "ru_RU": "Вы выбрали следующий каталог для использования бэкапов odoo: {SELECTED_ODOO_BACKUPS_DIR}\n",
    },
    NOTHING_SSH_PATH_NAME:{
        "ru_RU": "Вы не выбрали путь к ssh ключу",
    },
    YOU_SELECT_SSH_KEY_PATH:{
        "ru_RU": "Вы выбрали следующий путь для нахождения ssh ключа: {SELECTED_SSH_KEY_PATH}\n",
    },
    YOU_SELECT_ODOO_PORT:{
        "ru_RU": "Вы выбрали следующий порт, который будет слушать odoo: {SELECTED_ODOO_PORT}\n",
    },
    YOU_SELECT_POSTGRES_PORT:{
        "ru_RU": "Вы выбрали следующий порт, который будет слушать сервер PostgreSQL: {SELECTED_POSTGRES_PORT}\n",
    },
    YOU_SELECT_DEBUGGER_PORT:{
        "ru_RU": "Вы выбрали следующий порт, который будет слушать Python Debugger: {SELECTED_DEBUGGER_PORT}\n",
    },
    DO_YOU_WANT_CLONE_ODOO: {
        "ru_RU": "Вы хотите клонировать odoo? y/n\n"
    },
    CONFIG_JSON_IS_DEPRECATED:{
        "ru_RU": """ Файл с параметрами "config.json" является устаревшим. Пожалуйста обратитесь к документации """,
    },
}

def get_translation(string_to_translate):
    current_locale = locale.getdefaultlocale()
    translated_string = translations.get(string_to_translate, {}).get(current_locale[0], False)
    if not translated_string:
        translated_string = string_to_translate
    return translated_string