class ElementoRed:
    """
    Clase base para representar un elemento de la red eléctrica.

    Recibe un nombre (string)
    """

    def __init__(self, nombre):
        self.__nombre = nombre

    def get_nombre(self):
        return self.__nombre


class Generador(ElementoRed):
    """
    Clase que representa un generador.

    Hereda atributos de ElementoRed, nombre (string)
    Recibe potencia (float), potencia_max (float), costo_operacion (float)
    """

    def __init__(self, nombre, potencia, potencia_max, costo_operacion):
        super().__init__(nombre)

        self.__potencia_max = potencia_max
        self.__potencia_min = potencia_max * 0.1
        self.__costo_operacion = costo_operacion

        self.set_potencia(potencia)

    def get_info(self):
        return (
            f"Generador: {self.get_nombre()}, "
            f"Potencia: {self.__potencia} MW, "
            f"Máxima: {self.__potencia_max} MW, "
            f"Mínima: {self.__potencia_min} MW, "
            f"Costo: {self.__costo_operacion} USD/MWh"
        )

    def get_potencia(self):
        return self.__potencia

    def get_potencia_max(self):
        return self.__potencia_max

    def get_potencia_min(self):
        return self.__potencia_min

    def get_costo_operacion(self):
        return self.__costo_operacion

    def set_potencia(self, potencia):
        if self.__potencia_min <= potencia <= self.__potencia_max:
            self.__potencia = potencia
        else:
            raise ValueError(
                f"La potencia {potencia} MW está fuera del rango "
                f"[{self.__potencia_min}, {self.__potencia_max}] MW."
            )


class Carga(ElementoRed):
    """
    Clase que representa una carga.
    Hereda atributos de ElementoRed, nombre (string)
    Recibe demanda (float)
    """

    def __init__(self, nombre, demanda):
        super().__init__(nombre)
        self.set_demanda(demanda)

    def get_info(self):
        return (
            f"Carga: {self.get_nombre()}, "
            f"Demanda: {self.__demanda} MW"
        )

    def get_demanda(self):
        return self.__demanda

    def set_demanda(self, demanda):
        if demanda >= 0:
            self.__demanda = demanda
        else:
            raise ValueError("La demanda no puede ser negativa.")


class LineaTransmision(ElementoRed):
    """
    Clase que representa una línea de transmisión.
    Hereda atributos de ElementoRed, nombre (string)
    Recibe capacidad (float), perdidas (float), capacidad_max (float)
    """

    def __init__(self, nombre, capacidad, perdidas, capacidad_max):
        super().__init__(nombre)

        self.__capacidad_max = capacidad_max
        self.__perdidas = perdidas

        self.set_capacidad(capacidad)

    def get_info(self):
        return (
            f"Línea de Transmisión: {self.get_nombre()}, "
            f"Capacidad: {self.__capacidad} MW, "
            f"Pérdidas: {self.__perdidas}%, "
            f"Máxima: {self.__capacidad_max} MW"
        )

    def get_capacidad(self):
        return self.__capacidad

    def get_capacidad_max(self):
        return self.__capacidad_max

    def get_perdidas(self):
        return self.__perdidas

    def set_capacidad(self, capacidad):
        if 0 <= capacidad <= self.__capacidad_max:
            self.__capacidad = capacidad
        else:
            raise ValueError(
                f"La capacidad {capacidad} MW está fuera del rango "
                f"[0, {self.__capacidad_max}] MW."
            )



class SistemaPotencia:
    """
    Clase gestora del sistema eléctrico.

    Administra los generadores, cargas y líneas
    de transmisión que pertenecen al sistema.
    """

    def __init__(self, nombre):
        self.__nombre = nombre
        self.__generadores = []
        self.__cargas = []
        self.__lineas = []

    def get_nombre(self):
        return self.__nombre

    def agregar_generador(self, generador):
        if isinstance(generador, Generador):
            self.__generadores.append(generador)
        else:
            raise TypeError(
                "El elemento ingresado debe ser un objeto Generador."
            )

    def agregar_carga(self, carga):
        if isinstance(carga, Carga):
            self.__cargas.append(carga)
        else:
            raise TypeError(
                "El elemento ingresado debe ser un objeto Carga."
            )

    def agregar_linea(self, linea):
        if isinstance(linea, LineaTransmision):
            self.__lineas.append(linea)
        else:
            raise TypeError(
                "El elemento ingresado debe ser un objeto LineaTransmision."
            )

    def get_generadores(self):
        return self.__generadores

    def get_cargas(self):
        return self.__cargas

    def get_lineas(self):
        return self.__lineas

    def potencia_generada_total(self):
        total = 0

        for generador in self.__generadores:
            total += generador.get_potencia()
        
        return total

    def demanda_total(self):
        total = 0

        for carga in self.__cargas:
            total += carga.get_demanda()

        return total

    def get_info(self):
        return (
            f"Sistema: {self.__nombre}\n"
            f"Cantidad de generadores: {len(self.__generadores)}\n"
            f"Cantidad de cargas: {len(self.__cargas)}\n"
            f"Cantidad de líneas: {len(self.__lineas)}\n"
            f"Generación total: {self.potencia_generada_total()} MW\n"
            f"Demanda total: {self.demanda_total()} MW"
        )





if __name__ == "__main__":

        sistema = SistemaPotencia("Sistema de Prueba")

        g1 = Generador(
        "G1",
        potencia=100,
        potencia_max=200,
        costo_operacion=30
        )

        g2 = Generador(
        "G2",
        potencia=60,
        potencia_max=120,
        costo_operacion=45
        )

        c1 = Carga(
        "Carga 1",
        demanda=140
        )

        l1 = LineaTransmision(
        "Línea 1",
        capacidad=100,
        perdidas=2,
        capacidad_max=150
        )

        sistema.agregar_generador(g1)
        sistema.agregar_generador(g2)
        sistema.agregar_carga(c1)
        sistema.agregar_linea(l1)

        print(sistema.get_info())
