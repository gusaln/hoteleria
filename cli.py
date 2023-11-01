
from enum import IntEnum, auto
from app import PARAMETROS_ORDEN, App
from data import HabitacionTipo, ReservacionEstado
from term import *

class Vista(IntEnum):
    """Vistas del TUI"""

    Menu = auto()

    # Gestionar hoteles
    HotelesListar = auto()
    RegistrarHotel = auto()
    HotelModificar = auto()
    SeleccionarHotel = auto()
    DeseleccionarHotel = auto()

    # Gestionar un hotel
    HotelesHabitacionesListar = auto()
    HotelesHabitacionesDisponibles = auto()
    HabitacionModificar = auto()

    # Reservaciones
    Reservar = auto()
    ReservacionEliminar = auto()
    ReservacionModificar = auto()
    ReservacionesListar = auto()
    OrdenarReservaciones = auto()

    # Empleados
    EmpleadoRegistrar = auto()
    EmpleadoModificar = auto()
    EmpleadoEliminar = auto()
    EmpleadosListar = auto()

    ReservacionesReporteDelPeriodo = auto()
    ReservacionesReporteMejoresClientes = auto()
    ReservacionesReporteDuracion = auto()

    Salir = auto()

    def label(self):
        return {
            Vista.Salir: "Salir",
            Vista.Menu: "Menu",

            Vista.HotelesListar: "Hoteles: Listar",
            Vista.RegistrarHotel: "Hoteles: Registrar",
            Vista.HotelModificar: "Hoteles: Modificar",

            Vista.SeleccionarHotel: "Hoteles: Seleccionar",
            Vista.DeseleccionarHotel: "Hoteles: Deseleccionar",

            Vista.HotelesHabitacionesListar: "Hoteles: Gestionar habitaciones",
            Vista.HotelesHabitacionesDisponibles: "Hoteles: Habitaciones disponibles",
            Vista.HabitacionModificar: "Hoteles: Modificar habitación",

            Vista.Reservar: "Reservaciones: Reservar",
            Vista.ReservacionModificar: "Reservaciones: Actualizar una reservación",
            Vista.ReservacionEliminar: "Reservaciones: Eliminar una reservación",
            Vista.ReservacionesListar: "Reservaciones: Listar",

            Vista.EmpleadosListar: "Empleados: Listar",
            Vista.EmpleadoRegistrar: "Empleados: Registrar",
            Vista.EmpleadoModificar: "Empleados: Modificar",
            Vista.EmpleadoEliminar: "Empleados: Eliminar",

            Vista.ReservacionesReporteDelPeriodo: "Reporte: reservaciones en período",
            Vista.ReservacionesReporteMejoresClientes: "Reporte: mejores clientes",
            Vista.ReservacionesReporteDuracion: "Reporte: duración de estadías",
        }.get(self, self.name)

    def vista(self):
        return {
            Vista.Menu: vista_menu,
            Vista.HotelesListar: vista_hoteles_listar,
            # Vista.RegistrarHotel: vista_registrar_hotel,
            Vista.HotelModificar: vista_hotel_modificar,

            Vista.SeleccionarHotel: vista_seleccionar_hotel,
            Vista.DeseleccionarHotel: vista_deseleccionar_hotel,

            Vista.HotelesHabitacionesListar: vista_hotel_habitaciones_listar,
            Vista.HotelesHabitacionesDisponibles: vista_hotel_habitaciones_disponibles,
            Vista.HabitacionModificar: vista_habitacion_modificar,

            Vista.Reservar: vista_reservar,
            Vista.ReservacionModificar: vista_reservacion_modificar,
            Vista.ReservacionEliminar: vista_reservacion_eliminar,
            Vista.ReservacionesListar: vista_reservaciones_listar,
            Vista.OrdenarReservaciones: vista_cambiar_orden_reservaciones,

            Vista.EmpleadosListar: vista_empleados_listar,
            Vista.EmpleadoRegistrar: vista_empleados_registrar,
            Vista.EmpleadoModificar: vista_empleados_modificar,
            Vista.EmpleadoEliminar: vista_empleados_eliminar,

            Vista.ReservacionesReporteDelPeriodo: vista_reservaciones_reporte_del_periodo,
            Vista.ReservacionesReporteMejoresClientes: vista_reservaciones_reporte_mejores_clientes,
            Vista.ReservacionesReporteDuracion: vista_reservaciones_reporte_duracion_estadias,
        }.get(self, None)

    @staticmethod
    def menu_general():
        """Retorna las vistas en el menú principal"""
        return [
            Vista.HotelesListar,
            # Vista.RegistrarHotel,
            Vista.SeleccionarHotel,
            # Vista.HotelesHabitacionesListar,
            # Vista.HotelesHabitacionesDisponibles,

            Vista.Reservar,
            Vista.ReservacionesListar,
            Vista.ReservacionModificar,
            Vista.ReservacionEliminar,

            Vista.EmpleadosListar,
            Vista.EmpleadoRegistrar,
            Vista.EmpleadoModificar,
            Vista.EmpleadoEliminar,
            # Vista.ReservacionesReporteDelPeriodo,
            # Vista.ReservacionesReporteMejoresClientes,
            # Vista.ReservacionesReporteDuracion,
            Vista.Salir,
        ]

    @staticmethod
    def menu_para_hotel():
        """Retorna las vistas en el menú para el hotel"""
        return [
            Vista.DeseleccionarHotel,
            # Vista.HotelesHabitacionesListar,
            # Vista.HotelesHabitacionesDisponibles,
            # Vista.HabitacionModificar,

            Vista.Reservar,
            Vista.ReservacionesListar,
            Vista.ReservacionModificar,
            Vista.ReservacionEliminar,

            Vista.EmpleadosListar,
            Vista.EmpleadoRegistrar,
            Vista.EmpleadoModificar,
            Vista.EmpleadoEliminar,
            # Vista.ReservacionesReporteDelPeriodo,
            # Vista.ReservacionesReporteMejoresClientes,
            # Vista.ReservacionesReporteDuracion,
            Vista.Salir,
        ]


