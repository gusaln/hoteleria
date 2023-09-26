import os
import sys

from app import App
from config import leer_config

# Soluciona problemas con importar los otros módulos
sys.path.append(os.path.join(os.path.dirname(__file__)))

if __name__ == "__main__":
    app = App(leer_config())

    app.cargar()

    app.run()

    app.persistir()
