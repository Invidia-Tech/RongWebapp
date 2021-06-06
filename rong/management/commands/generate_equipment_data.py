import json

from django.core.management.base import BaseCommand
from django.forms import model_to_dict

from rong.models import Equipment


class Command(BaseCommand):

    def handle(self, *args, **options):
        eq_data = {eq.id: model_to_dict(eq) for eq in Equipment.objects.all()}
        with open('rong/static/rong/js/equipment.js', 'w', encoding='utf-8') as fh:
            fh.write("""(function ($) {
$.equipmentData = %s;
})(jQuery);
""" % json.dumps(eq_data))
