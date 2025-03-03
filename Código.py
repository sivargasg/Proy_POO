import tkinter as tk
from scipy.integrate import solve_ivp
from tkinter import ttk, messagebox
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class FuenteDC:
    def __init__(self, voltaje):
        self.voltaje = voltaje  # Voltaje en Voltios

    def entregar_tension(self, tiempo):
        # Devuelve un vector con el escalón DC usando np.
        return np.full_like(tiempo, self.voltaje, dtype=float)

class Resistencia:
    def __init__(self, valor):
        if valor <= 0:
            raise ValueError("La resistencia debe ser mayor que cero.")
        self.valor = valor  # Valor en Ohmios

class Inductor:
    def __init__(self, valor):
        if valor <= 0:
            raise ValueError("El inductor debe ser mayor que cero.")
        self.valor = valor  # Valor en Henrios

class Capacitor:
    def __init__(self, valor):
        if valor <= 0:
            raise ValueError("El capacitor debe ser mayor que cero.")
        self.valor = valor  # Valor en Faradios

class Circuito:
    def __init__(self, componentes: list, configuracion: str, fuente: FuenteDC):
        """
        componentes: lista de instancias de Resistencia, Inductor y/o Capacitor.
        configuracion: 'serie' o 'paralelo'
        fuente: instancia de FuenteDC.
        """
        self.componentes = componentes
        self.configuracion = configuracion.lower()
        self.fuente = fuente

    def simular(self, tiempo: np.ndarray):
        if self.configuracion == "serie":
            return self._simular_serie(tiempo)
        elif self.configuracion == "paralelo":
            return self._simular_paralelo(tiempo)
        else:
            raise ValueError("Configuración no soportada. Use 'serie' o 'paralelo'.")

    def _simular_serie(self, tiempo: np.ndarray):
        R = next((c for c in self.componentes if isinstance(c, Resistencia)), None)
        L = next((c for c in self.componentes if isinstance(c, Inductor)), None)
        C = next((c for c in self.componentes if isinstance(c, Capacitor)), None)
        V_s = self.fuente.entregar_tension(tiempo)
        V0 = V_s[0]

        # Por defecto se ponen todos los valores como cero
        I = np.zeros_like(tiempo)
        V_R = np.zeros_like(tiempo)
        V_L = np.zeros_like(tiempo)
        V_C = np.zeros_like(tiempo)
        
        if (C is not None) and (L is None):
            def ecuacion_RC(t, Vc):
                # Esta es la ecuación del diferencial de Vc sacada con un análisis al circuito  
                return (V0 - Vc) / (R.valor * C.valor)
            # Aqui se resuelve la ecuación anterior con una integral y un valor inicial
            sol = solve_ivp(ecuacion_RC, (tiempo[0], tiempo[-1]), [0], t_eval=tiempo)
            V_C = sol.y[0]
            # La corriente del circuito es la derivada de Vc por la capacitancia
            I = C.valor * np.gradient(V_C, tiempo)
            V_R = V_s - V_C

        elif (L is not None) and (C is None):
            def ecuacion_RL(t, I_val):
                return (V0 - R.valor * I_val) / L.valor
            sol = solve_ivp(ecuacion_RL, (tiempo[0], tiempo[-1]), [0], t_eval=tiempo)
            I = sol.y[0]
            V_R = R.valor * I
            V_L = V_s - V_R

        elif (L is not None) and (C is not None):
            def sistema_RLC(t, Y):
                ''' 
                "Y" es un vector que tiene dos ecuaciones: 
                la del diferencial de la corriente del inductor y la del diferencial 
                de voltaje del capacitor
                '''
                I_val, Vc = Y
                dIdt = (V0 - R.valor * I_val - Vc) / L.valor
                dVcdt = I_val / C.valor
                return [dIdt, dVcdt]
            sol = solve_ivp(sistema_RLC, (tiempo[0], tiempo[-1]), [0, 0], t_eval=tiempo)
            I = sol.y[0]
            V_C = sol.y[1]
            V_R = R.valor * I
            V_L = V_s - V_R - V_C
        
        elif (L is None) and (C is None) and (R is not None):
            I = np.full_like(tiempo, V0 / R.valor)
            V_R = np.full_like(tiempo, V0)
            
        else:
            raise ValueError("Para serie se requiere al menos una Resistencia, un Inductor y/o Capacitor. También se puede una Resistencia")

        resultados = {
            'Tiempo': tiempo,
            'Voltaje Fuente': V_s,
            'Corriente': I,
            'Voltaje Resistencia': V_R,
            'Voltaje Inductor': V_L,
            'Voltaje Capacitor': V_C
        }
        return resultados

    def _simular_paralelo(self, tiempo: np.ndarray):
        R = next((c for c in self.componentes if isinstance(c, Resistencia)), None)
        L = next((c for c in self.componentes if isinstance(c, Inductor)), None)
        C = next((c for c in self.componentes if isinstance(c, Capacitor)), None)
        V_s = self.fuente.entregar_tension(tiempo)
        V0 = V_s[0]

        V_nodo = np.zeros_like(tiempo)
        I_R = np.zeros_like(tiempo)
        I_C = np.zeros_like(tiempo)
        I_L = np.zeros_like(tiempo)
        I_total = np.zeros_like(tiempo)

        if (C is not None) and (L is None):
            def ecuacion_RC(t, V):
                return (V0 - V) / (R.valor * C.valor)
            sol = solve_ivp(ecuacion_RC, (tiempo[0], tiempo[-1]), [0], t_eval=tiempo)
            V_nodo = sol.y[0]
            I_R = V_nodo / R.valor
            I_C = C.valor * np.gradient(V_nodo, tiempo)
            I_total = I_R + I_C

        elif (L is not None) and (C is None):
            tau = L.valor / R.valor
            I_R0 = V0 / R.valor
            I_L = I_R0 * (1 - np.exp(-tiempo / tau))
            I_R = I_R0 * np.exp(-tiempo / tau)
            I_total = I_R + I_L
            V_nodo = np.full_like(tiempo, V0)

        elif (L is not None) and (C is not None):
            R_s_valor = 1.0  # Resistencia interna de la fuente para permitir el análisis
            def V_fuente(t):
                t_rampa = 0.001  # 1 ms para evitar cambios instantáneos
                return (V0 / t_rampa) * t if t < t_rampa else V0
            def sistema_RLC_par(t, y):
                V, I_L_val = y
                V0_t = V_fuente(t)
                dVdt = ((V0_t - V) / R_s_valor - V / R.valor - I_L_val) / C.valor
                dI_L_dt = V / L.valor
                return [dVdt, dI_L_dt]
            sol = solve_ivp(sistema_RLC_par, (tiempo[0], tiempo[-1]), [0, 0], t_eval=tiempo)
            V_nodo = sol.y[0]
            I_L = sol.y[1]
            I_R = V_nodo / R.valor
            I_C = C.valor * np.gradient(V_nodo, tiempo)
            I_total = I_R + I_C + I_L
        
        elif (L is None) and (C is None) and (R is not None):
            I_total = np.full_like(tiempo, V0 / R.valor)
            V_nodo = np.full_like(tiempo, V0)
            
        else:
            raise ValueError("Para paralelo se requiere al menos una Resistencia, un Inductor y/o Capacitor. También se puede una Resistencia")

        resultados = {
            'Tiempo': tiempo,
            'Voltaje Nodo': V_nodo,
            'Corriente Total': I_total,
            'Corriente Resistencia': I_R,
            'Corriente Inductor': I_L,
            'Corriente Capacitor': I_C
        }
        return resultados