def vista_menu(app: App, vista=None):
    """Muestra el menú principal"""

    if app.hotelSeleccionado is None:
        print_seccion(app.cadenaHotelera + " - Menú")

        vista = seleccionar_opcion(
            "Seleccione una operación",
            [v.label() for v in Vista.menu_general()],
            [v for v in Vista.menu_general()],
        )
    else:
        print_seccion(app.cadenaHotelera + " - Menú para " + app.hotelSeleccionado.nombre)
        vista = seleccionar_opcion(
            "Seleccione una operación",
            [v.label() for v in Vista.menu_para_hotel()],
            [v for v in Vista.menu_para_hotel()],
        )

    return Vista(vista)


def vista_seleccionar_hotel(app: App, vista=None):
    """Gestionar el hotel"""
    if app.hotelSeleccionado is None:
        app.hotelSeleccionado =  seleccionar_hotel(app.hoteles, "Seleccione un hotel")

    return Vista.Menu


def vista_deseleccionar_hotel(app: App, vista=None):
    """Deselecciona el hotel"""
    app.hotelSeleccionado = None
    print_info("Hotel deseleccionado")

    return Vista.Menu


def vista_hoteles_listar(app: App, vista=None):
    """Muestra los hoteles"""

    print_seccion(app.cadenaHotelera + " - Hoteles")

    app.hotelSeleccionado = None
    
    print_tabla_hoteles(list(app.hoteles))

    opciones = [
        ["Gestionar habitaciones de un hotel", Vista.HotelesHabitacionesListar],
        ["Modificar un Hotel", Vista.HotelModificar],
        ["Registrar Hotel", Vista.RegistrarHotel],
        ["Volver al menú", Vista.Menu],
        ["Salir del sistema", Vista.Salir],
    ]
    vista = seleccionar_opcion(
        "Seleccione una operación",
        [o[0] for o in opciones],
        [o[1] for o in opciones],
    )

    return vista or Vista.Menu


def vista_registrar_hotel(app: App, vista=None):
    return vista or Vista.RegistrarHotel


