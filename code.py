import board # Carga el módulo de los nombres de los pines (GP0, GP1, etc.)
import time # Carga el módulo de las pausas (sleep)
import adafruit_dht # Carga el driver del sensor DHT (DHT11/DHT22)
import digitalio

sensorTemperatura = adafruit_dht.DHT11(board.GP26) #Crea el objeto del sensor DHT11 indicando que su pin de datos está en GP0.

sensorInfrarojo = digitalio.DigitalInOut(board.GP22)
sensorInfrarojo.direction = digitalio.Direction.INPUT

ledAzul = digitalio.DigitalInOut(board.GP14)   
ledAzul.direction = digitalio.Direction.OUTPUT

ledVerde = digitalio.DigitalInOut(board.GP13)   
ledVerde.direction = digitalio.Direction.OUTPUT 

ledBlanco = digitalio.DigitalInOut(board.GP12)   
ledBlanco.direction = digitalio.Direction.OUTPUT 

ledAmarillo = digitalio.DigitalInOut(board.GP11)   
ledAmarillo.direction = digitalio.Direction.OUTPUT 

ledRojo = digitalio.DigitalInOut(board.GP10)   
ledRojo.direction = digitalio.Direction.OUTPUT 

ledNaranja = digitalio.DigitalInOut(board.GP15)   
ledNaranja.direction = digitalio.Direction.OUTPUT 

# Bucle principal para leer los datos
while True:
    try:
        # Intenta leer la temperatura y la humedad
        temperatura = sensorTemperatura.temperature #Lee la temperatura en °C
        humedad = sensorTemperatura.humidity #Lee la humedad relativa en %
        
        # Imprimir los valores en la consola
        print(f"Temperatura: {temperatura}°C")
        print(f"Humedad: {humedad}%")

    except RuntimeError as error:
        # Manejar errores si la lectura falla (común al principio)
        print(error.args[0])
        time.sleep(2.0)
        continue

    valor = sensorInfrarojo.value
    detectado = (valor == False)   # ajusta si tu módulo es al revés
    if detectado:
        print("Obstáculo DETECTADO")
        ledNaranja.value = (sensorInfrarojo.value == False)
        time.sleep(2.0)
        ledNaranja.value = False
        continue

    # Esperar 2 segundos antes de la siguiente lectura, los DHT11 no deben leerse más de ~1 vez por segundo; 2 s es una práctica segura para lecturas estables.
    time.sleep(2.0)