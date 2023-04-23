# yamdb_final

![](https://github.com/KiselevD92/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

## Описание проекта
Проект YaMDb собирает отзывы пользователей на произведения.

## Инструкции по запуску

**Как запустить проект:**
Клонировать репозиторий и перейти в него в командной строке:

```bash
@git clone https://github.com/yandex-praktikum/api_yamdb.git
@cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```bash
@python3 -m venv env
@source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```bash
@python3 -m pip install --upgrade pip
@pip install -r requirements.txt
```

Шаблон наполнения env-файла:

```bash
cp infra/.env.template infra/.env
```

Выполнить миграции:

```bash
@python3 manage.py migrate
```

Импортировать данные:

или из csv файлов:
```bash
@python3 manage.py import_data
```

или из сохраненного дампа БД:
```bash
@python3 manage.py loaddata ./static/data/data.json
```

Запустить проект:

```bash
@python3 manage.py runserver
```

Описание команд для запуска приложения в контейнерах:

```bash
sudo docker-compose up #для запуска контейнера
sudo docker-compose exec web python manage.py migrate # выполнить миграции
sudo docker-compose exec web python manage.py createsuperuser # создать суперпользователя
sudo docker-compose exec web python manage.py collectstatic --no-input # собрать статику
sudo docker-compose exec web python manage.py loaddata ./static/data/data.json #загрузка бд
```

Остановка и удаление контейнеров вместе с зависимостями
```bash
docker-compose down -v
```

Образ на сайте DockerHub
```bash
kiselevdv/yamdb:review.v1
```

## Использованные технологии
Python 3.7
Django 3
Django REST Framework
PostgreSQL
Simple-JWT

## Автор
Киселев Дмитрий
