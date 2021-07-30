import sys
import subprocess
import zipfile
import shutil
import os
import json
import glob
import math
from version import randomizer_commit, randomizer_version
try: 
    import requests
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
    import requests



def download_randomizer():
    zippath = 'randomizer.zip'

    # Make sure an old zip isn't sitting around
    if os.path.isfile(zippath):
        os.remove(zippath)

    # Download the zipped randomizer
    r = requests.get(f'https://github.com/Roman971/OoT-Randomizer/archive/{randomizer_commit}.zip', stream=True)
    with open(zippath, 'wb') as fp:
        for chunk in r.iter_content():
            fp.write(chunk)
    
    # Extract the zip file and add __init__.py
    with zipfile.ZipFile(zippath, 'r') as zf:
        zf.extractall('.')
    os.rename(f'OoT-Randomizer-{randomizer_commit}', 'randomizer')
    with open(os.path.join('randomizer', '__init__.py'), 'w') as fp:
        pass

    # Delete the zip file
    os.remove(zippath)

def check_version():
    if os.path.isfile(os.path.join('randomizer', 'version.py')):
        from randomizer import version as ootrversion
        if ootrversion.__version__ == randomizer_version:
            return
        else:
            print("Updating the randomizer...")
            shutil.rmtree('randomizer')
            download_randomizer()
    else:
        print("Downloading the randomizer...")
        download_randomizer()
    return

# This function will take things from the GUI eventually.
def randomizer_settings(rootdir=os.getcwd(), plando_filename='random_settings.json', worldcount=1, patch_filename='', patch_folder='patches', patch="Patch"):
    return {
        "rom": find_rom_file(),
        "output_dir": os.path.join(rootdir, patch_folder),
        "output_file": patch_filename,
        "compress_rom": patch,
        "enable_distribution_file": "True",
        "distribution_file": os.path.join(rootdir, "data", plando_filename),
        "create_spoiler": "True",
        "world_count": worldcount
    }

def init_randomizer_settings(plando_filename='random_settings.json', worldcount=1):
    settings = randomizer_settings(plando_filename=plando_filename, worldcount=worldcount)

    with open(os.path.join('data', 'randomizer_settings.json'), 'w') as fp:
        json.dump(settings, fp, indent=4)


def generate_patch_file(plando_filename='random_settings.json', worldcount=1, max_retries=3, patch_filename='', patch_folder='patches', patch="Patch"):
    settings = json.dumps(randomizer_settings(plando_filename=plando_filename, worldcount=worldcount, patch_filename=patch_filename, patch_folder=patch_folder, patch=patch))

    retries = 0
    while(True):
        print(f"RSL GENERATOR: RUNNING THE RANDOMIZER - ATTEMPT {retries+1} OF {max_retries}")
        completed_process = subprocess.run(
            [sys.executable, os.path.join("randomizer", "OoTRandomizer.py"), "--settings=-"],
            capture_output=True,
            input=settings,
            encoding='utf-8',
        )

        if completed_process.returncode != 0:
            retries += 1
            if retries < max_retries:
                continue
            print(f"RSL GENERATOR: MAX RETRIES ({max_retries}) REACHED. RESELECTING SETTINGS.")
            break
        break
    return completed_process

def update_plando_file(plando_filename='random_settings.json', hint_dist={}, named_items=[]):
    with open(os.path.join('data', plando_filename), 'r') as fp:
        plando = json.load(fp)
        # The randomizer complains that it can't create junk items if the item pool is already full.
        # Deleting it causes no changes to the seed as all location contents are already specified.
        if 'item_pool' in plando:
            del plando['item_pool']
        # Prevent previously generated hints from overriding the new distro 
        if 'gossip_stones' in plando:
            del plando['gossip_stones']
        # Add new hint distro
        if 'settings' in plando:
            plando['settings']['hint_dist_user'] = hint_dist
            plando['settings']['item_hints'] = named_items
        # Delete regular shop items to work around plando bug with random shopsanity
        # Also delete ice trap models to work around plando bug
        if 'locations' in plando:
            iterlocs = plando['locations'].copy()
            for l, i in iterlocs.items():
                if type(i) is dict:
                    if 'Buy ' in i['item']:
                        plando['locations'].pop(l)
                    if i['item'] == 'Ice Trap':
                        # scrubs don't have a model to delete but still use a dict for price
                        if 'model' in i:
                            plando['locations'][l].pop('model')
        # OW ER plando only works for one side of the OW entrance. "Reverse" entrances always fail.
        # The randomizer helpfully creates spoilers that use the reverse as the primary key.
        # Swap entrances links around to make this work.
        

    with open(os.path.join('data', plando_filename), 'w') as fp:
        json.dump(plando, fp, indent=4)

