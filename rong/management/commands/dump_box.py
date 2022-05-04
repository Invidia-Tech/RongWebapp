import json

from django.core.management.base import BaseCommand, CommandError

from rong.models import Box


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('box_id', help='Box ID to dump units from')
        parser.add_argument('filename')

    def handle(self, *args, **options):
        if not Box.objects.filter(pk=options['box_id']).exists():
            raise CommandError("Box does not exist")
        all_units = []
        for unit in Box.objects.get(pk=options['box_id']).boxunit_set.all():
            new_dict = dict(unit.__dict__)
            del new_dict["_state"]
            del new_dict["id"]
            del new_dict["box_id"]
            all_units.append(new_dict)
        with open("dumps/" + options['filename'], "w", encoding="utf-8") as fh:
            json.dump(all_units, fh)
        print("Done, dumped %d units to %s" % (len(all_units), options['filename']))
