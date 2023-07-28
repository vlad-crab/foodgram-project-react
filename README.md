foodgram-project-react

![foodgram-project workflow](https://github.com/vlad-crab/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

https://foodgram-vladcrab.ddns.net/

### Описание
Проект foodgram это площадка для размещения рецептов.

Пользователи могут публиковать собственные рецепты или следовать чужим кулинарным изощрениям.

Есть возможность фильтрации рецептов по тегам и авторам что позволит найти именно то что нужно.

Чтобы любимые рецепты не потерялись их можно добавить в избранное как и лучших по вашему мнению авторов.

Для удобства покупки нужных ингридиентов пользователю предоставлена возможность скачать список покупок в котором будут все нужные ингридиенты и их количества.

Полную документацию по API можно найти на http://localhost/api/docs/ после запуска проекта.


### Запуск проекта:
- Для запуска у вас должен быть установлен Docker.
- Клонировать репозиторий и перейти в командной строке bash в директорию /foodgram-project-react/infra/.
- Выполнить последовательно следующие команды.

```cmd
docker-compose up -d
```

```cmd
docker-compose exec web python manage.py makemigrations
```

```cmd
docker-compose exec web python manage.py migrate
```

```cmd
docker-compose exec web python manage.py load_ingredient_data
```

Если есть необходимость, заполняем базу тестовыми данными командой:

```bash
docker-compose exec web python manage.py loaddata fixtures.json
```

Создать администратора для управления админ панелью, можно командой:

```bash
winpty docker-compose exec web python manage.py createsuperuser
```

Проект уже запущен и доступен на http://localhost/

Адрес админ-панели http://localhost/admin/

Чтобы остановить работу контейнеров нужно из той-же дирректории infra выполнить комманду
```cmd
docker-compose down -v
```