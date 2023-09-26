import datetime
from enum import IntEnum, auto
import json
import os
from typing import List, Dict
from config import CURRENT_DIR, Config
from data import Cliente, HabitacionTipo, Hotel, MejorCliente, Reservacion, ReservacionEstado
import csv
from listas import Queue

from ordenamiento import Ordenable, heapsort, mergesort, quicksort, shellsort
from term import *


PARAMETROS_ORDEN = dict(
    (i + 1, p)
    for i, p in enumerate(
        (
            ["F. de entrada", lambda r: r.fecha_entrada],
            ["F. de salida", lambda r: r.fecha_salida],
            ["Estado", lambda r: r.estado],
            ["Habitación", lambda r: r.habitacion],
            ["Duración estadía", lambda r: r.duracion()],
            ["Precio", lambda r: r.precio],
            ["# personas", lambda r: r.personas_count],
            ["ID", lambda r: r.id],
        )
    )
)


class App:
    """
    Representa a la aplicación.

    Contiene el estado actual de la aplicación así como sus operaciones.
    """

    def __init__(self, config: Config):
        self.config = config
        self.cadenaHotelera = config.cadena

        self.hoteles = Queue()
        self.clientes = {}
        self.reservaciones = Queue()

        # Esta línea es para ayudar al IDE a entender que aquí va a un Hotel
        self.hotelSeleccionado = Hotel(0, "", "", {}, {})
        self.hotelSeleccionado = None

        self.ordenamiento = [1]

    ## Métodos de I.O.
    def cargar(self):
        """Carga los datos del sistema.

        De no haber datos, se utilizan cargan los datos de muestra como valores iniciales.
        """

        print_info("Cargando archivos de datos")

        clientes_file_path = os.path.abspath(self.config.archivo_clientes)
        if not os.path.exists(clientes_file_path):
            clientes_file_path = os.path.join(CURRENT_DIR, "seeds", "clientes.csv")

        with open(clientes_file_path) as fp:
            for row in csv.reader(
                fp.readlines(),
                delimiter=";",
                lineterminator="\n",
                quoting=csv.QUOTE_MINIMAL,
            ):
                id, nombre, email = row
                self.clientes[id] = Cliente(id, nombre, email)

        hoteles_file_path = os.path.abspath(self.config.archivo_hoteles)
        if not os.path.exists(hoteles_file_path):
            hoteles_file_path = os.path.join(CURRENT_DIR, "seeds", "hoteles.json")

        with open(hoteles_file_path) as fp:
            hoteles = json.load(fp)
            for hotelRaw in hoteles:
                tipos = {}
                tiposRaw = hotelRaw["tipos"]
                for tipo in tiposRaw:
                    tipos[tipo["nombre"]] = HabitacionTipo(tipo["nombre"], tipo["capacidad"], tipo["precio"])

                self.hoteles.push(Hotel(
                    hotelRaw["nombre"],
                    hotelRaw["direccion"],
                    hotelRaw["habitaciones"],
                    tipos,
                    hotelRaw["id"],
                ))

        reservaciones_file_path = os.path.abspath(self.config.archivo_reservaciones)
        if not os.path.exists(reservaciones_file_path):
            reservaciones_file_path = os.path.join(
                CURRENT_DIR, "seeds", "reservaciones.csv"
            )

        with open(reservaciones_file_path) as fp:
            for row in csv.reader(
                fp.readlines(),
                delimiter=";",
                lineterminator="\n",
                quoting=csv.QUOTE_MINIMAL,
            ):
                (
                    id,
                    hotel_id,
                    cliente_ci,
                    habitacion,
                    estado,
                    fecha_entrada,
                    fecha_salida,
                    hora_entrada,
                    hora_salida,
                    precio,
                    personas_count,
                    observaciones,
                ) = row
                fecha_entrada = datetime.datetime.strptime(fecha_entrada, "%Y-%m-%d")
                fecha_salida = datetime.datetime.strptime(fecha_salida, "%Y-%m-%d")
                hora_entrada = datetime.datetime.strptime(hora_entrada, "%H:%M").time()
                hora_salida = datetime.datetime.strptime(hora_salida, "%H:%M").time()
                precio = float(precio)

                self.reservaciones.push(
                    Reservacion(
                        hotel_id,
                        self.clientes[cliente_ci],
                        habitacion,
                        ReservacionEstado(estado),
                        fecha_entrada,
                        fecha_salida,
                        precio,
                        hora_entrada,
                        hora_salida,
                        personas_count,
                        observaciones,
                        id=id,
                    )
                )

        # self.hotelSeleccionado = self.hoteles.peek()

        print_info("Datos cargados")

    def persistir(self):
        """Persiste el estado actual del sistema"""

        print_info("Guardando datos")

        clientes_file_path = os.path.abspath(self.config.archivo_clientes)
        hoteles_file_path = os.path.abspath(self.config.archivo_hoteles)
        reservaciones_file_path = os.path.abspath(self.config.archivo_reservaciones)

        with open(clientes_file_path, "w") as fp:
            csvwriter = csv.writer(
                fp, delimiter=";", lineterminator="\n", quoting=csv.QUOTE_MINIMAL
            )
            for id, cliente in self.clientes.items():
                csvwriter.writerow((id, cliente.nombre, cliente.email))

        with open(hoteles_file_path, "w") as fp:
            hoteles = [
                {"id": h.id, "nombre": h.nombre, "direccion": h.direccion, "habitaciones": h.habitaciones, "tipos": [h.habitacionesTipos[t].__dict__ for t in h.habitacionesTipos]} 
                for h in self.hoteles
                ]
            json.dump(hoteles, fp)

        with open(reservaciones_file_path, "w") as fp:
            csvwriter = csv.writer(
                fp, delimiter=";", lineterminator="\n", quoting=csv.QUOTE_MINIMAL
            )

            for reservacion in self.reservaciones:
                id = reservacion.id
                hotel_id = reservacion.hotel_id
                cliente_ci = reservacion.cliente.ci
                habitacion = reservacion.habitacion
                estado = reservacion.estado
                fecha_entrada = reservacion.fecha_entrada.strftime("%Y-%m-%d")
                fecha_salida = reservacion.fecha_salida.strftime("%Y-%m-%d")
                hora_entrada = reservacion.hora_entrada.strftime("%H:%M")
                hora_salida = reservacion.hora_salida.strftime("%H:%M")
                precio = reservacion.precio
                personas_count = reservacion.personas_count
                observaciones = reservacion.observaciones
                csvwriter.writerow(
                    (
                        id,
                        hotel_id,
                        cliente_ci,
                        habitacion,
                        estado,
                        fecha_entrada,
                        fecha_salida,
                        hora_entrada,
                        hora_salida,
                        precio,
                        personas_count,
                        observaciones,
                    )
                )

        print_info("Datos guardados")

    ## Operaciones de la App

    def esta_ocupada(
        self,
        habitacion: str,
        fecha_inicial: datetime.datetime,
        fecha_final: datetime.datetime,
    ):
        """Devuelve si la habitación está ocupada en el rango de fechas."""
        reservaciones = filter(lambda r: r.habitacion == habitacion, self.reservaciones)
        reservaciones = filter(
            lambda r: r.fecha_entrada >= fecha_inicial
            and r.fecha_salida <= fecha_final,
            reservaciones,
        )

        return len(reservaciones)

    def capacidad(self, habitacion: str) -> int:
        """Devuelve la capacidad de la habitación."""
        if not self.tiene_habitacion(habitacion):
            return 0

        return HabitacionTipo(self.habitaciones[habitacion]).capacidad()

    def tiene_habitacion(self, habitacion: str):
        """Devuelve si la habitación existe."""
        return self.hotelSeleccionado is not None and self.hotelSeleccionado.tiene_habitacion(habitacion)

    def tipo_habitacion(self, habitacion: str):
        """Devuelve el tipo de la habitación."""
        if self.hotelSeleccionado is not None:
            return self.hotelSeleccionado.tipo_habitacion(habitacion)
        return None

    def get_reservaciones_por_periodo(
        self, fecha_inicial: datetime.datetime, fecha_final: datetime.datetime
    ):
        """Devuelve las reservaciones que se encuentran en el rango de fechas."""

        return filter(
            lambda r: r.fecha_entrada < fecha_final and r.fecha_salida > fecha_inicial,
            self.reservaciones,
        )

    def reporte_en_periodo(
        self, fecha_inicial: datetime.datetime, fecha_final: datetime.datetime, asc=True
    ):
        """Devuelve un reporte de las reservaciones que se encuentran en el rango de fechas ordenadas por precio."""

        reservaciones = self.get_reservaciones_por_periodo(fecha_inicial, fecha_final)

        if asc:
            reservaciones = map(lambda r: Ordenable(r, r.precio), reservaciones)
        else:
            reservaciones = map(lambda r: Ordenable(r, -r.precio), reservaciones)

        reservaciones = list(reservaciones)
        mergesort(reservaciones)

        return [ordenable.data for ordenable in reservaciones]

    def reporte_cant_reservaciones(self, asc=True):
        """Devuelve un reporte de los mejores clientes.

        El criterio utilizado es la cantidad de reservaciones.
        """

        clientes_count = {}

        for r in self.reservaciones:
            if r.cliente.ci not in clientes_count:
                clientes_count[r.cliente.ci] = 1
            else:
                clientes_count[r.cliente.ci] += 1

        resultados = []
        if asc:
            resultados = map(
                lambda pair: Ordenable(pair[0], pair[1]),
                clientes_count.items(),
            )
        else:
            resultados = map(
                lambda pair: Ordenable(pair[0], -pair[1]),
                clientes_count.items(),
            )

        resultados = list(resultados)
        shellsort(resultados)

        return [
            MejorCliente(self.clientes[ordenable.data], clientes_count[ordenable.data])
            for ordenable in resultados
        ]

    def reporte_estadia(self, asc=True):
        """Devuelve un reporte de las reservaciones ordenadas por duración de estadía."""

        reservaciones = self.reservaciones

        if asc:
            reservaciones = map(
                lambda r: Ordenable(r, r.duracion()), self.reservaciones
            )
        else:
            reservaciones = map(
                lambda r: Ordenable(r, -r.duracion()), self.reservaciones
            )

        reservaciones = list(reservaciones)
        heapsort(reservaciones)

        return [ordenable.data for ordenable in reservaciones]

    def crear_reservacion(
        self,
        cliente_ci: str,
        habitacion: str,
        fecha_entrada: datetime.datetime,
        fecha_salida: datetime.datetime,
        hora_entrada: datetime.time = None,
        hora_salida: datetime.time = None,
        personas_count=1,
        observaciones=None,
    ) -> Reservacion:
        """Crea una nueva reservación."""

        precio_por_dia = self.precios[self.habitaciones[habitacion]]
        duracion_dias = (fecha_salida - fecha_entrada).days
        precio = precio_por_dia * duracion_dias

        r = Reservacion(
            self.hotelSeleccionado.id,
            self.clientes[cliente_ci],
            habitacion,
            ReservacionEstado.Pendiente,
            fecha_entrada,
            fecha_salida,
            precio,
            hora_entrada,
            hora_salida,
            personas_count,
            observaciones,
        )

        self.reservaciones.push(r)
        self.persistir()

        return r

    ## OPERACIONES DE CLI

    # VISTA_SALIR = -1
    # VISTA_MENU = 0
    # VISTA_RESERVAR = 1
    # VISTA_RESERVACIONES_LISTAR = 2
    # VISTA_RESERVACIONES_REPORTE_DEL_PERIODO = 3
    # VISTA_RESERVACIONES_REPORTE_MEJORES_CLIENTES = 4
    # VISTA_RESERVACIONES_REPORTE_DURACION = 5

    def run(self):
        """Ejecuta el TUI de la aplicación"""

        print_titulo("Bienvenido al sistema de gestión de la cadena '%s'" % self.cadenaHotelera)

        vista = Vista.Menu

        while True:
            if vista is Vista.Salir:
                return

            elif vista is Vista.Menu:
                vista = vista_menu(self, vista)

            elif vista is Vista.ReservacionesListar:
                vista = vista_reservaciones_listar(self, vista)

            elif vista is Vista.Reservar:
                vista = vista_reservar(self, vista)

            elif vista is Vista.ReservacionesReporteDelPeriodo:
                vista = vista_reservaciones_reporte_del_periodo(self, vista)

            elif vista is Vista.ReservacionesReporteMejoresClientes:
                vista = vista_reservaciones_reporte_mejores_clientes(self, vista)

            elif vista is Vista.ReservacionesReporteDuracion:
                vista = vista_reservaciones_reporte_duracion_estadias(self, vista)

            else:
                return

            print(vista, "-" * 80, end="\n\n")

    def format_ordenamiento(self):
        """Formatea el ordenamiento"""
        return ", ".join(
            ("" if o > 0 else "-") + PARAMETROS_ORDEN[abs(o)][0]
            for o in self.ordenamiento
        )

    def reservaciones_ordenadas(self):
        """Ordena las reservaciones"""

        ordenados = list(self.reservaciones)
        if len(self.ordenamiento) > 0:
            for ordenamiento in self.ordenamiento[::-1]:
                getter = PARAMETROS_ORDEN[abs(ordenamiento)][1]

                ordenables = [Ordenable(r, getter(r)) for r in ordenados]
                quicksort(ordenables)
                if ordenamiento < 0:
                    ordenados = [r.data for r in ordenables[::-1]]
                else:
                    ordenados = [r.data for r in ordenables]

        return ordenados


