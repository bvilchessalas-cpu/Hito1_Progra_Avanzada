class ElementoRed:
    """
    Clase base para representar un elemento de la red eléctrica.
    Recibe un nombre (string).
    """

    def __init__(self, nombre: str):
        self.__nombre = nombre

    def get_nombre(self) -> str:
        return self.__nombre


class Generador(ElementoRed):
    """
    Clase que representa un generador eléctrico.
    Hereda de ElementoRed.
    """

    def __init__(
        self,
        nombre: str,
        potencia: float,
        potencia_max: float,
        costo_operacion: float,
    ):
        super().__init__(nombre)
        if potencia_max <= 0:
            raise ValueError("La potencia máxima debe ser mayor a 0 MW.")
        if costo_operacion < 0:
            raise ValueError("El costo de operación no puede ser negativo.")

        self.__potencia_max = float(potencia_max)
        self.__potencia_min = float(potencia_max) * 0.1
        self.__costo_operacion = float(costo_operacion)
        self.__potencia = 0.0

        self.set_potencia(potencia)

    def get_info(self) -> str:
        return (
            f"Generador: {self.get_nombre()}, "
            f"Potencia: {self.__potencia:.1f} MW, "
            f"Máxima: {self.__potencia_max:.1f} MW, "
            f"Mínima: {self.__potencia_min:.1f} MW, "
            f"Costo: {self.__costo_operacion:.1f} USD/MWh"
        )

    def get_potencia(self) -> float:
        return self.__potencia

    def get_potencia_max(self) -> float:
        return self.__potencia_max

    def get_potencia_min(self) -> float:
        return self.__potencia_min

    def get_costo_operacion(self) -> float:
        return self.__costo_operacion

    def set_potencia(self, potencia: float) -> None:
        # Permite 0.0 MW (generador apagado) o dentro del rango técnico [P_min, P_max]
        if potencia == 0.0 or (self.__potencia_min <= potencia <= self.__potencia_max):
            self.__potencia = float(potencia)
        else:
            raise ValueError(
                f"La potencia {potencia} MW está fuera del rango técnico "
                f"[{self.__potencia_min}, {self.__potencia_max}] MW (o 0 MW si está apagado)."
            )


class Carga(ElementoRed):
    """
    Clase que representa una carga o consumo en la red.
    Hereda de ElementoRed.
    """

    def __init__(self, nombre: str, demanda: float):
        super().__init__(nombre)
        self.__demanda = 0.0
        self.set_demanda(demanda)

    def get_info(self) -> str:
        return f"Carga: {self.get_nombre()}, Demanda: {self.__demanda:.1f} MW"

    def get_demanda(self) -> float:
        return self.__demanda

    def set_demanda(self, demanda: float) -> None:
        if demanda >= 0:
            self.__demanda = float(demanda)
        else:
            raise ValueError("La demanda no puede ser negativa.")


class LineaTransmision(ElementoRed):
    """
    Clase que representa una línea de transmisión entre barras.
    Hereda de ElementoRed.
    """

    def __init__(
        self,
        nombre: str,
        capacidad: float,
        perdidas: float,
        capacidad_max: float,
    ):
        super().__init__(nombre)
        self.__capacidad_max = float(capacidad_max)
        self.__perdidas = float(perdidas)
        self.__capacidad = 0.0
        self.set_capacidad(capacidad)

    def get_info(self) -> str:
        return (
            f"Línea de Transmisión: {self.get_nombre()}, "
            f"Capacidad: {self.__capacidad:.1f} MW, "
            f"Pérdidas: {self.__perdidas:.1f}%, "
            f"Máxima: {self.__capacidad_max:.1f} MW"
        )

    def get_capacidad(self) -> float:
        return self.__capacidad

    def get_capacidad_max(self) -> float:
        return self.__capacidad_max

    def get_perdidas(self) -> float:
        return self.__perdidas

    def set_capacidad(self, capacidad: float) -> None:
        if 0 <= capacidad <= self.__capacidad_max:
            self.__capacidad = float(capacidad)
        else:
            raise ValueError(
                f"La capacidad {capacidad} MW está fuera del rango "
                f"[0, {self.__capacidad_max}] MW."
            )


