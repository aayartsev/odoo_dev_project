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
DO_NOT_CHANGE = "Do not change, it will generate automatically"
ADMIN_PASSWD_MESSAGE = """Do not change, it will get from "db_manager_password" param from config.json file"""
THIS_IS_NOT_PROJECT_DIRECTORY = """This is not {PROJECT_NAME} directory. If you want to init new project use "{PROJECT_NAME} {INIT_PARAM}" command"""
ALREADY_INITED_PROJECT = """This dir is already {PROJECT_NAME} project"""
CHECK_CONFIG_FILE = """Check your '{CONFIG_FILE_NAME}' file, we can not parse it."""
PRE_COMMIT_FILE_WAS_NOT_FOUND = """Pre-commit file {PRE_COMMIT_FILE} was not found at {ODOO_PROJECT_DIR_PATH}"""

translations = {
    USER_NOT_IN_DOCKER_GROUP: {
        "ru_RU": """Вам необходимо добавить пользователя {CURRENT_USER} в группу {LINUX_DOCKER_GROUPNAME}"""
                 """запустите следующую команду от имени root или с помощью sudo:  usermod -a -G {LINUX_DOCKER_GROUPNAME} {CURRENT_USER}"""
                 """Затем перезапустите ваш компьтер""",
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
    DO_NOT_CHANGE:{
        "ru_RU": "Не изменяйте данный параметр, его значение будет сгенерировано автоматически"
    },
    ADMIN_PASSWD_MESSAGE:{
        "ru_RU": """Не изменяйте данный параметр, его значение будет взято из"""
                 """ параметра "db_manager_password" файла конфигурации config.json"""
    },
    THIS_IS_NOT_PROJECT_DIRECTORY: {
        "ru_RU": """Данный каталог не является odpm проектом. Если вы хотите создать новый проект, используйте команду "{PROJECT_NAME} {INIT_PARAM}". """
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
}

def get_translation(string_to_translate):
    current_locale = locale.getdefaultlocale()
    translated_string = translations.get(string_to_translate, {}).get(current_locale[0], False)
    if not translated_string:
        translated_string = string_to_translate
    return translated_string