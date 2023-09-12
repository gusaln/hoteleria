from collections import namedtuple
from typing import List

# Representa un par ordenable, donde `data` es el `valor` y key es la clave de ordenamiento
Ordenable = namedtuple("Ordenable", ["data", "key"])


def quicksort(arr: List[Ordenable], lo=0, hi=None):
    """Implementa quicksort recursivamente.

    Se modifica al arreglo para mejor rendimiento.
    """
    if hi is None:
        hi = len(arr) - 1

    # Aseguramos que los indices estén en el rango correcto
    if lo >= hi or lo < 0:
        return

    # Particionamos el arreglo y obtenemos el nuevo pivote
    pivote_index = quicksort_particionar(arr, lo, hi)

    # Ordenamos los subarreglos a la izquierda y a la derecha del pivote
    quicksort(arr, lo, pivote_index - 1)
    quicksort(arr, pivote_index + 1, hi)


def quicksort_particionar(arr: List[Ordenable], lo, hi):
    """Función de partición de quicksort.

    Toma a `arr[hi]` como pivote y en el rango [:param:`lo`, :param:`hi`] mueve todos los elementos menores al pivote a
    la izquierda y todos los elementos mayores a la derecha.

    :param arr: arreglo a ordenar
    :param lo: índice inferior del rango a ordenar en el arreglo
    :param hi: índice superior del rango a ordenar en el arreglo
    :return: Indice en el que se colocó el pivote
    """
    pivote = arr[hi]

    # Posición final del pivote
    nuevo_pivote_index = lo - 1

    # Recorremos el arreglo en el rango [lo, hi)
    for j in range(lo, hi):
        if arr[j].key <= pivote.key:
            nuevo_pivote_index = nuevo_pivote_index + 1
            arr[nuevo_pivote_index], arr[j] = arr[j], arr[nuevo_pivote_index]

    nuevo_pivote_index = nuevo_pivote_index + 1
    arr[nuevo_pivote_index], arr[hi] = arr[hi], arr[nuevo_pivote_index]
    return nuevo_pivote_index


def heapsort(arr: List[Ordenable]):
    """Implementa heapsort.

    Se modifica al arreglo para mejor rendimiento.

    :param arr: arreglo a ordenar
    """
    heap_size = len(arr)

    # Construimos un max heap. Al construir el heap, el valor en la raíz 0, es el mayor.
    for k in range((heap_size // 2), -1, -1):
        heapsort_max_heapify(arr, heap_size, k)

    # Movemos la raíz del heap al final del arreglo
    for k in range(heap_size - 1, 0, -1):
        # Intercambiamos la raíz con el primer elementos.
        arr[0], arr[k] = arr[k], arr[0]

        # Dado que el arreglo se ordena en su sitio, debemos especificar hasta donde llega el heap.
        # k = heap_size - 1, por lo que al usarla como heap_size, el algoritmo ignorará los elementos ya ordenados
        heapsort_max_heapify(arr, k, 0)


def heapsort_max_heapify(heap: List[Ordenable], heap_size, i):
    """Ordena un max heap.


    :param heap: que representa al heap
    :param heap_size: el tamaño del :param:`heap`
    :param i: índice de la raíz del :param:`heap`
    """
    left_child = 2 * i + 1
    right_child = 2 * i + 2
    mayor_index = i

    if left_child < heap_size and heap[left_child].key > heap[mayor_index].key:
        mayor_index = left_child

    if right_child < heap_size and heap[right_child].key > heap[mayor_index].key:
        mayor_index = right_child

    # El proceso se detiene cuando la raíz es el mayor elemento del heap
    if mayor_index != i:
        heap[i], heap[mayor_index] = heap[mayor_index], heap[i]
        heapsort_max_heapify(heap, heap_size, mayor_index)


def mergesort(arr: List[Ordenable]):
    """Implementa mergesort recursivamente.

    :param arr: arreglo a ordenar
    """
    if len(arr) < 2:
        return

    mitad = len(arr) // 2
    arr_izq = arr[:mitad]
    arr_der = arr[mitad:]

    # Ordenamos los subarreglos
    mergesort(arr_izq)
    mergesort(arr_der)

    cursor_izq = cursor_der = cursor_principal = 0
    arr_izq_len = len(arr_izq)
    arr_der_len = len(arr_der)

    # Reinsertamos los elementos de cada subarreglo ordenados en el arreglo principal hasta que se acabe uno de los
    # subarreglos
    while cursor_izq < arr_izq_len and cursor_der < arr_der_len:
        if arr_izq[cursor_izq].key < arr_der[cursor_der].key:
            arr[cursor_principal] = arr_izq[cursor_izq]
            cursor_izq += 1
        else:
            arr[cursor_principal] = arr_der[cursor_der]
            cursor_der += 1
        cursor_principal += 1

    # Colocamos los elementos que restan de arr_izq en el arreglo principal
    while cursor_izq < arr_izq_len:
        arr[cursor_principal] = arr_izq[cursor_izq]
        cursor_izq += 1
        cursor_principal += 1

    # Colocamos los elementos que restan de arr_der en el arreglo principal
    while cursor_der < arr_der_len:
        arr[cursor_principal] = arr_der[cursor_der]
        cursor_der += 1
        cursor_principal += 1


def shellsort(arr: List[Ordenable]):
    """Implementa shellsort.

    Se modifica al arreglo para mejor rendimiento.

    :param arr: arreglo a ordenar
    """

    n = len(arr)

    # Seleccionamos el intervalo usando la secuencia original de Shell en la serie n/2, n/4, n/8, ...
    separacion = n // 2
    while separacion > 0:
        # Iteramos a lo largo del arreglo
        for hi in range(separacion, n):
            temp = arr[hi]
            lo = hi
            while lo >= separacion and arr[lo - separacion].key > temp.key:
                arr[lo] = arr[lo - separacion]
                lo -= separacion

            arr[lo] = temp
        separacion //= 2
