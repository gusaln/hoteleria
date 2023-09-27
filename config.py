import json
import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(CURRENT_DIR, "data", "config.json")


class Config():
    """Representa la configuración del sistema"""

    def __init__(self, cadena: str, archivo_hoteles: str, archivo_reservaciones: str, archivo_clientes: str, archivo_actividades: str):
        self.cadena = cadena
        self.archivo_hoteles = archivo_hoteles
        self.archivo_reservaciones = archivo_reservaciones
        self.archivo_clientes = archivo_clientes
        self.archivo_actividades = archivo_actividades


def leer_config():
    """Lee el archivo de configuración"""

    path = CONFIG_FILE
    if not os.path.exists(path):
        path = os.path.join(CURRENT_DIR, "seeds", "config.json")
    with open(path) as fp:
        raw = json.load(fp)
        return Config(raw["cadena"], raw["archivo_hoteles"], raw["archivo_reservaciones"], raw["archivo_clientes"], raw["archivo_actividades"])
