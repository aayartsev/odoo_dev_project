import argparse

try:
    from . import cli_params
except:
    import cli_params

arg_parser = argparse.ArgumentParser(
                    prog="odpm",
                    description="Odoo Developer Project Manager",
                    epilog="Developing is not configuration")

arg_parser.add_argument(
    cli_params.INIT_PARAM,
    help="Use this param to initiate dir as odpm project",
    nargs="?",
    default=None,
    const=True,
    type=str,
)

arg_parser.add_argument(
    cli_params.INSTALL_PIP_PARAM,
    help="Will start install of all python packages from odoo "
    "requirements.txt and from requirements_txt param to "
    "environment inside docker container",
    action='store_true',
    
)

arg_parser.add_argument(
    cli_params.BUILD_IMAGE_PARAM,
    help="Will build image for your odoo version",
)

arg_parser.add_argument(
    cli_params.CONFIG_BASE64_DATA,
    help="Will read base64 string and will try to parse its content as json string",
)

arg_parser.add_argument(
    cli_params.GET_DB_LIST_PARAM,
    help="Will show list of databases",
)

arg_parser.add_argument(
    cli_params.START_PRECOMMIT_PARAM,
    help="""Will start pre-commit for your project inside container, specified in parameter "developing_project" from file "user_settings.json" """,
    action='store_true',
)

arg_parser.add_argument(
    cli_params.SET_ADMIN_PASS_PARAM,
    help="""When you specify the value of this parameter, the administrator account (user with id = 2) will have its password and login changed to those specified in the "db_default_admin_login" and "db_default_admin_password" parameters in the "user_settings.json" configuration file. Be sure to specify the name of the database for which you want to change the password and use the "-d database_name" parameter""",
)

arg_parser.add_argument(
    cli_params.TRANSLATE_PARAM,
    help="""Will update translation for selected language, for example ru_RU or eu_US for database from -d param and for modules form "update_modules" and "init_modules" from "user_settings.json" file """,
    type=str,
)

arg_parser.add_argument(
    cli_params.DB_DROP_PARAM,
    help="""Accept database name as parameter. Database with selected  name will be deleted. If you will use it with  params "-d", "-i", "-u", and select the same name, system will with first step delete DB and with second step will create new DB with the same name, and will install selected modules.""",
    action='store_true',
)

arg_parser.add_argument(
    cli_params.DB_RESTORE_PARAM,
    help="""As a parameter, the path to the archive is specified, relative to the directory specified in the "backups/localdir" parameter of the configuration file "user_settings.json". The DB name for restoration will be taken from the "-d" parameter.""",
    type=str
)

arg_parser.add_argument(
    cli_params.D_PARAM,
    help="""To specify the name of the database to work with. If there is no such database, it will be automatically created based on the "db_creation_data" parameter from the configuration file "user_settings.json".""",
    type=str
)

arg_parser.add_argument(
    cli_params.I_PARAM,
    help="""The parameter indicates that the modules specified in the "init_modules" parameter of the "user_settings.json" configuration file should be initialized.""",
    action='store_true',
)

arg_parser.add_argument(
    cli_params.U_PARAM,
    help="""The parameter indicates that the modules specified in the "update_modules" parameter of the "user_settings.json" configuration file should be updated.""",
    action='store_true',
)

arg_parser.add_argument(
    cli_params.T_PARAM,
    cli_params.TEST_PARAM,
    help="""Will run tests of modules specified in "init_modules" and "update_modules", works only when using parameters "-d", "-i", "-u". If the database is being created from scratch, tests of all installed modules will be run. This may take a long time.""",
    action='store_true',
)

arg_parser.add_argument(
    cli_params.BRANCH_PARAM,
    help="""Used together with the "--init" parameter to specify the branch of the git repository to be cloned.""",
    type=str,
)

arg_parser.add_argument(
    cli_params.SCREENCASTS_PARAM,
    help="""Used together with the "-t" or "--test" parameter to specify saving of screencast video for tours errors. This videos will be saved to "odoo_tests" directory inside project""",
    action='store_true',
)

args = arg_parser.parse_args()