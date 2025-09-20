import board
import digitalio
import time

# Configurar el pin GPIO para el LED (cambia GP18 por el pin que uses)
led = digitalio.DigitalInOut(board.GP18)
led.direction = digitalio.Direction.OUTPUT

print("Iniciando prueba del LED...")
print("Presiona Ctrl+C para detener")

# Bucle principal
try:
    while True:
        # Encender LED
        led.value = True
        print("LED encendido")
        time.sleep(1.0)
        
        # Apagar LED
        led.value = False
        print("LED apagado")
        time.sleep(1.0)

except KeyboardInterrupt:
    print("\nPrueba finalizada")
    led.value = False  # Asegurar que el LED se apague

""" Conexión del circuito:
Pin positivo del LED → Pin GPIO (GP18 en el ejemplo)
Pin negativo del LED → Resistencia de 220Ω → Pin GND del microcontrolador

Notas importantes:
Cambia board.GP18 por el pin GPIO que estés usando
La resistencia es importante para limitar la corriente y proteger el LED
Usa Ctrl+C para detener el programa
El código incluye manejo de excepciones para apagar el LED al finalizar """