import json
import os
import hashlib

DATA_FILE = "money_data.json"


def default_data():
    return {
        "setup_done": False,
        "name": "",
        "password_hash": "",
        "balance": 0,
        "transactions": [],
        "goals": []
    }


def load_data():
    if not os.path.exists(DATA_FILE):
        return default_data()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return default_data()


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )


def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def check_password(password, password_hash):
    return hash_password(password) == password_hash