def vista_hotel_modificar(app: App, vista=None):
    """Muestra la vista de modificar un hotel"""
    hotel = app.hotelSeleccionado or seleccionar_hotel(app.hoteles, "Seleccione un hotel")

    original_nombre = hotel.nombre
    original_direccion = hotel.direccion
    original_telefono = hotel.telefono

    print_info("Datos del hotel (no puede modificar el id):")
    print_info("         id:", hotel.id)
    print_info("     nombre:", hotel.nombre)
    print_info("  dirección:", hotel.direccion)
    print_info("   teléfono:", hotel.telefono)

    hotel.nombre = leer_str(f"Indique la nueva nombre (deje en blanco para no modificar):", predeterminado=hotel.nombre)
    hotel.direccion = leer_str(f"Indique la nueva dirección (deje en blanco para no modificar):", predeterminado=hotel.direccion)
    hotel.telefono = leer_str(f"Indique la nueva teléfono (deje en blanco para no modificar):", predeterminado=hotel.telefono)

    if hotel.nombre != original_nombre or hotel.direccion != original_direccion or hotel.telefono != original_telefono:
        print_info("Hotel modificado")
        app.registrar_actividad("Hotel modificado", data={"id": hotel.id, "nombre": hotel.nombre, "direccion": hotel.direccion, "telefono": hotel.telefono})

    if app.hotelSeleccionado is None:
        return Vista.HotelesListar

    return Vista.HotelesHabitacionesListar


def vista_hotel_habitaciones_listar(app: App, vista=None):
    """Muestra las habitaciones de un hotel"""

    hotel = app.hotelSeleccionado or seleccionar_hotel(app.hoteles, "Seleccione un hotel")

    print_seccion(app.cadenaHotelera + " - Habitaciones de " + hotel.nombre)

    print_tabla_habitaciones(hotel)

    opciones = [
        ["Modificar hotel", Vista.HotelModificar],
        ["Modificar habitación", Vista.HabitacionModificar],
        ["Volver al menú", Vista.Menu],
        ["Salir del sistema", Vista.Salir],
    ]
    vista = seleccionar_opcion(
        "Seleccione una operación",
        [o[0] for o in opciones],
        [o[1] for o in opciones],
    )

    return vista or Vista.HotelesListar


def vista_hotel_habitaciones_disponibles(app: App, vista=None):
    """Muestra las habitaciones de un hotel y su disponiblidad"""

    hotel = app.hotelSeleccionado or seleccionar_hotel(app.hoteles, "Seleccione un hotel")

    print_seccion(app.cadenaHotelera + " - Habitaciones disponibles de " + hotel.nombre)

    fecha_inicial = leer_date("Indique la fecha inicial")
    fecha_final = leer_date("Indique la fecha final")

    habitaciones_bytipo = hotel.get_habitaciones_por_tipo()
    disponibles_bytipo = app.get_habitaciones_disponibles_en_periodo(fecha_inicial, fecha_final, hotel)

    for tipo, habitaciones in habitaciones_bytipo.items():
        print(":::", tipo)
        for habitacion in habitaciones:
            if habitacion in disponibles_bytipo[tipo]:
                print("  - [ ]", habitacion)
            else:
                print("  - [X]", habitacion)

    opciones = [
        ["Modificar hotel", Vista.HotelModificar],
        ["Modificar habitación", Vista.HabitacionModificar],
        ["Ver reservaciones", Vista.ReservacionesListar],
        ["Volver al menú", Vista.Menu],
        ["Salir del sistema", Vista.Salir],
    ]
    vista = seleccionar_opcion(
        "Seleccione una operación",
        [o[0] for o in opciones],
        [o[1] for o in opciones],
    )

    return vista or Vista.HotelesListar


