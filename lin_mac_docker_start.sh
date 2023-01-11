SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $SCRIPT_DIR/docker_env.sh

cd $ODOO_DIR
git stash
git checkout $ODOO_VERSION

ln -s $ODOO_DIR $PROJECT_DIR_PATH
cd $OODOO_PROJECT_DIR_PATH
ln -s $OODOO_PROJECT_DIR_PATH $PROJECT_DIR_PATH

cd $PROJECT_DIR_PATH

# Список модулей для установки, который автоматически подставитсья при укзании параметра текущего скрипта -i, имена модулей указываеются через запятую без пробелов
INSTALL_MODULES="first_module"
# Список модулей для обновления, который автоматически подставитсья при укзании параметра текущего скрипта -u, имена модулей указываеются через запятую без пробелов
UPDATE_MODULES="first_module"

# Первоначальная строка запуска системы. Здесь мы запускаем python3 которому в качестве параметра указываем запуск модуля debugpy, который будет прослушивать порт 5678, затеп уже в качестве параметров мы передаем файл старта odoo со всеми необходимыми для нас параметрами. Я явно указываю путь ф файлу конфигурации, который мы пробросили 
START_PYTHON_COMMAND="python3 -u -m debugpy --listen 0.0.0.0:5678 $DOCKER_ODOO_DIR/odoo-bin -c $DOCKER_PROJECT_DIR/odoo.conf --limit-time-real 99999 --http-port 8069"

TEST_COMMAND=" --test-enable --stop-after-init"
TRANSLATE_COMMAND=" --language ru_RU --load-language ru_RU --i18n-overwrite"

# Для удобной разработки я ввел свои параметры командной строки для текущего сприпта:
# ПОРЯДОК РАБОТЫ С ПАРАМЕТРАМИ - ЕСЛИ НУЖНО СОЗДАТЬ СВОЮ БАЗУ, ПЕРВЫМ ДОЛЖЕН БЫТЬ ФЛАГ -d и ОБЯЗАТЕЛЬНО имя базы через пробел, потом остальные флаги, порядок остальных флагов не важен.
#  -d флаг который указывает на то что система будет запущена в режиме монобазы, через пробел в качестве параметра указывается имя базы, если базы не существует - 
#     будет запущен механизм созданяи базы с демо данными, а если есть просто произойдет запуск системы с доступом только к базе с этим именем
#  -i флаг который указывает что модули указанные в параметре $INSTALL_MODULES будут подставлены в команду запуска odoo и для них запуститься сценарий установки
#  -u флаг который указывает что модули указанные в параметре $UPDATE_MODULES будут подставлены в команду запуска odoo и для них запуститься сценарий обновления
#  -t флаг который указывает что будут запущены тесты при запуске, а после их выполнения система отсановится
# смотрим работу с параметрами тут https://wiki.bash-hackers.org/howto/getopts_tutorial
while getopts ":u :i :t :r :e: :d: " opt
    do
        case "${opt}" in
            i) START_PYTHON_COMMAND="$START_PYTHON_COMMAND -i $INSTALL_MODULES" ;;
            u) START_PYTHON_COMMAND="$START_PYTHON_COMMAND -u $UPDATE_MODULES" ;;
            t) START_PYTHON_COMMAND="$START_PYTHON_COMMAND $TEST_COMMAND" ;;
            r) START_PYTHON_COMMAND="$START_PYTHON_COMMAND $TRANSLATE_COMMAND" ;;
            d) START_PYTHON_COMMAND="$START_PYTHON_COMMAND -d ${OPTARG}" ;;
        esac
    done

# Теперь для запуска odoo нам надо сначала активировать окружение
START_STRING="bash -c ' cd $DOCKER_PROJECT_DIR && source $DOCKER_VENV_DIR/bin/activate && ${START_PYTHON_COMMAND}'"
export START_STRING
echo $START_STRING
var2="docker-compose up --no-log-prefix"
eval "$var2"
