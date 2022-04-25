import sys
import json
from glob import glob
import csv

#for x in range(1000):
#    print('Generating seed %d' % x)
#    main()

spoilers = './failed_settings/'

print("Processing plandos")

fcount = 0
settings = {}
ignore_settings = ['misc_hints','hint_dist_user','allowed_tricks','disabled_locations','starting_items','starting_songs','starting_equipment', 'clearer_hints',
                   'logic_earliest_adult_trade', 'logic_latest_adult_trade', 'no_collectible_hearts', 'credits_autoscroll', 'fast_bunny_hood', 'ocarina_songs',
                   'big_poe_count_random', 'chicken_count_random', 'fast_tokens', 'fast_chests', 'useful_cutscenes', 'skip_some_minigame_phases',
                   'logic_no_night_tokens_without_suns_song', 'dungeon_shortcuts_choice', 'decouple_entrances', 'starting_age', 'trials_random',
                   'one_item_per_dungeon', 'logic_rules']
for filename in glob(spoilers + '*.json'):
    fcount = fcount + 1
    sys.stdout.write("\r%d   " % (fcount))
    with open(filename) as inf:
        sp = json.load(inf)
        for s, v in sp['settings'].items():
            if s not in ignore_settings:
                key = str(s) + ':' + str(v)
                if key in settings:
                    settings[key] += 1
                else:
                    settings[key] = 1

sorted_settings = {k: v for k, v in sorted(settings.items(), key=lambda item: item[1]) if v > 10}

print('Done')
for s, c in sorted_settings.items():
    print(s, ':', c)