"""Compile a list of hints based on the settings."""
import random
from re import U

from randomizer.Enums.Events import Events
from randomizer.Enums.HintType import HintType
from randomizer.Enums.Items import Items
from randomizer.Enums.Kongs import Kongs
from randomizer.Enums.Levels import Levels
from randomizer.Enums.Regions import Regions
from randomizer.Enums.Transitions import Transitions
from randomizer.Lists.Item import ItemList, NameFromKong
from randomizer.Lists.MapsAndExits import GetMapId
from randomizer.Lists.ShufflableExit import ShufflableExits
from randomizer.Lists.WrinklyHints import HintLocation, hints
from randomizer.Patching.UpdateHints import UpdateHint, updateRandomHint
from randomizer.Spoiler import Spoiler


class Hint:
    """Hint object for Wrinkly hint text."""

    def __init__(
        self,
        *,
        hint="",
        important=True,
        priority=1,
        kongs=[Kongs.donkey, Kongs.diddy, Kongs.lanky, Kongs.tiny, Kongs.chunky],
        repeats=1,
        base=False,
        keywords=[],
        permitted_levels=[Levels.JungleJapes, Levels.AngryAztec, Levels.FranticFactory, Levels.GloomyGalleon, Levels.FungiForest, Levels.CrystalCaves, Levels.CreepyCastle],
        subtype="joke",
        joke=False,
        joke_defined=False,
    ):
        """Create wrinkly hint text object."""
        self.kongs = kongs.copy()
        self.hint = hint
        self.important = important
        self.priority = priority
        self.repeats = repeats
        self.base = base
        self.used = False
        self.was_important = important
        self.original_repeats = repeats
        self.original_priority = priority
        self.keywords = keywords.copy()
        self.permitted_levels = permitted_levels.copy()
        self.subtype = subtype
        self.joke = base
        if joke_defined:
            self.joke = joke

    def use_hint(self):
        """Set hint as used."""
        if self.repeats == 1:
            self.used = True
            self.repeats = 0
        else:
            self.repeats -= 1
            self.priority += 1

    def downgrade(self):
        """Downgrade hint status."""
        self.important = False


class MoveInfo:
    """Move Info for Wrinkly hint text."""

    def __init__(self, *, name="", kong="", move_type="", move_level=0, important=False):
        """Create move info object."""
        self.name = name
        self.kong = kong
        move_types = ["special", "slam", "gun", "ammobelt", "instrument"]
        encoded_move_type = move_types.index(move_type)
        self.move_type = encoded_move_type
        self.move_level = move_level
        self.important = important
        ref_kong = kong
        if ref_kong == Kongs.any:
            ref_kong = Kongs.donkey
        self.item_key = (encoded_move_type << 5) | ((move_level - 1) << 3) | ref_kong


hint_list = [
    Hint(hint="Did you know - Donkey Kong officially features in Donkey Kong 64.", important=False, base=True),
    Hint(hint="Fungi Forest was originally intended to be in the other N64 Rareware title, Banjo Kazooie.", important=False, base=True),
    Hint(hint="Holding up-left when trapped inside of a trap bubble will break you out of it without spinning your stick.", important=False, base=True),
    Hint(hint="Tiny Kong is the youngest sister of Dixie Kong.", important=False, base=True),
    Hint(hint="Mornin.", important=False, base=True),
    Hint(hint="Lanky Kong is the only kong with no canonical relation to the main Kong family tree.", important=False, base=True),
    Hint(hint="Despite the line in the DK Rap stating otherwise, Chunky is the kong who can jump highest in DK64.", important=False, base=True),
    Hint(hint="Despite the line in the DK Rap stating otherwise, Tiny is one of the two slowest kongs in DK64.", important=False, base=True),
    Hint(hint="Candy Kong does not appear in Jungle Japes or Fungi Forest.", important=False, base=True),
    Hint(hint="If you fail the twelfth round of K. Rool, the game will dictate that K. Rool is victorious and end the fight.", important=False, base=True),
    Hint(hint="Donkey Kong 64 Randomizer started as a LUA Script in early 2019, evolving into a ROM Hack in 2021.", important=False, base=True),
    Hint(hint="The maximum in-game time that the vanilla file screen time can display is 1165 hours and 5 minutes.", important=False, base=True),
    Hint(hint="Chunky Kong is the brother of Kiddy Kong.", important=False, base=True),
    Hint(hint="Fungi Forest contains mushrooms.", important=False, base=True),
    Hint(hint="Igloos can be found in Crystal Caves.", important=False, base=True),
    Hint(hint="Frantic Factory has multiple floors where things can be found.", important=False, base=True),
    Hint(hint="Angry Aztec has so much sand, it's even in the wind.", important=False, base=True),
    Hint(hint="DK Isles does not have a key.", important=False, base=True),
    Hint(hint="You can find a rabbit in Fungi Forest and in Crystal Caves.", important=False, base=True),
    Hint(hint="You can find a beetle in Angry Aztec and in Crystal Caves.", important=False, base=True),
    Hint(hint="You can find a vulture in Angry Aztec.", important=False, base=True),
    Hint(hint="You can find an owl in Fungi Forest.", important=False, base=True),
    Hint(hint="To buy moves, you will need coins.", important=False, base=True),
    Hint(hint="You can change the music and sound effects volume in the sound settings on the main menu.", important=False, base=True),
    Hint(hint="Coin Hoard is a Monkey Smash game mode where players compete to collect the most coins.", important=False, base=True),
    Hint(hint="Capture Pad is a Monkey Smash game mode where players attempt to capture pads in different corners of the arena.", important=False, base=True),
    Hint(hint="I have nothing to say to you.", important=False, base=True),
    Hint(hint="I had something to tell you, but I forgot what it is.", important=False, base=True),
    Hint(hint="I don't know anything.", important=False, base=True),
    Hint(hint="I'm as lost as you are. Good luck!", important=False, base=True),
    Hint(hint="Wrinkly? Never heard of him.", important=False, base=True),
    Hint(
        hint="This is it. The peak of all randomizers. No other randomizer exists besides DK64 Randomizer where you can listen to the dk rap in its natural habitat while freeing Chunky Kong in Jungle Japes.",
        important=False,
        base=True,
    ),
    Hint(hint="Why do they call it oven when you of in the cold food of out hot eat the food?", important=False, base=True),
    Hint(hint="Wanna become famous? Buy followers, coconuts and donks at DK64Randomizer (DK64Randomizer . com)!", important=False, base=True),
    Hint(hint="What you gonna do, SpikeVegeta?", important=False, base=True),
    Hint(hint="You don't care? Just give it to me? Okay, here it is.", important=False, base=True),
    Hint(hint="Rumor has it this game was developed in a cave with only a box of scraps!", important=False, base=True),
    Hint(hint="If you backflip right before Chunky punches K. Rool, you must go into first person camera to face him before the punch.", important=False, base=True),
    Hint(hint="The barrier to Hideout Helm can be cleared by obtaining 801 Golden Bananas. It can also be cleared with fewer than that.", important=False, base=True),
]

kong_list = ["Donkey", "Diddy", "Lanky", "Tiny", "Chunky"]

kong_cryptic = [
    [
        "The kong who is bigger, faster and potentially stronger too",
        "The kong who fires in spurts",
        "The kong with a tie",
        "The kong who slaps their instrument to the jungle beat",
    ],
    [
        "The kong who can fly real high",
        "The kong who features in the first two Donkey Kong Country games",
        "The kong who wants to see red",
        "The kong who frees the only female playable kong",
    ],
    [
        "The kong who inflates like a balloon, just like a balloon",
        "The kong who waddles in his overalls",
        "The kong who has a cold race with an insect",
        "The kong who lacks style, grace but not a funny face",
    ],
    ["The kong who likes jazz", "The kong who shoots K. Rool's tiny toes", "The kong who has ammo that is light as a feather", "The kong who can shrink in size"],
    [
        "The kong who is one hell of a guy",
        "The kong who can pick up boulders",
        "The kong who fights a blocky boss",
        "The kong who bows down to a dragonfly",
    ],
]

all_levels = [Levels.JungleJapes, Levels.AngryAztec, Levels.FranticFactory, Levels.GloomyGalleon, Levels.FungiForest, Levels.CrystalCaves, Levels.CreepyCastle]
level_list = ["Jungle Japes", "Angry Aztec", "Frantic Factory", "Gloomy Galleon", "Fungi Forest", "Crystal Caves", "Creepy Castle", "Hideout Helm"]
level_list_isles = ["Jungle Japes", "Angry Aztec", "Frantic Factory", "Gloomy Galleon", "Fungi Forest", "Crystal Caves", "Creepy Castle", "DK Isles"]

