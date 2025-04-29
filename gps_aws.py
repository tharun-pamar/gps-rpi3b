from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import gpsd
import time

# Connect to local gpsd
gpsd.connect()

# MQTT client setup
client = AWSIoTMQTTClient("EpicsOBUClient")
client.configureEndpoint("a359o8qgb081eq-ats.iot.eu-north-1.amazonaws.com", 8883)
client.configureCredentials("/home/pi/certs/AmazonRootCA1.pem", 
                            "/home/pi/certs/private.pem.key", 
                            "/home/pi/certs/certificate.pem.crt")

client.configureOfflinePublishQueueing(-1)
client.configureDrainingFrequency(2)
client.configureConnectDisconnectTimeout(10)
client.configureMQTTOperationTimeout(5)

client.connect()

# Loop to send GPS data
while True:
    packet = gpsd.get_current()
    latitude = packet.lat
    longitude = packet.lon
    payload = f'{{"latitude": {latitude}, "longitude": {longitude}}}'
    print(f"Publishing: {payload}")
    client.publish("epics/test1", payload, 0)
    time.sleep(5)