# Se hace interfaz con Tkinter
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Circuitos RLC, RL, RC")
        self.geometry("800x600")

        # Variables de entrada
        self.resistencia_var = tk.StringVar()
        self.inductor_var = tk.StringVar()
        self.capacitor_var = tk.StringVar()
        self.configuracion_var = tk.StringVar(value="serie")
        self.duracion_var = tk.StringVar(value="1")
        self.voltaje_var = tk.StringVar(value="10")

        # Crear widgets de entrada
        self._crear_widgets()

        # Área para la gráfica
        self.fig, self.ax = plt.subplots(figsize=(7, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _crear_widgets(self):
        frame = tk.Frame(self)
        frame.pack(pady=10)

        tk.Label(frame, text="Resistencia (Ohm):").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(frame, textvariable=self.resistencia_var).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Inductor (H):").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(frame, textvariable=self.inductor_var).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Capacitor (F):").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(frame, textvariable=self.capacitor_var).grid(row=2, column=1, padx=5, pady=5)

        tk.Label(frame, text="Voltaje Fuente (V):").grid(row=3, column=0, padx=5, pady=5)
        tk.Entry(frame, textvariable=self.voltaje_var).grid(row=3, column=1, padx=5, pady=5)

        tk.Label(frame, text="Configuración:").grid(row=4, column=0, padx=5, pady=5)
        opciones = [("Serie", "serie"), ("Paralelo", "paralelo")]
        col = 1
        for texto, valor in opciones:
            tk.Radiobutton(frame, text=texto, variable=self.configuracion_var, value=valor).grid(row=4, column=col, padx=5, pady=5)
            col += 1

        tk.Label(frame, text="Duración (s):").grid(row=5, column=0, padx=5, pady=5)
        tk.Entry(frame, textvariable=self.duracion_var).grid(row=5, column=1, padx=5, pady=5)

        tk.Button(frame, text="Simular", command=self.simular).grid(row=6, column=0, columnspan=2, pady=10)

    def simular(self):
        try:
            R_val = float(self.resistencia_var.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor numérico válido para la Resistencia.")
            return

        try:
            L_val = float(self.inductor_var.get()) if self.inductor_var.get() != "" else None
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor numérico válido para el Inductor.")
            return

        try:
            C_val = float(self.capacitor_var.get()) if self.capacitor_var.get() != "" else None
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor numérico válido para el Capacitor.")
            return

        try:
            duracion = float(self.duracion_var.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor numérico válido para la duración.")
            return

        try:
            voltaje = float(self.voltaje_var.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor numérico válido para el Voltaje de la Fuente.")
            return

        # Crear la fuente DC con el voltaje ingresado
        fuente = FuenteDC(voltaje=voltaje)
        componentes = []
        if R_val:
            componentes.append(Resistencia(valor=R_val))
        if L_val is not None:
            componentes.append(Inductor(valor=L_val))
        if C_val is not None:
            componentes.append(Capacitor(valor=C_val))

        configuracion = self.configuracion_var.get()
        circuito = Circuito(componentes=componentes, configuracion=configuracion, fuente=fuente)

        # Generar vector de tiempo
        t = np.linspace(0, duracion, 500)
        resultados = circuito.simular(t)
        self.graficar(resultados)

    def graficar(self, resultados: dict):
        self.fig.clf()
        tiempo = resultados['Tiempo']

        if self.configuracion_var.get() == "serie":
            ax1 = self.fig.add_subplot(2, 1, 1)
            ax1.plot(tiempo, resultados['Voltaje Fuente'], linestyle='--', color='black', label='Voltaje Fuente')
            ax1.plot(tiempo, resultados['Voltaje Resistencia'], color='green', label='Voltaje Resistencia')
            ax1.plot(tiempo, resultados['Voltaje Inductor'], color='red', label='Voltaje Inductor')
            ax1.plot(tiempo, resultados['Voltaje Capacitor'], color='blue', label='Voltaje Capacitor')
            ax1.set_title("Respuesta de Voltajes en Circuito Serie")
            ax1.set_xlabel("Tiempo (s)")
            ax1.set_ylabel("Voltaje (V)")
            ax1.legend()
            ax1.grid(True)

            ax2 = self.fig.add_subplot(2, 1, 2)
            ax2.plot(tiempo, resultados['Corriente'], color='orange', label='Corriente Circuito')
            ax2.set_title("Respuesta de Corriente en Circuito Serie")
            ax2.set_xlabel("Tiempo (s)")
            ax2.set_ylabel("Corriente (A)")
            ax2.legend()
            ax2.grid(True)
        else:
            ax1 = self.fig.add_subplot(2, 1, 1)
            ax1.plot(tiempo, resultados['Voltaje Nodo'], color='black', label='Voltaje Nodo')
            ax1.set_title("Respuesta de Voltaje en el Nodo (Circuito Paralelo)")
            ax1.set_xlabel("Tiempo (s)")
            ax1.set_ylabel("Voltaje (V)")
            ax1.legend()
            ax1.grid(True)

            ax2 = self.fig.add_subplot(2, 1, 2)
            ax2.plot(tiempo, resultados['Corriente Resistencia'], color='green', label='Corriente Resistencia')
            ax2.plot(tiempo, resultados['Corriente Inductor'], color='red', label='Corriente Inductor')
            ax2.plot(tiempo, resultados['Corriente Capacitor'], color='blue', label='Corriente Capacitor')
            ax2.plot(tiempo, resultados['Corriente Total'], linestyle='--', color='orange', label='Corriente Total')
            ax2.set_title("Respuesta de Corriente (Circuito Paralelo)")
            ax2.set_xlabel("Tiempo (s)")
            ax2.set_ylabel("Corriente (A)")
            ax2.legend()
            ax2.grid(True)

        self.fig.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    app = App()
    app.mainloop()

