import datetime
from enum import StrEnum
from collections import namedtuple
from typing import Dict, List


class HabitacionTipo():
    """Representa el tipo de habitación."""

    def __init__(self, codigo: str, nombre: str, capacidad: int, precio: float):
        self.codigo = codigo
        self.nombre = nombre
        self.capacidad = capacidad
        self.precio = precio

    def __repr__(self):
        return "<Habitación código={0.codigo} nombre={0.nombre} capacidad={0.capacidad} precio={0.precio:.2f}>".format(self)


class Hotel():
    """Representa un hotel."""

    def __init__(self, nombre: str, direccion: str, telefono: str, habitaciones: Dict[str, str], habitacionesTipos: Dict[str, HabitacionTipo], id=None):
        self.id = id or int(datetime.datetime.now().timestamp() * 1000)
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.habitaciones = habitaciones
        self.habitacionesTipos = habitacionesTipos

    def get_habitaciones_por_tipo(self) -> Dict[str, List[str]]:
        """
        Devuelve las habitaciones agrupadas por tipo.


        :return: Un `dict` con las habitaciones agrupadas por tipo.
        """

        habitaciones_por_tipo = {}
        for habitacion, tipo in self.habitaciones.items():
            if tipo not in habitaciones_por_tipo:
                habitaciones_por_tipo[tipo] = [habitacion]
            else:
                habitaciones_por_tipo[tipo].append(habitacion)

        return habitaciones_por_tipo

    def capacidad(self) -> int:
        """Devuelve la capacidad del hotel."""
        capacidad = 0

        for habitacion in self.habitaciones.values():
            capacidad += self.habitacionesTipos[habitacion].capacidad

        return capacidad

    def capacidad_disponible(self, habitaciones_ocupadas: List[str] = []) -> int:
        """Devuelve la capacidad disponible del hotel."""
        capacidad = 0

        busy = dict((h, True) for h in habitaciones_ocupadas)

        for habitacion in self.habitaciones.values():
            if habitacion not in busy:
                capacidad += self.habitacionesTipos[habitacion].capacidad

        return capacidad

    def tiene_habitacion(self, habitacion: str) -> bool:
        """Devuelve si la habitación existe."""
        return habitacion in self.habitaciones

    def tipo_habitacion(self, habitacion: str) -> HabitacionTipo:
        """Devuelve el tipo de la habitación."""
        if self.tiene_habitacion(habitacion):
            return self.habitacionesTipos[self.habitaciones[habitacion]]
        return None


class Empleado:
    """Representa un empleado."""

    def __init__(
            self,
            hotel_id: int,
            ci: str,
            nombre: str,
            puesto: str,
            salario: float,
            fecha_contratacion: datetime.datetime,
            id: int = None):
        self.id = id or int(datetime.datetime.now().timestamp() * 1000)
        self.hotel_id = hotel_id
        self.ci = ci
        self.nombre = nombre
        self.puesto = puesto
        self.salario = salario
        self.fecha_contratacion = fecha_contratacion

    def __str__(self):
        return f"Empleado id={self.id} hotel_id={self.hotel_id} ci={self.ci} nombre={self.nombre}"

    # def __cmp__(self, other) -> int:
        # return self.id - other.id

    def __le__(self, other) -> bool:
        if other is None:
            return False

        return self.id <= other.id

    def __ge__(self, other) -> bool:
        if other is None:
            return True

        return self.id >= other.id

    def __lt__(self, other) -> bool:
        if other is None:
            return False

        return self.id < other.id

    def __gt__(self, other) -> bool:
        if other is None:
            return True

        return self.id > other.id

    def __eq__(self, other) -> bool:
        if other is None:
            return False

        return self.id == other.id


