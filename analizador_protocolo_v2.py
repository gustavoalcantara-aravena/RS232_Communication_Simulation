import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import time
import random
import numpy as np

class AnalizadorProtocolo(tk.Tk):
    """Analizador de protocolo RS-232.
    
    Esta clase implementa una interfaz gráfica para analizar y visualizar
    datos transmitidos a través del protocolo RS-232, incluyendo la 
    interpretación de tramas y la visualización de señales.
    """
    
    # Constantes de configuración
    DEFAULT_WINDOW_SIZE = "1200x800"
    DEFAULT_BAUD_RATES = ["9600", "19200", "38400", "57600", "115200"]
    DEFAULT_PORTS = ["/dev/ttyS0", "/dev/ttyS1"]
    VOLTAGE_RANGE = (-12, 12)  # Voltaje mínimo y máximo en V
    
    def __init__(self):
        """Inicializa la aplicación y configura la interfaz gráfica."""
        super().__init__()
        self.title("Analizador de Protocolo RS-232")
        self.geometry(self.DEFAULT_WINDOW_SIZE)
        
        # Crear el frame principal
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel de control superior
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Configuración", padding="10")
        self.control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Controles
        self.puerto_label = ttk.Label(self.control_frame, text="Puerto:")
        self.puerto_label.pack(side=tk.LEFT, padx=5)
        self.puerto_combo = ttk.Combobox(self.control_frame, values=self.DEFAULT_PORTS)
        self.puerto_combo.set(self.DEFAULT_PORTS[1])  # /dev/ttyS1 por defecto
        self.puerto_combo.pack(side=tk.LEFT, padx=5)
        
        self.velocidad_label = ttk.Label(self.control_frame, text="Velocidad:")
        self.velocidad_label.pack(side=tk.LEFT, padx=5)
        self.velocidad_combo = ttk.Combobox(self.control_frame, values=self.DEFAULT_BAUD_RATES)
        self.velocidad_combo.set(self.DEFAULT_BAUD_RATES[0])  # 9600 por defecto
        self.velocidad_combo.pack(side=tk.LEFT, padx=5)
        
        self.iniciar_btn = ttk.Button(self.control_frame, text="Iniciar Análisis", 
                                    command=self.iniciar_analisis)
        self.iniciar_btn.pack(side=tk.LEFT, padx=20)
        
        # Panel de visualización
        self.visual_frame = ttk.Frame(self.main_frame)
        self.visual_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Gráfico de señal
        self.fig = Figure(figsize=(12, 4))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.visual_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configurar gráfico
        self.ax.set_title("Análisis de Señal RS-232")
        self.ax.set_ylabel("Voltaje (V)")
        self.ax.set_xlabel("Tiempo (ms)")
        self.ax.grid(True)
        self.ax.set_ylim(-13, 13)
        
        # Panel de información
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Análisis de Trama", padding="10")
        self.info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Texto para bits
        self.bits_frame = ttk.Frame(self.info_frame)
        self.bits_frame.pack(fill=tk.X, pady=5)
        ttk.Label(self.bits_frame, text="Bits: ").pack(side=tk.LEFT)
        self.bits_text = tk.Text(self.bits_frame, height=2, width=50)
        self.bits_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Explicación
        self.explicacion_text = tk.Text(self.info_frame, height=6, width=50)
        self.explicacion_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Variables de control
        self.analizando = False
        self.x_data = []
        self.y_data = []
        self.bits_actuales = []
        self.tiempo_bit = 1000 / int(self.velocidad_combo.get())  # ms
        
    def iniciar_analisis(self):
        """Inicia o detiene el análisis de datos RS-232."""
        if not self.analizando:
            try:
                # Configurar puerto serie
                self.puerto = self.puerto_combo.get()
                baudrate = int(self.velocidad_combo.get())
                self.ser = serial.Serial(
                    port=self.puerto,
                    baudrate=baudrate,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=0.1
                )
                
                self.analizando = True
                self.iniciar_btn.config(text="Detener Análisis")
                self.bits_actuales = []
                self.x_data = []
                self.y_data = []
                self.analizar_trama()
                
            except serial.SerialException as e:
                messagebox.showerror("Error", f"Error al abrir el puerto {self.puerto}: {str(e)}")
                self.analizando = False
                self.iniciar_btn.config(text="Iniciar Análisis")
                return
        else:
            self.analizando = False
            self.iniciar_btn.config(text="Iniciar Análisis")
            if hasattr(self, 'ser') and self.ser.is_open:
                self.ser.close()
                
    def analizar_trama(self):
        """Analiza los datos recibidos del puerto serial."""
        try:
            if self.ser and self.ser.is_open and self.analizando:
                # Leer datos del puerto serial
                datos = self.ser.readline().decode().strip()
                
                if datos and datos.startswith("<") and datos.endswith(">"):
                    try:
                        # Extraer trama y voltaje
                        partes = datos[1:-1].split("|")
                        trama = partes[0].split(":")[1]
                        valor = float(partes[1].split(":")[1])
                        
                        # Analizar partes de la trama
                        bit_inicio = trama[0]
                        bits_datos = trama[1:9]
                        bit_paridad = trama[9]
                        bit_parada = trama[10]
                        
                        # Verificar paridad
                        paridad_calculada = '1' if bits_datos.count('1') % 2 == 0 else '0'
                        paridad_correcta = paridad_calculada == bit_paridad
                        
                        # Actualizar información en la interfaz
                        self.bits_text.delete('1.0', tk.END)
                        self.bits_text.insert(tk.END, f"Trama: {trama} | Valor: {valor:.2f}V")
                        
                        # Explicar la trama
                        self.explicacion_text.delete('1.0', tk.END)
                        self.explicacion_text.insert(tk.END, f"=== Análisis de Trama RS-232 ===\n")
                        self.explicacion_text.insert(tk.END, f"1. Bit de inicio: {bit_inicio} ({'-12V' if bit_inicio == '0' else '+12V'})\n")
                        self.explicacion_text.insert(tk.END, f"2. Bits de datos: {bits_datos} (Valor: {int(bits_datos, 2)})\n")
                        self.explicacion_text.insert(tk.END, f"3. Bit de paridad: {bit_paridad} ({'Correcto' if paridad_correcta else 'Error'})\n")
                        self.explicacion_text.insert(tk.END, f"4. Bit de parada: {bit_parada} ({'+12V' if bit_parada == '1' else '-12V'})\n")
                        self.explicacion_text.insert(tk.END, f"\nVoltaje actual: {valor:.2f}V")
                        self.explicacion_text.insert(tk.END, f"\nVelocidad: {self.velocidad_combo.get()} bps")
                        self.explicacion_text.insert(tk.END, f"\nTiempo por bit: {self.tiempo_bit:.2f} ms")
                        
                        # Generar puntos para la señal
                        self.generar_puntos_señal(trama, valor)
                        
                        # Actualizar gráfico
                        self.actualizar_grafico()
                    except ValueError as e:
                        print(f"Error al procesar datos: {datos}")
                        
        except serial.SerialException as e:
            messagebox.showerror("Error", f"Error de comunicación serial: {str(e)}")
            self.analizando = False
            self.iniciar_btn.config(text="Iniciar Análisis")
            if hasattr(self, 'ser') and self.ser.is_open:
                self.ser.close()
            return
        
        # Programar siguiente actualización
        if self.analizando:
            self.after(int(self.tiempo_bit * 10), self.analizar_trama)
        
    def generar_puntos_señal(self, bits, voltaje_actual):
        """Genera puntos para la señal a partir de los bits.
        
        Args:
            bits (str): Cadena de bits a representar
            voltaje_actual (float): Voltaje actual de la señal
        """
        # Varios puntos por bit para mostrar transiciones
        for bit in bits:
            for i in range(10):
                tiempo = len(self.x_data) * (self.tiempo_bit / 10)
                self.x_data.append(tiempo)
                # Agregar ruido a la señal para hacerla más realista
                # Usar el voltaje actual para una representación más precisa
                if bit == '1':
                    base_voltage = voltaje_actual
                else:
                    base_voltage = -voltaje_actual
                ruido = random.uniform(-0.2, 0.2)  # Menos ruido para mejor visualización
                self.y_data.append(base_voltage + ruido)
        
        # Mantener solo los últimos 100 puntos
        if len(self.x_data) > 100:
            self.x_data = self.x_data[-100:]
            self.y_data = self.y_data[-100:]
    
    def actualizar_grafico(self):
        """Actualiza la visualización del gráfico."""
        self.ax.clear()
        self.ax.plot(self.x_data, self.y_data, 'b-', linewidth=2)
        self.ax.set_ylim(-13, 13)
        self.ax.grid(True)
        self.ax.set_title("Análisis de Señal RS-232")
        self.ax.set_ylabel("Voltaje (V)")
        self.ax.set_xlabel("Tiempo (ms)")
        
        # Agregar líneas de referencia
        self.ax.axhline(y=12, color='g', linestyle=':', alpha=0.5)
        self.ax.axhline(y=-12, color='r', linestyle=':', alpha=0.5)
        self.ax.axhline(y=0, color='gray', linestyle=':', alpha=0.3)
        
        self.canvas.draw()

if __name__ == "__main__":
    app = AnalizadorProtocolo()
    app.mainloop()