### Vistas ###

class Vista(IntEnum):
    """Vistas del TUI"""

    Menu = auto()

    HotelesListar = auto()

    Reservar = auto()
    ReservacionesListar = auto()
    ReservacionesReporteDelPeriodo = auto()
    ReservacionesReporteMejoresClientes = auto()
    ReservacionesReporteDuracion = auto()

    Salir = auto()

    def label(self):
        return {
            self.Salir: "Salir",
            self.Menu: "Menu",

            self.HotelesListar: "Ver Hoteles",

            self.Reservar: "Reservar",
            self.ReservacionesListar: "Ver Reservaciones",
            self.ReservacionesReporteDelPeriodo: "Reporte: reservaciones en período",
            self.ReservacionesReporteMejoresClientes: "Reporte: mejores clientes",
            self.ReservacionesReporteDuracion: "Reporte: duración de estadías",
        }[self.value]

def vista_menu(app: App, vista=None):
    """Muestra el menú principal"""

    print_seccion(app.cadenaHotelera + " - Menú")

    vista = seleccionar_opcion(
        "Seleccione una operación",
        [v.label() for v in Vista if v is not Vista.Menu],
        [v for v in Vista if v is not Vista.Menu],
    )

    return Vista(vista)

def vista_reservar(app: App, vista=None):
    """Muestra la vista de reservar"""
    print_seccion(app.cadenaHotelera + " - Reservar")

    fecha_inicial = leer_date("Indique la fecha en la que desea llegar")
    fecha_final = leer_date("Indique la fecha en la que desea salir")
    personas_count = leer_numero("Indique el número de personas que se quedarán", 1)

    reservaciones_del_periodo = set(
        r.habitacion
        for r in app.get_reservaciones_por_periodo(fecha_inicial, fecha_final)
    )
    tipos_utiles = [t for t in HabitacionTipo if t.capacidad() >= personas_count]

    habitaciones_disponibles = []
    for h, tipo in app.habitaciones.items():
        if h not in reservaciones_del_periodo and tipo in tipos_utiles:
            habitaciones_disponibles.append(h)

    if len(habitaciones_disponibles) < 0:
        print_info(
            "No tenemos habitaciones disponibles en ese período para esa cantidad de personas"
        )
        return Vista.Menu

    print_info("Tenemos habitaciones disponibles")
    for tipo, precio in app.precios.items():
        if tipo not in tipos_utiles:
            continue
        print(f"  - {HabitacionTipo(tipo).label()} en {precio}")

    if not leer_si_no(
        "¿Desa proceder con la reservación con alguna de estas opciones?"
    ):
        return Vista.Menu

    tipo_seleccionado = seleccionar_opcion(
        "Indique el tipo de habitación",
        [HabitacionTipo(tipo).label() for tipo in tipos_utiles],
        tipos_utiles,
    )

    duracion_dias = (fecha_final - fecha_inicial).days
    precio = duracion_dias * app.precios[tipo_seleccionado]

    habitacion = None
    for h in habitaciones_disponibles:
        if app.tipo_habitacion(h) == tipo_seleccionado:
            habitacion = h
            break

    if not leer_si_no(
        f"Sería un total de {precio} por la habitación {habitacion} por {duracion_dias} día(s) ¿Desa proceder?"
    ):
        return vista or Vista.Menu

    ci = "{:0>8}".format(leer_numero("Indique la C.I. del cliente"))
    if ci in app.clientes:
        print_info("Este cliente ya está registrado.")
        print_info(app.clientes[ci].nombre)
    else:
        print_info("Este cliente no esta registrado. Vamos a solucionarlo.")
        nombre = leer_str("¿Cuál es el nombre del cliente?")
        email = leer_email("¿Cuál es el email del cliente?")

        app.clientes[ci] = Cliente(ci, nombre, email)
        print_info("Cliente registrado.")

    observaciones = leer_str(
        "¿Alguna observación sobre de la reservación? (presione <enter> para dejar el campo vacío)"
    )
    if observaciones == "":
        observaciones = None

    reservacion = app.crear_reservacion(
        ci,
        habitacion,
        fecha_inicial,
        fecha_final,
        personas_count=personas_count,
        observaciones=observaciones,
    )

    print_info("Reservación registrada")
    print(reservacion)

    return Vista.Menu

