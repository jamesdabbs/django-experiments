from django.core.management.base import BaseCommand

from wide_tables.scripts import run_benchmarks


class Command(BaseCommand):
    """ Allows calling ./manage.py wide_table_benchmarks to run benchmarks from the command line """
    args = '(None)'
    help = 'Runs the wide table benchmarking script'

    def handle(self, *args, **options):
        run_benchmarks()