def generate_hint_distro(spoiler='plando_Spoiler.json'):
    named_items = []

    hint_dist = {
        "name":                  "rsl",
        "gui_name":              "Random Settings League",
        "description":           "Random Settings League dynamic hints. Hero's path hints for items required only for trials, up to 5 way of the hero, 3 foolish",
        "add_locations":         [],
        "remove_locations":      [],
        "add_items":             [],
        "remove_items":          [],
        "dungeons_woth_limit":   1,
        "dungeons_barren_limit": 1,
        "named_items_required":  True,
        "vague_named_items":     True,
        "distribution":          {
            "trial":      {"order":  1, "weight": 0.0, "fixed":   0, "copies": 1},
            "always":     {"order":  2, "weight": 0.0, "fixed":   0, "copies": 1},
            "named-item": {"order":  3, "weight": 0.0, "fixed":   0, "copies": 1},
            "woth":       {"order":  4, "weight": 0.0, "fixed":   2, "copies": 2},
            "barren":     {"order":  5, "weight": 0.0, "fixed":   3, "copies": 2},
            "sometimes":  {"order":  6, "weight": 0.0, "fixed":   7, "copies": 1},
            "entrance":   {"order":  7, "weight": 0.0, "fixed":   0, "copies": 1},
            "random":     {"order":  8, "weight": 0.0, "fixed":   0, "copies": 1},
            "item":       {"order":  9, "weight": 0.0, "fixed":   0, "copies": 1},
            "song":       {"order": 10, "weight": 0.0, "fixed":   0, "copies": 1},
            "overworld":  {"order": 11, "weight": 0.0, "fixed":   0, "copies": 1},
            "dungeon":    {"order": 12, "weight": 0.0, "fixed":   0, "copies": 1},
            "junk":       {"order": 13, "weight": 1.0, "fixed":   0, "copies": 1},
        }
    }

    with open(os.path.join('data', spoiler), 'r') as fp:
        plando = json.load(fp)

    # Generate named item/hero's path hints
    trials = []
    wincon = []
    if plando['settings']['triforce_hunt'] == False:
        hintable_items = {
            'Light Arrows',
            'Magic Meter',
            'Bow',
            'Farores Wind',
            'Small Key (Ganons Castle)',
            'Progressive Strength Upgrade',
            'Mirror Shield',
            'Megaton Hammer',
            'Progressive Hookshot',
            'Zeldas Lullaby',
            'Song of Time',
            'Fire Arrows',
            'Bombchus'
        }
        rewards = {
            "Queen Gohma": "Deku Tree",
            "King Dodongo": "Dodongos Cavern",
            "Barinade": "Jabu Jabus Belly",
            "Phantom Ganon": "Forest Temple",
            "Volvagia": "Fire Temple",
            "Morpha": "Water Temple",
            "Bongo Bongo": "Shadow Temple",
            "Twinrova": "Spirit Temple"
        }
        for trial, status in plando['trials'].items():
            if status == 'active':
                trials.append(trial + ' ' + plando['dungeons']['Ganons Castle'])
        if (plando['settings']['bridge'] == 'medallions'
        or plando['settings']['bridge'] == 'dungeons'
        or (plando['settings']['shuffle_ganon_bosskey'] == 'on_lacs'
            and (plando['settings']['lacs_condition'] == 'medallions'
            or plando['settings']['lacs_condition'] == 'dungeons'))):
            for boss, dungeon in rewards.items():
                if 'Medallion' in plando['locations'][boss]:
                    wincon.append(dungeon + ' ' + plando['dungeons'][dungeon])
        if (plando['settings']['bridge'] == 'stones'
        or plando['settings']['bridge'] == 'dungeons'
        or (plando['settings']['shuffle_ganon_bosskey'] == 'on_lacs'
            and (plando['settings']['lacs_condition'] == 'stones'
            or plando['settings']['lacs_condition'] == 'dungeons'))):
            for boss, dungeon in rewards.items():
                if 'Medallion' not in plando['locations'][boss]:
                    wincon.append(dungeon + ' ' + plando['dungeons'][dungeon])
        # potentially duplicates two dungeons if the opposite win con is medallions or dungeons, but does not affect the algorithm
        if (plando['settings']['bridge'] == 'vanilla'
        or (plando['settings']['shuffle_ganon_bosskey'] == 'on_lacs'
            and plando['settings']['lacs_condition'] == 'vanilla')):
            for boss, dungeon in rewards.items():
                if plando['locations'][boss] == 'Shadow Medallion' or plando['locations'][boss] == 'Spirit Medallion':
                    wincon.append(dungeon + ' ' + plando['dungeons'][dungeon])

        # Always hints pointing to named-item hints cause the location to be locked. Named-item hints
        # will correctly not generate a hint in this case, but named_items_required=true doesn't handle 
        # having the item already hinted and throws an error thinking it's not hinted.
        # Bingo handled this by disabling always hints. DDR doesn't use named_items_required.
        # For RSL we don't want to do either. To work around this until the randomizer is fixed, detect
        # and remove always-hinted named items from the item_hints list prior to generation.
        # I'm not sure how to import modules from dynamically downloaded files, so just duplicate the 
        # rando logic here for now.
        always_locations = ['ZR Frogs Ocarina Game', 'KF Links House Cow', 'DMT Biggoron']
        if plando['randomized_settings']['big_poe_count'] > 3:
            always_locations.append('Market 10 Big Poes')
        if plando['settings']['complete_mask_quest'] != True:
            always_locations.append('Deku Theater Mask of Truth')
        if stones_required_by_settings(plando['settings']) < 2:
            always_locations.append('Song from Ocarina of Time')
            always_locations.append('HF Ocarina of Time Item')
        if medallions_required_by_settings(plando['settings']) < 5:
            always_locations.append('Sheik in Kakariko')
        if tokens_required_by_settings(plando['settings']) < 30:
            always_locations.append('Kak 30 Gold Skulltula Reward')
        if tokens_required_by_settings(plando['settings']) < 40:
            always_locations.append('Kak 40 Gold Skulltula Reward')
        if tokens_required_by_settings(plando['settings']) < 50:
            always_locations.append('Kak 50 Gold Skulltula Reward')
        # Special case for Skip Child Zelda as it's always ignored for hints in the randomizer
        # This gets converted to a starting item in the spoiler and the SCZ is removed, so may
        # not be relevant to check
        if 'skip_child_zelda' in plando['settings'].keys():
            if plando['settings']['skip_child_zelda'] == True:
                always_locations.append('Song from Impa')
        always_items = []
        for l in always_locations:
            if l in plando['locations']:
                if type(plando['locations'][l]) is dict:
                    always_items.append(plando['locations'][l]['item'])
                else:
                    always_items.append(plando['locations'][l])
        
        # Exclude total starting items to prevent from hinting more items than exist in the world
        for i, num in plando['starting_items'].items():
            if i in hintable_items:
                for x in range(num):
                    always_items.append(i)

        if (plando['randomized_settings']['trials'] > 0
        or plando['settings']['bridge'] == 'vanilla'):
            if 'Light Arrows' not in always_items:
                named_items.append('Light Arrows')
        
        if ((plando['settings']['item_pool_value'] == 'minimal'
        or plando['settings']['item_pool_value'] == 'scarce')
        and not any(dungeon in wincon for dungeon in ['Spirit Temple vanilla', 'Spirit Temple mq', 'Shadow Temple vanilla', 'Shadow Temple mq', 'Fire Temple mq', 'Water Temple mq'])):
            if 'Magic Meter' not in always_items:
                named_items.append('Magic Meter')

        if (plando['settings']['item_pool_value'] == 'minimal'
        and plando['settings']['bridge'] == 'open'
        and plando['settings']['shuffle_ganon_bosskey'] in ['remove','vanilla','dungeon','any_dungeon','overworld','keysanity']):
            if 'Bow' not in always_items:
                named_items.append('Bow')

        if (plando['settings']['shuffle_smallkeys'] in ['keysanity']
        and any(trial in trials for trial in ['Light vanilla','Light mq','Water mq'])):
            always_count = always_items.count('Small Key (Ganons Castle)')
            if plando['dungeons']['Ganons Castle'] == 'vanilla':
                for i in range(min(always_count,2), 2):
                    named_items.append('Small Key (Ganons Castle)')
            else:
                for i in range(min(always_count,3), 3):
                    named_items.append('Small Key (Ganons Castle)')
        
        if any(trial in trials for trial in ['Light vanilla','Light mq','Fire vanilla','Fire mq']):
            always_count = always_items.count('Progressive Strength Upgrade')
            for i in range(min(always_count,3), 3):
                named_items.append('Progressive Strength Upgrade')
        
        if (any(trial in trials for trial in ['Spirit vanilla','Spirit mq'])
        and not any(dungeon in wincon for dungeon in ['Spirit Temple vanilla', 'Spirit Temple mq'])):
            if 'Mirror Shield' not in always_items:
                named_items.append('Mirror Shield')
        
        if (any(trial in trials for trial in ['Shadow vanilla','Water vanilla', 'Spirit mq'])
        and not any(dungeon in wincon for dungeon in ['Fire Temple vanilla', 'Fire Temple mq', 'Spirit Temple mq'])):
            if 'Megaton Hammer' not in always_items:
                named_items.append('Megaton Hammer')
        
        if (any(trial in trials for trial in ['Fire vanilla'])
        and not any(dungeon in wincon for dungeon in ['Water Temple vanilla', 'Water Temple mq', 'Spirit Temple mq'])
        and (plando['settings']['gerudo_fortress'] == 'open'
            or plando['settings']['shuffle_overworld_entrances'] == True)):
            always_count = always_items.count('Progressive Hookshot')
            for i in range(min(always_count,2), 2):
                named_items.append('Progressive Hookshot')
        
        if (any(trial in trials for trial in ['Light vanilla'])
        and not any(dungeon in wincon for dungeon in ['Water Temple vanilla', 'Water Temple mq', 'Shadow Temple vanilla', 'Shadow Temple mq', 'Spirit Temple vanilla', 'Spirit Temple mq'])
        and plando['settings']['shuffle_smallkeys'] == 'vanilla'
        and plando['settings']['shuffle_song_items'] == 'any'):
            if 'Zeldas Lullaby' not in always_items:
                named_items.append('Zeldas Lullaby')
        
        if (any(trial in trials for trial in ['Light vanilla'])
        and not any(dungeon in wincon for dungeon in ['Deku Tree mq', 'Dodongos Cavern mq', 'Jabu Jabus Belly mq','Forest Temple mq', 'Fire Temple mq', 'Water Temple mq', 'Shadow Temple mq', 'Spirit Temple mq'])
        and plando['settings']['open_door_of_time'] == True
        and plando['settings']['shuffle_song_items'] == 'any'):
            if 'Song of Time' not in always_items:
                named_items.append('Song of Time')
        
        if any(trial in trials for trial in ['Spirit mq']):
            if 'Fire Arrows' not in always_items:
                named_items.append('Fire Arrows')
        
        if (any(trial in trials for trial in ['Spirit mq'])
        and plando['settings']['bombchus_in_logic'] == True
        and plando['settings']['shuffle_medigoron_carpet_salesman'] == True
        and plando['settings']['item_pool_value'] == 'minimal'):
            if 'Bombchus' not in always_items:
                named_items.append('Bombchus')

    # modify WotH hint exclusions based on settings
    hint_dist['remove_items'].append({'item': 'Gold Skulltula Token', 'types': ['woth', 'sometimes']})
    if any(dungeon in wincon for dungeon in ['Forest Temple vanilla', 'Forest Temple mq']):
        hint_dist['remove_items'].append({'item': 'Small Key (Forest Temple)', 'types': ['woth', 'sometimes']})
        hint_dist['remove_items'].append({'item': 'Boss Key (Forest Temple)', 'types': ['woth', 'sometimes']})
    if any(dungeon in wincon for dungeon in ['Fire Temple vanilla', 'Forest Temple mq']):
        hint_dist['remove_items'].append({'item': 'Small Key (Fire Temple)', 'types': ['woth', 'sometimes']})
        hint_dist['remove_items'].append({'item': 'Boss Key (Fire Temple)', 'types': ['woth', 'sometimes']})
    if any(dungeon in wincon for dungeon in ['Water Temple vanilla', 'Forest Temple mq']):
        hint_dist['remove_items'].append({'item': 'Small Key (Water Temple)', 'types': ['woth', 'sometimes']})
        hint_dist['remove_items'].append({'item': 'Boss Key (Water Temple)', 'types': ['woth', 'sometimes']})
    if any(dungeon in wincon for dungeon in ['Shadow Temple vanilla', 'Forest Temple mq']):
        hint_dist['remove_items'].append({'item': 'Small Key (Shadow Temple)', 'types': ['woth', 'sometimes']})
        hint_dist['remove_items'].append({'item': 'Boss Key (Shadow Temple)', 'types': ['woth', 'sometimes']})
    if any(dungeon in wincon for dungeon in ['Spirit Temple vanilla', 'Forest Temple mq']):
        hint_dist['remove_items'].append({'item': 'Small Key (Spirit Temple)', 'types': ['woth', 'sometimes']})
        hint_dist['remove_items'].append({'item': 'Boss Key (Spirit Temple)', 'types': ['woth', 'sometimes']})
    if plando['settings']['shuffle_song_items'] != 'any':
        hint_dist['remove_items'].append({'item': 'Zeldas Lullaby', 'types': ['woth', 'sometimes']})
    if plando['settings']['item_pool_value'] != 'minimal':
        hint_dist['remove_items'].append({'item': 'Goron Tunic', 'types': ['woth', 'sometimes']})
        hint_dist['remove_items'].append({'item': 'Zora Tunic', 'types': ['woth', 'sometimes']})
    if (plando['settings']['item_pool_value'] != 'minimal'
    and plando['settings']['shopsanity'] == 'off'
    and plando['settings']['shuffle_medigoron_carpet_salesman'] == False):
        hint_dist['remove_items'].append({'item': 'Progressive Wallet', 'types': ['woth', 'sometimes']})

    # Adjust woth count to balance with total hero's path hints
    num_path = float(max(len(named_items),0.75))
    hint_dist['distribution']['woth']['fixed'] = math.floor(2 + (3.9/(num_path ** 0.75)))

    return hint_dist, named_items

