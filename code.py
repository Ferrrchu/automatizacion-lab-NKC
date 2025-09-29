import board # Carga el módulo de los nombres de los pines (GP0, GP1, etc.)
import time # Carga el módulo de las pausas (sleep)
import adafruit_dht # Carga el driver del sensor DHT (DHT11/DHT22)
import digitalio # Para manejo de entradas y salidas digitales
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import json


# Configuración de RED
SSID = "wfrre-Docentes"
PASSWORD = "20$tscFrre.24"
BROKER = "10.13.100.154"  
NOMBRE_EQUIPO = "NKC"
DESCOVERY_TOPIC = "descubrir"
TOPIC = f"sensores/{NOMBRE_EQUIPO}"

print(f"Intentando conectar a {SSID}...")
try:
    wifi.radio.connect(SSID, PASSWORD)
    print(f"Conectado a {SSID}")
    print(f"Dirección IP: {wifi.radio.ipv4_address}")
except Exception as e:
    print(f"Error al conectar a WiFi: {e}")
    while True:
        pass 

# Configuración MQTT 
pool = socketpool.SocketPool(wifi.radio)

def connect(client, userdata, flags, rc):
    print("Conectado al broker MQTT")
    client.publish(DESCOVERY_TOPIC, json.dumps({"equipo":NOMBRE_EQUIPO,"magnitudes": ["temperatura", "humedad"]}))

mqtt_client = MQTT.MQTT(
    broker=BROKER,
    port=1883,
    socket_pool=pool
)

mqtt_client.on_connect = connect
mqtt_client.connect()

# Usamos estas varaibles globales para controlar cada cuanto publicamos
LAST_PUB = 0
PUB_INTERVAL = 5  

def publish():
    global last_pub
    now = time.monotonic()
   
    if now - last_pub >= PUB_INTERVAL:
        try:
            temp_topic = f"{TOPIC}/temperatura" 
            mqtt_client.publish(temp_topic, str(temperatura))
            
            hum_topic = f"{TOPIC}/humedad" 
            mqtt_client.publish(hum_topic, str(humedad))
            
            last_pub = now
          
        except Exception as e:
            print(f"Error publicando MQTT: {e}")


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

#Variable para activar y desactivar la impresion constante por consola de la temperatura y humedad
mostrarPorConsola = True

# Variables para controlar cuándo mostrar mensajes de alarma
rangoTemperaturaAnterior = None
rangoHumedadAnterior = None

# Variable de estado del mecanismo de seguridad
seguridadActivada = True

# Variable para alternar entre modo temperatura y modo humedad
modoLectura = True 

# Variables para temporización no bloqueante
intervaloLectura = 2.0  # segundos
ultimoTiempoLectura = time.monotonic()

# Variables para parpadeo no bloqueante
parpadeando = False
ultimoCambio = 0
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

def mostrarCaracter(caracter, anodo):
    patron = segmentos[caracter]
    if anodo == True:                           
        for pin, encendido in zip(pinesCA, patron):
            pin.value = not encendido
    else:                              
        for pin, encendido in zip(pinesCC, patron):
            pin.value = encendido               
    return

def mensajeDisplay(mensaje):
    time.sleep(0.3)
    if len(mensaje) < 2:
        mensaje += ' '  # Asegura al menos dos caracteres
    for i in range(len(mensaje)):
        letra1 = mensaje[i]
        if i == len(mensaje)-1:
            letra2 = ' ' # Si el tamaño del mensaje es impar, el último carácter se muestra solo
        else:
            letra2 = mensaje[i+1]
        mostrarCaracter(letra1, True)
        mostrarCaracter(letra2, False)
        time.sleep(0.3)
    mostrarCaracter(' ', True) #limpiamos los displays :P
    mostrarCaracter(' ', False)

def mostrarTemperaturaHumedad(valor):
    valorTruncado = str(int(valor))
    if len(valorTruncado) < 2:
        valorTruncado += ' ' 
    valor1 = valorTruncado[0]
    valor2 = valorTruncado[1]
    mostrarCaracter(valor1, True)
    mostrarCaracter(valor2, False)

def alarmaTemperatura(temperatura):
    global rangoTemperaturaAnterior
    
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
        mensaje = "ALERTA: Temperatura extremadamente baja"
    elif 25 < temperatura < 26:
        rango_actual = "intermedia-baja"
        ledVerde.value = True
        ledBlanco.value = True
        mensaje = "ALERTA: Temperatura baja"
    elif 26 <= temperatura <= 27:
        rango_actual = "normal"
        ledBlanco.value = True
        mensaje = "Temperatura normal"
    elif 27 < temperatura < 28:
        rango_actual = "intermedia-alta"
        ledBlanco.value = True
        ledAmarillo.value = True
        mensaje = "ALERTA: Temperatura alta"
    elif temperatura >= 28:
        rango_actual = "maxima"
        ledBlanco.value = True
        ledAmarillo.value = True
        ledRojo.value = True
        mensaje = "ALERTA: Temperatura extremadamente alta"
    else:
        rango_actual = "fuera-rango"
        mensaje = "Valores fuera de rango definidos."

    if rango_actual != rangoTemperaturaAnterior:
        print(mensaje)
        rangoTemperaturaAnterior = rango_actual

