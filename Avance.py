import matplotlib.pyplot as plt # Primero se debe instalar con el comando "pip install matplotlib"


class Componente:
    def __init__(self, nombre: str, valor: float):
        self.nombre = nombre
        self.valor = valor  # Valor puede ser resistencia, capacitancia o inductancia

    def calcular_corriente(self, voltaje: float) -> float:
        pass

    def calcular_voltaje(self, corriente: float) -> float:
        pass

class Resistencia(Componente):
    def calcular_corriente(self, voltaje: float) -> float:
        return voltaje / self.valor  # Ley de Ohm: I = V / R

    def calcular_voltaje(self, corriente: float) -> float:
        return corriente * self.valor  # Ley de Ohm: V = I * R

class FuenteDC:
    def __init__(self, tension: float):
        self.tension = tension  # Tensión de la fuente en volts

    def entregar_tension(self) -> float:
        return self.tension

class Circuito:
    def __init__(self, componentes: list, configuracion: str):
        self.componentes = componentes
        self.configuracion = configuracion

    def calcular_corriente_total(self) -> float:
        """Cálculo simplificado para un circuito en serie."""
        match self.configuracion:
            case "serie":
                resistencia_total = sum(componente.valor for componente in 
                                        self.componentes if 
                                        isinstance(componente, Resistencia))
                fuente = next((componente for componente in self.componentes 
                               if isinstance(componente, FuenteDC)), 0)
                if fuente:
                    return fuente.tension / resistencia_total
            case "paralelo":
                return 0.0
        pass

    def graficar_resultados(self):
        """Generar gráficas de voltaje y corriente para cada componente."""
        # Para hacer la gráfica se crean listas con los elementos que se van a imprimir
        voltajes = []
        nombres = []
        corrientes = []

        corriente_total = self.calcular_corriente_total()
        for componente in self.componentes:
            if isinstance(componente, Resistencia): # Comprueba si la clase es una resistencia
                voltaje = componente.calcular_voltaje(corriente_total)
                voltajes.append(voltaje)
                nombres.append(componente.nombre)
                corrientes.append(corriente_total)
                # Se calculan los valores respectivos a la resistencia y se añaden a las listas
                
        # Se define el tamaño de la ventana con la gráfica
        plt.figure(figsize=(10, 6))

        # Se crea la gráfica de voltajes en una subgráfica
        plt.subplot(2, 1, 1)
        plt.bar(nombres, voltajes, color='blue') # Genera gráfico de barras con los valores de la lista
        plt.title("Voltajes en los Componentes")
        plt.ylabel("Voltaje (V)") # Nombre del eje
        plt.grid(axis='y', linestyle='--', alpha=0.7) # Se configuran las líneas guía de la gráfica

        # Lo mismo de arriba pero con la de corrientes
        plt.subplot(2, 1, 2)
        plt.bar(nombres, corrientes, color='orange')
        plt.title("Corrientes en los Componentes")
        plt.ylabel("Corriente (A)")
        plt.xlabel("Componentes")
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Se acomodan las gráficas para que no se solapen y luego se muestran
        plt.tight_layout()
        plt.show()

# Ejemplo:
if __name__ == "__main__":
    r1 = Resistencia("R1", 100)  
    r2 = Resistencia("R2", 200)  
    fuente_tension = FuenteDC(10)        

    circuito = Circuito([fuente_tension, r1, r2], "serie")
    
    print(f"Corriente total en el circuito: {circuito.calcular_corriente_total()} A")
    circuito.graficar_resultados()