level_cryptic = [
    [
        "The level with a localized storm",
        "The level with a dirt mountain",
        "The level which has two retailers and no race",
    ],
    ["The level with four vases", "The level with two kongs cages", "The level with a spinning totem"],
    ["The level with a toy production facility", "The level with a tower of blocks", "The level with a game from 1981", "The level where you need two quarters to play"],
    ["The level with the most water", "The level where you free a water dweller", "The level with stacks of gold"],
    ["The level with only two retailers and two races", "The level where night can be acquired at will", "The level with a nocturnal tree dweller"],
    [
        "The level with two inches of water",
        "The level with two ice shields",
        "The level with an Ice Tomato",
    ],
    ["The level with battlements", "The level with a dungeon, ballroom and a library", "The level with drawbridge and a moat"],
    ["The timed level", "The level with no boss", "The level with no small bananas"],
]
level_cryptic_isles = level_cryptic.copy()
level_cryptic_isles.remove(level_cryptic_isles[-1])
level_cryptic_isles.append(["The hub world", "The world with DK's ugly mug on it", "The world with only a Cranky's Lab and Snide's HQ in it"])

shop_owners = ["Cranky", "Funky", "Candy"]
shop_cryptic = [
    [
        "The shop owner with a walking stick",
        "The shop owner who is old",
        "The shop owner who is persistently grumpy",
        "The shop owner who resides near your Treehouse",
    ],
    [
        "The shop owner who has an armory",
        "The shop owner who has a banana on his shop",
        "The shop owner with sunglasses",
        "The shop owner who calls everyone Dude",
    ],
    ["The shop owner who is flirtatious", "The shop owner who is not present in Fungi Forest", "The shop owner who is not present in Jungle Japes", "The shop owner with blonde hair"],
]

moves_data = [
    # Commented out logic sections are saved if we need to revert to the old hint system
    # Donkey
    MoveInfo(name="Baboon Blast", move_level=1, move_type="special", kong=Kongs.donkey),
    MoveInfo(name="Strong Kong", move_level=2, move_type="special", kong=Kongs.donkey),
    MoveInfo(name="Gorilla Grab", move_level=3, move_type="special", kong=Kongs.donkey),
    # Diddy
    MoveInfo(name="Chimpy Charge", move_level=1, move_type="special", kong=Kongs.diddy),
    MoveInfo(name="Rocketbarrel Boost", move_level=2, move_type="special", kong=Kongs.diddy, important=True),  # (spoiler.settings.krool_diddy or spoiler.settings.helm_diddy)),
    MoveInfo(name="Simian Spring", move_level=3, move_type="special", kong=Kongs.diddy),
    # Lanky
    MoveInfo(name="Orangstand", move_level=1, move_type="special", kong=Kongs.lanky),
    MoveInfo(name="Baboon Balloon", move_level=2, move_type="special", kong=Kongs.lanky),
    MoveInfo(name="Orangstand Sprint", move_level=3, move_type="special", kong=Kongs.lanky),
    # Tiny
    MoveInfo(name="Mini Monkey", move_level=1, move_type="special", kong=Kongs.tiny, important=True),  # spoiler.settings.krool_tiny),
    MoveInfo(name="Ponytail Twirl", move_level=2, move_type="special", kong=Kongs.tiny),
    MoveInfo(name="Monkeyport", move_level=3, move_type="special", kong=Kongs.tiny, important=True),
    # Chunky
    MoveInfo(name="Hunky Chunky", move_level=1, move_type="special", kong=Kongs.chunky, important=True),  # spoiler.settings.krool_chunky),
    MoveInfo(name="Primate Punch", move_level=2, move_type="special", kong=Kongs.chunky, important=True),  # spoiler.settings.krool_chunky),
    MoveInfo(name="Gorilla Gone", move_level=3, move_type="special", kong=Kongs.chunky, important=True),  # spoiler.settings.krool_chunky),
    # Slam
    MoveInfo(name="Slam Upgrade", move_level=1, move_type="slam", kong=Kongs.any),
    MoveInfo(name="Slam Upgrade", move_level=2, move_type="slam", kong=Kongs.any),
    MoveInfo(name="Slam Upgrade", move_level=3, move_type="slam", kong=Kongs.any),
    # Guns
    MoveInfo(name="Coconut Shooter", move_level=1, move_type="gun", kong=Kongs.donkey, important=True),
    MoveInfo(name="Peanut Popguns", move_level=1, move_type="gun", kong=Kongs.diddy, important=True),  # spoiler.settings.krool_diddy),
    MoveInfo(name="Grape Shooter", move_level=1, move_type="gun", kong=Kongs.lanky),
    MoveInfo(name="Feather Bow", move_level=1, move_type="gun", kong=Kongs.tiny, important=True),  # spoiler.settings.krool_tiny),
    MoveInfo(name="Pineapple Launcher", move_level=1, move_type="gun", kong=Kongs.chunky),
    # Gun Upgrades
    MoveInfo(name="Homing Ammo", move_level=2, move_type="gun", kong=Kongs.any),
    MoveInfo(name="Sniper Scope", move_level=3, move_type="gun", kong=Kongs.any),
    # Ammo Belt
    MoveInfo(name="Ammo Belt Upgrade", move_level=1, move_type="ammobelt", kong=Kongs.any),
    MoveInfo(name="Ammo Belt Upgrade", move_level=2, move_type="ammobelt", kong=Kongs.any),
    # Instruments
    MoveInfo(name="Bongo Blast", move_level=1, move_type="instrument", kong=Kongs.donkey, important=True),  # spoiler.settings.helm_donkey),
    MoveInfo(name="Guitar Gazump", move_level=1, move_type="instrument", kong=Kongs.diddy, important=True),  # spoiler.settings.helm_diddy),
    MoveInfo(name="Trombone Tremor", move_level=1, move_type="instrument", kong=Kongs.lanky, important=True),  # (spoiler.settings.helm_lanky or spoiler.settings.krool_lanky)),
    MoveInfo(name="Saxophone Slam", move_level=1, move_type="instrument", kong=Kongs.tiny, important=True),  # spoiler.settings.helm_tiny),
    MoveInfo(name="Triangle Trample", move_level=1, move_type="instrument", kong=Kongs.chunky, important=True),  # spoiler.settings.helm_chunky),
    # Instrument Upgrades
    MoveInfo(name="Instrument Upgrade", move_level=2, move_type="instrument", kong=Kongs.any),
    MoveInfo(name="Instrument Upgrade", move_level=3, move_type="instrument", kong=Kongs.any),
    MoveInfo(name="Instrument Upgrade", move_level=4, move_type="instrument", kong=Kongs.any),
]

kong_placement_levels = [
    {
        "name": "Jungle Japes",
        "level": 0,
    },
    {
        "name": "Llama Temple",
        "level": 1,
    },
    {
        "name": "Tiny Temple",
        "level": 1,
    },
    {
        "name": "Frantic Factory",
        "level": 2,
    },
]


# Hint distribution that will be adjusted based on settings
# These values are "if this is an option, then you must have at least X of this hint"
hint_distribution = {
    HintType.Joke: 1,
    HintType.KRoolOrder: 2,
    HintType.HelmOrder: 2,  # must have one on the path
    HintType.FullShop: 8,
    HintType.MoveLocation: 7,  # must be placed before you can buy the move
    HintType.DirtPatch: 0,
    HintType.BLocker: 3,  # must be placed on the path and before the level they hint
    HintType.TroffNScoff: 0,
    HintType.KongLocation: 2,  # must be placed before you find them and placed in a door of a free kong
    HintType.MedalsRequired: 1,
    HintType.Entrance: 8,
}
HINT_CAP = 35  # There are this many total slots for hints


