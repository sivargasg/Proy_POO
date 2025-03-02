A continuación se presenta la propuesta del diagrama de clases para simular circuitos eléctricos en corriente directa utilizando POO:

```mermaid
classDiagram
    class FuenteDC {
      +float voltaje
      +entregar_tension(tiempo: np.ndarray) np.ndarray
    }

    class Resistencia {
      +float valor
      +__init__(valor: float)
    }

    class Inductor {
      +float valor
      +__init__(valor: float)
    }

    class Capacitor {
      +float valor
      +__init__(valor: float)
    }

    class Circuito {
      +list componentes
      +string configuracion
      +FuenteDC fuente
      +simular(tiempo: np.ndarray) dict
      -_simular_serie(tiempo: np.ndarray) dict
      -_simular_paralelo(tiempo: np.ndarray) dict
    }

    class App {
      +resistencia_var: tk.StringVar
      +inductor_var: tk.StringVar
      +capacitor_var: tk.StringVar
      +configuracion_var: tk.StringVar
      +duracion_var: tk.StringVar
      +voltaje_var: tk.StringVar
      +_crear_widgets()
      +simular()
      +graficar(resultados: dict)
    }

    tk.Tk <|-- App
    Circuito --> FuenteDC : usa
    Circuito o-- "1" Resistencia
    Circuito o-- "0..1" Inductor
    Circuito o-- "0..1" Capacitor 
    App --> Circuito : crea
```

Por otra parte, para crear las gráficas de tensión y corriente se utiliza matplotlib.