class Nodo(ElementoRed):
    """
    [NUEVO HITO 2] Clase que representa una Barra (Nodo) del sistema eléctrico.
    Agrupa los generadores y cargas conectados físicamente a la barra.
    """

    def __init__(self, nombre: str, voltaje_nominal_kv: float = 220.0):
        super().__init__(nombre)
        if voltaje_nominal_kv <= 0:
            raise ValueError("El voltaje nominal debe ser positivo.")
        self.__voltaje_nominal_kv = float(voltaje_nominal_kv)
        self.__generadores_locales = []
        self.__cargas_locales = []

    def get_voltaje_nominal(self) -> float:
        return self.__voltaje_nominal_kv

    def conectar_generador(self, generador: Generador) -> None:
        if isinstance(generador, Generador):
            self.__generadores_locales.append(generador)
        else:
            raise TypeError("Se esperaba un objeto de tipo Generador.")

    def conectar_carga(self, carga: Carga) -> None:
        if isinstance(carga, Carga):
            self.__cargas_locales.append(carga)
        else:
            raise TypeError("Se esperaba un objeto de tipo Carga.")

    def get_generadores_locales(self) -> list:
        return list(self.__generadores_locales)

    def get_cargas_locales(self) -> list:
        return list(self.__cargas_locales)

    def balance_nodal_mw(self) -> float:
        inyectada = sum(g.get_potencia() for g in self.__generadores_locales)
        retirada = sum(c.get_demanda() for c in self.__cargas_locales)
        return inyectada - retirada

    def get_info(self) -> str:
        return (
            f"Nodo (Barra): {self.get_nombre()} ({self.__voltaje_nominal_kv} kV) | "
            f"Generadores: {len(self.__generadores_locales)}, "
            f"Cargas: {len(self.__cargas_locales)}, "
            f"Inyección Neta: {self.balance_nodal_mw():.1f} MW"
        )