def compileHints(spoiler: Spoiler):
    """Create a hint distribution, generate buff hints, and place them in locations."""
    # Determine what hint types are valid for these settings
    valid_types = [HintType.Joke]
    if spoiler.settings.krool_phase_count < 5:
        valid_types.append(HintType.KRoolOrder)
    if spoiler.settings.helm_setting != "skip_all" and spoiler.settings.helm_phase_count < 5:
        valid_types.append(HintType.HelmOrder)
    if not spoiler.settings.unlock_all_moves and spoiler.settings.move_rando != "off":
        valid_types.append(HintType.FullShop)
        valid_types.append(HintType.MoveLocation)
    if spoiler.settings.random_patches:
        valid_types.append(HintType.DirtPatch)
    if spoiler.settings.randomize_blocker_required_amounts:
        valid_types.append(HintType.BLocker)
    if spoiler.settings.randomize_cb_required_amounts:
        valid_types.append(HintType.TroffNScoff)
    if spoiler.settings.kong_rando:
        valid_types.append(HintType.KongLocation)
    if spoiler.settings.coin_door_open == "need_both" or spoiler.settings.coin_door_open == "need_rw":
        valid_types.append(HintType.MedalsRequired)
    if spoiler.settings.shuffle_loading_zones == "all":
        # In entrance rando, we care more about T&S than B. Locker
        temp = hint_distribution[HintType.BLocker]
        hint_distribution[HintType.BLocker] = max(1, hint_distribution[HintType.TroffNScoff])  # Always want a helm hint in there
        hint_distribution[HintType.TroffNScoff] = temp
        valid_types.append(HintType.Entrance)

    # Make sure we have exactly 35 hints placed
    hint_count = 0
    for type in hint_distribution:
        if type in valid_types:
            hint_count += hint_distribution[type]
        else:
            hint_distribution[type] = 0
    # Fill extra hints if we need them
    while hint_count < HINT_CAP:
        filler_type = random.choice(valid_types)
        hint_distribution[filler_type] += 1
        hint_count += 1
    # Remove random hints if we went over the cap
    while hint_count > HINT_CAP:
        removed_type = random.choice(valid_types)
        if hint_distribution[removed_type] > 0:
            hint_distribution[removed_type] -= 1
            hint_count -= 1
    # In level order (or vanilla) progression, there are hints that we want to be in the player's path
    level_order_matters = not spoiler.settings.no_logic and spoiler.settings.shuffle_loading_zones != "all"
    progression_hint_locations = None
    if level_order_matters:
        # These hint locations are *much* more likely to be seen, as they'll be available as players pass through lobbies on their first visit
        progression_hint_locations = []
        for level in all_levels:
            for kong in spoiler.settings.owned_kongs_by_level[level]:
                # If we don't have DK + Grab then these hints are skipped basically every time so they're not on the player's path
                if (
                    level == Levels.FranticFactory
                    and kong not in [Kongs.donkey, Kongs.chunky]
                    and (Kongs.donkey not in spoiler.settings.owned_kongs_by_level[level] or Items.GorillaGrab not in spoiler.settings.owned_moves_by_level[level])
                ):
                    continue
                if (
                    level == Levels.FungiForest
                    and kong is not Kongs.chunky
                    and (Kongs.donkey not in spoiler.settings.owned_kongs_by_level[level] or Items.GorillaGrab not in spoiler.settings.owned_moves_by_level[level])
                ):
                    continue
                # Caves Diddy needs a whole suite of moves to see this hint
                if (
                    level == Levels.CrystalCaves
                    and kong is Kongs.diddy
                    and (
                        Kongs.chunky not in spoiler.settings.owned_kongs_by_level[level]
                        or Items.PrimatePunch not in spoiler.settings.owned_moves_by_level[level]
                        or Items.RocketbarrelBoost not in spoiler.settings.owned_moves_by_level[level]
                    )
                ):
                    continue
                # Everyone else in Caves still needs Chunky + Punch
                if level == Levels.CrystalCaves and (Kongs.chunky not in spoiler.settings.owned_kongs_by_level[level] or Items.PrimatePunch not in spoiler.settings.owned_moves_by_level[level]):
                    continue
                # Aztec Chunky also needs Tiny + Feather + Hunky Chunky
                if (
                    level == Levels.AngryAztec
                    and kong is Kongs.chunky
                    and (
                        Kongs.tiny not in spoiler.settings.owned_kongs_by_level[level]
                        or Items.Feather not in spoiler.settings.owned_moves_by_level[level]
                        or Items.HunkyChunky not in spoiler.settings.owned_moves_by_level[level]
                    )
                ):
                    continue
                hint_for_location = [hint for hint in hints if hint.level == level and hint.kong == kong][0]  # Should only match one
                progression_hint_locations.append(hint_for_location)

    # Now place hints by type from most-restrictive to least restrictive. Usually anything we want on the player's path should get placed first
    # Kongs should be hinted before they're available and should only be hinted to free Kongs, making them very restrictive
    hinted_kongs = []
    placed_kong_hints = 0
    while placed_kong_hints < hint_distribution[HintType.KongLocation]:
        kong_map = random.choice(kong_placement_levels)
        kong_index = spoiler.shuffled_kong_placement[kong_map["name"]]["locked"]["kong"]
        free_kong = spoiler.shuffled_kong_placement[kong_map["name"]]["puzzle"]["kong"]
        level_index = kong_map["level"]

        level_restriction = None
        # If this is the first time we're hinting this kong, attempt to put it in an earlier level (regardless of whether or not you can read it)
        # This only matters if level order matters
        if level_order_matters and kong_index not in hinted_kongs:
            level_restriction = [level for level in all_levels if spoiler.settings.EntryGBs[level] <= spoiler.settings.EntryGBs[kong_map["level"]]]
        # This list of free kongs is sometimes only a subset of the correct list. A more precise list could be calculated but it would be slow.
        free_kongs = spoiler.settings.starting_kong_list.copy()
        free_kongs.append(free_kong)
        hint_location = getRandomHintLocation(kongs=free_kongs, levels=level_restriction)
        # If this fails, it's extremely likely there's already a very useful hint in the very few spot(s) this could be
        if hint_location is None:
            if level_restriction is not None:
                # Can't make it too easy on em - put this hint in any hint door for these kongs
                hint_location = getRandomHintLocation(kongs=free_kongs)
            else:
                # In the unfathomably rare world where our freeing kong is out of hint doors, replace this hint with a joke hint
                # When I say unfathomably, I'm talking "you start with all moves and free B. Lockers but only 4 Kongs"
                hint_distribution[HintType.Joke] += 1  # Adding meme hints to meme seeds is just thematic at this point
                hint_distribution[HintType.KongLocation] -= 1
                continue

        freeing_kong_name = kong_list[free_kong]
        if spoiler.settings.wrinkly_hints == "cryptic":
            if not kong_index == Kongs.any:
                kong_name = random.choice(kong_cryptic[kong_index])
            level_name = random.choice(level_cryptic[level_index])
        else:
            if not kong_index == Kongs.any:
                kong_name = kong_list[kong_index]
            level_name = level_list[level_index]
        unlock_verb = "frees"
        if kong_index == Kongs.any:
            unlock_verb = "accesses"
            kong_name = "an empty cage"
        message = f"{freeing_kong_name} {unlock_verb} {kong_name} in {level_name}."
        hinted_kongs.append(kong_index)
        hint_location.hint_type = HintType.KongLocation
        UpdateHint(hint_location, message)
        placed_kong_hints += 1

    # B. Locker hints need to be on the player's path to be useful
    hinted_blocker_combos = []
    for i in range(hint_distribution[HintType.BLocker]):
        # If there's a specific level order to the seed, place the hints on the player's path so these hints aren't useless
        location_restriction = None
        if level_order_matters:
            location_restriction = progression_hint_locations
        # Pick random hint locations until we get one that can hint a future level
        hintable_levels = []
        while len(hintable_levels) == 0:
            hint_location = getRandomHintLocation(location_list=location_restriction)
            # Only hint levels more expensive than the current one AND we care about level order AND this hint's lobby doesn't already hint this level
            hintable_levels = [
                level
                for level in all_levels
                if (not level_order_matters or spoiler.settings.EntryGBs[level] > spoiler.settings.EntryGBs[hint_location.level]) and (hint_location.level, level) not in hinted_blocker_combos
            ]
            # If Helm is random, always place at least one Helm hint - this helps non-maximized Helm seeds and slightly nerfs this category of hints otherwise.
            if not spoiler.settings.maximize_helm_blocker:
                if i == 0:
                    hintable_levels = [Levels.HideoutHelm]
                else:
                    hintable_levels.append(Levels.HideoutHelm)
        hinted_level = random.choice(hintable_levels)
        hinted_blocker_combos.append((hint_location.level, hinted_level))
        level_name = level_list[hinted_level]
        if spoiler.settings.wrinkly_hints == "cryptic":
            level_name = random.choice(level_cryptic[hinted_level])
        message = f"The barrier to {level_name} can be cleared by obtaining {spoiler.settings.EntryGBs[hinted_level]} Golden Bananas."
        hint_location.hint_type = HintType.BLocker
        UpdateHint(hint_location, message)

    # At least one Helm Order hint should be placed on the progression path
    helm_hint_on_path = False
    for i in range(hint_distribution[HintType.HelmOrder]):
        location_restriction = None
        # If we haven't randomly placed one on the path yet, force the last one to be on the player's path
        if level_order_matters and not helm_hint_on_path and i == hint_distribution[HintType.HelmOrder] - 1:
            location_restriction = progression_hint_locations
        hint_location = getRandomHintLocation(location_list=location_restriction)
        # If this one is on the player's path, then we've satisfied the restriction
        if progression_hint_locations is None or hint_location in progression_hint_locations:
            helm_hint_on_path = True

        default_order = [Kongs.donkey, Kongs.chunky, Kongs.tiny, Kongs.lanky, Kongs.diddy]
        helm_order = []
        for room in spoiler.settings.helm_order:
            helm_order.append(default_order[room])
        associated_hint = f"Helm Room order is {NameFromKong(helm_order[0])}"
        for x in range(len(helm_order)):
            if x != 0:
                associated_hint += f" then {NameFromKong(helm_order[x])}"
        hint_location.hint_type = HintType.HelmOrder
        UpdateHint(hint_location, associated_hint)

    # Moves should be hinted before they're available
    moves_hinted_and_lobbies = {}  # Avoid putting a hint for the same move in the same lobby twice
    locationless_move_keys = []  # Keep track of moves we know have run out of locations to hint
    placed_move_hints = 0
    while placed_move_hints < hint_distribution[HintType.MoveLocation]:
        # First pick a random item from the WOTH - valid items are moves (not kongs) and must not be one of our known impossible-to-place items
        woth_item = None
        valid_woth_item_locations = [loc for loc in spoiler.woth.keys() if loc not in locationless_move_keys and any(shopName in loc for shopName in shop_owners)]
        if len(valid_woth_item_locations) == 0:
            # In the OBSCENELY rare case that we can't hint any more moves, then we'll settle for joke hints
            # This would only happen in the case where all moves are in early worlds, coins are plentiful, and the distribution here is insanely high
            # Your punishment for these extreme settings is more joke hints
            hint_diff = hint_distribution[HintType.MoveLocation] - placed_move_hints
            hint_distribution[HintType.Joke] += hint_diff
            hint_distribution[HintType.MoveLocation] -= hint_diff
            break
        woth_item_location = random.choice(valid_woth_item_locations)
        # This gets the level of the location by matching names which is very bad but faster than the alternative of looping through every location for the item
        # This matches "Caves", "Castl", "Isles", etc. and should only match one item
        # This could be Isles, which has no hints, so we gotta be careful with this index
        index_of_level_with_location = level_list_isles.index([name for name in level_list_isles if woth_item_location[:5] in name][0])
        # Now we need to find the Item object associated with this name
        for item_id in ItemList:
            if ItemList[item_id].name == spoiler.woth[woth_item_location]:
                woth_item = item_id
                break
        # Determine what levels are before this level
        hintable_levels = all_levels.copy()
        # Only if we care about the level order do we restrict these hints' locations
        if level_order_matters:
            # Determine a sorted order of levels by B. Lockers - this may not be the actual "progression" but it'll do for now
            levels_in_order = all_levels.copy()
            levels_in_order.sort(key=lambda l: spoiler.settings.EntryGBs[l])

            hintable_levels = []
            cheapest_levels_with_item = []
            # Go through our levels in progression order
            for level in levels_in_order:
                # If the level doesn't have access to the move, we can hint it in the lobby
                if woth_item not in spoiler.settings.owned_moves_by_level[level]:
                    hintable_levels.append(level)
                # We hit our first level that has logical access to the move, time to get to work
                else:
                    # Find all levels with B. Lockers of the same price as this one
                    cheapest_levels_candidates = [
                        candidate for candidate in all_levels if spoiler.settings.EntryGBs[candidate] == spoiler.settings.EntryGBs[level] and candidate not in hintable_levels
                    ]
                    # If there's only one candidate then this is the level that gives logical access to the move, so we're done
                    # If it's an Isles shop we're hinting or hard level progression we don't need to pare down the lobby options, so we're done
                    if len(cheapest_levels_candidates) == 1 or index_of_level_with_location >= 7:  # or hard level progression (TBD)
                        cheapest_levels_with_item = cheapest_levels_candidates
                    # In normal level progression, we need to remove levels that are beyond the shop's level
                    else:
                        # Determine the level order of the shop
                        level_order_of_shop_location = -1
                        for order in spoiler.settings.level_order:
                            if index_of_level_with_location == spoiler.settings.level_order[order]:
                                level_order_of_shop_location = order
                                break
                        # For each of our cheap levels
                        for cheap_level in cheapest_levels_candidates:
                            # Get the level order of this cheap level (will only match one)
                            cheap_level_order = [o for o in spoiler.settings.level_order if cheap_level == spoiler.settings.level_order[o]][0]
                            # If this level is before our shop's level in the order, it can have the hint
                            if cheap_level_order <= level_order_of_shop_location:
                                cheapest_levels_with_item.append(cheap_level)
                    break
            # We can also hint the cheapest levels that have access to this item
            # This manifests in the form of finding a hint in Japes lobby for Pineapple in an earlier level if Chunky is unlocked in Japes
            hintable_levels.extend(cheapest_levels_with_item)
        # Don't place the same hint in the same lobby
        if woth_item in moves_hinted_and_lobbies.keys():
            for lobby_with_this_hint in moves_hinted_and_lobbies[woth_item]:
                if lobby_with_this_hint in hintable_levels:
                    hintable_levels.remove(lobby_with_this_hint)
        else:
            moves_hinted_and_lobbies[woth_item] = []

        hint_location = getRandomHintLocation(levels=hintable_levels, move_name=spoiler.woth[woth_item_location])
        # If we've been too restrictive and ran out of spots for this move to be hinted in, don't bother trying to fix it. Just pick another move
        if hint_location is None:
            locationless_move_keys.append(woth_item_location)
            continue

        shop_level = level_list_isles[index_of_level_with_location]
        if spoiler.settings.wrinkly_hints == "cryptic":
            shop_level = random.choice(level_cryptic_isles[index_of_level_with_location])
        shop_name = [name for name in shop_owners if name in woth_item_location][0]  # Should only match one
        message = f"On the Way of the Hoard, {ItemList[woth_item].name} is bought from {shop_name} in {shop_level}."
        moves_hinted_and_lobbies[woth_item].append(hint_location.level)
        hint_location.hint_type = HintType.MoveLocation
        UpdateHint(hint_location, message)
        placed_move_hints += 1

    # For T&S hints, we want to hint levels after the hint location and only levels that we don't start with keys for
    if hint_distribution[HintType.TroffNScoff] > 0:
        # Determine what levels have incomplete T&S
        levels_with_tns = []
        for keyEvent in spoiler.settings.krool_keys_required:
            if keyEvent == Events.JapesKeyTurnedIn:
                levels_with_tns.append(spoiler.settings.level_order[1])
            if keyEvent == Events.AztecKeyTurnedIn:
                levels_with_tns.append(spoiler.settings.level_order[2])
            if keyEvent == Events.FactoryKeyTurnedIn:
                levels_with_tns.append(spoiler.settings.level_order[3])
            if keyEvent == Events.GalleonKeyTurnedIn:
                levels_with_tns.append(spoiler.settings.level_order[4])
            if keyEvent == Events.ForestKeyTurnedIn:
                levels_with_tns.append(spoiler.settings.level_order[5])
            if keyEvent == Events.CavesKeyTurnedIn:
                levels_with_tns.append(spoiler.settings.level_order[6])
            if keyEvent == Events.CastleKeyTurnedIn:
                levels_with_tns.append(spoiler.settings.level_order[7])
        for i in range(hint_distribution[HintType.TroffNScoff]):
            # Make sure the location we randomly pick either is a level or is before a level that has a T&S
            future_tns_levels = []
            while not any(future_tns_levels):
                hint_location = getRandomHintLocation()
                future_tns_levels = [
                    level for level in all_levels if level in levels_with_tns and (not level_order_matters or spoiler.settings.EntryGBs[level] >= spoiler.settings.EntryGBs[hint_location.level])
                ]
            hinted_level = random.choice(future_tns_levels)
            level_name = level_list[hinted_level]
            if spoiler.settings.wrinkly_hints == "cryptic":
                level_name = random.choice(level_cryptic[hinted_level])
            count = spoiler.settings.BossBananas[hinted_level]
            cb_name = "Small Bananas"
            if count == 1:
                cb_name = "Small Banana"
            message = f"The barrier to the boss in {level_name} can be cleared by obtaining {count} {cb_name}."
            hint_location.hint_type = HintType.TroffNScoff
            UpdateHint(hint_location, message)

    # Entrance hints are tricky, there's some requirements we must hit:
    # We must hint each of Japes, Aztec, and Factory at least once
    # The rest of the hints are tied to a variety of important locations
    if hint_distribution[HintType.Entrance] > 0:
        criticalJapesRegions = [
            Regions.JungleJapesMain,
            Regions.JapesBeyondFeatherGate,
            Regions.TinyHive,
            Regions.JapesLankyCave,
            Regions.Mine,
        ]
        criticalAztecRegions = [
            Regions.AngryAztecStart,
            Regions.AngryAztecMain,
        ]
        criticalFactoryRegions = [
            Regions.FranticFactoryStart,
            Regions.ChunkyRoomPlatform,
            Regions.PowerHut,
            Regions.BeyondHatch,
            Regions.InsideCore,
        ]
        usefulRegions = [
            criticalJapesRegions,
            criticalAztecRegions,
            criticalFactoryRegions,
            [Regions.BananaFairyRoom],
            [Regions.TrainingGrounds],
            [
                Regions.GloomyGalleonStart,
                Regions.LighthouseArea,
                Regions.Shipyard,
            ],
            [
                Regions.FungiForestStart,
                Regions.GiantMushroomArea,
                Regions.MushroomLowerExterior,
                Regions.MushroomNightExterior,
                Regions.MushroomUpperExterior,
                Regions.MillArea,
            ],
            [
                Regions.CrystalCavesMain,
                Regions.IglooArea,
                Regions.CabinArea,
            ],
            [
                Regions.CreepyCastleMain,
                Regions.CastleWaterfall,
            ],
            [Regions.LowerCave],
            [Regions.UpperCave],
        ]
        for i in range(hint_distribution[HintType.Entrance]):
            message = ""
            # Always put in at least one Japes hint
            if i == 0:
                japesHintEntrances = [entrance for entrance, back in spoiler.shuffled_exit_data.items() if back.regionId in criticalJapesRegions]
                random.shuffle(japesHintEntrances)
                japesHintPlaced = False
                while len(japesHintEntrances) > 0:
                    japesHinted = japesHintEntrances.pop()
                    message = TryCreatingLoadingZoneHint(spoiler, japesHinted, criticalJapesRegions)
                    if message != "":
                        japesHintPlaced = True
                        break
                if not japesHintPlaced:
                    print("Japes LZR hint unable to be placed!")
            # Always put in at least one Aztec hint
            elif i == 1:
                aztecHintEntrances = [entrance for entrance, back in spoiler.shuffled_exit_data.items() if back.regionId in criticalAztecRegions]
                random.shuffle(aztecHintEntrances)
                aztecHintPlaced = False
                while len(aztecHintEntrances) > 0:
                    aztecHinted = aztecHintEntrances.pop()
                    message = TryCreatingLoadingZoneHint(spoiler, aztecHinted, criticalAztecRegions)
                    if message != "":
                        aztecHintPlaced = True
                        break
                if not aztecHintPlaced:
                    print("Aztec LZR hint unable to be placed!")
            # Always put in at least one Factory hint
            elif i == 2:
                factoryHintEntrances = [entrance for entrance, back in spoiler.shuffled_exit_data.items() if back.regionId in criticalFactoryRegions]
                random.shuffle(factoryHintEntrances)
                factoryHintPlaced = False
                while len(factoryHintEntrances) > 0:
                    factoryHinted = factoryHintEntrances.pop()
                    message = TryCreatingLoadingZoneHint(spoiler, factoryHinted, criticalFactoryRegions)
                    if message != "":
                        factoryHintPlaced = True
                        break
                if not factoryHintPlaced:
                    print("Factory LZR hint unable to be placed!")
            else:
                region_to_hint = random.choice(usefulRegions)
                usefulHintEntrances = [entrance for entrance, back in spoiler.shuffled_exit_data.items() if back.regionId in region_to_hint]
                random.shuffle(usefulHintEntrances)
                usefulHintPlaced = False
                while len(usefulHintEntrances) > 0:
                    usefulHinted = usefulHintEntrances.pop()
                    message = TryCreatingLoadingZoneHint(spoiler, usefulHinted, region_to_hint)
                    if message != "":
                        usefulHintPlaced = True
                        break
                if not usefulHintPlaced:
                    print(f"Useful LZR hint to {usefulHinted.name} unable to be placed!")
            hint_location = getRandomHintLocation()
            hint_location.hint_type = HintType.Entrance
            UpdateHint(hint_location, message)

    # Precalculations are needed for this hint type so don't bother if we don't have any
    if hint_distribution[HintType.FullShop] > 0:
        # Collate nested lists for a list of shop moves
        shop_dump_hints = []
        for shop in range(3):  # Order: Cranky, Funky, Candy
            for level in range(8):  # Order: Japes, Aztec, Factory, Galleon, Fungi, Caves, Castle, Isles
                level_listing = []
                for kong in range(5):
                    # Get Moves in slot
                    data_section = spoiler.move_data[shop][kong][level]
                    for move in moves_data:
                        if move.item_key == data_section:
                            if move.name not in level_listing:
                                level_listing.append(move.name)
                # If there are no moves in this shop, definitely don't hint it (it might not even exist)
                if len(level_listing) == 0:
                    continue
                move_series = level_listing[0]
                if len(level_listing) > 1:
                    move_series = f"{', '.join(level_listing[:-1])} and {level_listing[-1]}"
                shop_name = shop_owners[shop]
                level_name = level_list_isles[level]
                if spoiler.settings.wrinkly_hints == "cryptic":
                    level_name = random.choice(level_cryptic_isles[level])
                shop_dump_hint = f"{shop_name}'s in {level_name} contains {move_series}"
                shop_dump_hints.append(shop_dump_hint)
        random.shuffle(shop_dump_hints)
        # Locations for these hints are random - you may get useful information about moves you've left behind
        placed_full_shop_hints = 0
        while placed_full_shop_hints < hint_distribution[HintType.FullShop]:
            hint_location = getRandomHintLocation()
            # In the other OBSCENELY rare case where we run out of shops to hint (usually requires over 15 shop hints), convert remaining hints to joke hints
            if len(shop_dump_hints) == 0:
                hint_diff = hint_distribution[HintType.FullShop] - placed_full_shop_hints
                hint_distribution[HintType.Joke] += hint_diff
                hint_distribution[HintType.FullShop] -= hint_diff
                break
            message = shop_dump_hints.pop()
            hint_location.hint_type = HintType.FullShop
            UpdateHint(hint_location, message)
            placed_full_shop_hints += 1

    # No need to do anything fancy here - there's already a K. Rool hint on the player's path (the wall in Helm)
    for i in range(hint_distribution[HintType.KRoolOrder]):
        hint_location = getRandomHintLocation()
        associated_hint = f"K. Rool order is {NameFromKong(spoiler.settings.krool_order[0])}"
        for x in range(len(spoiler.settings.krool_order)):
            if x != 0:
                associated_hint += f" then {NameFromKong(spoiler.settings.krool_order[x])}"
        hint_location.hint_type = HintType.KRoolOrder
        UpdateHint(hint_location, associated_hint)

    # Dirt patch hints are already garbage anyway - no restrictions here
    for i in range(hint_distribution[HintType.DirtPatch]):
        dirt_patch_name = random.choice(spoiler.dirt_patch_placement)
        hint_location = getRandomHintLocation()
        message = f"There is a dirt patch located at {dirt_patch_name}"
        hint_location.hint_type = HintType.DirtPatch
        UpdateHint(hint_location, message)

    # Very useless hint, can be found at Cranky's anyway
    for i in range(hint_distribution[HintType.MedalsRequired]):
        hint_location = getRandomHintLocation()
        message = f"{spoiler.settings.medal_requirement} medals are required to access Jetpac."
        hint_location.hint_type = HintType.MedalsRequired
        UpdateHint(hint_location, message)

    # Finally, place our joke hints
    for i in range(hint_distribution[HintType.Joke]):
        hint_location = getRandomHintLocation()
        joke_hint_list = hint_list.copy()
        random.shuffle(joke_hint_list)
        message = joke_hint_list.pop().hint
        hint_location.hint_type = HintType.Joke
        UpdateHint(hint_location, message)

    UpdateSpoilerHintList(spoiler)
    spoiler.hint_distribution = hint_distribution
    return True


