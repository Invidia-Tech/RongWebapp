import json

from django.core.management.base import BaseCommand
from django.forms import model_to_dict

from rong.models import Equipment


class Command(BaseCommand):

    def handle(self, *args, **options):
        eq_data = {eq.id: model_to_dict(eq) for eq in Equipment.objects.all()}
        with open('src/modules/equipment.js', 'w', encoding='utf-8') as fh:
            fh.write("""export let equipmentData = %s;
""" % json.dumps(eq_data))
