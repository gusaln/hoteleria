import datetime
from typing import List

from data import Cliente, MejorCliente, Reservacion
import re


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

    print("-->", *info)


def leer_str(mensaje=None, prompt="> "):
    """Lee un string

    Esta función imprime un mensaje de haber uno, salta una línea y espera la entrada del usuario
    """
    if mensaje is not None:
        print(mensaje)

    if not prompt.endswith("> "):
        prompt = prompt + "> "

    return input(prompt).strip()


email_pattern = re.compile(
    "^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
)


def leer_email(mensaje=None):
    """Lee un email"""
    while True:
        email = leer_str(mensaje)
        if email_pattern.match(email):
            return email

        print_error("Email inválido")


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
    """Lee un boolean"""
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

    fmt = "{id: <13}  {cliente_ci: <8}  {habitacion: <4}  {estado: <9}  {fecha_entrada: <10}  {fecha_salida: <10}  {duracion: <8}  {precio: >6}  {personas_count: ^13}  {observaciones}"
    print(
        fmt.format(
            id="ID",
            cliente_ci="Cliente",
            habitacion="Hab.",
            fecha_entrada="F. Entrada",
            fecha_salida="F. Salida",
            duracion="Duración",
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
                duracion=r.duracion(),
                estado=r.estado,
                precio=r.precio,
                personas_count=r.personas_count,
                observaciones=r.observaciones or "-",
            )
        )
    print()


def print_tabla_mejores_clientes(clientes: List[MejorCliente]):
    """Imprime una tabla con los clientes"""

    fmt = "{ci: <8}  {nombre: <24}  {count: <3}"
    print(
        fmt.format(
            ci="C.I.",
            nombre="Nombre",
            email="Email",
            count="# Reservaciones",
        ),
    )
    for cliente, count in clientes:
        print(
            fmt.format(
                ci=cliente.ci,
                nombre=cliente.nombre,
                count=count,
            )
        )
    print()


def leer_date(mensaje: str):
    """Lee una fecha"""
    while True:
        try:
            return datetime.datetime.strptime(
                leer_str(mensaje + " (formato dd/mm/aaaa)"), "%d/%m/%Y"
            )
        except ValueError:
            print_error("Debe indicar una fecha en el formato dd/mm/aaaa")
