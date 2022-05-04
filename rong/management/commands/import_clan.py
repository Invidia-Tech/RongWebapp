import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from rong.models import Box, BoxUnit, User, Clan, ClanMember, BoxItem, Pilot, HitTag, ClanBattle, ClanBattleBossInfo, \
    ClanBattleComp, HitGroup, ClanBattleScore, Unit, Flight
from rong.models.clan_battle_score import ClanBattleHitType
from rong.models.team import create_team


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('filename')

    def handle(self, *args, **options):
        unit_mapping = {unit.id: unit for unit in Unit.valid_units()}

        def populate_team(team):
            return [unit_mapping[unit] for unit in team if unit is not None]

        with open("dumps/" + options['filename'], "r", encoding="utf-8") as fh:
            clan_data = json.load(fh)
        # user mapping
        existing_users = {user.platform_id:user for user in User.objects.filter(platform_id__in=[u["platform_id"] for u in clan_data["users"]])}
        print(str(existing_users))
        user_mapping = {}
        created_users = 0
        for u in clan_data["users"]:
            if u["platform_id"] in existing_users:
                user_mapping[u["id"]] = existing_users[u["platform_id"]]
            else:
                u_data = dict(u)
                del u_data["id"]
                u_data["is_superadmin"] = False
                user = User(**u_data)
                user.save()
                created_users += 1
                user_mapping[u["id"]] = user
        print("Created %d missing users" % created_users)

        c_data = dict(clan_data)
        del c_data["members"]
        del c_data["battles"]
        del c_data["pilots"]
        del c_data["tags"]
        del c_data["users"]
        del c_data["admin_id"]

        clan = Clan(**c_data)
        clan.admin = user_mapping[clan_data["admin_id"]]

        # create members
        tosave = [clan]
        member_mapping = {}
        flight_pilot_mapping = {}
        tag_mapping = {}
        queued_tags = []

        for member_data in clan_data["members"]:
            m_data = dict(member_data)
            if "box" in m_data:
                del m_data["box"]
            del m_data["id"]
            del m_data["user_id"]
            member = ClanMember(**m_data)
            member.clan = clan
            if member_data["user_id"]:
                member.user = user_mapping[member_data["user_id"]]
            if "box" in member_data:
                member.box = Box(last_update=member_data["box"]["last_update"])
                tosave.append(member.box)
                for unit_data in member_data["box"]["units"]:
                    box_unit = BoxUnit(**unit_data)
                    box_unit.box = member.box
                    tosave.append(box_unit)
                for item_data in member_data["box"]["items"]:
                    box_item = BoxItem(**item_data)
                    box_item.box = member.box
                    tosave.append(box_item)
            tosave.append(member)
            member_mapping[member_data["id"]] = member

        for pilot_data in clan_data["pilots"]:
            p_data = dict(pilot_data)
            del p_data["id"]
            del p_data["user_id"]
            pilot = Pilot(**p_data)
            pilot.user = user_mapping[pilot_data["user_id"]]
            pilot.clan = clan
            tosave.append(pilot)
            flight_pilot_mapping[pilot_data["id"]] = pilot

        for tag_data in clan_data["tags"]:
            t_data = dict(tag_data)
            del t_data["id"]
            tag = HitTag(**t_data)
            tag.clan = clan
            tosave.append(tag)
            tag_mapping[tag_data["id"]] = tag

        for battle_data in clan_data["battles"]:
            b_data = dict(battle_data)
            del b_data["id"]
            del b_data["bosses"]
            del b_data["comps"]
            del b_data["hits"]
            del b_data["flights"]
            del b_data["hit_groups"]
            cb = ClanBattle(**b_data)
            cb.clan = clan
            tosave.append(cb)

            for boss_data in battle_data["bosses"]:
                boss = ClanBattleBossInfo(**boss_data)
                boss.clan_battle = cb
                tosave.append(boss)

            comp_mapping = {}
            for comp_data in battle_data["comps"]:
                c_data = dict(comp_data)
                del c_data["id"]
                del c_data["submitter_id"]
                if "team" in c_data:
                    del c_data["team"]
                comp = ClanBattleComp(**c_data)
                if comp_data["submitter_id"]:
                    comp.submitter = user_mapping[comp_data["submitter_id"]]
                if "team" in comp_data:
                    comp.team, _ = create_team(populate_team(comp_data["team"]))
                comp.clan_battle = cb
                tosave.append(comp)
                comp_mapping[comp_data["id"]] = comp

            group_mapping = {}
            for group_data in battle_data["hit_groups"]:
                g_data = dict(group_data)
                del g_data["id"]
                group = HitGroup(**g_data)
                group.clan_battle = cb
                tosave.append(group)
                group_mapping[group_data["id"]] = group

            for hit_data in battle_data["hits"]:
                h_data = dict(hit_data)
                del h_data["member_id"]
                del h_data["pilot_id"]
                del h_data["group_id"]
                del h_data["comp_id"]
                if "team" in h_data:
                    del h_data["team"]
                del h_data["tags"]
                del h_data["hit_type"]
                hit = ClanBattleScore(**h_data)
                hit.clan_battle = cb
                hit.member = member_mapping[hit_data["member_id"]]
                hit.hit_type = ClanBattleHitType(hit_data["hit_type"])
                if hit_data["pilot_id"]:
                    hit.pilot = member_mapping[hit_data["pilot_id"]]
                if hit_data["group_id"]:
                    hit.group = group_mapping[hit_data["group_id"]]
                if hit_data["comp_id"]:
                    hit.comp = comp_mapping[hit_data["comp_id"]]
                if "team" in hit_data:
                    # todo actually check order_map? shouldn't be needed tho
                    hit.team, order_map = create_team(populate_team(hit_data["team"]))
                if hit_data["tags"]:
                    queued_tags.append((hit, hit_data["tags"]))
                tosave.append(hit)

            for flight_data in battle_data["flights"]:
                f_data = dict(flight_data)
                del f_data["pilot_id"]
                del f_data["passenger_id"]
                if "team" in f_data:
                    del f_data["team"]
                flight = Flight(**f_data)
                flight.pilot = flight_pilot_mapping[flight_data["pilot_id"]]
                if flight_data["passenger_id"]:
                    flight.passenger = member_mapping[flight_data["passenger_id"]]
                flight.clan = clan
                flight.cb = cb
                if "team" in flight_data:
                    flight.team, _ = create_team(populate_team(flight_data["team"]))
                tosave.append(flight)


        # done, save
        with transaction.atomic():
            print("Creating %d records" % (len(tosave)))
            type_mapping = {}
            for obj in tosave:
                typ = str(type(obj))
                if typ not in type_mapping:
                    type_mapping[typ] = 0
                type_mapping[typ] += 1
            print(str(type_mapping))
            for model in tosave:
                model.save()
            for hit, tag_list in queued_tags:
                for tag_id in tag_list:
                    hit.tags.add(tag_mapping[tag_id])
            pass