def getRandomHintLocation(location_list=None, kongs=None, levels=None, move_name=None):
    """Return an unoccupied hint location. The parameters can be used to specify location requirements."""
    valid_unoccupied_hint_locations = [
        hint
        for hint in hints
        if hint.hint == ""
        and (location_list is None or hint in location_list)
        and (kongs is None or hint.kong in kongs)
        and (levels is None or hint.level in levels)
        and move_name not in hint.banned_keywords
    ]
    # If it's too specific, we may not be able to find any
    if len(valid_unoccupied_hint_locations) == 0:
        return None
    hint_location = random.choice(valid_unoccupied_hint_locations)
    # Update the reference so we're updating the main list instead of a copy of it
    for hint in hints:
        if hint.name == hint_location.name:
            return hint
    return None


def pushHintToList(hint: Hint):
    """Push hint to hint list."""
    hint_list.append(hint)


def resetHintList():
    """Reset hint list to default state."""
    for hint in hint_list:
        if not hint.base:
            hint_list.remove(hint)
        else:
            hint.used = False
            hint.important = hint.was_important
            hint.repeats = hint.original_repeats
            hint.priority = hint.original_priority


def compileHintsOld(spoiler: Spoiler):
    """Push hints to hint list based on settings. Old method that is now unused."""
    resetHintList()
    # K Rool Order
    if spoiler.settings.krool_phase_order_rando and len(spoiler.settings.krool_order) > 1:
        associated_hint = f"K. Rool order is {NameFromKong(spoiler.settings.krool_order[0])}"
        for x in range(len(spoiler.settings.krool_order)):
            if x != 0:
                associated_hint += f" then {NameFromKong(spoiler.settings.krool_order[x])}"
        hint_list.append(Hint(hint=associated_hint, repeats=2, kongs=spoiler.settings.krool_order.copy(), subtype="k_rool"))
    # Helm Order
    default_order = [Kongs.donkey, Kongs.chunky, Kongs.tiny, Kongs.lanky, Kongs.diddy]
    new_order = []
    if spoiler.settings.helm_phase_order_rando and len(spoiler.settings.helm_order) > 1:
        for room in spoiler.settings.helm_order:
            new_order.append(default_order[room])
        associated_hint = f"Helm Room order is {NameFromKong(new_order[0])}"
        for x in range(len(new_order)):
            if x != 0:
                associated_hint += f" then {NameFromKong(new_order[x])}"
        hint_list.append(Hint(hint=associated_hint, repeats=3, kongs=new_order.copy(), subtype="k_rool"))
    # K. Rool Moves
    if spoiler.settings.shuffle_items == "moves" and spoiler.move_data is not None:
        krool_move_requirements = [0, 2, 1, 1, 4]
        total_moves_for_krool = 0
        for x in spoiler.settings.krool_order:
            total_moves_for_krool += krool_move_requirements[x]

        # Collate nested lists for a list of shop moves
        shop_data = []
        for shop in range(3):  # Order: Cranky, Funky, Candy
            shop_listing = []
            for level in range(8):  # Order: Japes, Aztec, Factory, Galleon, Fungi, Caves, Castle, Isles
                level_listing = []
                for kong in range(5):
                    # Get Moves in slot
                    data_section = spoiler.move_data[shop][kong][level]
                    for move in moves_data:
                        if move.item_key == data_section:
                            if move.name not in level_listing:
                                level_listing.append(move.name)
                shop_listing.append(level_listing)
            shop_data.append(shop_listing)

        # Compile all hints that could be generated from shops
        dump_hints = []
        single_hints = []
        for shop_index, shop in enumerate(shop_data):
            for level_index, level in enumerate(shop):
                # Single Hints
                for move in level:
                    is_important = False
                    for move_item in moves_data:
                        if move_item.name == move and move_item.important:
                            is_important = True
                    shop_name = shop_owners[shop_index]
                    level_name = level_list_isles[level_index]
                    if spoiler.settings.wrinkly_hints == "cryptic":
                        level_name = random.choice(level_cryptic_isles[level_index])
                    single_hints.append({"hint": f"{move} can be purchased from {shop_name} in {level_name}", "important": is_important, "move": move})
                # Dump Hints
                if len(level) > 0:
                    shop_name = shop_owners[shop_index]
                    level_name = level_list_isles[level_index]
                    if spoiler.settings.wrinkly_hints == "cryptic":
                        level_name = random.choice(level_cryptic_isles[level_index])
                    move_series = level[0]
                    if len(level) > 1:
                        move_series = f"{', '.join(level[:-1])} and {level[-1]}"
                    hint_start = f"{shop_name}'s in {level_name} contains {move_series}"
                    dump_hints.append({"hint": hint_start, "moves": level})
        # Shuffle and add dump hints to list
        random.shuffle(dump_hints)
        priority_barriers = [3, 6, 10]
        shop_priority = 1
        shop_importance = True
        for dump_hint in dump_hints:
            if shop_importance:
                hint_list.append(Hint(hint=dump_hint["hint"], important=False, keywords=dump_hint["moves"], subtype="shop_dump"))
            if shop_priority <= len(priority_barriers):
                if (shop_index + 1) >= priority_barriers[shop_priority - 1]:
                    if shop_priority == len(priority_barriers):
                        shop_importance = False
                    else:
                        shop_priority += 1
        # Shuffle and add single hints to list
        random.shuffle(single_hints)
        for single_hint in single_hints:
            hint_list.append(Hint(hint=single_hint["hint"], priority=2, important=single_hint["important"], keywords=[single_hint["move"]], subtype="move_location"))
    if spoiler.settings.kong_rando:
        kong_json = spoiler.shuffled_kong_placement
        placement_levels = [
            {
                "name": "Jungle Japes",
                "level": 0,
            },
            {
                "name": "Llama Temple",
                "level": 1,
            },
            {
                "name": "Tiny Temple",
                "level": 1,
            },
            {
                "name": "Frantic Factory",
                "level": 2,
            },
        ]
        for kong_map in placement_levels:
            kong_index = kong_json[kong_map["name"]]["locked"]["kong"]
            free_kong = kong_json[kong_map["name"]]["puzzle"]["kong"]
            level_index = kong_map["level"]
            if spoiler.settings.wrinkly_hints == "cryptic":
                if not kong_index == Kongs.any:
                    kong_name = random.choice(kong_cryptic[kong_index])
                level_name = random.choice(level_cryptic[level_index])
            else:
                if not kong_index == Kongs.any:
                    kong_name = kong_list[kong_index]
                level_name = level_list[level_index]
            hint_priority = 2
            if kong_index == Kongs.any:
                kong_name = "An empty cage"
                hint_priority = 3
            hint_list.append(Hint(hint=f"{kong_name} can be found in {level_name}.", kongs=[free_kong], priority=hint_priority, subtype="kong_location"))
    if spoiler.settings.random_patches:
        level_patches = {
            "DK Isles": 0,
            "Jungle Japes": 0,
            "Angry Aztec": 0,
            "Frantic Factory": 0,
            "Gloomy Galleon": 0,
            "Fungi Forest": 0,
            "Crystal Caves": 0,
            "Creepy Castle": 0,
        }
        for patch in spoiler.dirt_patch_placement:
            for level in level_patches:
                if level in patch:
                    level_patches[level] += 1
        level_ordering = list(level_patches.keys())
        random.shuffle(level_ordering)
        for importance in range(2):
            for index in range(4):
                level_name = level_ordering[index + (4 * importance)]
                patch_count = level_patches[level_name]
                if patch_count > 0:
                    patch_mult = "patches"
                    patch_pre = "are"
                    if patch_count == 1:
                        patch_mult = "patch"
                        patch_pre = "is"
                    patch_text = f"There {patch_pre} {patch_count} {patch_mult} in {level_name}"
                    hint_list.append(Hint(hint=patch_text, priority=index + 3, important=False, subtype="level_patch_count"))
        patch_list = spoiler.dirt_patch_placement.copy()
        random.shuffle(patch_list)
        for importance in range(2):
            for index in range(4):
                patch_name = patch_list[index + (importance * 4)]
                patch_text = f"There is a dirt patch located at {patch_name}"
                hint_list.append(Hint(hint=patch_text, priority=index + 4, important=importance == 0, subtype="patch_location"))
    if spoiler.settings.shuffle_loading_zones == "all":
        AddLoadingZoneHints(spoiler)
    if spoiler.settings.coin_door_open == "need_both" or spoiler.settings.coin_door_open == "need_rw":
        hint_list.append(Hint(hint=f"{spoiler.settings.medal_requirement} medals are required to access Jetpac.", priority=4, subtype="medal"))
    if spoiler.settings.perma_death:
        hint_list.append(Hint(hint="The curse can only be removed upon disabling K. Rools machine.", subtype="permadeath"))
    if spoiler.settings.level_randomization != "level_order":
        for x in spoiler.settings.krool_keys_required:
            key_index = x - 4
            if spoiler.settings.wrinkly_hints == "cryptic":
                level_name = random.choice(level_cryptic[key_index])
            else:
                level_name = level_list[key_index]
            hint_list.append(Hint(hint=f"You will need to obtain the key from {level_name} to fight your greatest foe.", important=False, subtype="key_is_required"))
    # Way of the Hoard hints
    shopNames = ["Candy", "Funky", "Cranky"]
    moveSpecificSuffixes = [" Donkey", " Diddy", " Lanky", " Tiny", " Chunky", " Shared"]
    wothLocations = [key for key in spoiler.woth.keys() if any(shopName in key for shopName in shopNames)]
    selectedWothLocations = random.sample(wothLocations, min(5, len(wothLocations)))
    wothPriority = random.randint(1, 4)
    for wothLocation in selectedWothLocations:
        suffix = [specificSuffix for specificSuffix in moveSpecificSuffixes if specificSuffix in wothLocation]
        if len(suffix) > 0:
            wothHint = str(wothLocation).removesuffix(suffix[0])
        hint_list.append(Hint(hint=f"{wothHint} is on the Way of the Hoard.", important=random.choice([True, True, False]), priority=wothPriority, subtype="way_of_the_hoard"))
        wothPriority += random.randint(1, 2)

    # PADDED HINTS
    cb_list = [
        {"kong": "Donkey", "color": "Yellow"},
        {"kong": "Diddy", "color": "Red"},
        {"kong": "Lanky", "color": "Blue"},
        {"kong": "Tiny", "color": "Purple"},
        {"kong": "Chunky", "color": "Green"},
    ]
    # hint_list.append(Hint(hint=f"Your seed is {spoiler.settings.seed}")
    hint_list.append(Hint(hint=f"You can find bananas in {level_list[random.randint(0,6)]}, but also in other levels.", important=False, subtype="joke", joke=True, joke_defined=True))
    cb_hint = random.choice(cb_list)
    hint_list.append(Hint(hint=f"{cb_hint['kong']} can find {cb_hint['color']} bananas in {random.choice(level_list)}.", important=False, subtype="joke", joke=True, joke_defined=True))
    hint_list.append(Hint(hint=f"{spoiler.settings.krool_key_count} Keys are required to reach K. Rool.", important=False, subtype="key_count_required"))

    if spoiler.settings.shuffle_loading_zones == "levels":

        lobby_entrance_order = {
            Transitions.IslesMainToJapesLobby: Levels.JungleJapes,
            Transitions.IslesMainToAztecLobby: Levels.AngryAztec,
            Transitions.IslesMainToFactoryLobby: Levels.FranticFactory,
            Transitions.IslesMainToGalleonLobby: Levels.GloomyGalleon,
            Transitions.IslesMainToForestLobby: Levels.FungiForest,
            Transitions.IslesMainToCavesLobby: Levels.CrystalCaves,
            Transitions.IslesMainToCastleLobby: Levels.CreepyCastle,
        }
        lobby_exit_order = {
            Transitions.IslesJapesLobbyToMain: Levels.JungleJapes,
            Transitions.IslesAztecLobbyToMain: Levels.AngryAztec,
            Transitions.IslesFactoryLobbyToMain: Levels.FranticFactory,
            Transitions.IslesGalleonLobbyToMain: Levels.GloomyGalleon,
            Transitions.IslesForestLobbyToMain: Levels.FungiForest,
            Transitions.IslesCavesLobbyToMain: Levels.CrystalCaves,
            Transitions.IslesCastleLobbyToMain: Levels.CreepyCastle,
        }
        level_positions = {}
        level_order = {}
        shuffled_level_list = []
        for transition, vanilla_level in lobby_entrance_order.items():
            shuffled_level = lobby_exit_order[spoiler.shuffled_exit_data[transition].reverse]
            level_positions[shuffled_level] = vanilla_level
            level_order[vanilla_level] = shuffled_level
    if spoiler.settings.randomize_blocker_required_amounts is True and spoiler.settings.shuffle_loading_zones == "levels":
        for i in list(level_order.values()):
            shuffled_level_list.append(i.name)
        for x in range(8):
            count = spoiler.settings.EntryGBs[x]
            gb_name = "Golden Bananas"
            if count == 1:
                gb_name = "Golden Banana"
            level_name = level_list[x]
            # current_level_position = level_positions.index(level_name)
            gb_importance = False
            permitted_levels = all_levels.copy()
            priority_level = x + 1
            if spoiler.settings.shuffle_loading_zones == "levels":
                if x != 7:
                    current_level_order = level_positions[x]
                    permitted_levels = []
                    for y in range(7):
                        if y < current_level_order:
                            permitted_levels.append(level_order[y])
                    if level_name.replace(" ", "") in shuffled_level_list[4:7]:
                        priority_level = 4
                        gb_importance = True
                if spoiler.settings.maximize_helm_blocker is False and x == 7:
                    priority_level = 1
                    gb_importance = True
            if spoiler.settings.wrinkly_hints == "cryptic":
                level_name = random.choice(level_cryptic[x])

            hint_list.append(
                Hint(
                    hint=f"The barrier to {level_name} can be cleared by obtaining {count} {gb_name}.",
                    important=gb_importance,
                    priority=priority_level,
                    permitted_levels=permitted_levels.copy(),
                    subtype="gb_amount",
                )
            )
    for x in range(7):
        count = spoiler.settings.BossBananas[x]
        cb_name = "Small Bananas"
        if count == 1:
            cb_name = "Small Banana"
        if spoiler.settings.wrinkly_hints == "cryptic":
            level_name = random.choice(level_cryptic[x])
        else:
            level_name = level_list[x]
        permitted_levels = all_levels.copy()
        if spoiler.settings.shuffle_loading_zones == "levels":
            current_level_order = level_positions[x]
            permitted_levels = []
            for y in range(7):
                if y <= current_level_order:
                    permitted_levels.append(level_order[y])
        hint_list.append(
            Hint(hint=f"The barrier to the boss in {level_name} can be cleared by obtaining {count} {cb_name}.", important=False, permitted_levels=permitted_levels.copy(), subtype="cb_amount")
        )
    # Write Hints
    hint_distro = {}
    # 1 Joke Hint
    joke_hints = []
    for hint in hint_list:
        if not hint.important and not hint.used and hint.joke:
            joke_hints.append(hint)
    random_joke_hint = random.choice(joke_hints)
    placed = False
    joke_hint_count = 0
    while not placed:
        placed = updateRandomHint(random_joke_hint.hint, random_joke_hint.kongs.copy(), random_joke_hint.keywords.copy(), random_joke_hint.permitted_levels.copy())
        if placed:
            random_joke_hint.use_hint()
            joke_hint_count += 1
            subtype = random_joke_hint.subtype
            if subtype in hint_distro:
                hint_distro[subtype] += 1
            else:
                hint_distro[subtype] = 1
            break
    # Important
    random.shuffle(hint_list)
    priority_level = 1
    no_important_hints = False
    important_hint_count = 0
    while not no_important_hints:
        found_important = False
        for hint in hint_list:
            if hint.important and hint.priority == priority_level and not hint.used and not hint.joke:
                found_important = True
                placed = updateRandomHint(hint.hint, hint.kongs.copy(), hint.keywords.copy(), hint.permitted_levels.copy())
                if placed:
                    hint.use_hint()
                    important_hint_count += 1
                    subtype = hint.subtype
                    if subtype in hint_distro:
                        hint_distro[subtype] += 1
                    else:
                        hint_distro[subtype] = 1
                else:
                    hint.downgrade()
        if not found_important:
            no_important_hints = True
        priority_level += 1
    # Unimportant
    joke_hints = []
    vacant_slots = 0
    for hint in hint_list:
        if not hint.important and not hint.used and not hint.joke:
            joke_hints.append(hint)
    for hint in hints:
        if hint.hint == "":
            vacant_slots += 1
    random.shuffle(joke_hints)
    unimportant_hint_count = 0
    error_hint_count = 0
    if vacant_slots > 0:
        slot = 0
        tries = 100
        usage_slot = 0
        while slot < vacant_slots:
            placed = False
            if not joke_hints[usage_slot].used:
                placed = updateRandomHint(joke_hints[usage_slot].hint, joke_hints[usage_slot].kongs, joke_hints[usage_slot].keywords.copy(), joke_hints[usage_slot].permitted_levels.copy())
            if placed:
                joke_hints[usage_slot].use_hint()
                unimportant_hint_count += 1
                subtype = joke_hints[usage_slot].subtype
                if subtype in hint_distro:
                    hint_distro[subtype] += 1
                else:
                    hint_distro[subtype] = 1
                slot += 1
            else:
                tries -= 1
            usage_slot += 1
            if usage_slot >= len(joke_hints):
                usage_slot = 0
            if tries == 0:
                hints_to_replace = []
                for hint in hint_list:
                    if not hint.joke:
                        hints_to_replace.append(hint.hint)
                for hint in hints:
                    if hint.hint == "":
                        hint.hint = random.choice(hints_to_replace)
                for hint in hints:
                    if hint.hint == "":
                        hint.hint = "I have so little to tell you that this hint got placed here. If you see this, please report with your spoiler log in the bug reports channel in the DK64 Randomizer discord."
                        subtype = "error"
                        if subtype in hint_distro:
                            hint_distro[subtype] += 1
                        else:
                            hint_distro[subtype] = 1
                        error_hint_count += 1
                slot = vacant_slots
    UpdateSpoilerHintList(spoiler)
    return True


