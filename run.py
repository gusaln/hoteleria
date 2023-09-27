import os
import sys

from app import App
from cli import Vista
from config import leer_config
from term import print_titulo

# Soluciona problemas con importar los otros módulos
sys.path.append(os.path.join(os.path.dirname(__file__)))


def run(app: App):
    """Ejecuta el TUI de la aplicación"""

    print_titulo("Bienvenido al sistema de gestión de la cadena '%s'" %
                 app.cadenaHotelera)

    vista = Vista.Menu

    while True:
        if vista is Vista.Salir or vista is None:
            return

        vista_cb = vista.vista()
        if vista_cb is not None:
            vista = vista_cb(app, vista)
            # print(vista.name)
            # input("Presione <enter> para continuar")

        print("-" * 80, end="\n\n")


if __name__ == "__main__":
    app = App(leer_config())
    app.cargar()

    run(app)
    app.persistir()
