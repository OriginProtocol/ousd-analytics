from notify.main import run_all

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run all triggers and execute actions'

    def handle(self, *args, **options):
        run_all()