def AddLoadingZoneHints(spoiler: Spoiler):
    """Add hints for loading zone transitions and their destinations."""
    # One hint for each of the critical areas: Japes, Aztec, Factory
    criticalJapesRegions = [
        Regions.JungleJapesMain,
        Regions.JapesBeyondFeatherGate,
        Regions.TinyHive,
        Regions.JapesLankyCave,
        Regions.Mine,
    ]
    criticalAztecRegions = [
        Regions.AngryAztecStart,
        Regions.AngryAztecMain,
    ]
    criticalFactoryRegions = [
        Regions.FranticFactoryStart,
        Regions.ChunkyRoomPlatform,
        Regions.PowerHut,
        Regions.BeyondHatch,
        Regions.InsideCore,
    ]
    japesHintEntrances = [entrance for entrance, back in spoiler.shuffled_exit_data.items() if back.regionId in criticalJapesRegions]
    random.shuffle(japesHintEntrances)
    japesHintPlaced = False
    while len(japesHintEntrances) > 0:
        japesHinted = japesHintEntrances.pop()
        if TryAddingLoadingZoneHint(spoiler, japesHinted, 1, criticalJapesRegions):
            japesHintPlaced = True
            break
    if not japesHintPlaced:
        print("Japes LZR hint unable to be placed!")

    aztecHintEntrances = [entrance for entrance, back in spoiler.shuffled_exit_data.items() if back.regionId in criticalAztecRegions]
    random.shuffle(aztecHintEntrances)
    aztecHintPlaced = False
    while len(aztecHintEntrances) > 0:
        aztecHinted = aztecHintEntrances.pop()
        if TryAddingLoadingZoneHint(spoiler, aztecHinted, 1, criticalAztecRegions):
            aztecHintPlaced = True
            break
    if not aztecHintPlaced:
        print("Aztec LZR hint unable to be placed!")

    factoryHintEntrances = [entrance for entrance, back in spoiler.shuffled_exit_data.items() if back.regionId in criticalFactoryRegions]
    random.shuffle(factoryHintEntrances)
    factoryHintPlaced = False
    while len(factoryHintEntrances) > 0:
        factoryHinted = factoryHintEntrances.pop()
        if TryAddingLoadingZoneHint(spoiler, factoryHinted, 1, criticalFactoryRegions):
            factoryHintPlaced = True
            break
    if not factoryHintPlaced:
        print("Factory LZR hint unable to be placed!")

    # Three hints for any of these useful areas: Banana Fairy, Galleon, Fungi, Caves, Castle, Crypt, Tunnel
    usefulRegions = [
        [Regions.BananaFairyRoom],
        [
            Regions.GloomyGalleonStart,
            Regions.LighthouseArea,
            Regions.Shipyard,
        ],
        [
            Regions.FungiForestStart,
            Regions.GiantMushroomArea,
            Regions.MushroomLowerExterior,
            Regions.MushroomNightExterior,
            Regions.MushroomUpperExterior,
            Regions.MillArea,
        ],
        [
            Regions.CrystalCavesMain,
            Regions.IglooArea,
            Regions.CabinArea,
        ],
        [
            Regions.CreepyCastleMain,
            Regions.CastleWaterfall,
        ],
        [Regions.LowerCave],
        [Regions.UpperCave],
    ]
    hintedUsefulAreas = random.sample(usefulRegions, 3)
    for regions in hintedUsefulAreas:
        usefulHintEntrances = [entrance for entrance, back in spoiler.shuffled_exit_data.items() if back.regionId in regions]
        random.shuffle(usefulHintEntrances)
        usefulHintPlaced = False
        while len(usefulHintEntrances) > 0:
            usefulHinted = usefulHintEntrances.pop()
            if TryAddingLoadingZoneHint(spoiler, usefulHinted, 3, regions):
                usefulHintPlaced = True
                break
        if not usefulHintPlaced:
            print(f"Useful LZR hint to {usefulHinted.name} unable to be placed!")

    # Remaining hints for any shuffled exits in the game
    # Restrict DK isles main areas from being hinted
    uselessDkIslesRegions = [
        Regions.IslesMain,
        Regions.IslesMainUpper,
    ]
    remainingTransitions = [entrance for entrance, back in spoiler.shuffled_exit_data.items() if back.regionId not in uselessDkIslesRegions]
    random.shuffle(remainingTransitions)
    remainingHintCount = 4
    for transition in remainingTransitions:
        if remainingHintCount == 0:
            break
        elif TryAddingLoadingZoneHint(spoiler, transition, 5):
            remainingHintCount -= 1
    if remainingHintCount > 0:
        print("Unable to place remaining LZR hints!")


