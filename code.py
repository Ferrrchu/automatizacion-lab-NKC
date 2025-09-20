import board
import time
import adafruit_dht

# Ctrl + Shift + P para abrir la consola
# Definir el tipo de sensor y el pin GPIO al que está conectado
dht_device = adafruit_dht.DHT11(board.GP0)

# Bucle principal para leer los datos
while True:
    try:
        # Intenta leer la temperatura y la humedad
        temperatura = dht_device.temperature
        humedad = dht_device.humidity
        
        # Imprimir los valores en la consola
        print(f"Temperatura: {temperatura}°C")
        print(f"Humedad: {humedad}%")

    except RuntimeError as error:
        # Manejar errores si la lectura falla (común al principio)
        print(error.args[0])
        time.sleep(2.0)
        continue

    # Esperar 2 segundos antes de la siguiente lectura
    time.sleep(2.0)