A continuación se presenta la propuesta del diagrama de clases para simular circuitos eléctricos en corriente directa utilizando POO:

```mermaid
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
        +calcular_corriente(v: float) -> float
        +calcular_voltaje(i: float) -> float
    }

    class FuenteDC {
        +float tensión
        +get_tension() -> float
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
    Circuito --* "1..3" Componente : contiene
    Circuito --* "1" FuenteDC : utiliza
```

Por otra parte, para crear las gráficas de tensión y corriente se planea utilizar matplotlib.
