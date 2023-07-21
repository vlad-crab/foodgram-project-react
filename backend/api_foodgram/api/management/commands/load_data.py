import csv
import os

from django.core.management.base import BaseCommand

from api_foodgram.settings import BASE_DIR

from api.models import Ingredient


class Command(BaseCommand):
    help = "Load ingredients to DB"

    def handle(self, *args, **options):
        path = os.path.join(BASE_DIR, 'data/ingredients.csv')
        with open(path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measure_unit=row[1]
                )
        self.stdout.write("Все ингредиенты загружены в базу данных")
