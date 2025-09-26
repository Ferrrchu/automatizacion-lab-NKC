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

def alarmaTemperatura(temperatura):
    ledAzul.value = False
    ledVerde.value = False
    ledBlanco.value = False
    ledAmarillo.value = False
    ledRojo.value = False

    if temperatura <= 25:
        ledAzul.value = True
        print("ALERTA: Temperatura mínima")
    elif 25 < temperatura < 26:
        ledVerde.value = True
        print("ALERTA: Temperatura intermedia-baja")
    elif 26 <= temperatura <= 27:
        ledBlanco.value = True
        print("ALERTA: Temperatura estándar")
    elif 27 < temperatura < 28:
        ledAmarillo.value = True
        print("ALERTA: Temperatura intermedia-alta")
    elif temperatura >= 28:
        ledRojo.value = True
        print("ALERTA: Temperatura máxima")
    else:
        print("Valores fuera de rango definidos.")

def alarmaHumedad(humedad):
    ledAzul.value = False
    ledVerde.value = False
    ledBlanco.value = False
    ledAmarillo.value = False
    ledRojo.value = False
    
    if humedad <= 40:
        ledAzul.value = True
        print("ALERTA: humedad mínima")
    elif 40 < humedad <= 45:
        ledVerde.value = True
        print("ALERTA: humedad intermedia-baja")
    elif 45 < humedad <= 50:
        ledBlanco.value = True
        print("ALERTA: humedad estándar")
    elif 50 < humedad <= 55:
        ledAmarillo.value = True
        print("ALERTA: humedad intermedia-alta")
    elif humedad > 55:
        ledRojo.value = True
        print("ALERTA: humedad máxima")
    else:
        print("Valores fuera de rango definidos.")

# Variables para temporización no bloqueante
intervalo_lectura = 2.0  # segundos
ultimo_tiempo_lectura = time.monotonic()

# Variables para parpadeo no bloqueante
parpadeando = False
fin_parpadeo = 0
ultimo_cambio = 0
intervalo = 0.2

# Bucle principal para leer los datos
while True:
    ahora = time.monotonic()

    # Leer sensor DHT11 cada intervalo_lectura segundos
    if ahora - ultimo_tiempo_lectura >= intervalo_lectura:
        try:
            temperatura = sensorTemperatura.temperature
            humedad = sensorTemperatura.humidity
            print(f"Temperatura: {temperatura}°C")
            print(f"Humedad: {humedad}%")
        except RuntimeError as error:
            print(error.args[0])
        ultimo_tiempo_lectura = ahora

    valor = sensorInfrarojo.value
    detectado = (valor == False)
    if detectado and not parpadeando:
        parpadeando = True
        fin_parpadeo = ahora + 5
        ultimo_cambio = ahora
        ledNaranja.value = True
        print("Intruso DETECTADO")

    if parpadeando:
        if ahora - ultimo_cambio >= intervalo:
            ledNaranja.value = not ledNaranja.value
            ultimo_cambio = ahora
        if ahora >= fin_parpadeo:
            parpadeando = False
            ledNaranja.value = False