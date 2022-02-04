import csv

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

import recipes.models as model


class Command(BaseCommand):
    help = 'Import data from csv file'

    def print_error(error, row, print_error):
        if print_error:
            print('Error:', error.args, '\nRow ID:', row.get('id'))

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)

    def handle(self, *args, **options):
        with open(options['file_path'], encoding='utf-8', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            total_count = 0
            successfull = 0
            for row in csv_reader:
                total_count += 1
                try:
                    model.objects.get_or_create(**row)
                    successfull += 1
                except IntegrityError as error:
                    print_error(error, row, print_errors)
                except ValueError as error:
                    print_error(error, row, print_errors)
            errors = total_count - successfull
            print('Model: {}\nSuccessfull: {}; errors: {}'.format(
                model.__name__, successfull, errors
            ))
