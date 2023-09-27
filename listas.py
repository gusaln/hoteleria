class QueueNodo():
    def __init__ (self, valor = None):
        self.valor = valor
        self.siguiente = None

class Queue():
    def __init__(self):
        self.cabeza = None
        self.longitud = 0


    def __len__(self):
        return self.longitud
    
    def __iter__(self):
        actual = self.cabeza

        while actual:
            yield actual.valor
            actual = actual.siguiente

    def peek(self):
        return self.cabeza

    def remove(self, valor):
        self.remove_when(lambda v: v == valor)

    def remove_when(self, cb):
        if self.cabeza is None:
            return

        actual = self.cabeza
        if cb(actual.valor):
            self.cabeza = actual.siguiente
            return

        while actual and actual.siguiente:
            if cb(actual.siguiente.valor):
                actual.siguiente = actual.siguiente.siguiente
                self.longitud -= 1
            actual = actual.siguiente

    def pop(self):
        if self.cabeza is None:
            return None
        
        valor = self.cabeza.valor
        self.cabeza = self.cabeza.siguiente
        self.longitud -= 1

        return valor

    def push(self, valor):
        nodo = QueueNodo(valor)

        if self.cabeza is None:
            self.cabeza = nodo
        else:
            ultimo = self.cabeza
            while ultimo.siguiente is not None:
                ultimo = ultimo.siguiente

            ultimo.siguiente = nodo
            
        self.longitud += 1


class StackNodo():
    def __init__ (self, valor):
        self.valor = valor
        self.anterior = None

class Stack():
    """Implementación de una pila"""

    def __init__(self):
        self.cabeza = None
        self.longitud = 0

    
    def __len__(self):
        return self.longitud
    
    def __iter__(self):
        actual = self.cabeza

        while actual:
            yield actual.valor
            actual = actual.anterior

    def peek(self):
        return self.cabeza

    def unstack(self):
        if self.cabeza is None:
            return None
        
        valor = self.cabeza.valor
        self.cabeza = self.cabeza.anterior
        self.longitud -= 1

        return valor

    def stack(self, valor):
        nodo = StackNodo(valor)

        if self.cabeza is not None:
            nodo.anterior = self.cabeza

        self.cabeza = nodo
        self.longitud += 1

