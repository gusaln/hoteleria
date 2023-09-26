import datetime
from enum import StrEnum
from collections import namedtuple
from typing import Dict


class HabitacionTipo():
    """Representa el tipo de habitación."""

    def __init__(self, nombre: str, capacidad: int, precio: float):
        self.nombre = nombre
        self.capacidad = capacidad
        self.precio = precio

    def __repr__(self):
        return "<HabitacionTipo %s capacidad=%d precio=%f>" % (self.nombre, self.capacidad, self.precio)


class Hotel():
    """Representa un hotel."""

    def __init__(self, nombre: str, direccion: str, habitaciones: Dict[str, str], habitacionesTipos: Dict[str, HabitacionTipo], id=None):
        self.id = id or int(datetime.datetime.now().timestamp() * 1000)
        self.nombre = nombre
        self.direccion = direccion
        self.habitaciones = habitaciones
        self.habitacionesTipos = habitacionesTipos

    def tiene_habitacion(self, habitacion: str) -> bool:
        """Devuelve si la habitación existe."""
        return habitacion in self.habitaciones

    def tipo_habitacion(self, habitacion: str):
        """Devuelve el tipo de la habitación."""
        if self.tiene_habitacion(habitacion):
            return self.habitaciones[habitacion]
        return None


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
        return (self.fecha_salida - self.fecha_entrada).days

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
