# Simulador RS-232

Este proyecto incluye un simulador de transmisión RS-232 y un analizador de protocolo.

## Requisitos

### Python y Dependencias

```bash
# Instalar Python 3.8 o superior
python3 --version

# Instalar dependencias
pip install pyserial
pip install matplotlib
pip install seaborn
pip install numpy
```

### Configuración del Puerto Serial

#### En Ubuntu/Linux:

1. Crear puertos seriales virtuales:
```bash
sudo modprobe tty_pts
sudo socat -d -d pty,raw,echo=0,link=/dev/ttyS0 pty,raw,echo=0,link=/dev/ttyS1
```

2. Dar permisos:
```bash
sudo chmod 666 /dev/ttyS0
sudo chmod 666 /dev/ttyS1
```

#### En Windows:

1. Instalar [com0com](http://com0com.sourceforge.net/)
2. Usar el Com0Com Setup para crear un par de puertos virtuales (ejemplo: COM1-COM2)
3. En el código, cambiar los puertos:
   - Cambiar `/dev/ttyS0` por `COM1`
   - Cambiar `/dev/ttyS1` por `COM2`

## Ejecución

1. Primero, iniciar el analizador:
```bash
python3 analizador_protocolo_v2.py
```

2. Luego, en otra terminal, iniciar el transmisor:
```bash
python3 transmisor_rs232_v2.py
```

## Uso

1. En el transmisor:
   - Seleccionar el puerto (ttyS0/COM1)
   - Seleccionar la velocidad (por defecto 9600)
   - Hacer clic en "Iniciar Transmisión"

2. En el analizador:
   - Seleccionar el puerto correspondiente (ttyS1/COM2)
   - Seleccionar la misma velocidad que el transmisor
   - Hacer clic en "Iniciar Análisis"

## Solución de Problemas

### Error de Permisos en Linux
Si aparece error de permisos:
```bash
sudo usermod -a -G dialout $USER
sudo chmod a+rw /dev/ttyS0
sudo chmod a+rw /dev/ttyS1
```
Luego cerrar sesión y volver a iniciar.

### Error de Puerto en Windows
Si los puertos COM no aparecen:
1. Abrir el Administrador de Dispositivos
2. Verificar que los puertos COM estén instalados
3. Anotar los números de puerto exactos
4. Modificar el código con los números correctos

### Error de Matplotlib
Si hay error con el backend de matplotlib:
```python
import matplotlib
matplotlib.use('TkAgg')
```
Agregar estas líneas al inicio del código.

## Características

- Transmisión RS-232 completa:
  - 1 bit de inicio (0)
  - 8 bits de datos
  - 1 bit de paridad (par)
  - 1 bit de parada (1)
- Visualización en tiempo real
- Análisis de tramas
- Interfaz gráfica moderna
- Soporte para diferentes velocidades
- Visualización de voltajes (±12V)

## Notas Técnicas

- El sistema usa puertos seriales virtuales para simular la comunicación RS-232
- Los voltajes se simulan entre -12V y +12V según el estándar RS-232
- La paridad se calcula como paridad par
- La velocidad máxima recomendada es 115200 bps
