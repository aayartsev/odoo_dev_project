- [x] Сделать загрузку requirements.txt для оду в папку docker_home и потом проверять на наличие установленных пакетов, можно так же сделать счетчик попыток

- [x] Сделать мультиязычность сообщений для пользователя и логов
- [x] Разобраться почему логгер не работает внутри контейнера
- [x] разбить приложение, которое запускается внутри контейнера на модули, а не хранить все в одном файле
- [x] переделать объект config из словаря в объект
- [x] сделать удаление базы при использовании ключа --db-drop таким, что если имя не указано и есть ключ -d брать имя оттуда, получится сокращенный вариант
- [x] сделать сброс пароля таким образом, чтобы при использовании одной команды --set-admin-pass без указания параметров логин и пароль брались из файла конфигурации
- [x] рассмотреть возможность указания пароля для менеджера баз данных в файле конфигурации
- [x] добавить dev режим
- [x] сделать механизм формирования окружения: т.е. опросить пользователя, где он хочет создать те или иные каталоги и сделать возможность клонирования основного репозитория odoo частью менеджера
- [ ] создать системный пакет odpm версии 3.0 на основании текущих наработок, тогда не нужно будет заниматься дурацким копированием в папку проекта
- [x] надо подумать как выносить шаблон конфигурации odoo в папку проекта, чтобы разработчик мог его модифицировать под свои нужды
- [ ] проработать вариант для запуска проекта через VSCode docker окружения
- [x] рассмотреть вариант разделения файл config.json на две части: одна будет с личными настройками разработчика, а вторая с настройками самого проекта
- [x] рассмотреть вариант использования разных версий python для разных версий odoo
- [x] сделать каталог(правда это расходится с идеей передачи всего контекста проекта в одном файле конфигурации) для sql файлов, чтобы менеджер при развертывании базы из архива мог применять эти изменения
- [ ] добавить команду для просмотра версий установленных python пакетов
- [ ] docker-compose up --force-recreate - сделать проверку на работоспособность сети или контейнера
- [x] сделать возможным переход по методам системы с помощью Ctrl+Click.
- [x] сделать автоматический парсер зависимостей oca модулей и автоматическое их добавление к проекту
- [ ] сделать автоматический поиск python зависимостей и добавление их к проекту
- [ ] устранить падение контейнера при использовании dev режима