# Helpers for conditional always hints
def stones_required_by_settings(world):
    stones = 0
    if world['bridge'] == 'stones':
        stones = max(stones, world['bridge_stones'])
    if world['shuffle_ganon_bosskey'] == 'on_lacs' and world['lacs_condition'] == 'stones':
        stones = max(stones, world['lacs_stones'])
    if world['bridge'] == 'dungeons':
        stones = max(stones, world['bridge_rewards'] - 6)
    if world['shuffle_ganon_bosskey'] == 'on_lacs' and world['lacs_condition'] == 'dungeons':
        stones = max(stones, world['lacs_rewards'] - 6)

    return stones


def medallions_required_by_settings(world):
    medallions = 0
    if world['bridge'] == 'medallions':
        medallions = max(medallions, world['bridge_medallions'])
    if world['shuffle_ganon_bosskey'] == 'on_lacs' and world['lacs_condition'] == 'medallions':
        medallions = max(medallions, world['lacs_medallions'])
    if world['bridge'] == 'dungeons':
        medallions = max(medallions, max(world['bridge_rewards'] - 3, 0))
    if world['shuffle_ganon_bosskey'] == 'on_lacs' and world['lacs_condition'] == 'dungeons':
        medallions = max(medallions, max(world['lacs_rewards'] - 3, 0))

    return medallions


