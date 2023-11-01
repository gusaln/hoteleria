from listas import Stack


class Arbol(object):
    """Árbol"""
    def __init__(self, valor):
        self.valor = valor
        self.izquierda = None
        self.derecha = None


    def serialize(self) -> list:
        """Encodes a tree to a single string."""

        normalizado = list()
        stack = [self]
        while stack:
            tmp = stack.pop()
            if tmp is not None:
                normalizado.append(tmp.valor)
                stack.append(tmp.izquierda)
                stack.append(tmp.derecha)
        return normalizado


class ArbolBinario(Arbol):
    """Árbol binario"""

    def agregar(self, valor):
        if valor < self.valor:
            if self.izquierda is None:
                self.izquierda = ArbolBinario(valor)
            else:
                self.izquierda.agregar(valor)
        elif valor > self.valor:
            if self.derecha is None:
                self.derecha = ArbolBinario(valor)
            else:
                self.derecha.agregar(valor)

    def buscar(self, busqueda):
        """Devuelve el nodo con el valor busqueda"""
        if self is None:
            return None
        if self.valor == busqueda:
            return self
        if busqueda < self.valor:
            return self.buscar(self.izquierda, busqueda)
        else:
            return self.buscar(self.derecha, busqueda)


    def borrar(self, busqueda):
        """Borra el nodo con el valor busqueda"""
        if busqueda < self.valor:
            self.izquierda = self.izquierda.borrar(busqueda)
        elif busqueda > self.valor:
            self.derecha = self.derecha.borrar(busqueda)

        # Existe la posibilidad de que no esté en el árbol, por lo que verificamos que sea igual en lugar de usar sólo `else`
        elif self.valor == busqueda:
            if self.izquierda is None and self.derecha is None:
                return None
            if self.izquierda is None:
                return self.derecha
            if self.derecha is None:
                return self.izquierda

            sucesor = self.derecha.minimo()
            
            self.valor = sucesor.valor
            self.derecha = self.derecha.borrar()

        return self

    def minimo(self):
        """Devuelve el nodo del árbol con el valor mínimo"""
        minimo = self
        while minimo.izquierda is not None:
            minimo = minimo.izquierda
        return minimo

    def inorden(self):
        """Devuelve el arbol en inorden"""
        if self.izquierda:
            yield from self.izquierda.inorden()
        yield self.valor
        if self.derecha:
            yield from self.derecha.inorden()

    def preorden(self):
        """Devuelve el arbol en preorden"""
        yield self.valor
        if self.izquierda:
            yield from self.izquierda.preorden()
        if self.derecha:
            yield from self.derecha.preorden()

    def posorden(self):
        """Devuelve el arbol en posorden"""
        if self.izquierda:
            yield from self.izquierda.posorden()
        if self.derecha:
            yield from self.derecha.posorden()
        yield self.valor


    def __iter__(self):
        yield from self.inorden()


    @staticmethod
    def deserialize(normalizado: list):
        """Decodes your encoded data to tree."""
        if normalizado == []:
            return None

        root = ArbolBinario(normalizado.pop())
        stack = []
        stack.append(root)
        while stack:
            tmp = stack.pop()
            izquierda = normalizado.pop() if len(normalizado) > 0 else None
            derecha = normalizado.pop() if len(normalizado) > 0 else None
            if izquierda != None:
                tmp.izquierda = ArbolBinario(izquierda)
                stack.append(tmp.izquierda)
            else:
                tmp.izquierda = None

            if derecha != None:
                tmp.derecha = ArbolBinario(derecha)
                stack.append(tmp.derecha)
            else:
                tmp.derecha = None
        return root
