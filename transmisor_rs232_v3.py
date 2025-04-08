import serial
import time
import random
import tkinter as tk
from tkinter import ttk, messagebox
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
import numpy as np

class SensorIndustrial(tk.Tk):
    """Simulador de sensor industrial con transmisión RS-232.
    
    Esta clase implementa una interfaz gráfica para simular un sensor industrial
    que transmite datos a través del protocolo RS-232. Incluye visualización
    de la señal en tiempo real y estado de los pines DB-9.
    """
    
    # Constantes de configuración
    DEFAULT_WINDOW_SIZE = "800x600"
    DEFAULT_BAUD_RATES = ["1200", "2400", "4800", "9600", "19200"]
    DEFAULT_PORTS = ["COM6", "COM7", "COM8"]
    DEFAULT_SENSORS = ["Temperatura", "Presión", "Nivel", "Caudal"]
    VOLTAGE_RANGE = (-12, 12)  # Voltaje mínimo y máximo en V
    
    def __init__(self):
        """Inicializa la aplicación y configura la interfaz gráfica."""
        super().__init__()

        self.title("Sensor Industrial - Transmisor RS-232")
        self.geometry(self.DEFAULT_WINDOW_SIZE)
        
        # Configurar tema oscuro
        sns.set_theme(style="darkgrid")
        self.palette = sns.color_palette("husl", 8)
        self.bg_color = '#{:02x}{:02x}{:02x}'.format(
            int(sns.color_palette("dark")[0][0] * 255),
            int(sns.color_palette("dark")[0][1] * 255),
            int(sns.color_palette("dark")[0][2] * 255)
        )
        self.configure(bg=self.bg_color)

        # Configuración del estilo
        style = ttk.Style()
        style.configure('Industrial.TFrame', background=self.bg_color)
        style.configure('Industrial.TLabel', background=self.bg_color, foreground='white')
        style.configure('Industrial.TButton', font=('Arial', 10, 'bold'))

        # Marco principal
        self.main_frame = ttk.Frame(self, style='Industrial.TFrame', padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame superior para título y controles
        top_frame = ttk.Frame(self.main_frame, style='Industrial.TFrame')
        top_frame.pack(fill=tk.X, pady=10)

        # Botón de iniciar/detener en la izquierda
        self.btn_transmitir = ttk.Button(top_frame, text="Iniciar Transmisión", 
                                      command=self.iniciar_transmision)
        self.btn_transmitir.pack(side=tk.LEFT, padx=10)

        # Selector de tipo de sensor
        ttk.Label(top_frame, text="Tipo:", 
                 style='Industrial.TLabel').pack(side=tk.LEFT, padx=5)
        self.sensor_type = ttk.Combobox(top_frame, 
                                       values=["Temperatura", "Presión", "Nivel", "Caudal"],
                                       width=10)
        self.sensor_type.set("Temperatura")
        self.sensor_type.pack(side=tk.LEFT, padx=5)

        # Control de puerto COM
        ttk.Label(top_frame, text="Puerto:", 
                 style='Industrial.TLabel').pack(side=tk.LEFT, padx=5)
        self.port_select = ttk.Combobox(top_frame, 
                                     values=self.DEFAULT_PORTS,
                                     width=10)
        self.port_select.set("COM6")  # Puerto por defecto
        self.port_select.pack(side=tk.LEFT, padx=5)

        # Control de velocidad
        ttk.Label(top_frame, text="Baudios:", 
                 style='Industrial.TLabel').pack(side=tk.LEFT, padx=5)
        self.baud_rate = ttk.Combobox(top_frame, 
                                     values=["1200", "2400", "4800", "9600", "19200"],
                                     width=8)
        self.baud_rate.set("9600")
        self.baud_rate.pack(side=tk.LEFT, padx=5)

        # Título centrado
        title_label = ttk.Label(top_frame, 
                               text="Simulación de Sensor Industrial - RS-232",
                               font=('Arial', 14, 'bold'),
                               style='Industrial.TLabel')
        title_label.pack(side=tk.LEFT, expand=True, padx=10)

        # Panel de visualización
        self.visual_frame = ttk.LabelFrame(self.main_frame, text="Visualización de Datos", 
                                         padding="10", style='Industrial.TLabel')
        self.visual_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Panel de pines RS-232
        self.pin_frame = ttk.LabelFrame(self.visual_frame, text="Estado de Pines DB-9",
                                      padding="15", style='Industrial.TLabel')
        self.pin_frame.pack(fill=tk.X, padx=10, pady=10)

        # Canvas para los pines
        self.pin_canvas = tk.Canvas(self.pin_frame, bg='#2b2b2b', height=120,
                                  highlightthickness=0)
        self.pin_canvas.pack(fill=tk.X, padx=5, pady=5)

        # Panel de señal
        self.signal_frame = ttk.LabelFrame(self.visual_frame, text="Señal de Transmisión RS-232",
                                         padding="15", style='Industrial.TLabel')
        self.signal_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Crear un frame para matplotlib
        plot_frame = ttk.Frame(self.signal_frame)
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configurar figura de matplotlib
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(8, 4))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Configurar gráfico
        self.ax.set_facecolor('#1C1C1C')
        self.fig.patch.set_facecolor('#1C1C1C')
        self.line, = self.ax.plot([0], [0], '-', color='#00ff88', linewidth=2)
        self.scatter = self.ax.scatter([0], [0], color='#00ff88', s=50)
        
        # Configurar ejes
        self.ax.grid(True, color='#404040', linestyle='--', alpha=0.5)
        self.ax.set_ylim(-12, 12)  # Rango de voltaje extendido
        self.ax.set_xlim(0, 50)
        self.ax.set_ylabel('Voltaje (V)', color='white')
        self.ax.set_xlabel('Tiempo (ms)', color='white')
        self.ax.tick_params(colors='white')

        # Etiqueta de estado
        self.status_label = ttk.Label(self.main_frame, text="Estado: Detenido",
                                    style='Industrial.TLabel')
        self.status_label.pack(pady=5)

        # Dibujar pines RS-232
        self.dibujar_pines_rs232()

        # Inicializar datos para el gráfico
        self.x_data = [0]
        self.y_data = [0]
        self.ser = None
        self.transmitiendo = False

    def generar_dato_sensor(self):
        """Genera un valor de sensor simulado entre -12V y +12V"""
        return random.uniform(-12, 12)

    def dibujar_pines_rs232(self):
        """Dibuja la representación de los pines DB-9"""
        pin_coords = {
            'DCD': (50, 30),   # Pin 1
            'RX': (100, 30),   # Pin 2
            'TX': (150, 30),   # Pin 3
            'DTR': (200, 30),  # Pin 4
            'GND': (250, 30),  # Pin 5
            'DSR': (300, 30),  # Pin 6
            'RTS': (350, 30),  # Pin 7
            'CTS': (400, 30),  # Pin 8
            'RI': (450, 30)    # Pin 9
        }

        # Dibujar cada pin
        for nombre, (x, y) in pin_coords.items():
            # Círculo del pin
            self.pin_canvas.create_oval(x-10, y-10, x+10, y+10, 
                                      fill='#333333', outline='#666666', tags=nombre)
            # Texto del pin
            self.pin_canvas.create_text(x, y+25, text=nombre, fill='white')

            # Configurar eventos del mouse
            self.pin_canvas.tag_bind(nombre, '<Enter>', 
                                   lambda e, n=nombre: self.mostrar_descripcion_pin(n, e.x))
            self.pin_canvas.tag_bind(nombre, '<Leave>', 
                                   lambda e: self.ocultar_descripcion_pin())

    def mostrar_descripcion_pin(self, nombre, x):
        """Muestra la descripción del pin al pasar el mouse"""
        descripciones = {
            'DCD': 'Data Carrier Detect - Detecta portadora de datos',
            'RX': 'Receive Data - Recepción de datos',
            'TX': 'Transmit Data - Transmisión de datos',
            'DTR': 'Data Terminal Ready - Terminal de datos lista',
            'GND': 'Ground - Tierra (referencia)',
            'DSR': 'Data Set Ready - Equipo de datos listo',
            'RTS': 'Request to Send - Solicitud de envío',
            'CTS': 'Clear to Send - Listo para enviar',
            'RI': 'Ring Indicator - Indicador de llamada'
        }
        self.pin_canvas.delete('descripcion')
        self.pin_canvas.create_text(x, 80, text=descripciones[nombre],
                                  fill='white', tags='descripcion')

    def ocultar_descripcion_pin(self):
        """Oculta la descripción del pin"""
        self.pin_canvas.delete('descripcion')

    def activar_pin(self, nombre, activo=True):
        """Activa o desactiva visualmente un pin"""
        color = '#00ff88' if activo else '#333333'
        self.pin_canvas.itemconfig(nombre, fill=color)

    def dibujar_grid(self):
        """Dibuja la cuadrícula del gráfico"""
        self.ax.grid(True, color='#404040', linestyle='--', alpha=0.5)
        self.ax.set_facecolor('#1C1C1C')
        self.fig.patch.set_facecolor('#1C1C1C')
        self.canvas.draw()

    def mostrar_datos_binarios(self, datos_binarios):
        """Muestra los datos binarios en la interfaz"""
        # Crear una ventana emergente para mostrar los datos binarios
        if hasattr(self, 'ventana_datos') and self.ventana_datos.winfo_exists():
            self.ventana_datos.destroy()
            
        self.ventana_datos = tk.Toplevel(self)
        self.ventana_datos.title("Datos Binarios")
        self.ventana_datos.geometry("400x200")
        
        # Frame para los datos
        frame = ttk.Frame(self.ventana_datos, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Mostrar los bits
        ttk.Label(frame, text="Trama RS-232:", 
                 font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Crear un widget Text para mostrar los bits con formato
        text = tk.Text(frame, height=4, width=40, font=('Courier', 12))
        text.pack(pady=5)
        text.insert('1.0', datos_binarios)
        text.configure(state='disabled')

    def dibujar_señal(self, valor):
        """Actualiza la visualización de la señal"""
        # Agregar nuevo punto
        self.x_data.append(self.x_data[-1] + 1)
        self.y_data.append(valor)
        
        # Mantener solo los últimos 50 puntos
        if len(self.x_data) > 50:
            self.x_data = self.x_data[-50:]
            self.y_data = self.y_data[-50:]
        
        # Actualizar datos de la línea y puntos
        self.line.set_data(self.x_data, self.y_data)
        self.scatter.set_offsets(list(zip(self.x_data, self.y_data)))
        
        # Ajustar límites
        self.ax.set_xlim(max(0, self.x_data[-1] - 49), self.x_data[-1] + 1)
        
        # Redibujar
        self.canvas.draw()

    def iniciar_transmision(self):
        """Inicia o detiene la transmisión de datos"""
        if not hasattr(self, 'transmitiendo') or not self.transmitiendo:
            try:
                puerto = self.port_select.get()
                baudrate = int(self.baud_rate.get())
                
                self.ser = serial.Serial(
                    port=puerto,
                    baudrate=baudrate,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=1
                )
                
                if not self.ser.is_open:
                    self.ser.open()
                    
                self.transmitiendo = True
                self.btn_transmitir.config(text="Detener Transmisión")
                self.status_label.config(text=f"Estado: Conectado a {puerto} a {baudrate} baudios")
                self.transmitir()
                
            except serial.SerialException as e:
                self.status_label.config(text=f"Error de conexión: {str(e)}")
            except ValueError as e:
                self.status_label.config(text=f"Error de configuración: {str(e)}")
        else:
            self.detener_transmision()

    def transmitir(self):
        """Transmite datos por el puerto serial"""
        if self.transmitiendo:
            valor = self.generar_dato_sensor()
            tipo = self.sensor_type.get()
            mensaje = f"{tipo}: {valor:.2f}"
            
            try:
                baudrate = int(self.baud_rate.get())
                puerto = self.port_select.get()
                if not self.ser or not self.ser.is_open:
                    self.ser = serial.Serial(puerto, baudrate, timeout=1)
                elif self.ser.baudrate != baudrate:
                    self.ser.baudrate = baudrate
                
                # Activar pines relevantes
                self.activar_pin('TX', True)     # TX activo durante transmisión
                self.activar_pin('RTS', True)    # RTS activo para solicitar envío
                self.activar_pin('DTR', True)    # DTR siempre activo
                
                # Crear trama RS-232
                # Convertir el valor a un byte (0-255)
                byte_valor = int((valor + 12) * 10)  # Convertir rango -12V a +12V en 0-255
                byte_valor = max(0, min(255, byte_valor))  # Asegurar rango válido
                
                # Formar trama RS-232:
                # - 1 bit de inicio (0)
                # - 8 bits de datos
                # - 1 bit de paridad (par)
                # - 1 bit de parada (1)
                bits_datos = format(byte_valor, '08b')
                paridad = '1' if bits_datos.count('1') % 2 == 0 else '0'  # Paridad par
                trama = f"0{bits_datos}{paridad}1"  # Inicio(0) + Datos + Paridad + Parada(1)
                
                # Mostrar datos binarios con explicación de la trama
                self.mostrar_datos_binarios(trama)
                
                # Enviar datos con formato especial para el analizador incluyendo la trama
                mensaje_formateado = f"<TRAMA:{trama}|VOLT:{valor}>\n"
                self.ser.write(mensaje_formateado.encode())
                
                # Visualizar la señal
                self.dibujar_señal(valor)
                
                # Desactivar pines después de un tiempo
                self.after(50, lambda: self.activar_pin('TX', False))
                self.after(100, lambda: self.activar_pin('RTS', False))
                
                # Actualizar estado con información detallada
                self.status_label.config(
                    text=f"Estado: Transmitiendo a {baudrate} baudios | Bits enviados: {len(trama)}")
                
            except serial.SerialException as e:
                print(f"Error de puerto serial: {e}")
                if self.ser and self.ser.is_open:
                    self.ser.close()
                self.ser = None
                self.status_label.config(text=f"Error: {str(e)}")
                
            # Calcular delay basado en baudrate
            delay = max(1000, int(1000 * (10 / int(self.baud_rate.get()))))  # mínimo 1 segundo
            self.after(delay, self.transmitir)

    def detener_transmision(self):
        """Detiene la transmisión de datos"""
        self.transmitiendo = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.btn_transmitir.config(text="Iniciar Transmisión")
        self.status_label.config(text="Estado: Detenido")

    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        self.detener_transmision()
        self.destroy()

if __name__ == "__main__":
    app = SensorIndustrial()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