def tokens_required_by_settings(world):
    tokens = 0
    if world['bridge'] == 'tokens':
        tokens = max(tokens, world['bridge_tokens'])
    if world['shuffle_ganon_bosskey'] == 'on_lacs' and world['lacs_condition'] == 'tokens':
        tokens = max(tokens, world['lacs_tokens'])

    return tokens

# This function will probably need some more meat to it. If the user is patching the z64 file in the same directory it will find that
def find_rom_file():
    rom_extensions = ["*.n64", "*.N64", "*.z64", "*.Z64"]
    for ext in rom_extensions:
        rom_filename = glob.glob(os.path.join(os.getcwd(), "**", ext), recursive=True)
        if len(rom_filename) > 0:
            break
    
    # No rom file found
    if len(rom_filename) == 0:
        raise FileNotFoundError("RSL GENERATOR ERROR: NO .n64 or .z64 ROM FILE FOUND.")
    return rom_filename[0]


# Compare weights file to settings list to check for changes to the randomizer settings table
def check_for_setting_changes(weights, randomizer_settings):
    # Find new or changed settings by name
    old_settings = list(set(weights.keys()) - set(randomizer_settings.keys()))
    new_settings = list(set(randomizer_settings.keys()) - set(weights.keys()))
    if len(old_settings) > 0:
        for setting in old_settings:
            print(f"{setting} with options {list(weights[setting].keys())} is no longer a setting.")
            weights.pop(setting)
        print("-------------------------------------")
    if len(new_settings) > 0:
        for setting in new_settings:
            print(f"{setting} with options {list(randomizer_settings[setting].keys())} is a new setting!")
        print("-------------------------------------")

    # Find new or changed options
    for setting in weights.keys():
        # Randomizer has appropriate types for each variable but we store options as strings
        randomizer_settings_strings = set(map(lambda x:x.lower(), map(str, list(randomizer_settings[setting].keys()))))
        old_options = list(set(weights[setting].keys()) - randomizer_settings_strings)
        new_options = list(randomizer_settings_strings - set(weights[setting].keys()))
        if len(old_options) > 0:
            for name in old_options:
                print(f"{setting} option {name} no longer exists.")
        if len(new_options) > 0:
            for name in new_options:
                print(f"{setting} option {name} is new!")


class RandomizerError(Exception):
    pass