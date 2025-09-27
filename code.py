import board # Carga el módulo de los nombres de los pines (GP0, GP1, etc.)
import time # Carga el módulo de las pausas (sleep)
import adafruit_dht # Carga el driver del sensor DHT (DHT11/DHT22)
import digitalio # Para manejo de entradas y salidas digitales

sensorTemperatura = adafruit_dht.DHT11(board.GP26)

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

# Variables para controlar cuándo mostrar mensajes de alarma
rango_temperatura_anterior = None
rango_humedad_anterior = None

# Variable de estado del mecanismo de seguridad
seguridad_activada = True

# Variable para alternar entre modo temperatura y modo humedad
modoLectura = True 

# Variables para temporización no bloqueante
intervalo_lectura = 2.0  # segundos
ultimo_tiempo_lectura = time.monotonic()

# Variables para parpadeo no bloqueante
parpadeando = False
fin_parpadeo = 0
ultimo_cambio = 0
intervalo = 0.2

def alarmaTemperatura(temperatura):
    global rango_temperatura_anterior
    
    ledAzul.value = False
    ledVerde.value = False
    ledBlanco.value = False
    ledAmarillo.value = False
    ledRojo.value = False

    if temperatura <= 25:
        rango_actual = "minima"
        ledAzul.value = True
        ledVerde.value = True
        ledBlanco.value = True
        mensaje = "ALERTA: Temperatura mínima"
    elif 25 < temperatura < 26:
        rango_actual = "intermedia-baja"
        ledVerde.value = True
        ledBlanco.value = True
        mensaje = "ALERTA: Temperatura intermedia-baja"
    elif 26 <= temperatura <= 27:
        rango_actual = "normal"
        ledBlanco.value = True
        mensaje = "Temperatura normal"
    elif 27 < temperatura < 28:
        rango_actual = "intermedia-alta"
        ledBlanco.value = True
        ledAmarillo.value = True
        mensaje = "ALERTA: Temperatura intermedia-alta"
    elif temperatura >= 28:
        rango_actual = "maxima"
        ledBlanco.value = True
        ledAmarillo.value = True
        ledRojo.value = True
        mensaje = "ALERTA: Temperatura máxima"
    else:
        rango_actual = "fuera-rango"
        mensaje = "Valores fuera de rango definidos."

    if rango_actual != rango_temperatura_anterior:
        print(mensaje)
        rango_temperatura_anterior = rango_actual

def alarmaHumedad(humedad):
    global rango_humedad_anterior
    
    ledAzul.value = False
    ledVerde.value = False
    ledBlanco.value = False
    ledAmarillo.value = False
    ledRojo.value = False
    
    if humedad <= 40:
        rango_actual = "minima"
        ledAzul.value = True
        ledVerde.value = True
        ledBlanco.value = True
        mensaje = "ALERTA: humedad mínima"
    elif 40 < humedad <= 45:
        rango_actual = "intermedia-baja"
        ledVerde.value = True
        ledBlanco.value = True
        mensaje = "ALERTA: humedad intermedia-baja"
    elif 45 < humedad <= 55:
        rango_actual = "normal"
        ledBlanco.value = True
        mensaje = "Humedad estándar"
    elif 55 < humedad <= 60:
        rango_actual = "intermedia-alta"
        ledBlanco.value = True
        ledAmarillo.value = True
        mensaje = "ALERTA: humedad intermedia-alta"
    elif humedad > 60:
        rango_actual = "maxima"
        ledBlanco.value = True
        ledAmarillo.value = True
        ledRojo.value = True
        mensaje = "ALERTA: humedad máxima"
    else:
        rango_actual = "fuera-rango"
        mensaje = "Valores fuera de rango definidos."

    if rango_actual != rango_humedad_anterior:
        print(mensaje)
        rango_humedad_anterior = rango_actual

# Función para leer comandos del monitor serie
def leer_comando():
    import supervisor
    if supervisor.runtime.serial_bytes_available:
        linea = input().strip().lower()
        return linea
    return None

# Bucle principal para leer los datos
while True:
    ahora = time.monotonic()

    # Leer comandos del usuario
    comando = leer_comando()
    if comando == "activar":
        seguridad_activada = True
        print("Mecanismo de seguridad ACTIVADO")
    elif comando == "desactivar":
        seguridad_activada = False
        print("Mecanismo de seguridad DESACTIVADO")
    elif comando == "temperatura":
        modoLectura = True
        print("modo lectura TEMPERATURA activado")
    elif comando == "humedad":
        modoLectura = False
        print("modo lectura HUMEDAD activado")
    else: 
        print("Comando no reconocido. Comandos válidos: activar, desactivar, temperatura, humedad")

    # Leer sensor DHT11 cada intervalo_lectura segundos
    if ahora - ultimo_tiempo_lectura >= intervalo_lectura:
        try:
            temperatura = sensorTemperatura.temperature
            humedad = sensorTemperatura.humidity
            print(f"Temperatura: {temperatura}°C")
            print(f"Humedad: {humedad}%")

            if modoLectura:
                alarmaTemperatura(temperatura)
            else:
                alarmaHumedad(humedad)

        except RuntimeError as error:
            print(error.args[0])
        ultimo_tiempo_lectura = ahora

    valor = sensorInfrarojo.value
    detectado = (valor == False)
    if detectado and seguridad_activada and not parpadeando:
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