def vista_habitacion_modificar(app: App, vista=None):
    """Muestra la vista de modificar un tipo habitación"""

    hotel = app.hotelSeleccionado or seleccionar_hotel(app.hoteles, "Seleccione un hotel")

    print_seccion(app.cadenaHotelera + " - Modificar una habitación de " + hotel.nombre)
    habitacion = seleccionar_opcion(
        "Seleccione un tipo de habitación",
        ["%s capacidad=%d precio=%.2f" % (h.nombre, h.capacidad, h.precio) for h in hotel.habitacionesTipos.values()],
        [h for h in hotel.habitacionesTipos.values()],
    )

    original_nombre = habitacion.nombre
    original_capacidad = habitacion.capacidad
    original_precio = habitacion.precio

    print_info("Datos de la habitación (no puede modificar el código):")
    # print_debug(habitacion)
    print_info("     código:", habitacion.codigo)
    print_info("     nombre:", habitacion.nombre)
    print_info("  capacidad:", habitacion.capacidad)
    print_info("     precio: %.2f" % habitacion.precio)

    habitacion.nombre = leer_str(f"Indique la nueva nombre (deje en blanco para no modificar):", predeterminado=habitacion.nombre)
    habitacion.capacidad = leer_int(f"Indique la nueva capacidad (deje en blanco para no modificar):", predeterminado=habitacion.capacidad)
    habitacion.precio = leer_float(f"Indique la nueva precio (deje en blanco para no modificar):", predeterminado=habitacion.precio)

    if original_capacidad != habitacion.capacidad and original_nombre != habitacion.nombre and abs(original_precio - habitacion.precio) > 0.001:
        print_info("Habitación modificada")
        app.registrar_actividad("Habitación modificada", data={"hotel_id": hotel.id, "codigo": habitacion.codigo, "nombre": habitacion.nombre, "capacidad": habitacion.capacidad, "precio": habitacion.precio})

    if app.hotelSeleccionado is None:
        return Vista.HotelesListar

    return Vista.HotelesHabitacionesListar


def vista_reservar(app: App, vista=None):
    """Muestra la vista de reservar"""

    hotel = app.hotelSeleccionado or seleccionar_hotel(app.hoteles, "Seleccione un hotel")

    print_seccion(app.cadenaHotelera + " - Reservar habitación en " + hotel.nombre)

    fecha_inicial = leer_date("Indique la fecha en la que desea llegar")
    fecha_final = leer_date("Indique la fecha en la que desea salir")
    personas_count = leer_int("Indique el número de personas que se quedarán", 1)

    habitaciones_disponibles_bytipo = app.get_habitaciones_disponibles_en_periodo(fecha_inicial, fecha_final, hotel)
    # print_debug("habitaciones_disponibles_bytipo", habitaciones_disponibles_bytipo)

    tipos_utiles = dict((codigo, t) for codigo, t in hotel.habitacionesTipos.items() if t.capacidad >= personas_count)

    habitaciones_disponibles = set()
    tipos_disponibles = set()
    for tipo_codigo, habitaciones in habitaciones_disponibles_bytipo.items():
        if tipo_codigo in tipos_utiles:
            for h in habitaciones:
                habitaciones_disponibles.add(h)
            tipos_disponibles.add(hotel.habitacionesTipos[tipo_codigo])

    if len(habitaciones_disponibles) < 1:
        print_info(
            "No tenemos habitaciones disponibles en ese período para esa cantidad de personas"
        )
        return Vista.Menu

    print_info("Tenemos habitaciones disponibles")
    for tipo in sorted(tipos_disponibles, key=lambda t: t.precio):
        print(f"  - {tipo.nombre} en {tipo.precio}")

    if not leer_si_no(
        "¿Desa proceder con la reservación con alguna de estas opciones?"
    ):
        return Vista.Menu

    tipo_seleccionado = list(tipos_disponibles)[0] if len(tipos_disponibles) < 2 else seleccionar_opcion(
        "Indique el tipo de habitación",
        ["{0.nombre} :: {0.precio:.2f} por noche".format(tipo) for tipo in tipos_utiles.values()],
        list(tipos_disponibles),
    )

    duracion_dias = (fecha_final - fecha_inicial).days
    precio = duracion_dias * tipo_seleccionado.precio

    # print_debug("datos:", dict(tipo_seleccionado=tipo_seleccionado, duracion_dias=duracion_dias, precio=precio))

    habitacion = None
    for h in habitaciones_disponibles:
        # print_debug(hotel.tipo_habitacion(h), tipo_seleccionado)
        if hotel.tipo_habitacion(h) == tipo_seleccionado:
            habitacion = h
            break

    if habitacion is None:
        raise RuntimeError("Habitación no fue asignada")

    if not leer_si_no(
        f"Sería un total de {precio} por la habitación {habitacion} por {duracion_dias} día(s) ¿Desa proceder?"
    ):
        return Vista.Menu

    ci = "{:0>8}".format(leer_int("Indique la C.I. del cliente"))
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
        hotel,
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


