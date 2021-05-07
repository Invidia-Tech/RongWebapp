from django.core.management.base import BaseCommand, CommandError
import os.path
import requests
import UnityPy
import hashlib
import json
import glob
from PIL import Image
import math

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--download', action='store_true', help='Download latest icons from PCRD servers')

    def handle(self, *args, **options):
        if options['download']:
            if not os.path.exists('./redive_dbs/truthversion_en'):
                raise CommandError("Execution out of order: run update_database --download en first")
            
            with open('./redive_dbs/truthversion_en', "r", encoding="utf-8") as f:
                truth_version = json.load(f)
            
            # download manifest
            with requests.get('http://assets-priconne-redive-us.akamaized.net/dl/Resources/%d/Jpn/AssetBundles/iOS/manifest/unit_assetmanifest' % truth_version) as rm:
                manifest = rm.text.splitlines()

            # check current icons folder and download missing ones or checksum mismatches
            for mfline in manifest:
                filename, md5sum, _ = mfline.split(',', 2)
                filename = filename[2:]
                interested = False
                if filename.startswith("unit_icon_unit_") and filename.endswith(".unity3d"):
                    icon_of_what = filename[15:-8]
                    # interested in 'unknown' or an id between 100000 and 200000
                    if icon_of_what == "unknown":
                        interested = True
                    else:
                        try:
                            uid = int(icon_of_what)
                            interested = uid >= 100000 and uid < 200000
                        except:
                            pass
                
                if interested:
                    # does file already exist with correct hash?
                    if os.path.exists('assets/icons/%s' % filename):
                        with open('assets/icons/%s' % filename, 'rb') as fh:
                            md5current = hashlib.md5(fh.read()).hexdigest()
                        if md5sum.lower() == md5current.lower():
                            continue
                    
                    # download new file
                    with requests.get('http://assets-priconne-redive-us.akamaized.net/dl/pool/AssetBundles/%s/%s' % (md5sum[:2], md5sum)) as rf:
                        with open('assets/icons/%s' % filename, 'wb') as fh:
                            fh.write(rf.content)
        
        # compile icon spritesheet
        icon_files = glob.glob("assets/icons/unit_icon_unit_*.unity3d")
        tile_width = tile_height = 64
        sheet = Image.new(mode = "RGBA", size = (tile_width * 10, tile_height*math.ceil(len(icon_files)/10)))
        position_map = {}

        for index, image_path in enumerate(icon_files):
            icon_of = image_path[image_path.rindex("_")+1:-8]
            position = ((index % 10) * tile_width, (index // 10) * tile_height)
            env = UnityPy.load(image_path)
            for object in env.objects:
                if object.type == 'Texture2D':
                    data = object.read()
                    image = data.image
                    sheet.paste(image.resize((tile_width, tile_height)), position)
            position_map[icon_of] = position
        
        sheet.save("rong/static/rong/images/icon_sheet.webp", format='webp')
        sheet.convert("RGB").save("rong/static/rong/images/icon_sheet.jpg", format='jpeg', quality=90)
        sheet.quantize(colors=256).save("rong/static/rong/images/icon_sheet.png", format='png')

        with open('assets/icons/sheet_positions.json', 'w', encoding='utf-8') as fh:
            json.dump(position_map, fh)




