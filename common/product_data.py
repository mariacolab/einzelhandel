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
    json_data = load_json("common/class.json")
    logging.info(f"json_data: {json_data}")
    item = get_item_by_class_name(json_data, classification)
    logging.info(f"item: {item}")
    data = {
        "Produkt": item.get("class_name", ""),
        "Informationen": item.get("info", "") or "",
        "Regal": item.get("regal", "") or "",
        "Preis_pro_stueck": item.get("preis", {}).get("pro_stueck", "") or "",
        "Preis_pro_kg": item.get("preis", {}).get("pro_kg", "") or ""
    }
    logging.info(f"item_data: {data}")
    return data
