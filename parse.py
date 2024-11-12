import os
import re
import sys
import armaclass
import json


CARGO_NAMES = ("MagazineCargo", "ItemCargo", "WeaponCargo")
PROGRAMMER_REQUIRED_RADIOS = ["TFAR_anprc154", "TFAR_pnr1000a", "TFAR_rf7800str"]
# TFAR_COMPATIBLE_RADIOS = [
#     "gm_radio_r126",
#     "gm_radio_sem52a",
#     "vn_o_item_radio_m252",
#     "vn_b_item_radio_urc10",
#     "TFAR_anprc148jem",
#     "TFAR_anprc152",
#     "TFAR_fadak",
# ] + PROGRAMMER_REQUIRED_RADIOS

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    data_file = os.path.join(sys._MEIPASS, "data_unorganized.json")  # type: ignore
else:
    data_file = "data_unorganized.json"

with open(data_file) as file:
    item_data = json.load(file)


def parse_mission(sqm_path: str, equipment_path: str):
    with open(sqm_path) as file:
        sqm_data = armaclass.parse(file.read())
    player_inventories = []
    players = []
    inventory_data = {}
    # with open("entity.txt", "w") as file:
    #     json.dump(sqm_data, file, indent=4, sort_keys=True)
    # return sqm_data
    mission_name = sqm_data.get("sourceName", "").replace("_", " ")
    mission_data = sqm_data.get("Mission", {})
    entities = mission_data.get("Entities", {})

    with open(equipment_path) as equipment_file:
        equipment_code = equipment_file.read()
    # Regular expression pattern to extract variable assignments
    pattern = r"private\s+(\w+)\s*=\s*(.*?);"

    # Find all variable assignments using regular expressions
    matches = [] if equipment_code == "" else re.findall(pattern, equipment_code, re.DOTALL)

    # Dictionary to store parsed variable assignments
    variables = {}

    # Iterate over matches and extract variable names and values
    for match in matches:
        variable_name = match[0]
        variable_value = match[1]
        # Remove comments from variable values
        variable_value = re.sub(
            r"\/\*.*?\*\/|\/\/.*$", "", variable_value, flags=re.MULTILINE
        )
        # Parse variable value as Python object
        parsed_value = None
        if variable_value.startswith("[") and variable_value.endswith("]"):
            # Handle array values
            array_items = variable_value[1:-1].split("],")
            parsed_value = [
                list(
                    map(
                        lambda x: x.strip().strip('"'),
                        item.strip().strip("[]").strip("\"'").split(","),
                    )
                )
                for item in array_items
            ]
            if len(parsed_value) == 1:
                parsed_value = parsed_value[0]  # Unwrap single element arrays
        else:
            # Handle other types of values
            parsed_value = variable_value.strip().strip("\"'")

        if parsed_value == "true":
            parsed_value = True
        elif parsed_value == "false":
            parsed_value = False
        elif type(parsed_value) is list and len(parsed_value) == 2:
            parsed_value[1] = True if parsed_value[1] == "true" else False
        variables[variable_name] = parsed_value

    for entity, entity_value in entities.items():
        # print(f"Entity: {entity}; Entity value: {entity_value}")
        if (
            type(entity_value) is not dict
            or entity_value.get("dataType", "") != "Group"
        ):
            if (
                type(entity_value) is dict
                and entity_value.get("dataType", "") == "Layer"
            ):
                # print(f"Name of entity: {entity}")
                for layer_entity, layer_entity_value in entity_value.get(
                    "Entities", {}
                ).items():
                    if (
                        type(layer_entity_value) is dict
                        and layer_entity_value.get("dataType", "") == "Group"
                    ):
                        for group, group_value in layer_entity_value.get(
                            "Entities", {}
                        ).items():
                            if type(group_value) is not dict:
                                continue
                            attributes = group_value.get("Attributes", {})
                            # print(f"Group: {group}; Group value: {group_value.keys()}")
                            is_playable = bool(attributes.get("isPlayable", 0))
                            is_player = bool(attributes.get("isPlayer", 0))
                            if not any((is_playable, is_player)):
                                continue
                            players.append(group_value)
            else:
                continue
        elif type(entity_value) is dict and entity_value.get("dataType", "") == "Group":
            for layer_entity, layer_entity_value in entity_value.get(
                "Entities", {}
            ).items():
                if (
                    type(layer_entity_value) is dict
                    and layer_entity_value.get("dataType", "") == "Object"
                ):
                    if type(layer_entity_value) is not dict:
                        continue
                    attributes = layer_entity_value.get("Attributes", {})
                    # print(f"Group: {group}; Group value: {group_value.keys()}")
                    is_playable = bool(attributes.get("isPlayable", 0))
                    is_player = bool(attributes.get("isPlayer", 0))
                    if not any((is_playable, is_player)):
                        continue
                    players.append(layer_entity_value)
    for player in players:
        if type(player) is not dict or player.get("dataType", "") != "Object":
            continue
        # inventory_data[item_name] = item_value
        attributes = player.get("Attributes", {})
        is_playable = bool(attributes.get("isPlayable", 0))
        is_player = bool(attributes.get("isPlayer", 0))
        if not any((is_playable, is_player)):
            continue
        # print(f"Item class: {player}")
        description = attributes.get("description", {})
        inventory = attributes.get("Inventory", {})

        inventory = {
            "primaryWeapon": inventory.get(
                "primaryWeapon", {"name": "None", "displayName": "None"}
            ),
            "secondaryWeapon": inventory.get(
                "secondaryWeapon", {"name": "None", "displayName": "None"}
            ),
            "handgun": inventory.get(
                "handgun", {"name": "None", "displayName": "None"}
            ),
            "uniform": inventory.get(
                "uniform", {"name": "None", "displayName": "None"}
            ),
            "vest": inventory.get("vest", {"name": "None", "displayName": "None"}),
            "backpack": inventory.get(
                "backpack", {"name": "None", "displayName": "None"}
            ),
            "map": inventory.get(
                "map",
                (
                    variables["_mapsForEveryone"][0]
                    if variables.get("_mapsForEveryone", ["", False])[1]
                    else "None"
                ),
            ),
            "compass": inventory.get(
                "compass",
                (
                    variables["_compassesForEveryone"][0]
                    if variables.get("_compassesForEveryone", ["", False])[1]
                    else "None"
                ),
            ),
            "watch": inventory.get(
                "watch",
                (
                    (
                        variables["_handWatchesForEveryone"][0]
                        if variables.get("_handWatchesForEveryone", ["", False])[1]
                        else "None"
                    )
                    if "TFAR_microdagr" in PROGRAMMER_REQUIRED_RADIOS
                    else inventory.get(
                        "radio",
                        (
                            variables["_radiosForEveryone"][0]
                            if variables.get("_radiosForEveryone", ["", False])[1]
                            else "None"
                        ),
                    )
                ),
            ),
            "goggles": inventory.get("goggles", "None"),
            "radio": inventory.get(
                "radio",
                (
                    variables["_radiosForEveryone"][0]
                    if variables.get("_radiosForEveryone", ["", False])[1]
                    else "None"
                ),
            ),
            "headgear": inventory.get("headgear", "None"),
            "binocular": inventory.get(
                "binocular",
                {
                    "name": (
                        variables["_binocularsForEveryone"][0]
                        if variables.get("_binocularsForEveryone", ["", False])[1]
                        else "None"
                    )
                },
            ),
            "gps": inventory.get(
                "gps",
                (
                    variables["_GPSsForEveryone"][0]
                    if variables.get("_GPSsForEveryone", ["", False])[1]
                    else "None"
                ),
            ),
            "hmd": inventory.get("hmd", "None"),
        }

        # Uniform
        uniform = inventory["uniform"]
        items = []
        for cargo in CARGO_NAMES:
            if cargo in uniform:
                if "items" in uniform[cargo]:
                    del uniform[cargo]["items"]
                for item, item_value in uniform[cargo].items():
                    if type(item_value) is not dict:
                        continue
                    name = item_value.get("name")
                    item_dict = {"name": name}
                    if cargo == "WeaponCargo":
                        if "primaryMuzzleMag" in item_value:
                            primary_muzzle_mag = item_value["primaryMuzzleMag"]
                            item_dict["primaryMuzzleMag"] = {
                                "name": primary_muzzle_mag.get("name"),
                                "displayName": item_data.get(
                                    primary_muzzle_mag.get("name")
                                ),
                                "count": primary_muzzle_mag.get("count"),
                            }
                        if "secondaryMuzzleMag" in item_value:
                            primary_muzzle_mag = item_value["secondaryMuzzleMag"]
                            item_dict["secondaryMuzzleMag"] = {
                                "name": primary_muzzle_mag.get("name"),
                                "displayName": item_data.get(
                                    primary_muzzle_mag.get("name")
                                ),
                                "count": primary_muzzle_mag.get("count"),
                            }
                    if name is not None:
                        display_name = item_data.get(name)
                        item_dict["displayName"] = display_name
                    count = item_value.get("count")
                    if count is not None:
                        item_dict["count"] = count
                    items.append(item_dict)

        # Print parsed variables
        if variables.get("_medicalAndMiscForEveryone", False):
            for item_name, item_count in variables.get("_uniformItems", []):
                if int(item_count) > 0:
                    item_dict = {
                        "name": item_name,
                        "displayName": item_data.get(item_name),
                        "count": item_count,
                    }
                    items.append(item_dict)

        items.sort(key=lambda item: str(item.get("displayName", item.get("name", ""))))
        inventory["uniform"] = {
            "name": uniform.get("typeName"),
            "items": items,
            "displayName": item_data.get(inventory["uniform"].get("typeName")),
        }

        # Vest
        vest = inventory["vest"]
        items = []
        for cargo in CARGO_NAMES:
            if cargo in vest:
                if "items" in vest[cargo]:
                    del vest[cargo]["items"]
                for item, item_value in vest[cargo].items():
                    if type(item_value) is not dict:
                        continue
                    if type(item_value) is not dict:
                        continue
                    name = item_value.get("name")
                    item_dict = {"name": name}
                    if cargo == "WeaponCargo":
                        if "primaryMuzzleMag" in item_value:
                            primary_muzzle_mag = item_value["primaryMuzzleMag"]
                            item_dict["primaryMuzzleMag"] = {
                                "name": primary_muzzle_mag.get("name"),
                                "displayName": item_data.get(
                                    primary_muzzle_mag.get("name")
                                ),
                                "count": primary_muzzle_mag.get("count"),
                            }
                        if "secondaryMuzzleMag" in item_value:
                            primary_muzzle_mag = item_value["secondaryMuzzleMag"]
                            item_dict["secondaryMuzzleMag"] = {
                                "name": primary_muzzle_mag.get("name"),
                                "displayName": item_data.get(
                                    primary_muzzle_mag.get("name")
                                ),
                                "count": primary_muzzle_mag.get("count"),
                            }
                    if name is not None:
                        display_name = item_data.get(name)
                        item_dict["displayName"] = display_name
                    count = item_value.get("count")
                    if count is not None:
                        item_dict["count"] = count
                    items.append(item_dict)
        items.sort(key=lambda item: str(item.get("displayName", item.get("name", ""))))
        inventory["vest"] = {
            "name": vest.get("typeName"),
            "items": items,
            "displayName": item_data.get(inventory["vest"].get("typeName")),
        }

        # Backpack
        backpack = inventory["backpack"]
        items = []
        for cargo in CARGO_NAMES:
            if cargo in backpack:
                if "items" in backpack[cargo]:
                    del backpack[cargo]["items"]
                for item, item_value in backpack[cargo].items():
                    if type(item_value) is not dict:
                        continue
                    name = item_value.get("name")
                    item_dict = {"name": name}
                    if cargo == "WeaponCargo":
                        if "primaryMuzzleMag" in item_value:
                            primary_muzzle_mag = item_value["primaryMuzzleMag"]
                            item_dict["primaryMuzzleMag"] = {
                                "name": primary_muzzle_mag.get("name"),
                                "displayName": item_data.get(
                                    primary_muzzle_mag.get("name")
                                ),
                                "ammoLeft": primary_muzzle_mag.get("ammoLeft"),
                            }
                        if "secondaryMuzzleMag" in item_value:
                            secondary_muzzle_mag = item_value["secondaryMuzzleMag"]
                            item_dict["secondaryMuzzleMag"] = {
                                "name": secondary_muzzle_mag.get("name"),
                                "displayName": item_data.get(
                                    secondary_muzzle_mag.get("name")
                                ),
                                "ammoLeft": secondary_muzzle_mag.get("ammoLeft"),
                            }
                    if name is not None:
                        display_name = item_data.get(name)
                        item_dict["displayName"] = display_name
                    count = item_value.get("count")
                    if count is not None:
                        item_dict["count"] = count
                    items.append(item_dict)
        print(f"Items: {items}")
        items.sort(key=lambda item: str(item.get("displayName", item.get("name", ""))))
        inventory["backpack"] = {
            "name": backpack.get("typeName"),
            "items": items,
            "displayName": item_data.get(inventory["backpack"].get("typeName")),
        }

        if inventory.get("primaryWeapon"):
            if "firemode" in inventory["primaryWeapon"]:
                inventory["primaryWeapon"]["firemode"] = inventory["primaryWeapon"][
                    "firemode"
                ].split(":")[1]
            inventory["primaryWeapon"]["name"] = inventory["primaryWeapon"].get("name")
            inventory["primaryWeapon"]["displayName"] = item_data.get(
                inventory["primaryWeapon"].get("name")
            )
            if "primaryMuzzleMag" in inventory["primaryWeapon"]:
                inventory["primaryWeapon"]["primaryMuzzleMag"]["displayName"] = (
                    item_data.get(
                        inventory["primaryWeapon"]["primaryMuzzleMag"]["name"]
                    )
                )
            if "secondaryMuzzleMag" in inventory["primaryWeapon"]:
                inventory["primaryWeapon"]["secondaryMuzzleMag"]["displayName"] = (
                    item_data.get(
                        inventory["primaryWeapon"]["secondaryMuzzleMag"]["name"]
                    )
                )
            if "flashlight" in inventory["primaryWeapon"]:
                inventory["primaryWeapon"]["flashlight"] = {
                    "name": inventory["primaryWeapon"]["flashlight"],
                    "displayName": item_data.get(
                        inventory["primaryWeapon"]["flashlight"]
                    ),
                }
            if "muzzle" in inventory["primaryWeapon"]:
                inventory["primaryWeapon"]["muzzle"] = {
                    "name": inventory["primaryWeapon"]["muzzle"],
                    "displayName": item_data.get(inventory["primaryWeapon"]["muzzle"]),
                }
            if "optics" in inventory["primaryWeapon"]:
                inventory["primaryWeapon"]["optics"] = {
                    "name": inventory["primaryWeapon"]["optics"],
                    "displayName": item_data.get(inventory["primaryWeapon"]["optics"]),
                }
            if "underBarrel" in inventory["primaryWeapon"]:
                inventory["primaryWeapon"]["underBarrel"] = {
                    "name": inventory["primaryWeapon"]["underBarrel"],
                    "displayName": item_data.get(
                        inventory["primaryWeapon"]["underBarrel"]
                    ),
                }
        if inventory.get("handgun", {}).get("name", "") != "":
            if "firemode" in inventory["handgun"]:
                inventory["handgun"]["firemode"] = inventory["handgun"][
                    "firemode"
                ].split(":")[1]
            inventory["handgun"]["name"] = inventory["handgun"].get("name")
            inventory["handgun"]["displayName"] = item_data.get(
                inventory["handgun"].get("name")
            )
            if "primaryMuzzleMag" in inventory["handgun"]:
                inventory["handgun"]["primaryMuzzleMag"]["displayName"] = item_data.get(
                    inventory["handgun"]["primaryMuzzleMag"]["name"]
                )
            if "secondaryMuzzleMag" in inventory["handgun"]:
                inventory["handgun"]["secondaryMuzzleMag"]["displayName"] = (
                    item_data.get(inventory["handgun"]["secondaryMuzzleMag"]["name"])
                )
            if "flashlight" in inventory["handgun"]:
                inventory["handgun"]["flashlight"] = {
                    "name": inventory["handgun"]["flashlight"],
                    "displayName": item_data.get(inventory["handgun"]["flashlight"]),
                }
            if "muzzle" in inventory["handgun"]:
                inventory["handgun"]["muzzle"] = {
                    "name": inventory["handgun"]["muzzle"],
                    "displayName": item_data.get(inventory["handgun"]["muzzle"]),
                }
            if "optics" in inventory["handgun"]:
                inventory["handgun"]["optics"] = {
                    "name": inventory["handgun"]["optics"],
                    "displayName": item_data.get(inventory["handgun"]["optics"]),
                }
            if "underBarrel" in inventory["handgun"]:
                inventory["handgun"]["underBarrel"] = {
                    "name": inventory["handgun"]["underBarrel"],
                    "displayName": item_data.get(inventory["handgun"]["underBarrel"]),
                }
        if inventory.get("secondaryWeapon"):
            if "firemode" in inventory["secondaryWeapon"]:
                inventory["secondaryWeapon"]["firemode"] = inventory["secondaryWeapon"][
                    "firemode"
                ].split(":")[1]
            inventory["secondaryWeapon"]["name"] = inventory["secondaryWeapon"].get(
                "name"
            )
            inventory["secondaryWeapon"]["displayName"] = item_data.get(
                inventory["secondaryWeapon"].get("name")
            )
            if "primaryMuzzleMag" in inventory["secondaryWeapon"]:
                inventory["secondaryWeapon"]["primaryMuzzleMag"]["displayName"] = (
                    item_data.get(
                        inventory["secondaryWeapon"]["primaryMuzzleMag"]["name"]
                    )
                )
            if "secondaryMuzzleMag" in inventory["secondaryWeapon"]:
                inventory["secondaryWeapon"]["secondaryMuzzleMag"]["displayName"] = (
                    item_data.get(
                        inventory["secondaryWeapon"]["secondaryMuzzleMag"]["name"]
                    )
                )
            if "flashlight" in inventory["secondaryWeapon"]:
                inventory["secondaryWeapon"]["flashlight"] = {
                    "name": inventory["secondaryWeapon"]["flashlight"],
                    "displayName": item_data.get(
                        inventory["secondaryWeapon"]["flashlight"]
                    ),
                }
            if "muzzle" in inventory["secondaryWeapon"]:
                inventory["secondaryWeapon"]["muzzle"] = {
                    "name": inventory["secondaryWeapon"]["muzzle"],
                    "displayName": item_data.get(
                        inventory["secondaryWeapon"]["muzzle"]
                    ),
                }
            if "optics" in inventory["secondaryWeapon"]:
                inventory["secondaryWeapon"]["optics"] = {
                    "name": inventory["secondaryWeapon"]["optics"],
                    "displayName": item_data.get(
                        inventory["secondaryWeapon"]["optics"]
                    ),
                }
            if "underBarrel" in inventory["secondaryWeapon"]:
                inventory["secondaryWeapon"]["underBarrel"] = {
                    "name": inventory["secondaryWeapon"]["underBarrel"],
                    "displayName": item_data.get(
                        inventory["secondaryWeapon"]["underBarrel"]
                    ),
                }
        if inventory.get("headgear", "None") != "None":
            inventory["headgear"] = {
                "name": inventory["headgear"],
                "displayName": item_data.get(inventory["headgear"]),
            }
        inventory["binocular"]["displayName"] = item_data.get(
            inventory["binocular"].get("name")
        )
        inventory["compass"] = {
            "name": inventory["compass"],
            "displayName": item_data.get(inventory["compass"]),
        }
        inventory["gps"] = {
            "name": inventory["gps"],
            "displayName": item_data.get(inventory["gps"]),
        }
        inventory["map"] = {
            "name": inventory["map"],
            "displayName": item_data.get(inventory["map"]),
        }
        inventory["radio"] = {
            "name": inventory["radio"],
            "displayName": item_data.get(inventory["radio"]),
        }
        inventory["watch"] = {
            "name": inventory["watch"],
            "displayName": item_data.get(inventory["watch"]),
        }
        inventory["goggles"] = {
            "name": inventory["goggles"],
            "displayName": item_data.get(inventory["goggles"]),
        }
        inventory["hmd"] = {
            "name": inventory["hmd"],
            "displayName": item_data.get(inventory["hmd"]),
        }

        inventory["description"] = description
        player_inventories.append(inventory)
    return [mission_name, player_inventories]


# with open("output.sqm", "w") as output:
#     output.write(sqm_json)
