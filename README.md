# Проект Foodgram
### Описание проекта:
Foodgram - это продуктовый помощник, проект для просмотра и публикации рецептов. Очень стильный и интуитивнопонятный сайт. 
Возможности:
- Подписки на авторов
- Сохранение рецептов в избранное
- Фильтр рецептов по категориям
- Добавление рецептов в список покупок
- Скачивание текстового файла с ингредиентами для рецептов из списка покупок

### Ознакомиться с проектом можно по адресу:
http://158.160.0.123/recipes или http://www.food-gram.myvnc.com

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