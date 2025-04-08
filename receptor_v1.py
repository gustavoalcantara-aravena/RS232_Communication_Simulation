import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time


try:
    # Configurar el puerto serial virtual
    ser = serial.Serial('/tmp/ttyS2', 9600, timeout=1)
    print("Receptor conectado al puerto virtual /tmp/ttyS2")


    # Configurar la gráfica
    plt.ion()  # Modo interactivo
    fig, ax = plt.subplots()
    datos = []
    linea, = ax.plot([], [], 'bo-')
    ax.set_title("Datos recibidos por RS-232")
    ax.set_xlabel("Tiempo")
    ax.set_ylabel("Mensajes")


    # Recibir y graficar datos en tiempo real
    while True:
        if ser.in_waiting > 0:
            mensaje = ser.readline().decode().strip()
            print(f"Recibido: {mensaje}")
            datos.append(mensaje)
            
            # Actualizar gráfica
            linea.set_data(range(len(datos)), [i for i in range(len(datos))])
            ax.relim()
            ax.autoscale_view()
            plt.draw()
            plt.pause(0.1)


except serial.SerialException as e:
    print(f"Error al abrir el puerto serial: {e}")
except KeyboardInterrupt:
    print("\nRecepción terminada por el usuario")
except Exception as e:
    print(f"Error: {e}")
finally:
    # Cerrar el puerto serial si está abierto
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Puerto serial cerrado")
    plt.ioff()
    plt.close('all')
