import datetime
import json
import os
from typing import Dict
from config import CURRENT_DIR, Config
from data import Actividad, Cliente, Empleado, HabitacionTipo, Hotel, MejorCliente, Reservacion, ReservacionEstado
import csv
from listas import Queue, Stack

from ordenamiento import Ordenable, heapsort, mergesort, quicksort, shellsort
from arboles import ArbolBinario
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
        self.actividades = Stack()

        # Esta línea es para ayudar al IDE a entender que aquí va a un Arbol
        self.empleados = ArbolBinario(None)
        self.empleados = None

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
                ci, nombre, email = row
                self.clientes[ci] = Cliente(ci, nombre, email)

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

        empleados_file_path = os.path.abspath(self.config.archivo_empleados)
        empleados_seed = False
        if not os.path.exists(empleados_file_path):
            empleados_file_path = os.path.join(CURRENT_DIR, "seeds", "empleados.csv")
            empleados_seed = True

        empleados = list()
        with open(empleados_file_path) as fp:
            for row in csv.reader(
                fp.readlines(),
                delimiter=";",
                lineterminator="\n",
                quoting=csv.QUOTE_MINIMAL,
            ):
                id, hotel_id, ci, nombre, puesto, salario, fecha_contratacion = row
                id = int(id)
                hotel_id = int(hotel_id)
                salario = float(salario)
                fecha_contratacion = datetime.datetime.strptime(fecha_contratacion, "%Y-%m-%d")

                empleados.append(Empleado(hotel_id, ci, nombre, puesto, salario, fecha_contratacion, id=id))

        if len(empleados) > 0:
            # if empleados_seed:
            self.empleados = ArbolBinario(empleados[0])
            for e in empleados[1:]:
                self.empleados.agregar(e)
            # else:
                # self.empleados = ArbolBinario.deserialize(empleados)
        

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

        actividades_file_path = os.path.abspath(self.config.archivo_actividades)
        if not os.path.exists(actividades_file_path):
            return

        with open(actividades_file_path) as fp:
            actividades = []
            for row in csv.reader(
                fp.readlines(),
                delimiter=";",
                lineterminator="\n",
                quoting=csv.QUOTE_MINIMAL,
            ):
                (
                    fecha,
                    evento,
                    esError,
                    data,
                ) = row
                fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
                esError = bool(esError)
                data = json.loads(data)

                actividades.append(Actividad(evento, data, esError, fecha=fecha))
            for a in reversed(actividades):
                self.actividades.stack(a)

        print_info("Datos cargados")

    def persistir(self):
        """Persiste el estado actual del sistema"""

        print_info("Guardando datos")

        clientes_file_path = os.path.abspath(self.config.archivo_clientes)
        empleados_file_path = os.path.abspath(self.config.archivo_empleados)
        hoteles_file_path = os.path.abspath(self.config.archivo_hoteles)
        reservaciones_file_path = os.path.abspath(self.config.archivo_reservaciones)
        actividades_file_path = os.path.abspath(self.config.archivo_actividades)

        with open(clientes_file_path, "w") as fp:
            csvwriter = csv.writer(
                fp, delimiter=";", lineterminator="\n", quoting=csv.QUOTE_MINIMAL
            )
            for id, cliente in self.clientes.items():
                csvwriter.writerow((id, cliente.nombre, cliente.email))

        with open(empleados_file_path, "w") as fp:
            if self.empleados is not None:
                csvwriter = csv.writer(
                    fp, delimiter=";", lineterminator="\n", quoting=csv.QUOTE_MINIMAL
                )
                for e in self.empleados.serialize():
                    csvwriter.writerow((e.id, e.hotel_id, e.ci, e.nombre, e.puesto, e.salario, e.fecha_contratacion.strftime("%Y-%m-%d")))

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

        with open(actividades_file_path, "w") as fp:
            csvwriter = csv.writer(
                fp, delimiter=";", lineterminator="\n", quoting=csv.QUOTE_MINIMAL
            )

            for actividades in self.actividades:
                fecha = actividades.fecha.strftime("%Y-%m-%d %H:%M:%S")
                evento = actividades.evento
                esError = actividades.esError
                data = json.dumps(actividades.data)
                csvwriter.writerow(
                    (
                        fecha,
                        evento,
                        esError,
                        data,
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

    def tiene_habitacion(self, habitacion: str, hotel: Hotel = None):
        """Devuelve si la habitación existe."""
        hotel = hotel or self.hotelSeleccionado

        return hotel is not None and self.hotelSeleccionado.tiene_habitacion(habitacion)

    def tipo_habitacion(self, habitacion: str, hotel: Hotel = None):
        """Devuelve el tipo de la habitación."""
        hotel = hotel or self.hotelSeleccionado

        if hotel is not None:
            return hotel.tipo_habitacion(habitacion)
        return None

    def get_habitaciones_disponibles_en_periodo(
        self, 
        fecha_inicial: datetime.datetime, 
        fecha_final: datetime.datetime, 
        hotel: Hotel = None
    ) -> Dict[str, List[str]]:
        """
        Devuelve las habitaciones disponibles en el rango de fechas.
        
        :return: Un `dict` con las habitaciones disponibles agrupadas por el código del tipo.
        """
        hotel = hotel or self.hotelSeleccionado
        if hotel is None:
            return {}

        reservaciones_del_periodo = set(
            r.habitacion
            for r in self.get_reservaciones_por_periodo(fecha_inicial, fecha_final, hotel)
        )
        
        disponibles = {}

        for habitacion in hotel.habitaciones:
            if habitacion in reservaciones_del_periodo:
                continue

            tipo = hotel.tipo_habitacion(habitacion)
            if tipo.codigo not in disponibles:
                disponibles[tipo.codigo] = [habitacion]
            else:
                disponibles[tipo.codigo].append(habitacion)

        return disponibles

    def get_reservaciones_por_periodo(
        self, 
        fecha_inicial: datetime.datetime, 
        fecha_final: datetime.datetime, 
        hotel: Hotel = None
    ):
        """Devuelve las reservaciones que se encuentran en el rango de fechas."""

        hotel = hotel or self.hotelSeleccionado
        if hotel is None:
            return []

        return filter(
            lambda r: r.hotel_id == hotel.id and r.fecha_entrada < fecha_final and r.fecha_salida > fecha_inicial,
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
        hotel: Hotel,
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

        precio_por_dia = hotel.habitacionesTipos[hotel.habitaciones[habitacion]].precio
        duracion_dias = (fecha_salida - fecha_entrada).days
        precio = precio_por_dia * duracion_dias

        r = Reservacion(
            hotel.id,
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
        self.registrar_actividad("Reservación creada", {
            "id": r.id,
            "hotel_id": r.hotel_id,
            "cliente_ci": r.cliente.ci,
            "habitacion": r.habitacion,
            "fecha_entrada": r.fecha_entrada.strftime("%d/%m/%Y"),
            "fecha_salida": r.fecha_salida.strftime("%d/%m/%Y"),
            "hora_entrada": r.hora_entrada.strftime("%H:%M"),
            "hora_salida": r.hora_salida.strftime("%H:%M"),
            "personas_count": r.personas_count,
            "observaciones": r.observaciones
        })
        self.persistir()

        return r

    def registrar_actividad(
        self,
        evento: str,
        data: dict = {},
    ) -> Actividad:
        
        a = Actividad(evento, data)
        self.actividades.stack(a)
        self.persistir()

        return a

    def registrar_error(
        self,
        evento: str,
        data: dict = {},
    ) -> Actividad:
        
        a = Actividad(evento, data, esError=True)
        self.actividades.stack(a)
        self.persistir()

        return a

    def get_reservaciones_del_hotel(self, hotel_id: int) -> List[Reservacion]:
        """Devuelve las reservaciones de un hotel."""

        return list(filter(lambda r: r.hotel_id == hotel_id, self.reservaciones))

    def eliminar_reservacion(self, reservacion: Reservacion):
        """Elimina una reservación."""

        self.reservaciones.remove_when(lambda r: r.id == reservacion.id)
        self.registrar_actividad("Reservación eliminada", {
            "id": reservacion.id,
            "hotel_id": reservacion.hotel_id,
            "cliente_ci": reservacion.cliente.ci,
            "habitacion": reservacion.habitacion,
            "fecha_entrada": reservacion.fecha_entrada.strftime("%d/%m/%Y"),
            "fecha_salida": reservacion.fecha_salida.strftime("%d/%m/%Y"),
            "hora_entrada": reservacion.hora_entrada.strftime("%H:%M"),
            "hora_salida": reservacion.hora_salida.strftime("%H:%M"),
            "personas_count": reservacion.personas_count,
            "observaciones": reservacion.observaciones
        })
        self.persistir()

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


    def registrar_empleado(self, empleado: Empleado):
        """Registra un nuevo empleado"""

        if self.empleados is None:
            self.empleados = ArbolBinario(empleado)
        else:
            self.empleados.agregar(empleado)

        self.registrar_actividad("Empleado registrado", {
            "id": empleado.id,
            "hotel_id": empleado.hotel_id,
            "ci": empleado.ci,
            "nombre": empleado.nombre,
            "puesto": empleado.puesto,
            "salario": empleado.salario,
            "fecha_contratacion": empleado.fecha_contratacion.strftime("%d/%m/%Y"),
        })
        self.persistir()
        
        return empleado

    def get_empleados(self) -> Iterable[Empleado]:
        """Devuelve la lista de empleados"""
        if self.empleados is None:
            return tuple()

        return tuple(self.empleados.inorden())


    def get_empleados_por_ci(self) -> Dict[str, Empleado]:
        if self.empleados is None:
            return dict()

        return {e.ci: e for e in self.empleados}

    def get_empleados_de_hotel(self, hotel_id: int):
        """Devuelve la lista de empleados de un hotel"""
        if self.empleados is None:
            return tuple()

        # print_debug("hotel_id", hotel_id)
        for e in self.get_empleados():
            # print_debug("evaluando", e)
            if e.hotel_id == hotel_id:
                yield e

    def eliminar_empleado(self, empleado: Empleado):
        """Elimina un empleado"""

        if self.empleados is None:
            return 
        
        self.empleados = self.empleados.borrar(empleado)
        self.registrar_actividad("Empleado eliminado eliminada", {
            "id": empleado.id,
            "hotel_id": empleado.hotel_id,
            "ci": empleado.ci,
            "nombre": empleado.nombre,
            "puesto": empleado.puesto,
            "salario": empleado.salario,
            "fecha_contratacion": empleado.fecha_contratacion.strftime("%d/%m/%Y"),
        })
        self.persistir()
