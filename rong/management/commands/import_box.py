import json

from django.core.management.base import BaseCommand, CommandError

from rong.models import Box, BoxUnit


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('box_id', help='Box ID to import units into')
        parser.add_argument('filename')

    def handle(self, *args, **options):
        if not Box.objects.filter(pk=options['box_id']).exists():
            raise CommandError("Box does not exist")
        box = Box.objects.get(pk=options['box_id'])
        with open("dumps/" + options['filename'], "r", encoding="utf-8") as fh:
            units = json.load(fh)
        # delete old
        for unit in box.boxunit_set.all():
            unit.delete()
        # import new
        for unit in units:
            u_obj = BoxUnit(**unit)
            u_obj.box = box
            u_obj.save()
        print("Done, imported %d units from %s" % (len(units), options['filename']))
