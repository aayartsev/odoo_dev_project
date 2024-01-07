import sys
import os
import configparser
from contextlib import closing, contextmanager

from logger import get_module_logger
import cli_params

_logger = get_module_logger(__name__)

class OdooChecker():

    def __init__(self, config):
        _logger.info("Start Odoo Checker")
        self.odoo_dir = config["docker_odoo_dir"]
        self.odoo_config_data = config["odoo_config_data"]
        self.docker_path_odoo_conf = config["docker_path_odoo_conf"]
        self.args_dict = config["arguments"]
        self.db_lang = config["db_creation_data"]["db_lang"]
        self.db_country_code = config["db_creation_data"]["db_country_code"]
        self.db_default_admin_password = config["db_creation_data"]["db_default_admin_password"]
        self.db_default_admin_login = config["db_creation_data"]["db_default_admin_login"]
        self.db_create_demo = config["db_creation_data"]["create_demo"]
        self.db_manager_password = config.get("db_manager_password", False)

        sys.path.append(self.odoo_dir)

        from passlib.hash import pbkdf2_sha512
        import odoo
        from odoo.tools import config
        from odoo.api import Environment
        from odoo.release import version_info as odoo_version_info
        if odoo_version_info < (15, 0):
            environment_manage = Environment.manage
        else:
            @contextmanager
            def environment_manage():
                # Environment.manage is a no-op in Odoo 15+, but it
                # emits a noisy warning so let's avoid it.
                yield
        self.environment_manage = environment_manage
        if self.db_manager_password:
            if odoo_version_info[0] not in [11,12]:
                db_manager_password_crypt = pbkdf2_sha512.using(rounds=1).hash(self.db_manager_password)
                self.odoo_config_data["options"]["admin_passwd"] = db_manager_password_crypt
        self.create_config_file()
        odoo.tools.config.parse_config(["-c", self.docker_path_odoo_conf])
        # Enable database manager
        config['list_db'] = True
        os.chdir(self.odoo_dir)
        drop_db_name = self.args_dict.get(cli_params.DB_DROP_PARAM.replace("-", "_").strip("_"), False)
        get_db_list = self.args_dict.get(cli_params.GET_DB_LIST_PARAM.replace("-", "_").strip("_"), False)
        db_name = self.args_dict.get(cli_params.D_PARAM.replace("-", "_").strip("_"), False)
        db_restore_file_path = self.args_dict.get(cli_params.DB_RESTORE_PARAM.replace("-", "_").strip("_"), False)
        set_admin_pass = self.args_dict.get(cli_params.SET_ADMIN_PASS_PARAM.replace("-", "_").strip("_"), False)
        if db_restore_file_path:
            db_restore_file_path = os.path.join(self.odoo_dir, "../backups/", db_restore_file_path)
        # Start Odoo in environment context
        with self.environment_manage():

            if get_db_list:
                list = odoo.service.db.list_dbs(force=True)
                final_string = ""
                for database_name in list:
                    final_string += database_name + "\n"
                final_string = final_string.strip("\n")

            # Drop database
            if drop_db_name:
                if isinstance(drop_db_name, bool) and db_name:
                    drop_db_name = db_name
                db_exist = odoo.service.db.exp_db_exist(drop_db_name)
                if db_exist:
                    odoo.service.db.exp_drop(drop_db_name)

            if db_restore_file_path and db_name:
                odoo.service.db.restore_db(db_name, db_restore_file_path)

            if db_name:
                db_exist = odoo.service.db.exp_db_exist(db_name)
                if not db_exist:
                    odoo.service.db.exp_create_database(
                        db_name,
                        self.db_create_demo, self.db_lang,
                        user_password=self.db_default_admin_password,
                        login=self.db_default_admin_login,
                        country_code=self.db_country_code
                    )

            if set_admin_pass and db_name:
                new_password = self.db_default_admin_password
                password_crypt = pbkdf2_sha512.using(rounds=1).hash(new_password)
                sql_command = f""" UPDATE res_users SET password = '{password_crypt}', login = '{self.db_default_admin_login}' WHERE id = 2;"""
                db = odoo.sql_db.db_connect(db_name)
                with closing(db.cursor()) as cr:
                    cr.execute(sql_command, log_exceptions=True)
                    cr.commit()
    
    def create_config_file(self):
        odoo_conf = configparser.ConfigParser()
        for section in self.odoo_config_data:
            odoo_conf[section] = {}
            for key in self.odoo_config_data[section]:
                odoo_conf[section][key] = self.odoo_config_data[section][key]
        # Now we will create config file from received data threw current scrip argument
        with open(self.docker_path_odoo_conf, 'w') as odoo_config_file:
            odoo_conf.write(odoo_config_file)