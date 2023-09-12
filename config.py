import json
import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(CURRENT_DIR, "data", "config.json")


def leer_config():
    """Lee el archivo de configuración"""

    path = CONFIG_FILE
    if not os.path.exists(path):
        path = os.path.join(CURRENT_DIR, "seed", "config.json")
    with open(CONFIG_FILE) as fp:
        return json.load(fp)
