import json
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder

from rong.models import Box, Clan, User, Unit


def export_data(entity, exclude_columns=[]):
    export = dict(entity.__dict__)
    del export["_state"]
    if "_prefetched_objects_cache" in export:
        del export["_prefetched_objects_cache"]
    if "_ModelDiffMixin__initial" in export:
        del export["_ModelDiffMixin__initial"]
    for column in exclude_columns:
        if column in export:
            del export[column]
    #for key in export:
    #    if type(export[key]) is datetime:
    #        export[key] = export[key].timestamp()

    return export

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('clan_id', help='Clan ID to dump units from')
        parser.add_argument('filename')

    def handle(self, *args, **options):
        clan = Clan.objects.filter(pk=options['clan_id']).first()
        if not clan:
            raise CommandError("Clan does not exist")
        user_ids = set()
        clan_export = export_data(clan, ["id"])
        if clan.admin_id:
            user_ids.add(clan.admin_id)
        clan_export["members"] = []
        for member in clan.all_members.select_related('box').prefetch_related('box__boxunit_set', 'box__inventory'):
            member_data = export_data(member, ["clan_id", "box_id"])
            if member.user_id:
                user_ids.add(member.user_id)
            if member.box_id:
                member_data["box"] = export_data(member.box, ["id", "user_id", "name"])
                member_data["box"]["units"] = [export_data(box_unit, ["id", "box_id"]) for box_unit in member.box.boxunit_set.all()]
                member_data["box"]["items"] = [export_data(box_item, ["id", "box_id"]) for box_item in member.box.inventory.all()]
            clan_export["members"].append(member_data)
        clan_export["tags"] = [export_data(tag, ["clan_id"]) for tag in clan.hit_tags.all()]
        clan_export["battles"] = []
        for battle in clan.clanbattle_set.prefetch_related('bosses', 'comps', 'comps__team', 'hits', 'hits__tags', 'hits__team', 'hit_groups', 'flights', 'flights__team'):
            battle_data = export_data(battle, ["clan_id"])
            battle_data["bosses"] = [export_data(boss, ["id", "clan_battle_id"]) for boss in battle.bosses.all()]
            battle_data["comps"] = []
            for comp in battle.comps.all():
                comp_data = export_data(comp, ["clan_battle_id", "team_id"])
                if comp.team_id:
                    comp_data["team"] = [getattr(comp.team, "unit%d_id" % u) for u in range(1, 6)]
                if comp.submitter_id:
                    user_ids.add(comp.submitter_id)
                battle_data["comps"].append(comp_data)
            battle_data["hits"] = []
            for hit in battle.hits.all():
                hit_data = export_data(hit, ["id", "clan_battle_id", "team_id"])
                hit_data["hit_type"] = hit_data["hit_type"].value
                if hit.team_id:
                    hit_data["team"] = [getattr(hit.team, "unit%d_id" % u) for u in range(1,6)]
                hit_data["tags"] = [tag.id for tag in hit.tags.all()]
                battle_data["hits"].append(hit_data)
            battle_data["flights"] = []
            for flight in battle.flights.all():
                flight_data = export_data(flight, ["id", "clan_id", "cb_id", "team_id"])
                if flight.team_id:
                    flight_data["team"] = [getattr(flight.team, "unit%d_id" % u) for u in range(1, 6)]
                battle_data["flights"].append(flight_data)
            battle_data["hit_groups"] = [export_data(group, ["clan_battle_id"]) for group in battle.hit_groups.all()]
            clan_export["battles"].append(battle_data)
        clan_export["pilots"] = [export_data(pilot, ["clan_id"]) for pilot in clan.pilots.all()]
        for pilot in clan_export["pilots"]:
            if pilot["user_id"]:
                user_ids.add(pilot["user_id"])
        clan_export["users"] = [export_data(user) for user in User.objects.filter(id__in=user_ids)]

        with open("dumps/" + options['filename'], "w", encoding="utf-8") as fh:
            json.dump(clan_export, fh, cls=DjangoJSONEncoder, indent=2)
        print("Done, dumped to %s" % options['filename'])
