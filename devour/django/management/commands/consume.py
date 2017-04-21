from django.core.management.base import BaseCommand, CommandError
from devour.bin.devour_commands import consume

class Command(BaseCommand):
    help = 'Starts consumers that use django utilities.'

    def add_arguments(self, parser):
        parser.add_argument('consumer_name')

    def handle(self, *args, **options):
        consume(options['consumer_name'])
