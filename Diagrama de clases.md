classDiagram
    class Componente {
	    +str nombre
	    +float valor
	    +calcular_corriente(v: float) -> float
	    +calcular_voltaje(i: float) -> float
    }

    class Resistencia {
	    +calcular_corriente(v: float) -> float
	    +calcular_voltaje(i: float) -> float
    }

    class Inductor {
	    +calcular_corriente(v: float) -> float
	    +calcular_voltaje(i: float) -> float
    }

    class Capacitor {
	    +calcular_voltaje(i: float) -> float
        +calcular_corriente(v: float) -> float
    }

    class FuenteDC {
	    +float tensión
        +entregar_tensión() -> float
    }

    class Circuito {
	    +list componentes
	    +str configuración
	    +calcular_corriente_total() -> float
        +calcular_voltajes_componentes() -> list[float]
    }

    Componente <-- Resistencia
    Componente <-- Inductor
    Componente <-- Capacitor
    Circuito --* "1..3" Componente : tiene
    Circuito --* "1" FuenteDC : utiliza
