import datetime
from typing import List

from data import Reservacion


def print_error(m):
    """Imprime un error"""
    print("!!!" + m)


def print_titulo(titulo):
    """Imprime un título"""
    l = len(titulo)
    print()
    print("#" * (l + 4))
    print("#", titulo, "#")
    print("#" * (l + 4))
    print()


def print_seccion(*seccion):
    """Imprime el encabezado de una sección"""
    print(":::", *seccion)


def print_info(*info):
    """Imprime información"""
    print("  .", *info)


def revisar_caracteres(palabra):
    """Valida que una palabra solo contenga caracteres alfanuméricos y ciertos símbolos"""
    for letra in palabra:
        if letra in [
            ":",
            ";",
            "{",
            "}",
            "[",
            "]",
            "?",
            "!",
            "/",
            "<",
            ">",
            "=",
            "+",
            "_",
        ]:
            print("Solo se pueden leer valores alfanuméricos, intente de nuevo")
            return True
    return False


def leer_str(mensaje=None, prompt="> "):
    """Lee un string

    Esta función imprime un mensaje de haber uno, salta una línea y espera la entrada del usuario
    """
    if mensaje is not None:
        print(mensaje)

    if not prompt.endswith("> "):
        prompt = prompt + "> "

    res = input(prompt).strip()
    while revisar_caracteres(res):
        res = input(prompt).strip()
    return res


def leer_numero(mensaje=None, predeterminado=None):
    """Lee un valor entero"""
    while True:
        try:
            s = leer_str(mensaje)

            if predeterminado is not None and s == "":
                return predeterminado

            return int(s)
        except ValueError:
            print_error("Debe indicar un número")


def leer_si_no(mensaje):
    """Lee un bolean"""
    print(mensaje)

    return leer_str(prompt="['s' para sí / 'n' para no]").lower() == "s"


def seleccionar_opcion(mensaje: str, opciones, valores=[]):
    """Muestra un selector de opciones
    El selector siempre muestra la primera opción como cero.

    :param mensaje: es el mensaje que se muestra en el selector
    :param opciones: son las opciones que se van a mostrar
    :param valores: OPCIONAL. Digamos que el texto que se quiere mostrar en una opción no es el mismo que el valor que se quiere retornar.
            Este es un arreglo opcional con los valores que corresponden a cada opción
    """
    if len(valores) != len(opciones):
        valores = opciones

    while True:
        print(mensaje)
        for i, o in enumerate(opciones):
            print(f"  [{i+1}] {o}")

        raw = leer_numero()
        if raw > 0 and raw <= len(opciones):
            return valores[raw - 1]
        print_error("Opción inválida")
        print("")


### Operaciones específicas


def print_tabla_reservaciones(reservaciones: List[Reservacion]):
    """Imprime una tabla con las reservaciones"""

    fmt = "{id: <8}  {cliente_ci: <8}  {habitacion: <4}  {estado: <9}  {fecha_entrada: <10}  {fecha_salida: <10}  {precio: >6}  {personas_count: ^13}  {observaciones}"
    print(
        fmt.format(
            id="ID",
            cliente_ci="Cliente",
            habitacion="Hab.",
            fecha_entrada="F. Entrada",
            fecha_salida="F. Salida",
            estado="Estado",
            precio="Precio",
            personas_count="# de personas",
            observaciones="Observaciones",
        ),
    )
    for r in reservaciones:
        print(
            fmt.format(
                id=r.id,
                cliente_ci=r.cliente.ci,
                habitacion=r.habitacion,
                fecha_entrada=r.fecha_entrada.strftime("%d/%m/%Y"),
                fecha_salida=r.fecha_salida.strftime("%d/%m/%Y"),
                estado=r.estado,
                precio=r.precio,
                personas_count=r.personas_count,
                observaciones=r.observaciones or "-",
            )
        )


def leer_date(mensaje: str):
    while True:
        try:
            return datetime.datetime.strptime(leer_str(mensaje), "%d/%m/%Y")
        except ValueError:
            print_error("Debe indicar una fecha en el formato dd/mm/aaaa")
