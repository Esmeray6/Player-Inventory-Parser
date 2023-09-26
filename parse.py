import armaclass
import json

with open("data_unorganized.json") as file:
    item_data = json.load(file)


def parse_mission(mission: str):
    inventory_data = {}
    sqm_data = armaclass.parse(mission)
    # return sqm_data
    mission_data = sqm_data.get("Mission", {})
    entities = mission_data.get("Entities", {})
    for entity, entity_value in entities.items():
        # print(f"Entity: {entity}; Entity value: {entity_value}")
        if (
            type(entity_value) is not dict
            or entity_value.get("dataType", "") != "Group"
        ):
            continue
        # print(f"Entity: {entity}")
        for attribute, attribute_value in entity_value.get(
            "CustomAttributes", {}
        ).items():
            # print(f"Attribute: {attribute}; Attribute value: {attribute_value}")
            if (
                type(attribute_value) is not dict
                or attribute_value.get("property", "") != "groupID"
            ):
                continue
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

            inventory_data[description] = inventory
    return inventory_data


# with open("output.sqm", "w") as output:
#     output.write(sqm_json)
