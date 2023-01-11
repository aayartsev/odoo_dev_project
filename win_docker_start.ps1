#Requires -RunAsAdministrator
# Получаем путь к скрипту
$path = $MyInvocation.MyCommand.Path | split-path -parent
& $path\win_env_path.ps1
# Переходим в каталог с исходниками odoo
Set-Location $env:ODOO_PATH
# Сбрасываем все изменения, которые мы внесли в исходники odoo
git stash
# переключаемся на нужную версию
git checkout $env:ODOO_VERSION

#  Переходим в наш проект
Set-Location $env:PROJECT_DIR_PATH
# Делаем мягкую ссылку исходников odoo в наш проект
New-Item -ItemType SymbolicLink -Path "odoo" -Target $env:ODOO_PATH
# Делаем мягкую ссылку репозитория в наш проект
New-Item -ItemType SymbolicLink -Path "$env:GIT_PROJECT_NAME" -Target $env:OODOO_PROJECT_DIR_PATH

# Тут можно указать тоже самое для других модулей, если мы используем несколькоо репозиториев в проекте  

# Список модулей для установки, который автоматически подставитсья при укзании параметра текущего скрипта -i, имена модулей указываеются через запятую без пробелов
$INSTALL_MODULES="first_module"
# Список модулей для обновления, который автоматически подставитсья при укзании параметра текущего скрипта -u, имена модулей указываеются через запятую без пробелов
$UPDATE_MODULES="first_module"

# Первоначальная строка запуска системы. Здесь мы запускаем python3 которому в качестве параметра указываем запуск модуля debugpy, который будет прослушивать порт 5678, затеп уже в качестве параметров мы передаем файл старта odoo со всеми необходимыми для нас параметрами. Я явно указываю путь ф файлу конфигурации, который мы пробросили 
$START_PYTHON_COMMAND="python3 -u -m debugpy --listen 0.0.0.0:5678 $env:DOCKER_ODOO_DIR/odoo-bin -c $env:DOCKER_PROJECT_DIR/odoo.conf --limit-time-real 99999"
# Здесь мы добавляем команду, которая будет добавляться к команде запуска и инициировать запуск тестов для указанных модулей
$TEST_COMMAND=" --test-enable --stop-after-init"
$TRANSLATE_COMMAND=" --language ru_RU --load-language ru_RU --i18n-overwrite"

# Для удобной разработки я ввел свои параметры командной строки для текущего сприпта:
# ПОРЯДОК РАБОТЫ С ПАРАМЕТРАМИ - ЕСЛИ НУЖНО СОЗДАТЬ СВОЮ БАЗУ, ПЕРВЫМ ДОЛЖЕН БЫТЬ ФЛАГ -d и ОБЯЗАТЕЛЬНО имя базы через пробел, потом остальные флаги, порядок остальных флагов не важен.
#  -d флаг который указывает на то что система будет запущена в режиме монобазы, через пробел в качестве параметра указывается имя базы, если базы не существует - 
#     будет запущен механизм созданяи базы с демо данными, а если есть просто произойдет запуск системы с доступом только к базе с этим именем
#  -i флаг который указывает что модули указанные в параметре $INSTALL_MODULES будут подставлены в команду запуска odoo и для них запуститься сценарий установки
#  -u флаг который указывает что модули указанные в параметре $UPDATE_MODULES будут подставлены в команду запуска odoo и для них запуститься сценарий обновления
#  -t флаг который указывает что будут запущены тесты при запуске, а после их выполнения система отсановится
$param=$args
Switch ($param)
{
    -i {$START_PYTHON_COMMAND="$START_PYTHON_COMMAND -i $INSTALL_MODULES"}
    -u {$START_PYTHON_COMMAND="$START_PYTHON_COMMAND -u $UPDATE_MODULES"}
    -t {$START_PYTHON_COMMAND="$START_PYTHON_COMMAND $TEST_COMMAND"}
    -d {$START_PYTHON_COMMAND="$START_PYTHON_COMMAND -d $($param[1])"}
    -r {$START_PYTHON_COMMAND="$START_PYTHON_COMMAND $TRANSLATE_COMMAND"}
}

# Собираем строку
$START_STRING="bash -c 'cd $env:DOCKER_PROJECT_DIR && source $env:DOCKER_VENV_DIR/bin/activate && $START_PYTHON_COMMAND'"
[Environment]::SetEnvironmentVariable("START_STRING", "$START_STRING")
# выводим ее в консоль для отладки
Write-Host $env:START_STRING
# Запускаем финальную команду, которая и запустит все контейнеры с нужными нам настройками
docker-compose up