def alarmaHumedad(humedad):
    global rangoHumedadAnterior
    
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
        mensaje = "ALERTA: Humedad extremadamente baja"
    elif 40 < humedad <= 45:
        rango_actual = "intermedia-baja"
        ledVerde.value = True
        ledBlanco.value = True
        mensaje = "ALERTA: Humedad baja"
    elif 45 < humedad <= 55:
        rango_actual = "normal"
        ledBlanco.value = True
        mensaje = "Humedad normal"
    elif 55 < humedad <= 60:
        rango_actual = "intermedia-alta"
        ledBlanco.value = True
        ledAmarillo.value = True
        mensaje = "ALERTA: Humedad alta"
    elif humedad > 60:
        rango_actual = "maxima"
        ledBlanco.value = True
        ledAmarillo.value = True
        ledRojo.value = True
        mensaje = "ALERTA: Humedad extremadamente alta"
    else:
        rango_actual = "fuera-rango"
        mensaje = "Valores fuera de rango definidos."

    if rango_actual != rangoHumedadAnterior:
        print(mensaje)
        rangoHumedadAnterior = rango_actual

# Función para leer comandos del monitor serie
def leer_comando():
    import supervisor
    if supervisor.runtime.serial_bytes_available:
        linea = input().strip().lower()
        return linea
    return None

def menuDeComandos():
    print("\n\n ------------------------------------------------------------------ \n\
    Menu de comandos: \n \
    - menu: Muestra el menu de comandos.\n \
    - activar-seguridad: Activa el mecanismo de seguridad. \n \
    - desactivar-seguridad: Desactiva el mecanismo de seguridad \n \
    - apagar-alarma: Apaga la alarma de seguridad. \n \
    - temperatura: Mostrar temperatura por display. \n \
    - humedad: Mostrar humedad por display. \n \
    - activar-consola: Activa la impresión por consola de temperatura y humedad. \n \
    - desactivar-consola: Desactiva la impresión por consola de temperatura y humedad. \n \
------------------------------------------------------------------\n\n")
    time.sleep(3)

menuDeComandos()

# Bucle principal para leer los datos
while True:
    ahora = time.monotonic()

    # Leer comandos del usuario
    comando = leer_comando()
    if comando == "activar-seguridad":
        seguridadActivada = True
        print("Mecanismo de seguridad ACTIVADO")
    elif comando == "desactivar-seguridad":
        seguridadActivada = False
        print("Mecanismo de seguridad DESACTIVADO")
    elif comando == "apagar-alarma":
        parpadeando = False
        ledNaranja.value = False
        print("Alarma de seguridad apagada")
    elif comando == "temperatura":
        modoLectura = True
        print("Modo lectura TEMPERATURA activado")
        mensajeDisplay("TENPERATURA") #Mostramos N en vez de M porque no hay M en el display de 7 segmentos
    elif comando == "humedad":
        modoLectura = False
        print("Modo lectura HUMEDAD activado")
        mensajeDisplay("HUNEDAD") #Mostramos N en vez de M porque no hay M en el display de 7 segmentos
    elif comando == "menu":
        menuDeComandos()
    elif comando == "activar-consola":
        mostrarPorConsola = True
        print("Mostrar por consola ACTIVADO")
    elif comando == "desactivar-consola":
        mostrarPorConsola = False
        print("Mostrar por consola DESACTIVADO")

    # Leer sensor DHT11 cada intervaloLectura segundos
    if ahora - ultimoTiempoLectura >= intervaloLectura:
        try:
            temperatura = sensorTemperatura.temperature
            humedad = sensorTemperatura.humidity

            if mostrarPorConsola:
                print(f"Temperatura: {temperatura}°C")
                print(f"Humedad: {humedad}%")

            if modoLectura:
                alarmaTemperatura(temperatura)
                mostrarTemperaturaHumedad(temperatura)
            else:
                alarmaHumedad(humedad)
                mostrarTemperaturaHumedad(humedad)

        except RuntimeError as error:
            print(error.args[0])
        ultimoTiempoLectura = ahora

    valor = sensorInfrarojo.value
    detectado = (valor == False)
    if detectado and seguridadActivada and not parpadeando:
        print("Intruso DETECTADO")
        mensajeDisplay("INTRUSO DETECTADO")
        parpadeando = True
        ledNaranja.value = True
        ultimoCambio = ahora
        
    if parpadeando and ahora - ultimoCambio >= intervalo:
        ledNaranja.value = not ledNaranja.value
        ultimoCambio = ahora

    publish()