import paho.mqtt.client as mqtt


class Broker():
    def __init__(self,ip) -> None:
        self.ip=ip
        self.conectado=False

    def conectar(self):
        try:
            self.client = mqtt.Client("Control")#no se que significa esto, habría que verlo en el codigo del auto en la esp
            self.client.connect(self.ip)
            self.client.subscribe("respuesta")
            self.client.loop_start()
            self.client.on_message=self.on_message
            self.client.on_connect=self.on_connect
        except Exception as e:
             print(f"error en conectar braoker: {e}")

    def on_message(self,client, userdata, message):
            print("Mensaje: " , str(message.payload.decode("utf-8")))

    def on_connect(self,client, userdata, flags, rc):
        self.conectado=True
        print("Conexión/código de resultado: "+str(rc))
        self.client.subscribe("respuestas")
    
    def enviar_mensaje(self,topico,mensaje):
        self.client.publish(topico, mensaje)
