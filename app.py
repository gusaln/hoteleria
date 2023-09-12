import datetime
import os
from typing import List, Dict
from config import CURRENT_DIR
from data import Cliente, Reservacion, ReservacionEstado

from ordenamiento import Ordenable, heapsort, mergesort, shellsort
from term import *


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
        self.ordenamiento = []

    def cargar(self):
        """Carga los datos del sistema.

        De no haber datos, se utilizan cargan los datos de muestra como valores iniciales.
        """

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
                fecha_entrada = datetime.datetime.strptime(
                    fecha_entrada, "%Y-%m-%d"
                ).date()
                fecha_salida = datetime.datetime.strptime(
                    fecha_salida, "%Y-%m-%d"
                ).date()
                hora_entrada = datetime.datetime.strptime(hora_entrada, "%H:%M").time()
                hora_salida = datetime.datetime.strptime(hora_salida, "%H:%M").time()
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

    def persistir(self):
        """Persiste el estado actual del sistema"""

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

    def esta_ocupada(
        self,
        habitacion: str,
        fecha_inicial: datetime.datetime,
        fecha_final: datetime.datetime,
    ):
        reservaciones = filter(lambda r: r.habitacion == habitacion, self.reservaciones)
        reservaciones = filter(
            lambda r: r.fecha_entrada >= fecha_inicial
            and r.fecha_salida <= fecha_final,
            reservaciones,
        )

        return len(reservaciones)

    def tiene_habitacion(self, habitacion: str):
        return habitacion in self.habitaciones

    def tipo_habitacion(self, habitacion: str):
        if self.tiene_habitacion(habitacion):
            return self.habitaciones[habitacion]
        return None

    def get_reservaciones_por_periodo(
        self, fecha_inicial: datetime.datetime, fecha_final: datetime.datetime
    ):
        return filter(
            lambda r: r.fecha_entrada >= fecha_inicial
            and r.fecha_salida <= fecha_final,
            self.reservaciones,
        )

    def reporte_en_periodo(
        self, fecha_inicial: datetime.datetime, fecha_final: datetime.datetime, asc=True
    ):
        reservaciones = self.get_reservaciones_por_periodo(fecha_inicial, fecha_final)

        if asc:
            reservaciones = map(lambda r: Ordenable(r, r.precio), reservaciones)
        else:
            reservaciones = map(lambda r: Ordenable(r, -r.precio), reservaciones)

        reservaciones = list(reservaciones)
        mergesort(reservaciones)

        return [ordenable.data for ordenable in reservaciones]

    def reporte_cant_reservaciones(self, asc=True):
        clientes_count = {}

        for r in self.reservaciones:
            if r.cliente.ci not in clientes_count:
                clientes_count[r.cliente.ci] = 1
            else:
                clientes_count[r.cliente.ci] += 1

        resultados = []
        if asc:
            resultados = map(
                lambda ci, count: Ordenable(self.clientes[ci], count),
                clientes_count.items(),
            )
        else:
            resultados = map(
                lambda ci, count: Ordenable(self.clientes[ci], -count),
                clientes_count.items(),
            )

        resultados = list(resultados)
        shellsort(resultados)

        return [ordenable.data for ordenable in resultados]

    def reporte_estadia(self, asc=True):
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
        fecha_entrada: datetime.date,
        fecha_salida: datetime.date,
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
                exit(0)

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
        ]

        vista = seleccionar_opcion(
            "Seleccione una operación",
            [o[0] for o in opciones],
            [o[1] for o in opciones],
        )

        return vista or self.VISTA_MENU

    def vista_reservar(self, vista=None):
        pass

    def vista_listar_reservaciones(self, vista=None):
        print_seccion(self.hotel + " - Reservaciones")

        parametros_orden = [
            ["F. de entrada", lambda r: r.fecha_entrada],
            ["# Habitación", lambda r: r.habitacion],
            ["Duración estadía", lambda r: r.duracion()],
        ]

        ordenados = list(self.reservaciones)
        orden_actual = [1]
        if len(self.reservaciones) > 0:
            for o in orden_actual:
                getter = parametros_orden[abs(o) - 1][1]

                ordenables = [Ordenable(r, getter(r)) for r in ordenados]
                mergesort(ordenables)
                if o < 0:
                    ordenados = [r.data for r in ordenables[::-1]]
                else:
                    ordenados = [r.data for r in ordenables]

        opciones = [
            ["Ordenar", None],
            ["Volver al menú", lambda: False],
        ]

        while True:
            print_info(
                "Orden:",
                ", ".join(parametros_orden[abs(o) - 1][0] for o in orden_actual),
            )
            print_tabla_reservaciones(ordenados)

            accion = seleccionar_opcion(
                "Seleccione una operación",
                [o[0] for o in opciones],
                [o[1] for o in opciones],
            )

            if not accion():
                vista = self.VISTA_MENU
                break

        return vista or self.VISTA_LISTAR

    def vista_reporte_del_periodo(self, vista=None):
        print_seccion(self.hotel + " - Reporte del período")
        reservaciones = self.reporte_en_periodo(
            leer_date("Ingrese fecha inicial"), leer_date("Ingrese fecha final")
        )

        print_tabla_reservaciones(reservaciones)
        print("Presione enter para volver al menú")

        return self.VISTA_MENU

    def vista_reporte_mejores_clientes(self, vista=None):
        print_seccion(self.hotel + " - Reporte de Mejores clientes")

        return self.VISTA_MENU

    def vista_reporte_duracion_estadias(self, vista=None):
        print_seccion(self.hotel + " - Reporte de estadías")

        reservaciones = self.reporte_estadia()

        print_tabla_reservaciones(reservaciones)
        print("Presione enter para volver al menú")

        return self.VISTA_MENU