def TryAddingLoadingZoneHint(spoiler: Spoiler, transition, useful_rating, disallowedRegions: list = None):
    """Try to write a hint for the given transition. If this hint is determined to be bad, it will return false and not place the hint.

    NOTE: ONLY USED IN OLD HINT SYSTEM. Functionality was replicated for new hint system elsewhere.
    """
    if disallowedRegions is None:
        disallowedRegions = []
    pathToHint = transition
    # Don't hint entrances from dead-end rooms, follow the reverse pathway back until finding a place with multiple entrances
    if spoiler.settings.decoupled_loading_zones:
        while ShufflableExits[pathToHint].category is None:
            originPaths = [x for x, back in spoiler.shuffled_exit_data.items() if back.reverse == pathToHint]
            # In a few cases, there is no reverse loading zone. In this case we must keep the original path to hint
            if len(originPaths) == 0:
                break
            pathToHint = originPaths[0]
    # With coupled loading zones, never hint from a dead-end room, since it is forced to be coming from the same destination
    elif ShufflableExits[pathToHint].category is None:
        return False
    # Validate the region of the hinted entrance is not in disallowedRegions
    if ShufflableExits[pathToHint].region in disallowedRegions:
        return False
    # Validate the hinted destination is not the same as the hinted origin
    entranceMap = GetMapId(ShufflableExits[pathToHint].region)
    destinationMap = GetMapId(spoiler.shuffled_exit_data[transition].regionId)
    if entranceMap == destinationMap:
        return False
    entranceName = ShufflableExits[pathToHint].name
    destinationName: str = spoiler.shuffled_exit_data[transition].spoilerName
    fromExitName = destinationName.find(" from ")
    if fromExitName != -1:
        # Remove exit name from destination
        destinationName = destinationName[:fromExitName]
    pushHintToList(Hint(hint=f"If you're looking for {destinationName}, follow the path from {entranceName}.", priority=useful_rating, subtype="lzr"))
    return True


