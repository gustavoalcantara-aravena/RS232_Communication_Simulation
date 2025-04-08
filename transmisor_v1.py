import serial
import time


try:
    # Configurar el puerto serial virtual
    ser = serial.Serial('/tmp/ttyS1', 9600, timeout=1)
    print("Transmisor conectado al puerto virtual /tmp/ttyS1")


    # Enviar datos a través del puerto serial
    for i in range(10):
        mensaje = f"Mensaje {i}"
        ser.write(f"{mensaje}\n".encode())
        print(f"Enviado: {mensaje}")
        time.sleep(1)  # Esperar 1 segundo entre envíos


except serial.SerialException as e:
    print(f"Error al abrir el puerto serial: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    # Cerrar el puerto serial si está abierto
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Puerto serial cerrado")
