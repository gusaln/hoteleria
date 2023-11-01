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


def get_height_of(root: Arbol = None) -> int:
    """Devuelve la altura del árbol"""
    if root is None:
        return 0

    return 1 + max(get_height_of(root.izquierda), get_height_of(root.derecha))


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


# Create a tree node
class ArbolBinarioBalanceado(Arbol):
    def __init__(self, valor):
        super().__init__(valor)
        self.altura = 1

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

    def agregar(self, valor):
        if valor < self.valor:
            if self.izquierda is None:
                self.izquierda = ArbolBinarioBalanceado(valor)
            else:
                self.izquierda.agregar(valor)
        else:
            if self.derecha is None:
                self.derecha = ArbolBinarioBalanceado(valor)
            else:
                self.derecha.agregar(valor)

        self.altura = 1 + max(self.get_height(self.izquierda),
                              self.get_height(self.derecha))

        # Update the balance factor and balance the tree
        balanceFactor = self.get_balance(self)
        if balanceFactor > 1:
            if valor < self.izquierda.valor:
                return self.__rotar_derecha()
            else:
                self.izquierda = self.__rotar_izquierda(self.izquierda)
                return self.__rotar_derecha()

        if balanceFactor < -1:
            if valor > self.derecha.valor:
                return self.__rotar_izquierda()
            else:
                self.derecha = self.__rotar_derecha(self.derecha)
                return self.__rotar_izquierda()

        return self

    # Function to delete a node
    def borrar(self, valor):
        if valor < self.valor:
            self.izquierda = self.izquierda.borrar(valor)
        elif valor > self.valor:
            self.derecha = self.derecha.borrar(self, valor)
        else:
            if self.izquierda is None:
                temp = self.derecha
                return temp
            elif self.derecha is None:
                temp = self.izquierda
                return temp
            temp = self.get_minimo(self.derecha)
            self.valor = temp.valor
            self.derecha = self.borrar(self.derecha,
                                       temp.valor)
        # Update the balance factor of nodes
        self.altura = 1 + max(self.get_height(self.izquierda),
                              self.get_height(self.derecha))

        balanceFactor = self.get_balance(self)

        # Balance the tree
        if balanceFactor > 1:
            if self.get_balance(self.izquierda) >= 0:
                return self.__rotar_derecha()
            else:
                self.izquierda = self.__rotar_izquierda(self.izquierda)
                return self.__rotar_derecha()
        if balanceFactor < -1:
            if self.get_balance(self.derecha) <= 0:
                return self.__rotar_izquierda()
            else:
                self.derecha = self.__rotar_derecha(self.derecha)
                return self.__rotar_izquierda()
        return self

    # Function to perform left rotation
    def __rotar_izquierda(self, root = None):
        if root is None:
            root = self

        y = root.derecha
        temp = y.izquierda
        y.izquierda = self
        root.derecha = temp
        root.altura = 1 + max(root.get_height(root.izquierda),
                              root.get_height(root.derecha))
        y.altura = 1 + max(root.get_height(y.izquierda),
                           root.get_height(y.derecha))
        return y

    # Function to perform right rotation
    def __rotar_derecha(self, root = None):
        if root is None:
            root = self

        y = root.izquierda
        temp = y.derecha
        y.derecha = self
        root.izquierda = temp
        root.altura = 1 + max(root.get_height(root.izquierda),
                              root.get_height(root.derecha))
        y.altura = 1 + max(root.get_height(y.izquierda),
                           root.get_height(y.derecha))
        return y

    # Get the height of the node
    def get_height(self, root):
        if not root:
            return 0
        return root.altura

    # Get balance factore of the node
    def get_balance(self, root):
        if not root:
            return 0
        return self.get_height(root.izquierda) - self.get_height(root.derecha)

    def get_minimo(self, root):
        if root is None or root.izquierda is None:
            return root
        return self.get_minimo(root.izquierda)
