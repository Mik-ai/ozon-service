import json


def open_json(file_name: str) -> dict:
    with open(file_name, encoding="utf-8") as f:
        data = json.load(f)
    return data


def save_json(data: dict, file_name: str) -> None:
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f)
