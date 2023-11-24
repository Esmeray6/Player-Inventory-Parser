import os
import sys
import armaclass
import json


CARGO_NAMES = ("MagazineCargo", "ItemCargo", "WeaponCargo")

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    data_file = os.path.join(sys._MEIPASS, "data_unorganized.json")
else:
    data_file = "data_unorganized.json"

with open(data_file) as file:
    item_data = json.load(file)


def parse_mission(mission: str):
    player_inventories = []
    players = []
    inventory_data = {}
    sqm_data = armaclass.parse(mission)
    # with open("entity.txt", "w") as file:
    #     json.dump(sqm_data, file, indent=4, sort_keys=True)
    # return sqm_data
    mission_name = sqm_data.get("sourceName", "").replace("_", " ")
    mission_data = sqm_data.get("Mission", {})
    entities = mission_data.get("Entities", {})
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

        if "uniform" in inventory:
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
            inventory["uniform"] = {
                "name": uniform.get("typeName"),
                "items": items,
                "displayName": item_data.get(inventory["uniform"].get("typeName")),
            }
        if "vest" in inventory:
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
            items.sort(key=lambda item: item.get("displayName", ""))
            inventory["vest"] = {
                "name": vest.get("typeName"),
                "items": items,
                "displayName": item_data.get(inventory["vest"].get("typeName")),
            }
        if "backpack" in inventory:
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
            inventory["backpack"] = {
                "name": backpack.get("typeName"),
                "items": items,
                "displayName": item_data.get(inventory["backpack"].get("typeName")),
            }
        if "primaryWeapon" in inventory:
            if "firemode" in inventory["primaryWeapon"]:
                inventory["primaryWeapon"]["firemode"] = inventory["primaryWeapon"][
                    "firemode"
                ].split(":")[1]
            inventory["primaryWeapon"]["name"] = inventory["primaryWeapon"].get("name")
            inventory["primaryWeapon"]["displayName"] = item_data.get(
                inventory["primaryWeapon"].get("name")
            )
            if "primaryMuzzleMag" in inventory["primaryWeapon"]:
                inventory["primaryWeapon"]["primaryMuzzleMag"][
                    "displayName"
                ] = item_data.get(
                    inventory["primaryWeapon"]["primaryMuzzleMag"]["name"]
                )
            if "secondaryMuzzleMag" in inventory["primaryWeapon"]:
                inventory["primaryWeapon"]["secondaryMuzzleMag"][
                    "displayName"
                ] = item_data.get(
                    inventory["primaryWeapon"]["secondaryMuzzleMag"]["name"]
                )
            if "flashlight" in inventory["primaryWeapon"]:
                inventory["primaryWeapon"]["flashlight"] = {
                    "name": inventory["primaryWeapon"]["flashlight"],
                    "displayName": item_data[inventory["primaryWeapon"]["flashlight"]],
                }
            if "muzzle" in inventory["primaryWeapon"]:
                inventory["primaryWeapon"]["muzzle"] = {
                    "name": inventory["primaryWeapon"]["muzzle"],
                    "displayName": item_data[inventory["primaryWeapon"]["muzzle"]],
                }
            if "optics" in inventory["primaryWeapon"]:
                inventory["primaryWeapon"]["optics"] = {
                    "name": inventory["primaryWeapon"]["optics"],
                    "displayName": item_data[inventory["primaryWeapon"]["optics"]],
                }
            if "underBarrel" in inventory["primaryWeapon"]:
                inventory["primaryWeapon"]["underBarrel"] = {
                    "name": inventory["primaryWeapon"]["underBarrel"],
                    "displayName": item_data[inventory["primaryWeapon"]["underBarrel"]],
                }
        if "handgun" in inventory:
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
                inventory["handgun"]["secondaryMuzzleMag"][
                    "displayName"
                ] = item_data.get(inventory["handgun"]["secondaryMuzzleMag"]["name"])
            if "muzzle" in inventory["handgun"]:
                inventory["handgun"]["muzzle"] = {
                    "name": inventory["handgun"]["muzzle"],
                    "displayName": item_data[inventory["handgun"]["muzzle"]],
                }
            if "optics" in inventory["handgun"]:
                inventory["handgun"]["optics"] = {
                    "name": inventory["handgun"]["optics"],
                    "displayName": item_data[inventory["handgun"]["optics"]],
                }
            if "underBarrel" in inventory["handgun"]:
                inventory["handgun"]["underBarrel"] = {
                    "name": inventory["handgun"]["underBarrel"],
                    "displayName": item_data[inventory["handgun"]["underBarrel"]],
                }
        if "secondaryWeapon" in inventory:
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
                inventory["secondaryWeapon"]["primaryMuzzleMag"][
                    "displayName"
                ] = item_data.get(
                    inventory["secondaryWeapon"]["primaryMuzzleMag"]["name"]
                )
            if "secondaryMuzzleMag" in inventory["secondaryWeapon"]:
                inventory["secondaryWeapon"]["secondaryMuzzleMag"][
                    "displayName"
                ] = item_data.get(
                    inventory["secondaryWeapon"]["secondaryMuzzleMag"]["name"]
                )
            if "muzzle" in inventory["secondaryWeapon"]:
                inventory["secondaryWeapon"]["muzzle"] = {
                    "name": inventory["secondaryWeapon"]["muzzle"],
                    "displayName": item_data[inventory["secondaryWeapon"]["muzzle"]],
                }
            if "optics" in inventory["secondaryWeapon"]:
                inventory["secondaryWeapon"]["optics"] = {
                    "name": inventory["secondaryWeapon"]["optics"],
                    "displayName": item_data[inventory["secondaryWeapon"]["optics"]],
                }
            if "underBarrel" in inventory["secondaryWeapon"]:
                inventory["secondaryWeapon"]["underBarrel"] = {
                    "name": inventory["secondaryWeapon"]["underBarrel"],
                    "displayName": item_data[
                        inventory["secondaryWeapon"]["underBarrel"]
                    ],
                }
        if "binocular" in inventory:
            inventory["binocular"]["displayName"] = item_data.get(
                inventory["binocular"].get("name")
            )
        if "compass" in inventory:
            inventory["compass"] = {
                "name": inventory["compass"],
                "displayName": item_data.get(inventory["compass"]),
            }
        if "gps" in inventory:
            inventory["gps"] = {
                "name": inventory["gps"],
                "displayName": item_data.get(inventory["gps"]),
            }
        if "map" in inventory:
            inventory["map"] = {
                "name": inventory["map"],
                "displayName": item_data.get(inventory["map"]),
            }
        if "radio" in inventory:
            inventory["radio"] = {
                "name": inventory["radio"],
                "displayName": item_data.get(inventory["radio"]),
            }
        if "watch" in inventory:
            inventory["watch"] = {
                "name": inventory["watch"],
                "displayName": item_data.get(inventory["watch"]),
            }
        if "headgear" in inventory:
            inventory["headgear"] = {
                "name": inventory["headgear"],
                "displayName": item_data.get(inventory["headgear"]),
            }
        if "goggles" in inventory:
            inventory["goggles"] = {
                "name": inventory["goggles"],
                "displayName": item_data.get(inventory["goggles"]),
            }
        if "hmd" in inventory:
            inventory["hmd"] = {
                "name": inventory["hmd"],
                "displayName": item_data.get(inventory["hmd"]),
            }

        inventory["description"] = description
        player_inventories.append(inventory)
    return [mission_name, player_inventories]


# with open("output.sqm", "w") as output:
#     output.write(sqm_json)