class Factura:
    """Representa un factura."""

    def __init__(
            self,
            reservacion_id: int,
            total: float,
            balance_pagado: float,
            fecha: datetime.datetime,
            id: int = None):
        self.id = id or int(datetime.datetime.now().timestamp() * 1000)
        self.reservacion_id = reservacion_id
        self.total = total
        self.balance_pagado = balance_pagado
        self.fecha = fecha

    def __str__(self):
        return f"Factura id={self.id} reservacion_id={self.reservacion_id} fecha={self.fecha.strftime('%d/%m/%Y')} balance={self.balance_pagado} de {self.total}"

    # def __cmp__(self, other) -> int:
        # return self.id - other.id

    def __le__(self, other) -> bool:
        if other is None:
            return False
        if type(other) is Reservacion:
            return self.reservacion_id <= other.id

        return self.reservacion_id <= other.reservacion_id

    def __ge__(self, other) -> bool:
        if other is None:
            return True
        if type(other) is Reservacion:
            return self.reservacion_id >= other.id

        return self.reservacion_id >= other.reservacion_id

    def __lt__(self, other) -> bool:
        if other is None:
            return False
        if type(other) is Reservacion:
            return self.reservacion_id < other.id

        return self.reservacion_id < other.reservacion_id

    def __gt__(self, other) -> bool:
        if other is None:
            return True
        if type(other) is Reservacion:
            return self.reservacion_id > other.id

        return self.reservacion_id > other.reservacion_id

    def __eq__(self, other) -> bool:
        if other is None:
            return False
        if type(other) is Reservacion:
            return self.reservacion_id == other.id

        return self.reservacion_id == other.reservacion_id


class ReservacionEstado(StrEnum):
    """Representa el estado de una reservación."""

    Pendiente = "pendiente"
    Abonada = "abonada"
    Pagada = "pagada"
    Cancelada = "cancelada"

    def __repr__(self):
        return "<%s.%s>" % (self.__class__.__name__, self._name_)


class Cliente:
    """Representa un cliente."""

    def __init__(self, ci: str, nombre: str, email: str):
        self.ci = ci
        self.nombre = nombre
        self.email = email

    def __str__(self):
        return f"{self.ci} {self.nombre} {self.email}"


MejorCliente = namedtuple("MejorCliente", ["cliente", "reservaciones_count"])


class Reservacion:
    """Representa una reservación."""

    def __init__(
        self,
        hotel_id: int,
        cliente: Cliente,
        habitacion: str,
        estado: ReservacionEstado,
        fecha_entrada: datetime.datetime,
        fecha_salida: datetime.datetime,
        precio: float,
        hora_entrada: datetime.time = None,
        hora_salida: datetime.time = None,
        personas_count=1,
        observaciones=None,
        id=None,
    ):
        self.id = id or int(datetime.datetime.now().timestamp() * 1000)
        self.hotel_id = hotel_id
        self.cliente = cliente
        self.habitacion = habitacion
        self.estado = estado
        self.fecha_entrada = fecha_entrada
        self.fecha_salida = fecha_salida
        self.precio = precio
        self.hora_entrada = hora_entrada or datetime.time(8, 0)
        self.hora_salida = hora_salida or datetime.time(17, 0)
        self.personas_count = personas_count
        self.observaciones = observaciones

    def duracion(self):
        """Devuelve la duración de la reservación."""
        return (self.fecha_salida - self.fecha_entrada).days

    def format_fecha_entrada(self):
        """Devuelve la fecha de entrada en formato legible."""
        return self.fecha_entrada.strftime("%d/%m/%Y")

    def format_fecha_salida(self):
        """Devuelve la fecha de salida en formato legible."""
        return self.fecha_salida.strftime("%d/%m/%Y")

    def __str__(self) -> str:
        return """Reservacion {id}:
        \tcliente: {cliente_ci} - {cliente_nombre}, habitacion: {habitacion}, estado: {estado}, fecha_entrada: {fecha_entrada}, fecha_salida: {fecha_salida}
        \tprecio: {precio}, cantidad de personas: {personas_count}
        \tobservaciones: {observaciones}
        """.format(
            id=self.id,
            cliente_ci=self.cliente.ci,
            cliente_nombre=self.cliente.nombre,
            habitacion=self.habitacion,
            estado=self.estado,
            fecha_entrada=self.fecha_entrada,
            fecha_salida=self.fecha_salida,
            precio=self.precio,
            personas_count=self.personas_count,
            observaciones=self.observaciones or "-",
        )


class Actividad():
    """Representa una actividad."""

    def __init__(self, evento: str, data: dict = {}, esError: bool = False, fecha: datetime.datetime = None) -> None:
        self.evento = evento
        self.data = data
        self.esError = esError
        self.fecha = fecha or datetime.datetime.now()

    def tipo(self):
        """Devuelve el tipo de la actividad."""
        if self.esError:
            return "error"

        return "info"
