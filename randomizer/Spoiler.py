"""Spoiler class and functions."""

from email.policy import default
import json
from typing import OrderedDict

from randomizer.Enums.Events import Events
from randomizer.Enums.Items import Items
from randomizer.Enums.Kongs import Kongs
from randomizer.Enums.Levels import Levels
from randomizer.Enums.Locations import Locations
from randomizer.Enums.MoveTypes import MoveTypes
from randomizer.Enums.Regions import Regions
from randomizer.Enums.Transitions import Transitions
from randomizer.Enums.Types import Types
from randomizer.Lists.Item import ItemFromKong, ItemList, KongFromItem, NameFromKong
from randomizer.Lists.Location import LocationList
from randomizer.Lists.MapsAndExits import GetExitId, GetMapId, Maps
from randomizer.Lists.Minigame import BarrelMetaData, HelmMinigameLocations, MinigameRequirements
from randomizer.Settings import Settings
from randomizer.ShuffleExits import ShufflableExits


class Spoiler:
    """Class which contains all spoiler data passed into and out of randomizer."""

    def __init__(self, settings):
        """Initialize spoiler just with settings."""
        self.settings: Settings = settings
        self.playthrough = {}
        self.woth = {}
        self.shuffled_barrel_data = {}
        self.shuffled_exit_data = {}
        self.shuffled_exit_instructions = []
        self.music_bgm_data = {}
        self.music_fanfare_data = {}
        self.music_event_data = {}
        self.location_data = {}
        self.enemy_replacements = []

        self.move_data = []
        # 0: Cranky, 1: Funky, 2: Candy
        for i in range(3):
            moves = []
            # One for each kong
            for j in range(5):
                kongmoves = []
                # One for each level
                for k in range(8):
                    kongmoves.append(-1)
                moves.append(kongmoves)
            self.move_data.append(moves)

        self.hint_list = {}

    def toJson(self):
        """Convert spoiler to JSON."""
        # Verify we match our hash
        self.settings.verify_hash()
        # We want to convert raw spoiler data into the important bits and in human-readable formats.
        humanspoiler = OrderedDict()

        # Settings data
        settings = OrderedDict()
        settings["Seed"] = self.settings.seed_id
        # settings["algorithm"] = self.settings.algorithm # Don't need this for now, probably
        settings["No Logic"] = self.settings.no_logic
        settings["Shuffle Enemies"] = self.settings.enemy_rando
        settings["Move Randomization type"] = self.settings.move_rando
        settings["Loading Zones Shuffled"] = self.settings.shuffle_loading_zones
        settings["Decoupled Loading Zones"] = self.settings.decoupled_loading_zones
        startKongList = []
        for x in self.settings.starting_kong_list:
            startKongList.append(x.name.capitalize())
        if self.settings.randomize_blocker_required_amounts:
            settings["Maximum B Locker"] = self.settings.blocker_text
        if self.settings.randomize_cb_required_amounts:
            settings["Maximum Troff N Scoff"] = self.settings.troff_text
        settings["Open Lobbies"] = self.settings.open_lobbies
        settings["Open Levels"] = self.settings.open_levels
        settings["Randomize Pickups"] = self.settings.randomize_pickups
        settings["Randomize Patches"] = self.settings.random_patches
        settings["Puzzle Randomization"] = self.settings.puzzle_rando
        settings["Crown Door Open"] = self.settings.crown_door_open
        settings["Coin Door Open"] = self.settings.coin_door_open
        settings["Unlock Fairy Shockwave"] = self.settings.unlock_fairy_shockwave
        settings["Random Medal Requirement"] = self.settings.random_medal_requirement
        settings["Random Shop Prices"] = self.settings.random_prices
        settings["Banana Port Randomization"] = self.settings.bananaport_rando
        settings["Shuffle Shop Locations"] = self.settings.shuffle_shops
        settings["Shuffle Kasplats"] = self.settings.kasplat_rando_setting

        settings["Key 8 Required"] = self.settings.krool_access
        settings["Number of Keys Required"] = self.settings.krool_key_count
        settings["Fast Start"] = self.settings.fast_start_beginning_of_game
        settings["Helm Setting"] = self.settings.helm_setting
        settings["Quality of Life"] = self.settings.quality_of_life
        settings["Tag Anywhere"] = self.settings.enable_tag_anywhere
        settings["Fast GBs"] = self.settings.fast_gbs
        settings["High Requirements"] = self.settings.high_req
        humanspoiler["Settings"] = settings
        humanspoiler["Cosmetics"] = {}
        if self.settings.colors != {} or self.settings.klaptrap_model_index:
            humanspoiler["Cosmetics"]["Colors and Models"] = {}
            for color_item in self.settings.colors:
                if color_item == "dk":
                    humanspoiler["Cosmetics"]["Colors and Models"]["DK Color"] = self.settings.colors[color_item]
                else:
                    humanspoiler["Cosmetics"]["Colors and Models"][f"{color_item.capitalize()} Color"] = self.settings.colors[color_item]
            klap_models = {
                0x19: "Beaver",
                0x1E: "Klobber",
                0x20: "Kaboom",
                0x21: "Green Klaptrap",
                0x22: "Purple Klaptrap",
                0x23: "Red Klaptrap",
                0x24: "Klaptrap Teeth",
                0x26: "Krash",
                0x27: "Troff",
                0x30: "N64 Logo",
                0x34: "Mech Fish",
                0x42: "Krossbones",
                0x47: "Rabbit",
                0x4B: "Minecart Skeleton Head",
                0x51: "Tomato",
                0x62: "Ice Tomato",
                0x69: "Golden Banana",
                0x70: "Microbuffer",
                0x72: "Bell",
                0x96: "Missile (Car Race)",
                0xB0: "Red Buoy",
                0xB1: "Green Buoy",
                0xBD: "Rareware Logo",
            }
            if self.settings.klaptrap_model_index in klap_models:
                humanspoiler["Cosmetics"]["Colors and Models"]["Klatrap Model"] = klap_models[self.settings.klaptrap_model_index]
            else:
                humanspoiler["Cosmetics"]["Colors and Models"]["Klatrap Model"] = f"Unknown Model {hex(self.settings.klaptrap_model_index)}"

        humanspoiler["Requirements"] = {}
        # GB Counts
        gb_counts = {}
        level_list = ["Jungle Japes", "Angry Aztec", "Frantic Factory", "Gloomy Galleon", "Fungi Forest", "Crystal Caves", "Creepy Castle", "Hideout Helm"]
        for level_index, amount in enumerate(self.settings.EntryGBs):
            gb_counts[level_list[level_index]] = amount
        humanspoiler["Requirements"]["B Locker GBs"] = gb_counts
        # CB Counts
        cb_counts = {}
        for level_index, amount in enumerate(self.settings.BossBananas):
            cb_counts[level_list[level_index]] = amount
        humanspoiler["Requirements"]["Troff N Scoff Bananas"] = cb_counts
        humanspoiler["Requirements"]["Miscellaneous"] = {}
        humanspoiler["Kongs"] = {}
        humanspoiler["Kongs"]["Starting Kong List"] = startKongList
        humanspoiler["Kongs"]["Japes Kong Puzzle Solver"] = ItemList[ItemFromKong(self.settings.diddy_freeing_kong)].name
        humanspoiler["Kongs"]["Tiny Temple Puzzle Solver"] = ItemList[ItemFromKong(self.settings.tiny_freeing_kong)].name
        humanspoiler["Kongs"]["Llama Temple Puzzle Solver"] = ItemList[ItemFromKong(self.settings.lanky_freeing_kong)].name
        humanspoiler["Kongs"]["Factory Kong Puzzle Solver"] = ItemList[ItemFromKong(self.settings.chunky_freeing_kong)].name
        if self.settings.coin_door_open in ["need_both", "need_rw"]:
            humanspoiler["Requirements"]["Miscellaneous"]["Medal Requirement"] = self.settings.medal_requirement
        humanspoiler["End Game"] = {}
        humanspoiler["End Game"]["Keys Required for K Rool"] = self.GetKroolKeysRequired(self.settings.krool_keys_required)
        krool_order = []
        for phase in self.settings.krool_order:
            krool_order.append(ItemList[ItemFromKong(phase)].name.capitalize())
        humanspoiler["End Game"]["K Rool Phases"] = krool_order

        helm_default_order = [Kongs.donkey, Kongs.chunky, Kongs.tiny, Kongs.lanky, Kongs.diddy]
        helm_new_order = []
        for room in self.settings.helm_order:
            helm_new_order.append(helm_default_order[room].name.capitalize())
        humanspoiler["End Game"]["Helm Rooms"] = helm_new_order
        humanspoiler["Items"] = {
            "Kongs": {},
            "Shops": {},
            "Others": {},
        }

        prices = OrderedDict()
        if self.settings.random_prices != "vanilla":
            for item, price in self.settings.prices.items():
                if item == Items.ProgressiveSlam:
                    prices["Progressive Slam"] = f"{price[0]}→{price[1]}"
                elif item == Items.ProgressiveAmmoBelt:
                    prices["Progressive Ammo Belt"] = f"{price[0]}→{price[1]}"
                elif item == Items.ProgressiveInstrumentUpgrade:
                    prices["Progressive Instrument Upgrade"] = f"{price[0]}→{price[1]}→{price[2]}"
                else:
                    prices[f"{ItemList[item].name}"] = price

        if self.settings.shuffle_items != "none":
            # Playthrough data
            humanspoiler["Playthrough"] = self.playthrough

            # Woth data
            humanspoiler["Way of the Hoard"] = self.woth

            # Item location data
            locations = OrderedDict()

            for location, item in self.location_data.items():
                if not LocationList[location].constant:
                    item_name = ItemList[item].name
                    location_name = LocationList[location].name
                    item_group = "Others"
                    if location_name in ("Diddy Kong", "Lanky Kong", "Tiny Kong", "Chunky Kong"):
                        item_group = "Kongs"
                    elif "Cranky" in location_name or "Funky" in location_name or "Candy" in location_name:
                        item_group = "Shops"
                    if self.settings.random_prices != "vanilla":
                        if item_name in prices:
                            item_name = f"{item_name} ({prices[item_name]})"
                    humanspoiler["Items"][item_group][location_name] = item_name
        if len(humanspoiler["Items"]["Shops"].keys()) == 0:
            price_data = {}
            for price in prices:
                price_data[f"{price} Cost"] = prices[price]
            humanspoiler["Items"]["Shops"] = price_data

        if self.settings.shuffle_loading_zones == "levels":
            # Just show level order
            shuffled_exits = OrderedDict()
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
            for transition, vanilla_level in lobby_entrance_order.items():
                shuffled_level = lobby_exit_order[self.shuffled_exit_data[transition].reverse]
                shuffled_exits[vanilla_level.name] = shuffled_level.name
            humanspoiler["Shuffled Level Order"] = shuffled_exits
        elif self.settings.shuffle_loading_zones != "none":
            # Show full shuffled_exits data if more than just levels are shuffled
            shuffled_exits = OrderedDict()
            level_starts = {
                "DK Isles": [
                    "DK Isles",
                    "Japes Lobby",
                    "Aztec Lobby",
                    "Factory Lobby",
                    "Galleon Lobby",
                    "Fungi Lobby",
                    "Caves Lobby",
                    "Castle Lobby",
                    "Snide's Room",
                    "Training Grounds",
                    "Banana Fairy Isle",
                    "DK's Treehouse",
                ],
                "Jungle Japes": ["Jungle Japes"],
                "Angry Aztec": ["Angry Aztec"],
                "Frantic Factory": ["Frantic Factory"],
                "Gloomy Galleon": ["Gloomy Galleon"],
                "Fungi Forest": ["Fungi Forest"],
                "Crystal Caves": ["Crystal Caves"],
                "Creepy Castle": ["Creepy Castle"],
            }
            level_data = {"Other": {}}
            for level in level_starts:
                level_data[level] = {}
            for exit, dest in self.shuffled_exit_data.items():
                level_name = "Other"
                for level in level_starts:
                    for search_name in level_starts[level]:
                        if dest.spoilerName.find(search_name) == 0:
                            level_name = level
                shuffled_exits[ShufflableExits[exit].name] = dest.spoilerName
                level_data[level_name][ShufflableExits[exit].name] = dest.spoilerName
            humanspoiler["Shuffled Exits"] = shuffled_exits
            humanspoiler["Shuffled Exits (Sorted by destination)"] = level_data

        humanspoiler["Bosses"] = {}
        if self.settings.boss_location_rando:
            shuffled_bosses = OrderedDict()
            boss_names = {
                "JapesBoss": "Army Dillo 1",
                "AztecBoss": "Dogadon 1",
                "FactoryBoss": "Mad Jack",
                "GalleonBoss": "Pufftoss",
                "FungiBoss": "Dogadon 2",
                "CavesBoss": "Army Dillo 2",
                "CastleBoss": "King Kut Out",
            }
            for i in range(7):
                shuffled_bosses["".join(map(lambda x: x if x.islower() else " " + x, Levels(i).name))] = boss_names[Maps(self.settings.boss_maps[i]).name]
            humanspoiler["Bosses"]["Shuffled Boss Order"] = shuffled_bosses

        humanspoiler["Bosses"]["King Kut Out Properties"] = {}
        if self.settings.boss_kong_rando:
            shuffled_boss_kongs = OrderedDict()
            for i in range(7):
                shuffled_boss_kongs["".join(map(lambda x: x if x.islower() else " " + x, Levels(i).name))] = Kongs(self.settings.boss_kongs[i]).name.capitalize()
            humanspoiler["Bosses"]["Shuffled Boss Kongs"] = shuffled_boss_kongs
            kutout_order = ""
            for kong in self.settings.kutout_kongs:
                kutout_order = kutout_order + Kongs(kong).name.capitalize() + ", "
            humanspoiler["Bosses"]["King Kut Out Properties"]["Shuffled Kutout Kong Order"] = kutout_order.removesuffix(", ")

        if self.settings.hard_bosses:
            phase_names = []
            for phase in self.settings.kko_phase_order:
                phase_names.append(f"Phase {phase+1}")
            humanspoiler["Bosses"]["King Kut Out Properties"]["Shuffled Kutout Phases"] = ", ".join(phase_names)

        if self.settings.bonus_barrels in ("random", "selected"):
            shuffled_barrels = OrderedDict()
            for location, minigame in self.shuffled_barrel_data.items():
                if location in HelmMinigameLocations and self.settings.helm_barrels == "skip":
                    continue
                if location not in HelmMinigameLocations and self.settings.bonus_barrels == "skip":
                    continue
                shuffled_barrels[LocationList[location].name] = MinigameRequirements[minigame].name
            if len(shuffled_barrels) > 0:
                humanspoiler["Shuffled Bonus Barrels"] = shuffled_barrels

        if self.settings.music_bgm == "randomized":
            humanspoiler["Cosmetics"]["Background Music"] = self.music_bgm_data
        if self.settings.music_fanfares == "randomized":
            humanspoiler["Cosmetics"]["Fanfares"] = self.music_fanfare_data
        if self.settings.music_events == "randomized":
            humanspoiler["Cosmetics"]["Event Themes"] = self.music_event_data
        if self.settings.kasplat_rando:
            humanspoiler["Shuffled Kasplats"] = self.human_kasplats
        if self.settings.random_patches:
            humanspoiler["Shuffled Dirt Patches"] = self.human_patches
        if self.settings.bananaport_rando:
            humanspoiler["Shuffled Bananaports"] = self.human_warp_locations
        if len(self.hint_list) > 0:
            humanspoiler["Wrinkly Hints"] = self.hint_list
        if self.settings.shuffle_shops:
            shop_location_dict = {}
            for level in self.shuffled_shop_locations:
                level_name = "Unknown Level"

                level_dict = {
                    Levels.DKIsles: "DK Isles",
                    Levels.JungleJapes: "Jungle Japes",
                    Levels.AngryAztec: "Angry Aztec",
                    Levels.FranticFactory: "Frantic Factory",
                    Levels.GloomyGalleon: "Gloomy Galleon",
                    Levels.FungiForest: "Fungi Forest",
                    Levels.CrystalCaves: "Crystal Caves",
                    Levels.CreepyCastle: "Creepy Castle",
                }
                shop_dict = {Regions.CrankyGeneric: "Cranky", Regions.CandyGeneric: "Candy", Regions.FunkyGeneric: "Funky", Regions.Snide: "Snide"}
                if level in level_dict:
                    level_name = level_dict[level]
                for shop in self.shuffled_shop_locations[level]:
                    location_name = "Unknown Shop"
                    shop_name = "Unknown Shop"
                    new_shop = self.shuffled_shop_locations[level][shop]
                    if shop in shop_dict:
                        location_name = shop_dict[shop]
                    if new_shop in shop_dict:
                        shop_name = shop_dict[new_shop]
                    shop_location_dict[f"{level_name} - {location_name}"] = shop_name
            humanspoiler["Shop Locations"] = shop_location_dict
        for spoiler_dict in ("Items", "Bosses"):
            is_empty = True
            for y in humanspoiler[spoiler_dict]:
                if humanspoiler[spoiler_dict][y] != {}:
                    is_empty = False
            if is_empty:
                del humanspoiler[spoiler_dict]

        return json.dumps(humanspoiler, indent=4)

    def UpdateKasplats(self, kasplat_map):
        """Update kasplat data."""
        for kasplat, kong in kasplat_map.items():
            # Get kasplat info
            location = LocationList[kasplat]
            mapId = location.map
            original = location.kong
            self.human_kasplats[location.name] = NameFromKong(kong)
            map = None
            # See if map already exists in enemy_replacements
            for m in self.enemy_replacements:
                if m["container_map"] == mapId:
                    map = m
                    break
            # If not, create it
            if map is None:
                map = {"container_map": mapId}
                self.enemy_replacements.append(map)
            # Create kasplat_swaps section if doesn't exist
            if "kasplat_swaps" not in map:
                map["kasplat_swaps"] = []
            # Create swap entry and add to map
            swap = {"vanilla_location": original, "replace_with": kong}
            map["kasplat_swaps"].append(swap)

    def UpdateBarrels(self):
        """Update list of shuffled barrel minigames."""
        self.shuffled_barrel_data = {}
        for location, minigame in [(key, value.minigame) for (key, value) in BarrelMetaData.items()]:
            self.shuffled_barrel_data[location] = minigame

    def UpdateExits(self):
        """Update list of shuffled exits."""
        self.shuffled_exit_data = {}
        containerMaps = {}
        for key, exit in ShufflableExits.items():
            if exit.shuffled:
                try:
                    vanillaBack = exit.back
                    shuffledBack = ShufflableExits[exit.shuffledId].back
                    self.shuffled_exit_data[key] = shuffledBack
                    containerMapId = GetMapId(exit.region)
                    if containerMapId not in containerMaps:
                        containerMaps[containerMapId] = {"container_map": containerMapId, "zones": []}  # DK Isles
                    loading_zone_mapping = {}
                    loading_zone_mapping["vanilla_map"] = GetMapId(vanillaBack.regionId)
                    loading_zone_mapping["vanilla_exit"] = GetExitId(vanillaBack)
                    loading_zone_mapping["new_map"] = GetMapId(shuffledBack.regionId)
                    loading_zone_mapping["new_exit"] = GetExitId(shuffledBack)
                    containerMaps[containerMapId]["zones"].append(loading_zone_mapping)
                except Exception as ex:
                    print(ex)
        for key, containerMap in containerMaps.items():
            self.shuffled_exit_instructions.append(containerMap)

    def UpdateLocations(self, locations):
        """Update location list for what was produced by the fill."""
        self.location_data = {}
        self.shuffled_kong_placement = {}
        # Go ahead and set starting kong
        startkong = {"kong": self.settings.starting_kong, "write": 0x151}
        trainingGrounds = {"locked": startkong}
        self.shuffled_kong_placement["TrainingGrounds"] = trainingGrounds
        # Write additional starting kongs to empty cages, if any
        emptyCages = [x for x in [Locations.DiddyKong, Locations.LankyKong, Locations.TinyKong, Locations.ChunkyKong] if x not in self.settings.kong_locations]
        for emptyCage in emptyCages:
            self.WriteKongPlacement(emptyCage, Items.NoItem)

        # Loop through locations and set necessary data
        for id, location in locations.items():
            if location.item is not None and location.item is not Items.NoItem and not location.constant:
                self.location_data[id] = location.item
                if location.type == Types.Shop:
                    # Get indices from the location
                    shop_index = 0  # cranky
                    if location.movetype in [MoveTypes.Guns, MoveTypes.AmmoBelt]:
                        shop_index = 1  # funky
                    elif location.movetype == MoveTypes.Instruments:
                        shop_index = 2  # candy
                    kong_indices = [location.kong]
                    if location.kong == Kongs.any:
                        kong_indices = [Kongs.donkey, Kongs.diddy, Kongs.lanky, Kongs.tiny, Kongs.chunky]
                    level_index = location.level
                    # Isles level index is 8, but we need it to be 7 to fit it in move_data
                    if level_index == 8:
                        level_index = 7
                    # Use the item to find the data to write
                    move_type = ItemList[location.item].movetype
                    move_level = ItemList[location.item].index - 1
                    move_kong = ItemList[location.item].kong
                    for kong_index in kong_indices:
                        # print(f"Shop {shop_index}, Kong {kong_index}, Level {level_index} | Move: {move_type} lvl {move_level} for kong {move_kong}")
                        if move_type == 1 or move_type == 3 or (move_type == 2 and move_level > 0) or (move_type == 4 and move_level > 0):
                            move_kong = kong_index
                        data = (move_type << 5) | (move_level << 3) | move_kong
                        self.move_data[shop_index][kong_index][level_index] = data
                elif location.type == Types.Kong:
                    self.WriteKongPlacement(id, location.item)
            # Uncomment for more verbose spoiler with all locations
            # else:
            #     self.location_data[id] = Items.NoItem

    def WriteKongPlacement(self, locationId, item):
        """Write kong placement information for the given kong cage location."""
        locationName = "Jungle Japes"
        unlockKong = self.settings.diddy_freeing_kong
        lockedwrite = 0x152
        puzzlewrite = 0x153
        if locationId == Locations.LankyKong:
            locationName = "Llama Temple"
            unlockKong = self.settings.lanky_freeing_kong
            lockedwrite = 0x154
            puzzlewrite = 0x155
        elif locationId == Locations.TinyKong:
            locationName = "Tiny Temple"
            unlockKong = self.settings.tiny_freeing_kong
            lockedwrite = 0x156
            puzzlewrite = 0x157
        elif locationId == Locations.ChunkyKong:
            locationName = "Frantic Factory"
            unlockKong = self.settings.chunky_freeing_kong
            lockedwrite = 0x158
            puzzlewrite = 0x159
        lockedkong = {}
        lockedkong["kong"] = KongFromItem(item)
        lockedkong["write"] = lockedwrite
        puzzlekong = {"kong": unlockKong, "write": puzzlewrite}
        kongLocation = {"locked": lockedkong, "puzzle": puzzlekong}
        self.shuffled_kong_placement[locationName] = kongLocation

    def UpdatePlaythrough(self, locations, playthroughLocations):
        """Write playthrough as a list of dicts of location/item pairs."""
        self.playthrough = {}
        i = 0
        for sphere in playthroughLocations:
            newSphere = {}
            newSphere["Available GBs"] = sphere.availableGBs
            sphereLocations = list(map(lambda l: locations[l], sphere.locations))
            sphereLocations.sort(key=lambda l: l.type == Types.Banana)
            for location in sphereLocations:
                newSphere[location.name] = ItemList[location.item].name
            self.playthrough[i] = newSphere
            i += 1

    def UpdateWoth(self, locations, wothLocations):
        """Write woth locations as a dict of location/item pairs."""
        self.woth = {}
        for locationId in wothLocations:
            location = locations[locationId]
            self.woth[location.name] = ItemList[location.item].name

    @staticmethod
    def GetKroolKeysRequired(keyEvents):
        """Get key names from required key events to print in the spoiler."""
        keys = []
        if Events.JapesKeyTurnedIn in keyEvents:
            keys.append("Jungle Japes Key")
        if Events.AztecKeyTurnedIn in keyEvents:
            keys.append("Angry Aztec Key")
        if Events.FactoryKeyTurnedIn in keyEvents:
            keys.append("Frantic Factory Key")
        if Events.GalleonKeyTurnedIn in keyEvents:
            keys.append("Gloomy Galleon Key")
        if Events.ForestKeyTurnedIn in keyEvents:
            keys.append("Fungi Forest Key")
        if Events.CavesKeyTurnedIn in keyEvents:
            keys.append("Crystal Caves Key")
        if Events.CastleKeyTurnedIn in keyEvents:
            keys.append("Creepy Castle Key")
        if Events.HelmKeyTurnedIn in keyEvents:
            keys.append("Hideout Helm Key")
        return keys