def vista_reservaciones_listar(app: App, vista=None):
    """Muestra las reservaciones"""

    print_seccion(app.cadenaHotelera + " - Reservaciones")

    def seleccionar_orden():
        while True:
            print_info(
                "Estos son los parámetros por los que puede ordenar la lista:"
            )
            for p in PARAMETROS_ORDEN:
                print(f"  - [{p}] {PARAMETROS_ORDEN[p][0]}")

            print_info(
                "Indique el nro. de la opción para ordenar de forma ascendente y el nro. negativo para ordenar de forma descendente"
            )
            print_info(
                "Puede indicar varios valores separados por comas para ordenar por más de un parámetro de la forma '1, 2, -3'"
            )
            orden = leer_str(
                "Indique el orden o presione <enter> sin escribir nada para volver a la lista:"
            )
            if len(orden) == 0:
                return True

            try:
                orden = [
                    int(o) for o in filter(lambda s: len(s) > 0, orden.split(","))
                ]
            except ValueError:
                print_error(
                    "No se pudo procesar la entrada como parámetro de orden"
                )
                continue

            app.ordenamiento = list(
                filter(
                    lambda o: abs(o) in PARAMETROS_ORDEN,
                    orden,
                )
            )

            print_info(
                "Nuevo orden:",
                app.format_ordenamiento(),
            )

            break

        return True

    opciones = [
        ["Ordenar", seleccionar_orden],
        ["Volver al menú", lambda: False],
    ]

    while True:
        print_info(
            "Reservaciones ordenadas:",
            app.format_ordenamiento(),
        )
        print_tabla_reservaciones(app.reservaciones_ordenadas())
        print()

        accion = seleccionar_opcion(
            "Seleccione una operación",
            [o[0] for o in opciones],
            [o[1] for o in opciones],
        )

        if not accion():
            return Vista.Menu

    return vista or Vista.ReservacionesListar

