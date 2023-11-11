import os
import sys
import armaclass
import json

if getattr(sys, "frozen", False):
    data_file = os.path.join(sys._MEIPASS, "data_unorganized.json")
else:
    data_file = "data_unorganized.json"

with open(data_file) as file:
    item_data = json.load(file)


def parse_mission(mission: str):
    player_inventories = []
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
                print(f"Name of entity: {entity}")
                for layer_entity, layer_entity_value in entity_value.get(
                    "Entities", {}
                ).items():
                    if (
                        type(layer_entity_value) is dict
                        and layer_entity_value.get("dataType", "") == "Group"
                    ):
                        print(f"Name of layer entity: {layer_entity}")
                        entity = layer_entity
                        entity_value = layer_entity_value
            else:
                continue
        # print(f"Entity: {entity}")
        for item_name, item_value in (entity_value.get("Entities", {})).items():
            if (
                not type(item_value) is dict
                or item_value.get("dataType", "") != "Object"
            ):
                continue
            # print(f"Item name: {item_name}; Item value: {item_value}")
            # inventory_data[item_name] = item_value
            attributes = item_value.get("Attributes", {})
            is_playable = bool(attributes.get("isPlayable", 0))
            if not is_playable:
                continue
            description = attributes.get("description", {})
            inventory = attributes.get("Inventory", {})

            if "uniform" in inventory:
                uniform = inventory["uniform"]
                inventory["uniform"] = {
                    "name": uniform.get("typeName"),
                    "items": {
                        **uniform.get("ItemCargo", {}),
                        **uniform.get("MagazineCargo", {}),
                    },
                    "displayName": item_data.get(inventory["uniform"].get("typeName")),
                }
                items = []
                for item, item_value in inventory["uniform"]["items"].items():
                    # Make sure we're looking at the cargo, not any other items
                    if type(item_value) is not dict:
                        continue
                    name = item_value.get("name")
                    if name is not None:
                        display_name = item_data.get(name)
                        inventory["uniform"]["items"][item][
                            "displayName"
                        ] = display_name
                    items.append(item_value)
                inventory["uniform"]["items"] = items
            if "vest" in inventory:
                vest = inventory["vest"]
                inventory["vest"] = {
                    "name": vest.get("typeName"),
                    "items": {
                        **vest.get("ItemCargo", {}),
                        **vest.get("MagazineCargo", {}),
                    },
                    "displayName": item_data.get(inventory["vest"].get("typeName")),
                }
                items = []
                for item, item_value in inventory["vest"]["items"].items():
                    if type(item_value) is not dict:
                        continue
                    name = item_value.get("name")
                    if name is not None:
                        display_name = item_data.get(name)
                        inventory["vest"]["items"][item]["displayName"] = display_name
                    items.append(item_value)
                inventory["vest"]["items"] = items
            if "backpack" in inventory:
                backpack = inventory["backpack"]
                inventory["backpack"] = {
                    "name": backpack.get("typeName"),
                    "items": {
                        **backpack.get("ItemCargo", {}),
                        **backpack.get("MagazineCargo", {}),
                    },
                    "displayName": item_data.get(inventory["backpack"].get("typeName")),
                }
                items = []
                for item, item_value in inventory["backpack"]["items"].items():
                    if type(item_value) is not dict:
                        continue
                    name = item_value.get("name")
                    if name is not None:
                        display_name = item_data.get(name)
                        inventory["backpack"]["items"][item][
                            "displayName"
                        ] = display_name
                    items.append(item_value)
                inventory["backpack"]["items"] = items

            if "primaryWeapon" in inventory:
                if "firemode" in inventory["primaryWeapon"]:
                    inventory["primaryWeapon"]["firemode"] = inventory["primaryWeapon"][
                        "firemode"
                    ].split(":")[1]
                inventory["primaryWeapon"]["name"] = inventory["primaryWeapon"].get(
                    "name"
                )
                inventory["primaryWeapon"]["displayName"] = item_data.get(
                    inventory["primaryWeapon"].get("name")
                )
                if "primaryMuzzleMag" in inventory["primaryWeapon"]:
                    inventory["primaryWeapon"]["primaryMuzzleMag"][
                        "displayName"
                    ] = item_data.get(
                        inventory["primaryWeapon"]["primaryMuzzleMag"]["name"]
                    )
                if "flashlight" in inventory["primaryWeapon"]:
                    inventory["primaryWeapon"]["flashlight"] = {
                        "name": inventory["primaryWeapon"]["flashlight"],
                        "displayName": item_data[
                            inventory["primaryWeapon"]["flashlight"]
                        ],
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
                        "displayName": item_data[
                            inventory["primaryWeapon"]["underBarrel"]
                        ],
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
                    inventory["handgun"]["primaryMuzzleMag"][
                        "displayName"
                    ] = item_data.get(inventory["handgun"]["primaryMuzzleMag"]["name"])
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
                    inventory["secondaryWeapon"]["firemode"] = inventory[
                        "secondaryWeapon"
                    ]["firemode"].split(":")[1]
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
                if "muzzle" in inventory["secondaryWeapon"]:
                    inventory["secondaryWeapon"]["muzzle"] = {
                        "name": inventory["secondaryWeapon"]["muzzle"],
                        "displayName": item_data[
                            inventory["secondaryWeapon"]["muzzle"]
                        ],
                    }
                if "optics" in inventory["secondaryWeapon"]:
                    inventory["secondaryWeapon"]["optics"] = {
                        "name": inventory["secondaryWeapon"]["optics"],
                        "displayName": item_data[
                            inventory["secondaryWeapon"]["optics"]
                        ],
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