def vista_reservacion_modificar(app: App, vista=None):
    """Muestra la vista de modificar una reservación"""

    hotel = app.hotelSeleccionado or seleccionar_hotel(app.hoteles)

    print_seccion(app.cadenaHotelera + " - Modificar Reservación en " + hotel.nombre)

    reservacion = seleccionar_reservacion(app.get_reservaciones_del_hotel(hotel.id))
    print_info("Reservación seleccionada:")
    print(reservacion)

    estado = seleccionar_opcion(
        "Seleccione un estado",
        [e.value for e in ReservacionEstado if e != reservacion.estado],
        [e for e in ReservacionEstado if e != reservacion.estado],
    )

    if leer_si_no(f"¿Desea cambiar la reservación a '{estado}'?"):
        reservacion.estado = ReservacionEstado(estado)
        app.registrar_actividad("Reservación modificada", data={"id": reservacion.id, "estado": estado})
        print_info("Reservación modificada")

    return Vista.Menu


def vista_reservacion_eliminar(app: App, vista=None):
    """Muestra la vista de eliminar una reservación"""

    hotel = app.hotelSeleccionado or seleccionar_hotel(app.hoteles)

    print_seccion(app.cadenaHotelera + " - Eliminar Reservación en " + hotel.nombre)

    reservacion = seleccionar_reservacion(app.get_reservaciones_del_hotel(hotel.id))
    print_info("Reservación seleccionada:")
    print(reservacion)

    if leer_si_no("¿Desea eliminar esta reservación?"):
        app.eliminar_reservacion(reservacion)
        print_info("Reservación eliminada")

    return Vista.Menu


def vista_cambiar_orden_reservaciones(app: App, vista=None):
    while True:
        print_info(
            "Estos son los parámetros por los que puede ordenar la lista:"
        )
        for p in PARAMETROS_ORDEN:
            print(f"  - [{p}] {PARAMETROS_ORDEN[p][0]}")

        print_info("Indique el nro. de la opción para ordenar de forma ascendente y el nro. negativo para ordenar de forma descendente")
        print_info("Puede indicar varios valores separados por comas para ordenar por más de un parámetro de la forma '1, 2, -3'")
        orden = leer_str("Indique el orden o presione <enter> sin escribir nada para volver a la lista:")
        if len(orden) == 0:
            return True

        try:
            orden = [int(o) for o in filter(lambda s: len(s) > 0, orden.split(","))]
        except ValueError:
            print_error("No se pudo procesar la entrada como parámetro de orden")
            continue

        app.ordenamiento = list(
            filter(
                lambda o: abs(o) in PARAMETROS_ORDEN,
                orden,
            )
        )

        print_info("Nuevo orden:", app.format_ordenamiento())

        break

    return vista or Vista.HotelesListar


def vista_reservaciones_listar(app: App, vista=None):
    """Muestra las reservaciones"""

    if app.hotelSeleccionado is None:
        print_seccion(app.cadenaHotelera + " - Reservaciones")
    else:
        print_seccion(app.cadenaHotelera + " - Reservaciones de " + app.hotelSeleccionado.nombre)

    opciones = [
        ["Ordenar", Vista.OrdenarReservaciones],
        ["Modificar una", Vista.ReservacionModificar],
        ["Eliminar una", Vista.ReservacionEliminar],
        ["Volver al menú", Vista.Menu],
    ]

    print_info(
        "Reservaciones ordenadas por:",
        app.format_ordenamiento(),
    )
    print_tabla_reservaciones(app.reservaciones_ordenadas())

    vista = seleccionar_opcion(
        "Seleccione una operación",
        [o[0] for o in opciones],
        [o[1] for o in opciones],
    )

    return vista or Vista.ReservacionesListar


def vista_empleados_listar(app: App, vista=None):
    """Muestra los empleados"""

    empleados = None
    if app.hotelSeleccionado is None:
        print_seccion(app.cadenaHotelera + " - Empleados")
        empleados = list(app.get_empleados())
    else:
        print_seccion(f"{app.cadenaHotelera } - Empleados de \"{app.hotelSeleccionado.nombre}\"")
        empleados = list(app.get_empleados_de_hotel(app.hotelSeleccionado.id))

    # print_debug("empleados", empleados)

    opciones = [
        ["Registrar nuevo", Vista.EmpleadoRegistrar],
        ["Modificar uno", Vista.EmpleadoModificar],
        ["Eliminar uno", Vista.EmpleadoEliminar],
        ["Volver al menú", Vista.Menu],
    ]

    print_tabla_empleados(empleados)

    vista = seleccionar_opcion(
        "Seleccione una operación",
        [o[0] for o in opciones],
        [o[1] for o in opciones],
    )

    return vista or Vista.EmpleadosListar


