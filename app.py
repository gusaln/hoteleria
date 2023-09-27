import datetime
import json
import os
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
                    tipos[tipo["codigo"]] = HabitacionTipo(tipo["codigo"], tipo["nombre"], tipo["capacidad"], tipo["precio"])

                self.hoteles.push(Hotel(
                    hotelRaw["nombre"],
                    hotelRaw["direccion"],
                    hotelRaw["telefono"],
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
                id = int(id)
                hotel_id = int(hotel_id)
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
                {"id": h.id, "nombre": h.nombre, "direccion": h.direccion, "telefono": h.telefono, "habitaciones": h.habitaciones, "tipos": [h.habitacionesTipos[t].__dict__ for t in h.habitacionesTipos]} 
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

    def format_ordenamiento(self):
        """Formatea el ordenamiento"""
        return ", ".join(
            ("" if o > 0 else "-") + PARAMETROS_ORDEN[abs(o)][0]
            for o in self.ordenamiento
        )

    def reservaciones_ordenadas(self):
        """Ordena las reservaciones"""

        ordenados = None
        if self.hotelSeleccionado is not None:
            ordenados = filter(lambda r: r.hotel_id == self.hotelSeleccionado.id, self.reservaciones)
        else:
            ordenados = self.reservaciones
        ordenados = list(ordenados)

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
