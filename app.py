import datetime
import os
from typing import List, Dict
from config import CURRENT_DIR
from data import Cliente, MejorCliente, Reservacion, ReservacionEstado

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

    def __init__(
        self,
        hotel: str,
        habitaciones={},
        precios={},
        clientes: Dict[str, Cliente] = {},
        reservaciones: List[Reservacion] = [],
    ):
        self.hotel = hotel
        self.habitaciones = habitaciones
        self.precios = precios
        self.clientes = clientes
        self.reservaciones = reservaciones
        self.ordenamiento = [1]

    ## Métodos de I.O.

    def cargar(self):
        """Carga los datos del sistema.

        De no haber datos, se utilizan cargan los datos de muestra como valores iniciales.
        """

        print_info("Cargando archivos de datos")

        clientes_file_path = os.path.join(CURRENT_DIR, "data", "clientes.csv")
        if not os.path.exists(clientes_file_path):
            clientes_file_path = os.path.join(CURRENT_DIR, "seeds", "clientes.csv")

        with open(clientes_file_path) as fp:
            for l in fp.readlines():
                id, nombre, email = l.strip().split(",")
                self.clientes[id] = Cliente(id, nombre, email)

        reservaciones_file_path = os.path.join(CURRENT_DIR, "data", "reservaciones.csv")
        if not os.path.exists(reservaciones_file_path):
            reservaciones_file_path = os.path.join(
                CURRENT_DIR, "seeds", "reservaciones.csv"
            )

        with open(reservaciones_file_path) as fp:
            for l in fp.readlines():
                (
                    id,
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
                ) = l.strip().split(",")
                fecha_entrada = datetime.datetime.strptime(fecha_entrada, "%Y-%m-%d")
                fecha_salida = datetime.datetime.strptime(fecha_salida, "%Y-%m-%d")
                hora_entrada = datetime.datetime.strptime(hora_entrada, "%H:%M").time()
                hora_salida = datetime.datetime.strptime(hora_salida, "%H:%M").time()
                precio = float(precio)

                self.reservaciones.append(
                    Reservacion(
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

        print_info("Datos cargados")

    def persistir(self):
        """Persiste el estado actual del sistema"""

        print_info("Guardando datos")

        clientes_file_path = os.path.join(CURRENT_DIR, "data", "clientes.csv")
        reservaciones_file_path = os.path.join(CURRENT_DIR, "data", "reservaciones.csv")
        with open(clientes_file_path, "w") as fp:
            for id, cliente in self.clientes.items():
                fp.write(f"{id},{cliente.nombre},{cliente.email}\n")

        with open(reservaciones_file_path, "w") as fp:
            for reservacion in self.reservaciones:
                id = reservacion.id
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
                fp.write(
                    f"{id},{cliente_ci},{habitacion},{estado},{fecha_entrada},{fecha_salida},{hora_entrada},{hora_salida},{precio},{personas_count},{observaciones}\n"
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

    def tiene_habitacion(self, habitacion: str):
        """Devuelve si la habitación existe."""
        return habitacion in self.habitaciones

    def tipo_habitacion(self, habitacion: str):
        """Devuelve el tipo de la habitación."""
        if self.tiene_habitacion(habitacion):
            return self.habitaciones[habitacion]
        return None

    def get_reservaciones_por_periodo(
        self, fecha_inicial: datetime.datetime, fecha_final: datetime.datetime
    ):
        """Devuelve las reservaciones que se encuentran en el rango de fechas."""

        return filter(
            lambda r: r.fecha_entrada >= fecha_inicial
            and r.fecha_salida <= fecha_final,
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
    ):
        precio_por_dia = self.precios[self.habitaciones[habitacion]]
        duracion_dias = (fecha_salida - fecha_entrada).days
        precio = precio_por_dia * duracion_dias

        r = Reservacion(
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

        self.reservaciones.append(r)
        self.persistir()

        return r

    ## OPERACIONES DE CLI

    VISTA_SALIR = -1
    VISTA_MENU = 0
    VISTA_LISTAR = 1
    VISTA_REPORTE_DEL_PERIODO = 2
    VISTA_REPORTE_MEJORES_CLIENTES = 3
    VISTA_REPORTE_DURACION = 4

    def run(self):
        """Ejecuta el TUI de la aplicación"""

        print_titulo("Bienvenido al sistema de reservas de '%s'" % self.hotel)

        vista = self.VISTA_MENU

        while True:
            if vista == self.VISTA_SALIR:
                return

            elif vista == self.VISTA_MENU:
                vista = self.vista_menu(vista)

            elif vista == self.VISTA_LISTAR:
                vista = self.vista_listar_reservaciones(vista)

            elif vista == self.VISTA_REPORTE_DEL_PERIODO:
                vista = self.vista_reporte_del_periodo(vista)

            elif vista == self.VISTA_REPORTE_MEJORES_CLIENTES:
                vista = self.vista_reporte_mejores_clientes(vista)

            elif vista == self.VISTA_REPORTE_DURACION:
                vista = self.vista_reporte_duracion_estadias(vista)

            else:
                vista == self.VISTA_SALIR

            print("-" * 80, end="\n\n")

    def vista_menu(self, vista=None):
        """Muestra el menú principal"""

        print_seccion(self.hotel + " - Menú")

        opciones = [
            # ["Reservar", self.vista_reservar],
            ["Ver reservaciones", self.VISTA_LISTAR],
            [
                "Reporte: reservaciones en período",
                self.VISTA_REPORTE_DEL_PERIODO,
            ],
            ["Reporte: mejores clientes", self.VISTA_REPORTE_MEJORES_CLIENTES],
            ["Reporte: duración de estadías", self.VISTA_REPORTE_DURACION],
            ["Salir", self.VISTA_SALIR],
        ]

        vista = seleccionar_opcion(
            "Seleccione una operación",
            [o[0] for o in opciones],
            [o[1] for o in opciones],
        )

        return vista or self.VISTA_MENU

    def vista_reservar(self, vista=None):
        pass

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

    def vista_listar_reservaciones(self, vista=None):
        """Muestra las reservaciones"""

        print_seccion(self.hotel + " - Reservaciones")

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

                self.ordenamiento = list(
                    filter(
                        lambda o: abs(o) in PARAMETROS_ORDEN,
                        orden,
                    )
                )

                print_info(
                    "Nuevo orden:",
                    self.format_ordenamiento(),
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
                self.format_ordenamiento(),
            )
            print_tabla_reservaciones(self.reservaciones_ordenadas())
            print()

            accion = seleccionar_opcion(
                "Seleccione una operación",
                [o[0] for o in opciones],
                [o[1] for o in opciones],
            )

            if not accion():
                return self.VISTA_MENU

        return vista or self.VISTA_LISTAR

    def vista_reporte_del_periodo(self, vista=None):
        """Muestra el reporte del período"""

        print_seccion(self.hotel + " - Reporte del período")
        reservaciones = self.reporte_en_periodo(
            leer_date("Ingrese fecha inicial"),
            leer_date("Ingrese fecha final"),
            not leer_si_no("¿Desea orden descendente?"),
        )

        print()
        print_tabla_reservaciones(reservaciones)
        input("Presione <enter> para volver al menú > ")

        return self.VISTA_MENU

    def vista_reporte_mejores_clientes(self, vista=None):
        print_seccion(self.hotel + " - Reporte de Mejores clientes")

        mejores_clientes = self.reporte_cant_reservaciones(
            not leer_si_no("¿Desea orden descendente?")
        )

        print_tabla_mejores_clientes(mejores_clientes)

        input("Presione <enter> para volver al menú > ")

        return self.VISTA_MENU

    def vista_reporte_duracion_estadias(self, vista=None):
        print_seccion(self.hotel + " - Reporte de estadías")

        reservaciones = self.reporte_estadia(
            not leer_si_no("¿Desea orden descendente?")
        )

        print_tabla_reservaciones(reservaciones)
        input("Presione <enter> para volver al menú > ")

        return self.VISTA_MENU
