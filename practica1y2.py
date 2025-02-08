import network
from umqtt.simple import MQTTClient
from machine import Pin, time_pulse_us
import time

# Configuración WiFi
WIFI_SSID = "ANTONIOBM"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_BROKER = "192.168.137.167"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = ""
MQTT_TOPIC = "utng/sensor"
MQTT_PORT = 1883

# Configuración del sensor ultrasónico
TRIG_PIN = 5
ECHO_PIN = 18

trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

# Configuración del LED RGB
RED_PIN = 15
GREEN_PIN = 2
BLUE_PIN = 4

led_red = Pin(RED_PIN, Pin.OUT)
led_green = Pin(GREEN_PIN, Pin.OUT)
led_blue = Pin(BLUE_PIN, Pin.OUT)

# Función para conectar a WiFi
def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.3)
    print("\nWiFi Conectada!")

# Función para conectar al broker MQTT
def conectar_broker():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD)
    client.connect()
    print(f"Conectado a MQTT Broker: {MQTT_BROKER}, Topic: {MQTT_TOPIC}")
    return client

# Función para encender el LED RGB con un color específico
def set_color(red, green, blue):
    led_red.value(red)
    led_green.value(green)
    led_blue.value(blue)

# Función para medir distancia con HC-SR04
def medir_distancia():
    trig.off()
    time.sleep_us(2)
    trig.on()
    time.sleep_us(10)
    trig.off()

    duracion = time_pulse_us(echo, 1, 30000)  # Máximo 30 ms de espera
    if duracion < 0:
        return -1  # Error en la medición
    
    distancia = (duracion * 0.0343) / 2  # Convertir a cm
    return distancia

# Conectar a WiFi y MQTT
conectar_wifi()
client = conectar_broker()

distancia_anterior = -1  # Inicializamos con un valor inválido

# Bucle principal
while True:
    distancia = medir_distancia()
    print(f"Distancia: {distancia} cm")

    # Cambiar el color del LED RGB según la distancia
    if distancia == -1:
        set_color(0, 0, 0)  # Apagar LED si hay error
    elif distancia > 20:
        set_color(0, 1, 0)  # Verde
    elif distancia > 10:
        set_color(1, 1, 0)  # Amarillo
    else:
        set_color(1, 0, 0)  # Rojo

    # Publicar la distancia en MQTT solo si cambia
    if distancia != distancia_anterior:
        client.publish(MQTT_TOPIC, str(distancia))
        distancia_anterior = distancia  # Actualizar la distancia anterior

    time.sleep(2)  # Esperar 2 segundos antes de la siguiente medición