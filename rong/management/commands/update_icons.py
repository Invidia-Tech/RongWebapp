import glob
import hashlib
import json
import math
import os.path
import re

import UnityPy
import requests
from PIL import Image
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


def download_icons(manifest, interested_func):
    # check current icons folder and download missing ones or checksum mismatches
    for mfline in manifest:
        filename, md5sum, _ = mfline.split(',', 2)
        filename = filename[2:]
        interested = interested_func(filename)

        if interested:
            # does file already exist with correct hash?
            if os.path.exists('assets/icons/%s' % filename):
                with open('assets/icons/%s' % filename, 'rb') as fh:
                    md5current = hashlib.md5(fh.read()).hexdigest()
                if md5sum.lower() == md5current.lower():
                    continue

            # download new file
            with requests.get(
                    'http://prd-priconne-redive.akamaized.net/dl/pool/AssetBundles/%s/%s' % (md5sum[:2], md5sum)) as rf:
                with open('assets/icons/%s' % filename, 'wb') as fh:
                    fh.write(rf.content)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--download', action='store_true', help='Download latest icons from PCRD servers')

    def process_unit_icons(self):
        # select only current units
        icon_files = []
        with connection.cursor() as cur:
            cur.execute('SELECT "unit_id" FROM "redive_en"."unit_data" WHERE "unit_id" BETWEEN 100000 AND 199999')
            valid_ids = cur.fetchall()
            for [id] in valid_ids:
                for star in [1, 3, 6]:
                    fn = "assets/icons/unit_icon_unit_%d.unity3d" % (id + star * 10)
                    if os.path.exists(fn):
                        icon_files.append(fn)
        icon_files.append("assets/icons/unit_icon_unit_unknown.unity3d")
        num_tiles = len(icon_files)
        tile_width = tile_height = 64
        sheet = Image.new(mode="RGBA", size=(tile_width * 10, tile_height * math.ceil(num_tiles / 10)))
        positions = {}

        for index, image_path in enumerate(icon_files):
            icon_of = image_path[image_path.rindex("_") + 1:-8]
            position = ((index % 10) * tile_width, (index // 10) * tile_height)
            env = UnityPy.load(image_path)
            for object in env.objects:
                if object.type == 'Texture2D':
                    data = object.read()
                    image = data.image
                    sheet.paste(image.resize((tile_width, tile_height)), position)
            positions[icon_of] = position

        sheet.save("rong/static/rong/images/unit_icon_sheet.webp", format='webp')
        sheet.quantize(colors=256).save("rong/static/rong/images/unit_icon_sheet.png", format='png')

        # generate spritesheet for stars here too
        star_size = 10
        star_overlap = 2
        star_on = Image.open("rong/static/rong/images/star_on.png").resize((10, 10))
        star_off = Image.open("rong/static/rong/images/star_off.png").resize((10, 10))
        star_sheet = Image.new(mode="RGBA", size=(star_size * 5 - star_overlap * 4, star_size * 6))
        for star_num in range(6):
            for off in range(4, star_num - 1, -1):
                star_sheet.paste(star_off, (off * (star_size - star_overlap), star_num * star_size))
            for on in range(star_num - 1, -1, -1):
                star_sheet.paste(star_on, (on * (star_size - star_overlap), star_num * star_size))
        star_sheet.save("rong/static/rong/images/icon_stars.png", format='png')

        # generate CSS
        with open('src/styles/components/_unit_icon_positions.scss', 'w', encoding='utf-8') as css:
            css.write(".unit-icon {\n")
            for unit in positions:
                css.write(
                    "&.u-%s {background-position: -%dpx -%dpx; }\n" % (unit, positions[unit][0], positions[unit][1]))
            css.write("}\n.unit-pfp {\n")
            for unit in positions:
                css.write("&.u-%s {background-position: -%dpx -%dpx; }\n" % (
                unit, positions[unit][0] * 48 // 64, positions[unit][1] * 48 // 64))
            css.write("}\n.unit-ddicon {\n")
            for unit in positions:
                css.write("&.u-%s {background-position: -%dpx -%dpx; }\n" % (
                unit, positions[unit][0] * 32 // 64, positions[unit][1] * 32 // 64))
            css.write("}\n.unit-icon-stars {\n")
            for star_num in range(6):
                css.write("&.s-%d {background-position: 0px -%dpx; }\n" % (star_num, star_num * star_size))
            css.write("}\n")

        return positions

    def process_enemy_icons(self):
        # save enemy icons to individual files because there are too many of them
        icon_files = glob.glob("assets/icons/unit_icon_unit_*.unity3d")
        tile_width = tile_height = 64
        enemy_files = []
        regex = re.compile("[^a-zA-Z0-9]+")

        for image_path in icon_files:
            icon_of = regex.sub("-", os.path.basename(image_path)[15:-8])
            if icon_of.startswith("1") or icon_of.startswith("9"):
                # playable unit or NPC unit, not interested
                continue
            env = UnityPy.load(image_path)
            for object in env.objects:
                if object.type == 'Texture2D':
                    object.read().image.resize((tile_width, tile_height)).save(
                        "rong/static/rong/images/enemies/%s.png" % icon_of, format='png')
            enemy_files.append(icon_of)

        return enemy_files

    def process_equip_icons(self):
        # save equip icons to individual files because there are too many of them
        icon_files = glob.glob("assets/icons/icon_icon_equipment_*.unity3d")
        tile_width = tile_height = 64
        equip_files = []
        regex = re.compile("[^a-zA-Z0-9]+")

        for image_path in icon_files:
            icon_of = regex.sub("-", os.path.basename(image_path)[20:-8])
            env = UnityPy.load(image_path)
            for object in env.objects:
                if object.type == 'Texture2D':
                    object.read().image.resize((tile_width, tile_height)).save(
                        "rong/static/rong/images/equipment/%s.png" % icon_of, format='png')
            equip_files.append(icon_of)

        return equip_files

    def process_item_icons(self):
        # save item icons to individual files because there are too many of them
        icon_files = glob.glob("assets/icons/icon_icon_item_*.unity3d")
        tile_width = tile_height = 64
        item_files = []
        regex = re.compile("[^a-zA-Z0-9]+")

        for image_path in icon_files:
            icon_of = regex.sub("-", os.path.basename(image_path)[15:-8])
            env = UnityPy.load(image_path)
            for object in env.objects:
                if object.type == 'Texture2D':
                    object.read().image.resize((tile_width, tile_height)).save(
                        "rong/static/rong/images/items/%s.png" % icon_of, format='png')
            item_files.append(icon_of)

        return item_files

    def handle(self, *args, **options):
        if options['download']:
            if not os.path.exists('./redive_dbs/truthversion_jp'):
                raise CommandError("Execution out of order: run update_database --download jp first")

            with open('./redive_dbs/truthversion_jp', "r", encoding="utf-8") as f:
                truth_version = json.load(f)

            # download unit manifest
            with requests.get(
                    'http://prd-priconne-redive.akamaized.net/dl/Resources/%s/Jpn/AssetBundles/iOS/manifest/unit2_assetmanifest' % truth_version) as rm:
                unit_manifest = rm.text.splitlines()
            download_icons(unit_manifest, lambda fn: (fn.startswith("unit_icon_unit_") and fn.endswith(".unity3d")))

            # download equipment icons
            with requests.get(
                    'http://prd-priconne-redive.akamaized.net/dl/Resources/%s/Jpn/AssetBundles/iOS/manifest/icon2_assetmanifest' % truth_version) as rm:
                icon_manifest = rm.text.splitlines()
            download_icons(icon_manifest,
                           lambda fn: (fn.startswith("icon_icon_equipment_") and fn.endswith(".unity3d")))
            download_icons(icon_manifest,
                           lambda fn: (fn.startswith("icon_icon_item_") and fn.endswith(".unity3d")))

        sprite_data = {
            "units": self.process_unit_icons(),
            "enemies": self.process_enemy_icons(),
            "equipment": self.process_equip_icons(),
            "items": self.process_item_icons(),
        }

        with open('assets/icons/sprite_data.json', 'w', encoding='utf-8') as fh:
            json.dump(sprite_data, fh)