class SistemaPotencia:
    """
    Clase gestora del sistema eléctrico.
    En Hito 2 incorpora:
    - Tabla Hash (__nodos: dict) para acceso O(1) a barras por identificador.
    - Algoritmo Mergesort desde cero O(n log n) para ordenar generadores por costo.
    - Despacho Económico por orden de mérito.
    """

    def __init__(self, nombre: str):
        self.__nombre = nombre
        self.__generadores = []
        self.__cargas = []
        self.__lineas = []
        # TDA Tabla Hash (diccionario) para acceso O(1) por nombre de barra
        self.__nodos = {}

    def get_nombre(self) -> str:
        return self.__nombre

    # --- Gestión de Nodos mediante Tabla Hash O(1) ---
    def agregar_nodo(self, nodo: Nodo) -> None:
        if not isinstance(nodo, Nodo):
            raise TypeError("El elemento ingresado debe ser un objeto Nodo.")
        clave = nodo.get_nombre()
        if clave in self.__nodos:
            raise ValueError(f"El nodo '{clave}' ya está registrado en el sistema.")
        self.__nodos[clave] = nodo

    def obtener_nodo(self, nombre_nodo: str) -> Nodo:
        """
        Acceso en tiempo constante promedio O(1) mediante Tabla Hash.
        """
        if nombre_nodo in self.__nodos:
            return self.__nodos[nombre_nodo]
        raise KeyError(f"No existe el nodo '{nombre_nodo}' en la tabla hash.")

    def get_nodos(self) -> dict:
        return dict(self.__nodos)

    # --- Gestión de Elementos de Red ---
    def agregar_generador(self, generador: Generador, nombre_nodo: str = None) -> None:
        if not isinstance(generador, Generador):
            raise TypeError("El elemento ingresado debe ser un objeto Generador.")
        self.__generadores.append(generador)
        if nombre_nodo is not None:
            nodo = self.obtener_nodo(nombre_nodo)
            nodo.conectar_generador(generador)

    def agregar_carga(self, carga: Carga, nombre_nodo: str = None) -> None:
        if not isinstance(carga, Carga):
            raise TypeError("El elemento ingresado debe ser un objeto Carga.")
        self.__cargas.append(carga)
        if nombre_nodo is not None:
            nodo = self.obtener_nodo(nombre_nodo)
            nodo.conectar_carga(carga)

    def agregar_linea(self, linea: LineaTransmision) -> None:
        if not isinstance(linea, LineaTransmision):
            raise TypeError("El elemento ingresado debe ser un objeto LineaTransmision.")
        self.__lineas.append(linea)

    def get_generadores(self) -> list:
        return list(self.__generadores)

    def get_cargas(self) -> list:
        return list(self.__cargas)

    def get_lineas(self) -> list:
        return list(self.__lineas)

    # --- Algoritmo de Ordenamiento desde cero: Mergesort O(n log n) ---
    def _mergesort_generadores(self, lista_gen: list) -> list:
        """
        Ordena recursivamente una lista de objetos Generador de menor a mayor
        costo de operación (USD/MWh) utilizando el algoritmo Mergesort.
        Complejidad temporal: O(n log n) en mejor, promedio y peor caso.
        """
        if len(lista_gen) <= 1:
            return lista_gen

        medio = len(lista_gen) // 2
        izquierda = self._mergesort_generadores(lista_gen[:medio])
        derecha = self._mergesort_generadores(lista_gen[medio:])

        return self._merge(izquierda, derecha)

    def _merge(self, izquierda: list, derecha: list) -> list:
        """
        Mezcla dos sublistas ordenadas de generadores en O(n).
        """
        resultado = []
        i = 0
        j = 0

        while i < len(izquierda) and j < len(derecha):
            if izquierda[i].get_costo_operacion() <= derecha[j].get_costo_operacion():
                resultado.append(izquierda[i])
                i += 1
            else:
                resultado.append(derecha[j])
                j += 1

        while i < len(izquierda):
            resultado.append(izquierda[i])
            i += 1

        while j < len(derecha):
            resultado.append(derecha[j])
            j += 1

        return resultado

    def ordenar_generadores_por_merito(self) -> list:
        """
        Actualiza y retorna la lista de generadores ordenada por costo creciente.
        """
        self.__generadores = self._mergesort_generadores(self.__generadores)
        return list(self.__generadores)

    # --- Algoritmo de Despacho Económico ---
    def ejecutar_despacho_economico(self) -> float:
        """
        Clasifica los generadores de más barato a más caro con Mergesort O(n log n)
        y asigna potencia hasta cubrir la demanda total en O(n).
        Retorna el costo operativo total del sistema en USD/h.
        """
        demanda_pendiente = self.demanda_total()
        capacidad_sistema = sum(g.get_potencia_max() for g in self.__generadores)

        if demanda_pendiente > capacidad_sistema:
            raise ValueError(
                f"Demanda total ({demanda_pendiente} MW) supera la capacidad "
                f"instalada máxima del sistema ({capacidad_sistema} MW)."
            )

        # Paso 1: Ordenar generadores de menor a mayor costo en O(n log n)
        generadores_ordenados = self.ordenar_generadores_por_merito()

        # Paso 2: Asignar carga por orden de mérito en O(n)
        costo_total_usd_h = 0.0
        for gen in generadores_ordenados:
            if demanda_pendiente <= 0:
                gen.set_potencia(0.0)
            else:
                p_min = gen.get_potencia_min()
                p_max = gen.get_potencia_max()

                if demanda_pendiente >= p_max:
                    p_despachada = p_max
                elif demanda_pendiente >= p_min:
                    p_despachada = demanda_pendiente
                else:
                    # Si la demanda residual es menor al mínimo técnico,
                    # se despacha en su mínimo técnico P_min.
                    p_despachada = p_min

                gen.set_potencia(p_despachada)
                demanda_pendiente -= p_despachada
                costo_total_usd_h += p_despachada * gen.get_costo_operacion()

        return costo_total_usd_h

    def potencia_generada_total(self) -> float:
        return sum(g.get_potencia() for g in self.__generadores)

    def demanda_total(self) -> float:
        return sum(c.get_demanda() for c in self.__cargas)

    def get_info(self) -> str:
        info_gen = "\n  ".join(g.get_info() for g in self.__generadores)
        info_nodos = "\n  ".join(n.get_info() for n in self.__nodos.values())
        return (
            f"=== Sistema: {self.__nombre} ===\n"
            f"Nodos registrados (Hash O(1)): {len(self.__nodos)}\n"
            f"  {info_nodos}\n"
            f"Generadores en orden de mérito ({len(self.__generadores)}):\n"
            f"  {info_gen}\n"
            f"Generación total: {self.potencia_generada_total():.1f} MW\n"
            f"Demanda total:    {self.demanda_total():.1f} MW"
        )


