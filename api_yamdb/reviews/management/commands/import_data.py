from csv import DictReader
from django.core.management.base import BaseCommand

from reviews.models import (
    Category,
    Comment,
    Genre,
    GenreTitle,
    Review,
    Title
)
from users.models import User


IMPORT_OBJECTS = [
    (Category, 'category.csv'),
    (Genre, 'genre.csv'),
    (Title, 'titles.csv'),
    (GenreTitle, 'genre_title.csv'),
    (User, 'users.csv'),
    (Review, 'review.csv'),
    (Comment, 'comments.csv'),
]


class Command(BaseCommand):

    help = 'Загрузка данных из файлов csv в таблицы бд через модели'

    def handle(self, *args, **options):

        for model, filename in IMPORT_OBJECTS:
            model_obj = model.objects.all()
            model_obj.delete()
            print(f'Загружаем {filename}...')
            with open(f'./static/data/{filename}', 'r') as open_file:
                read_file = DictReader(open_file)
                for values in read_file:
                    model.objects.create(**values)
        print('Готово!')
