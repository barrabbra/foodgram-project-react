# Foodgram
Cервис для обмена рецептами.

Есть возможность создавать, редактировать, удалять и просматривать рецепты. Регистрация и вход в систему реализованная с помощью использования електронной почты.
Можно подписываться на авторов, добавлять рецепты в избранное или корзину. Есть возможность скачать список продуктов в формате pdf. Для выбора рецептов доступен поиск по тегам.
Полное описание API сервиса доступен по аресу /api/docs/

## Статус проекта
[![Foodgram Workflow](https://github.com/barrabbra/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/barrabbra/foodgram-project-react/actions/workflows/foodgram_workflow.yml)


## Стек технологий
Python 3.9, Django 4.0.1, Django REST Framework 3.13.1, PostgresQL, Docker, Yandex.Cloud.

## Установка
Для запуска локально, создайте файл `.env` в директории `/backend/` с содержанием:
```
DB_ENGINE=django.db.backends.postgresql (Указываем что используется postgresql в качестве БД)
DB_NAME=(название для БД)
POSTGRES_USER=(пользователь БД)
POSTGRES_PASSWORD=(пароль пользователя БД)
DB_HOST=(адрес БД)
DB_PORT=(порт)
SECRET_KEY=(секретный ключ джанги)
DEBUG=(True/False - разрешить или запретить дебаг режим)
ALLOWED_HOSTS=(через запятую без пробелов указать все доступные адреса, * - для любых)
```

#### Установка Docker
Для запуска проекта предварительно требуется установить [Docker](https://docs.docker.com/engine/install/) и [docker-compose](https://docs.docker.com/compose/install/).

### Установка проекта на сервер
1. Скопируйте файлы из папки `/infra/` на ваш сервер и `.env` файл из директории `/backend/`:
```bash
scp -r infra/ <username>@<server_ip>:/home/<username>/
scp backend/.env <username>@<server_ip>:/home/<username>/
```
2. Зайдите на сервер и измените `server_name` в конфиге nginx на ваше доменное имя:
```bash
nano nginx.conf
```

### Настройка проекта
1. Запустите docker compose:
```bash
docker-compose up -d
```
2. Примените миграции:
```bash
docker-compose exec backend python manage.py migrate
```
3. Соберите статику:
```bash
docker-compose exec backend python manage.py collectstatic
```
4. Создайте администратора:
```bash
docker-compose exec backend python manage.py createsuperuser
```
5. Загрузите начальный перечень ингредиентов (необязательно):
```bash
docker-compose exec backend python manage.py importcsv data/ingredients.csv Ingredient True
```
6. Загрузите начальный перечень тегов (необязательно):
```bash
docker-compose exec backend python manage.py importcsv data/tags.csv Tag True
```

## Как импортировать данные из своего csv файла?
Для начала убедитесь, что первая строчка вашего csv файла совпадает с названиями полей в модели. Если на первой строчке нет названия полей или они неправильные, исправьте, прежде чем приступать к импортированию.

### Импортирование с помощью скрипта
Выполните команду `python manage.py importcsv`с следующими параметрами:
`file_path` - путь до вашего файла csv,
`model` - название класса модели,
`print_errors` - требуется ли выводить каждую ошибку подробно (True/False)?
Пример:
```bash
docker-compose exec backend python manage.py importcsv data/ingredients.csv Ingredient True
```

## Сайт
Сайт доступен по ссылке:
[citysaltlakes.ru](http://citysaltlakes.ru/)