if __name__ == "__main__":
    sistema = SistemaPotencia("SEN - Simulación Hito 2")

    # 1. Creación y registro de Nodos en Tabla Hash O(1)
    n_quillota = Nodo("Barra_Quillota", 220.0)
    n_polpaico = Nodo("Barra_Polpaico", 500.0)
    n_jahuel = Nodo("Barra_AltoJahuel", 500.0)

    sistema.agregar_nodo(n_quillota)
    sistema.agregar_nodo(n_polpaico)
    sistema.agregar_nodo(n_jahuel)

    # 2. Creación de Generadores (ingresados desordenados por costo)
    g_diesel = Generador("G1_Diesel_Quillota", potencia=50, potencia_max=100, costo_operacion=120.0)
    g_solar = Generador("G2_Solar_Polpaico", potencia=80, potencia_max=150, costo_operacion=15.0)
    g_gas = Generador("G3_Gas_Quillota", potencia=100, potencia_max=200, costo_operacion=55.0)
    g_hidro = Generador("G4_Hidro_AltoJahuel", potencia=90, potencia_max=180, costo_operacion=25.0)

    sistema.agregar_generador(g_diesel, "Barra_Quillota")
    sistema.agregar_generador(g_solar, "Barra_Polpaico")
    sistema.agregar_generador(g_gas, "Barra_Quillota")
    sistema.agregar_generador(g_hidro, "Barra_AltoJahuel")

    # 3. Creación de Cargas (Demanda total = 380 MW)
    c_industrial = Carga("Carga_Minera_Polpaico", demanda=220.0)
    c_urbana = Carga("Carga_Urbana_AltoJahuel", demanda=160.0)

    sistema.agregar_carga(c_industrial, "Barra_Polpaico")
    sistema.agregar_carga(c_urbana, "Barra_AltoJahuel")

    # 4. Línea de transmisión
    l1 = LineaTransmision("L1_Polpaico_Quillota", capacidad=100, perdidas=2.0, capacidad_max=250)
    sistema.agregar_linea(l1)

    # 5. Prueba de búsqueda O(1) en Tabla Hash
    barra_buscada = sistema.obtener_nodo("Barra_Quillota")
    print(f"[Acceso Hash O(1)] -> {barra_buscada.get_info()}\n")

    # 6. Ejecución del Despacho Económico con Mergesort
    costo_total = sistema.ejecutar_despacho_economico()
    print(sistema.get_info())
    print(f"Costo Operativo Total Óptimo: {costo_total:,.2f} USD/h")