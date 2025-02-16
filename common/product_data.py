import json
import logging


def load_json(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


# Werte anhand des class_name auslesen
def get_item_by_class_name(json_data, class_name):
    for item in json_data:
        logging.info(f"curenet item: {item}")
        logging.info(f'curenet item: {item["class_name"].lower()} compare to {class_name.lower()}')
        if item["class_name"].lower() == class_name.lower():

            return item
    return None

def get_product_with_data(classification):
    json_data = load_json("class.json")
    logging.info(f"json_data: {json_data}")
    item = get_item_by_class_name(json_data, classification)
    logging.info(f"item: {item}")
    data = {
        "Produkt": item["class_name"],
        "Informationen": item.get("info"),
        "Regal": item.get("regal"),
        "Preis_pro_stueck": item["preis"].get("pro_stueck"),
        "Preis_pro_kg": item["preis"].get("pro_kg")
    }
    logging.info(f"item_data: {data}")