def vista_reservaciones_reporte_del_periodo(app: App, vista=None):
    """Muestra el reporte del período"""

    print_seccion(app.cadenaHotelera + " - Reporte del período")
    reservaciones = app.reporte_en_periodo(
        leer_date("Ingrese fecha inicial"),
        leer_date("Ingrese fecha final"),
        not leer_si_no("¿Desea orden descendente?"),
    )

    print()
    print_tabla_reservaciones(reservaciones)
    input("Presione <enter> para volver al menú > ")

    return Vista.Menu

def vista_reservaciones_reporte_mejores_clientes(app: App, vista=None):
    print_seccion(app.cadenaHotelera + " - Reporte de Mejores clientes")

    mejores_clientes = app.reporte_cant_reservaciones(
        not leer_si_no("¿Desea orden descendente?")
    )

    print_tabla_mejores_clientes(mejores_clientes)

    input("Presione <enter> para volver al menú > ")

    return Vista.Menu

def vista_reservaciones_reporte_duracion_estadias(app: App, vista=None):
    print_seccion(app.cadenaHotelera + " - Reporte de estadías")

    reservaciones = app.reporte_estadia(
        not leer_si_no("¿Desea orden descendente?")
    )

    print_tabla_reservaciones(reservaciones)
    input("Presione <enter> para volver al menú > ")

    return Vista.Menu