def TryCreatingLoadingZoneHint(spoiler: Spoiler, transition, disallowedRegions: list = None):
    """Try to create a hint message for the given transition. If this hint is determined to be bad, it will return false and not place the hint."""
    if disallowedRegions is None:
        disallowedRegions = []
    pathToHint = transition
    # Don't hint entrances from dead-end rooms, follow the reverse pathway back until finding a place with multiple entrances
    if spoiler.settings.decoupled_loading_zones:
        while ShufflableExits[pathToHint].category is None:
            originPaths = [x for x, back in spoiler.shuffled_exit_data.items() if back.reverse == pathToHint]
            # In a few cases, there is no reverse loading zone. In this case we must keep the original path to hint
            if len(originPaths) == 0:
                break
            pathToHint = originPaths[0]
    # With coupled loading zones, never hint from a dead-end room, since it is forced to be coming from the same destination
    elif ShufflableExits[pathToHint].category is None:
        return ""
    # Validate the region of the hinted entrance is not in disallowedRegions
    if ShufflableExits[pathToHint].region in disallowedRegions:
        return ""
    # Validate the hinted destination is not the same as the hinted origin
    entranceMap = GetMapId(ShufflableExits[pathToHint].region)
    destinationMap = GetMapId(spoiler.shuffled_exit_data[transition].regionId)
    if entranceMap == destinationMap:
        return ""
    entranceName = ShufflableExits[pathToHint].name
    destinationName: str = spoiler.shuffled_exit_data[transition].spoilerName
    fromExitName = destinationName.find(" from ")
    if fromExitName != -1:
        # Remove exit name from destination
        destinationName = destinationName[:fromExitName]
    return f"If you're looking for {destinationName}, follow the path from {entranceName}."


def UpdateSpoilerHintList(spoiler: Spoiler):
    """Write hints to spoiler object."""
    for hint in hints:
        spoiler.hint_list[hint.name] = hint.hint
