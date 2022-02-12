import csv

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from recipes import models


class Command(BaseCommand):
    help = 'Import data from csv file'

    def print_error(self, error, row, print_error):
        if print_error:
            print('Error:', error.args, '\nRow ID:', row.get('id'))

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)
        parser.add_argument('model', type=str)
        parser.add_argument('print_errors', type=bool)

    def handle(self, *args, **options):
        file_path = options['file_path']
        print_errors = options['print_errors']
        model = getattr(models, options['model'])
        with open(file_path, encoding='utf-8', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            total_count = 0
            successfull = 0
            for row in csv_reader:
                total_count += 1
                try:
                    model.objects.get_or_create(**row)
                    successfull += 1
                except IntegrityError as error:
                    self.print_error(error, row, print_errors)
                except ValueError as error:
                    self.print_error(error, row, print_errors)
                except AttributeError as error:
                    print(f'Модель {options["model"]} не найдена. {error}')
                    break
            errors = total_count - successfull
            print('Model: {}\nSuccessfull: {}; errors: {}'.format(
                model.__name__,
                successfull,
                errors,
            ))
