# Проект Продуктовый помощник - Foodgram
### Описание проекта:
«Продуктовый помощник» — это сайт, на котором можно публиковать собственные рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и создавать список покупок для заданных блюд.
 Вот, что было сделано в ходе работы над проектом:
- настроено взаимодействие Python-приложения с внешними API-сервисами;
- создан собственный API-сервис на базе проекта Django;
- подключено SPA к бэкенду на Django через API;
- созданы образы и запущены контейнеры Docker;
- созданы, развёрнуты и запущены на сервере мультиконтейнерные приложения;
- закреплены на практике основы DevOps, включая CI&CD.

Инструменты и стек: #python #JSON #YAML #Django #React #Telegram #API #Docker #Nginx #PostgreSQL #Gunicorn #JWT #Postman

### Ознакомиться с проектом можно по адресу:
http://158.160.0.123/recipes или http://food-gram.myvnc.com/recipes

### Шаблон заполнения env-файла
- DB_ENGINE=django.db.backends.postgresql `указываем, что работаем с postgresql`
- DB_NAME=postgres `имя базы данных`
- POSTGRES_USER=postgres `логин для подключения к базе данных`
- POSTGRES_PASSWORD=password `пароль для подключения к БД (установите свой)`
- DB_HOST=db  `название сервиса (контейнера)`
- DB_PORT=5432 `порт для подключения к БД`
- SECRET_KEY='ключ для Django settings'

### Запуск приложения используя контейнеры
1. Перейти в папку infra: ```cd infra```
2. Собрать контейнеры: ```docker-compose up -d --build```
3. Применить миграции: ```docker-compose exec web python manage.py migrate```
4. Cобрать статику: ```docker-compose exec web python manage.py collectstatic --no-input```

### Загрузить базу данных на сайт
```sh
docker-compose exec web python manage.py loaddata data/fixtures.json
```
### Можно загрузить только ингредиенты и теги
```sh
docker-compose exec web python manage.py procces_csv
```
### Остановка работы контейнеров
```sh
docker-compose stop
```

### Над бэкендом проекта работал
- [Александр Авров](https://github.com/AlexanderAvrov)

Фронтенд:
- [@practicum-russia](https://github.com/yandex-praktikum)
