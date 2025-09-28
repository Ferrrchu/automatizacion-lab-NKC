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

pinesXsegmentoCC = {"a":board.GP3, "b":board.GP2, "c":board.GP21,
              "d":board.GP20, "e":board.GP19, "f":board.GP4, "g":board.GP5}

pinesXsegmentoCA = {"a":board.GP7, "b":board.GP6, "c":board.GP18,
              "d":board.GP17, "e":board.GP16, "f":board.GP8, "g":board.GP9}

segmentos = {
    '0': (True,  True,  True,  True,  True,  True,  False),
    '1': (False, True,  True,  False, False, False, False),
    '2': (True,  True,  False, True,  True,  False, True),
    '3': (True,  True,  True,  True,  False, False, True,),
    '4': (False, True,  True,  False, False, True,  True),
    '5': (True,  False, True,  True,  False, True,  True),
    '6': (True,  False, True,  True,  True,  True,  True),
    '7': (True,  True,  True,  False, False, False, False),
    '8': (True,  True,  True,  True,  True,  True,  True),
    '9': (True,  True,  True,  True,  False, True,  True),
    
    'A': (True,  True,  True,  True, True,  False,  True),
    'B': (False, False, True,  True,  True,  True,  True),
    'C': (True,  False, False, True,  True,  True,  False),
    'D': (False, True,  True,  True,  True,  False, True),
    'E': (True,  True, False, True,  True,  True,  True),
    'F': (True,  False, False, False, True,  True,  True),
    'G': (True,  False, True,  True,  True,  True,  False),
    'H': (False, False,  True,  False, True,  True,  True),
    'I': (False, True,  True,  False, False, False, False),
    'J': (False, True,  True,  True,  True,  False, False),
    'L': (False, False, False, True,  True,  True,  False),
    'N': (True, True, True,  False, True,  True, False),
    'O': (True,  True,  True,  True,  True,  True,  False),
    'P': (True,  True,  False, False, True,  True,  True),
    'Q': (True,  True,  True,  False, False, True,  True),
    'R': (True, True, False, False, True,  True, False),
    'S': (True,  False, True,  True,  False, True,  True),
    'T': (False, False, False, True,  True,  True,  True),
    'U': (False, True,  True,  True,  True,  True,  False),
    'Y': (False, True,  True,  True,  False, True,  True),
    'Z': (True,  True,  False, True,  True,  False, True),

    ' ': (False, False, False, False, False, False, False),
}

# Variables para temporización no bloqueante
intervalo_lectura = 2.0  # segundos
ultimo_tiempo_lectura = time.monotonic()

# Variables para parpadeo no bloqueante
parpadeando = False
fin_parpadeo = 0
ultimo_cambio = 0
intervalo = 0.2

def inicializarPinesDisplay(pinesDisplay,anodo):
    pines=[]
    for segmento in ["a","b","c","d","e","f","g"]:
        dio = digitalio.DigitalInOut(pinesDisplay[segmento])
        dio.direction = digitalio.Direction.OUTPUT
        if anodo:
            dio.value = True
        else:   
            dio.value = False
        pines.append(dio)
    return pines

#Inicializamos los pines (son muchos y asi es mas rapido jaj)
pinesCC = inicializarPinesDisplay(pinesXsegmentoCC,False)
pinesCA = inicializarPinesDisplay(pinesXsegmentoCA,True)

def mostrarLetra(letra, anodo):
    patron = segmentos[letra]
    if anodo == True:                           
        for pin, encendido in zip(pinesCA, patron):
            pin.value = not encendido
    else:                              
        for pin, encendido in zip(pinesCC, patron):
            pin.value = encendido               
    return

def mensajeDisplay(mensaje):
    if len(mensaje) < 2:
        mensaje += ' '  # Asegura al menos dos caracteres
    for i in range(len(mensaje)):
        letra1 = mensaje[i]
        if i == len(mensaje)-1:
            letra2 = ' ' # Si el tamaño del mensaje es impar, el último carácter se muestra solo
        else:
            letra2 = mensaje[i+1]
        mostrarLetra(letra1, True)
        mostrarLetra(letra2, False)
        time.sleep(0.3)
    time.sleep(0.3)
    mostrarLetra(' ', True) #limpiamos los displays :P
    mostrarLetra(' ', False)

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
        mensajeDisplay("TENPERATURA  HUNEDAD") #N en vez de M porque en el display de 7 segmentos no hay M

    if parpadeando:
        if ahora - ultimo_cambio >= intervalo:
            ledNaranja.value = not ledNaranja.value
            ultimo_cambio = ahora
        if ahora >= fin_parpadeo:
            parpadeando = False
            ledNaranja.value = False