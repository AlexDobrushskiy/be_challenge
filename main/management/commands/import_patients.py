import json

from django.core.management.base import BaseCommand

from main.loaders import PatientLoader


class Command(BaseCommand):
    help = 'Imports patients'

    def add_arguments(self, parser):
        parser.add_argument('file_name', nargs=1, type=str)

    def handle(self, *args, **options):
        file_name = options['file_name'][0]
        with open(file_name, 'r') as f:
            data = f.read()
        json_data = json.loads(data)
        loader = PatientLoader(json_data)
        loader.load()