def vista_empleados_registrar(app: App, vista=None):
    """Muestra la vista de registrar empleado"""

    hotel = app.hotelSeleccionado or seleccionar_hotel(app.hoteles, "Seleccione un hotel")

    print_seccion(app.cadenaHotelera + " - Registrar empleado en " + hotel.nombre)

    ci = "{:0>8}".format(leer_int("Indique la C.I. del empleado"))

    empleados_por_ci = app.get_empleados_por_ci()
    if ci in empleados_por_ci:
        print_error("Este empleado ya está registrado.")
        print_info(empleados_por_ci[ci].nombre)
        
    else:
        nombre = leer_str("¿Cuál es el nombre del empleado?")
        puesto = leer_str("¿Cuál es el puesto del empleado?")
        salario = leer_float("¿Cuál es el salario del empleado?")
        fecha_contratacion = leer_date("¿Cuándo se contrato? (deje vacío para tomar el día de hoy)", datetime.datetime.now())

        empleado = app.registrar_empleado(Empleado(
            hotel.id,
            ci,
            nombre,
            puesto,
            salario,
            fecha_contratacion
        ))

        print_info("Empleado registrado:")
        print(empleado)

    # if app.hotelSeleccionado is None:
        # return Vista.Menu

    return Vista.EmpleadosListar


def vista_empleados_modificar(app: App, vista=None):
    """Muestra la vista de modificar un empleado"""
    hotel = app.hotelSeleccionado or seleccionar_hotel(app.hoteles, "Seleccione un hotel")

    empleado = seleccionar_empleado(app.get_empleados_de_hotel(hotel.id))

    original_nombre = empleado.nombre
    original_ci = empleado.ci
    original_puesto = empleado.puesto
    original_salario = empleado.salario

    print_info("Datos del empleado (no puede modificar el id):")
    print_tabla_empleados([empleado])

    empleado.nombre = leer_str(f"Indique el nuevo nombre (deje en blanco para no modificar):", predeterminado=empleado.nombre)
    empleado.ci = "{:0>8}".format(leer_int(f"Indique la nueva C.I. (deje en blanco para no modificar):", predeterminado=empleado.ci))
    empleado.puesto = leer_str(f"Indique el nuevo puesto (deje en blanco para no modificar):", predeterminado=empleado.puesto)
    empleado.salario = leer_float(f"Indique el nuevo salario (deje en blanco para no modificar):", predeterminado=empleado.salario)

    if empleado.nombre != original_nombre or empleado.ci != original_ci or empleado.puesto != original_puesto or empleado.salario != original_salario:
        print_tabla_empleados([empleado])
        print_info("Empleado modificado")
        app.registrar_actividad("Empleado modificado", data={"id": empleado.id, "nombre": empleado.nombre, "ci": empleado.ci, "puesto": empleado.puesto, "salario": empleado.salario})

    if app.hotelSeleccionado is None:
        return Vista.EmpleadosListar

    return Vista.Menu


def vista_empleados_eliminar(app: App, vista=None):
    """Muestra la vista de eliminar un Empleado"""

    hotel = app.hotelSeleccionado or seleccionar_hotel(app.hoteles)

    print_seccion(app.cadenaHotelera + " - Eliminar Empleado en " + hotel.nombre)

    empleado = seleccionar_empleado(app.get_empleados_de_hotel(hotel.id))
    print_info("Empleado seleccionado:")
    print(empleado)

    if leer_si_no("¿Desea eliminar a este empleado del sistema?"):
        app.eliminar_empleado(empleado)
        print_info("Empleado eliminado")

    return Vista.Menu

##
# Reportes
##

def vista_reservaciones_reporte_del_periodo(app: App, vista=None):
    """Muestra el reporte del período"""

    print_seccion(app.cadenaHotelera + " - Reporte del período")
    reservaciones = app.reporte_en_periodo(
        leer_date("Ingrese fecha inicial"),
        leer_date("Ingrese fecha final"),
        not leer_si_no("¿Desea orden descendente?"),
    )

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

