# Differences from Random Settings League Branch
This branch is updated to work with a bleeding-edge fork of the randomizer at https://github.com/mracsys/OoT-Randomizer. While best efforts go into preventing bugs, there WILL be more broken seeds on this branch compared to main Dev or Dev-R. If you run into a problem with a seed, DM mracsys#5846 in the Ocarina of Time Randomizer discord. This branch is not endorsed or supported by the OoTR or RSL admins.

## Randomizer Updates
- Support for experimental features identified in the readme at https://github.com/mracsys/OoT-Randomizer, including:
  - Fixed extra 25% Triforce Pieces in Triforce Hunt. Minimal item pool is allowed with TH.
  - Heart bridge and Ganon's Boss Key conditions, weighted the same as skulltula win conditions
  - Goron Pot with Strength trick is disabled
  - Small Key rings are shuffled at 20% chance globally, then 50% chance for each dungeon separately if key rings roll on
  - Mixed entrance pools are now any combination of interior, grotto, dungeon, and overworld pools. Global mixed pools chance is 50%, then 50% chance for each pool type individually
  - Boss shuffle is 50/50 off or full. Age-restricted is never possible.
  - Shuffle freestanding items are 80% off, 8% each for overworld/dungeon only, and 4% everywhere
  - Shuffle pots and crates are 80% off, 8% each for overworld/dungeon only, and 4% everywhere
  - Shuffle beehives is 50/50
  - Shuffle extra frog songs is 20% chance to be on
  - Pre-planted magic beans is 50/50
  - CSMC classic and with new textures is splits the old weights for Size and Textures (30% split to 15% classic and 15% sizes and textures). Pot/crate textures will be on if chest appearance is not vanilla.
  - Invisible chests are 50/50. Learn your MQ locations! Lens is never required in logic for normally visible chests!
  - Ending credits will always autoscroll through the Zelda/Link conversation
  - One Bonk KO is 50/50
  - Ageless items is 50/50 (deku sticks as adult, etc)
  - Blue Fire Arrows is 50/50
  - Ludicrous item pool is about 2.5% chance to be on
- Skulltula tokens can never be way of the hero or path to reward.
- A Song of Time and Ocarina path is enabled for closed door of time starting as child if both are logically reachable. Text in game is `path of time`
- Dual hints are merged but should not be enabled. If you get a double sometimes hint (like both Horseback Archery rewards), report the bug.
- Warp songs are limited to one per hint area

## Random Settings Script Updates
- Randomizer version tracks Dev-M instead of Dev-R
- Failed settings plandos are saved in the `failed_settings` folder before rerolling settings
- Weights in `devM.json` refactored to work with randomizer settings changes
- New `--stress_test` command line option to batch generate seeds. Useful to check for broken settings or settings combinations.
- New conditionals for heart win conditions, fixed Triforce Piece item pool percentage, and pot textures match chest textures

# Random Settings Generator
This script will generate a patch file for The Legend of Zelda Ocarina of Time Randomizer with randomly selected randomizer settings.
This script allows its user to randomize every setting in the Randomizer, not just settings that are natively supported to be randomized.

## Instructions
1. Have Python 3.7 (or newer) installed. This is also a requirement of the randomizer.
2. Download the zip file of the source code from the repository page and unzip anywhere: https://github.com/mracsys/plando-random-settings/archive/refs/heads/master.zip
3. Place your Ocarina of Time 1.0 rom that you wish to use in this directory. It must have the `.z64` file extension.
4. Run the code by double clicking `RandomSettingsGenerator.py` or running `python3 RandomSettingsGenerator.py` (or however you run python files on your system) via the command line.
5. Your patch file will be saved in the `patches` directory.

## Rolling seeds with Weight Overrides
If you are playing a format besides an official Random Setting League race, you may wish to edit the weights. 

1. Put the weights you wish to change into a JSON file in the weights folder
2. Open `RandomSettingsGenerator.py` in a text editor and add the line `global_override_fname = "<override file name>.json"` where you replace `<overworld file name>` with the name of your weights file.

We simplify this process by providing some presets. To use these presets, open `RandomSettingsGenerator.py` in a text editor and remove the `# ` (including the space after the `#`) from...

- Line 10 for multiworld
- Line 11 for DDR
- Line 12 for Beginner (!!! BROKEN ON THIS BRANCH !!!)
- Line 13 for Co-Op (!!! BROKEN ON THIS BRANCH !!!)

## Command Line Interface Options
If you opt to run the script via the command line, you have several options available to you
- `--no_seed`: Generates a plando file in the `data` directory but does not generate a patch file
- `--override <path_to_weights_file>`: Provide a weights override file to be used on top of the default RSL weights. Random settings will be generated using the weights in the override file. Any settings not in the override file will get their weights from the RSL weights. The file is expected to be in the weights directory at the moment.
- `--worldcount <integer>`: The number of worlds to generate for generating multiworld patch files. If this is not given, the default is 1.
- `--stress_test <integer>`: Generate the specified number of seeds. Useful for testing for broken settings combinations. Default value is 1.

# FAQ
> It didn't work! What do I do?

The error message should be logged in `ERRORLOG.TXT` so take a look there. If you cannot figure out what went wrong, head over to the Ocarina of Time Randomizer discord channel (https://discord.gg/ootrandomizer) and ping mracsys#5846 in the #rsl-discussion text channel.


> Do I need to download the randomizer?

Not anymore! Since this code doesn't function without the randomizer and having the wrong version will crash the code, we now manage that for you! This code base is all you will need to get started! Once you have your patch file you can patch with any version of the randomizer you have downloaded, the one we download in the `randomizer` directory or the web generator at https://ootrandomizer.com/