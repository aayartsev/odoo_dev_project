print("DB_MANAGEMENT")
import sys
import os
import re
import json
import configparser
import base64
import contextlib
from contextlib import closing
import venv
from pip._internal.operations.freeze import freeze
import logging

args = sys.argv[1:]
ARGS_DICT = {}
all_flags_args_keys = re.findall(r"-[a-z]\s|-[a-z]$", " ".join(args))
all_flags_args_keys = [arg.strip() for arg in all_flags_args_keys]
all_key_args_keys = re.findall(r"--[a-z-_0-9]*", " ".join(args))
all_key_args_keys = [arg.strip() for arg in all_key_args_keys]
all_args_keys = all_flags_args_keys + all_key_args_keys

current_index = 0
while current_index < len(args):
    item = args[current_index]
    if current_index < len(args)-1 and item in all_args_keys and args[args.index(item) + 1] not in all_args_keys:
        ARGS_DICT[item] = args[args.index(item) + 1]
        current_index += 2
    else:
        ARGS_DICT[item] = True
        current_index += 1

DOCKER_VENV_DIR = ARGS_DICT["--docker_venv_dir"]
DOCKER_PROJECT_DIR = ARGS_DICT["--docker_project_dir"]
REQUIREMENTS_TXT = ARGS_DICT["--requirements_txt"]
ODOO_VERSION = ARGS_DICT["--version"]

def isvirtualenv():
    return sys.prefix != sys.base_prefix

def findfile(startdir, pattern):
    for root, dirs, files in os.walk(startdir):
        for name in files:
            if name.find(pattern) >= 0:
                return root + os.sep + name

    return None

def set_venv():
    # This is the heart of this script that puts you inside the virtual environment. 
    # There is no need to undo this. When this script ends, your original path will 
    # be restored.
    os.environ['PATH'] = os.path.dirname(findfile(DOCKER_VENV_DIR, 'activate')) + os.pathsep + os.environ['PATH']
    sys.path.insert(1, os.path.dirname(findfile(DOCKER_VENV_DIR, 'easy_install.py')))

def check_packages_for_install(requirements_txt: list) -> None:
    # TODO autoinstall packages from requirements_txt if they non in already installed list of pip packages
    dict_of_packages = {}
    for line in freeze():
        dict_of_packages.update({
            line.split("==")[0]: line.split("==")[1]
        })
    for package in requirements_txt:
        if package not in freeze():
            os.system(f"""python3 -m pip install {package}""")

if isvirtualenv():
    logging.info("Already in virtual environment.")
else:
    if findfile(DOCKER_VENV_DIR, 'activate') is None:
        logging.info("No virtual environment found. Creating one.")
        env = venv.EnvBuilder(with_pip = True)
        env.create(DOCKER_VENV_DIR)
        set_venv()
        os.system(f"""cd {DOCKER_PROJECT_DIR} && wget -O odoo_requirements.txt https://raw.githubusercontent.com/odoo/odoo/{ODOO_VERSION}/requirements.txt && python3 -m pip install -r odoo_requirements.txt""")
        check_packages_for_install(REQUIREMENTS_TXT.split(" "))

    else:
        logging.info("Not in virtual environment. Virtual environment directory found.")
        set_venv()
        check_packages_for_install(REQUIREMENTS_TXT.split("#"))
        


ODOO_DIR = ARGS_DICT["--odoo_dir"]
sys.path.append(ODOO_DIR)

from passlib.hash import pbkdf2_sha512
import odoo
from odoo.tools import config
from odoo.api import Environment
from odoo.release import version_info as odoo_version_info
if odoo_version_info < (15, 0):
    environment_manage = Environment.manage
else:
    @contextlib.contextmanager
    def environment_manage():
        # Environment.manage is a no-op in Odoo 15+, but it
        # emits a noisy warning so let's avoid it.
        yield

CONFIG_FILE_PATH = ARGS_DICT["-c"]
config_base64_data = ARGS_DICT["--config_base64_data"]
config_data_bytes = base64.b64decode(config_base64_data)
config_string_data = config_data_bytes.decode()
config_data = json.loads(base64.b64decode(config_base64_data).decode())

odoo_conf = configparser.ConfigParser()
for section in config_data:
    odoo_conf[section] = {}
    for key in config_data[section]:
        odoo_conf[section][key] = config_data[section][key]
# Now we will create config file from received data threw current scrip argument
with open(CONFIG_FILE_PATH, 'w') as odoo_config_file:
    odoo_conf.write(odoo_config_file)

odoo.tools.config.parse_config(["-c", CONFIG_FILE_PATH])

DB_NAME = ARGS_DICT.get("-d", False)
LANG = ARGS_DICT["--db-lang"]
COUNTRY_CODE = ARGS_DICT["--db-country_code"]
if COUNTRY_CODE == "None":
    COUNTRY_CODE = None
USER_PASSWORD = ARGS_DICT["--default_password"]
CREATE_DEMO = ARGS_DICT.get("--create_demo", 'False') in ("true", "1", "t", "True")
LOGIN = ARGS_DICT["--default_login"]
DB_NAME = ARGS_DICT.get("-d", False)
RESTORE_DB_FILE_PATH = ARGS_DICT.get("--db-restore", False)
DROP_DB_NAME = ARGS_DICT.get("--db-drop", False)
GET_DBS_LIST = ARGS_DICT.get("--get_dbs_list", False)
SET_ADMIN_PASS = ARGS_DICT.get("--set_admin_pass", False)
if RESTORE_DB_FILE_PATH:
    RESTORE_DB_FILE_PATH = ARGS_DICT["--odoo_dir"] + "/../backups/" + RESTORE_DB_FILE_PATH


# Enable database manager
config['list_db'] = True

os.chdir(ODOO_DIR)


# Запускаем в контексте окружения Odoo
with environment_manage():
    if GET_DBS_LIST:
        list = odoo.service.db.list_dbs(force=True)
        final_string = ""
        for db_name in list:
            final_string += db_name + "\n"
        final_string = final_string.strip("\n")

    # Удаление базы данных
    if DROP_DB_NAME:
        db_exist = odoo.service.db.exp_db_exist(DROP_DB_NAME)
        if db_exist:
            odoo.service.db.exp_drop(DROP_DB_NAME)

    if RESTORE_DB_FILE_PATH and DB_NAME:
        odoo.service.db.restore_db(DB_NAME, RESTORE_DB_FILE_PATH)

    if DB_NAME:
        db_exist = odoo.service.db.exp_db_exist(DB_NAME)
        if not db_exist:
            odoo.service.db.exp_create_database(
                DB_NAME,
                CREATE_DEMO, LANG,
                user_password=USER_PASSWORD,
                login=LOGIN,
                country_code=COUNTRY_CODE
            )

    if SET_ADMIN_PASS and DB_NAME:
        password_crypt = pbkdf2_sha512.using(rounds=1).hash(SET_ADMIN_PASS)
        # TODO check field name for password for different versions and check admin id
        sql_command = f""" UPDATE res_users SET password = '{password_crypt}', login = '{"admin"}' WHERE id = 2;"""
        db = odoo.sql_db.db_connect(DB_NAME)
        with closing(db.cursor()) as cr:
            cr.execute(sql_command, log_exceptions=True)
            cr.commit()