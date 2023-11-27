import threading
import requests
import time
from brazo import Brazo
from broker import Broker
import subprocess
from os import system


ip = subprocess.getoutput("ifconfig | grep 'inet ' | grep -Fv 127.0.0.1 | awk '{print $2}'")

class Posicion():
    def __init__(self,indice,x,y,q1,q2) -> None:
        self.indice=indice
        self.x=x
        self.y=y
        self.q1=q1
        self.q2=q2

    def registro(self):
        return f"{self.indice},{self.x},{self.y},{self.q1},{self.q2}"
    
    def __str__(self) -> str:
        return f"Movimiento: {self.indice}, X:{self.x}, Y:{self.y}, q1:{self.q1}, q2:{self.q2}"
    
class Control_brzao():
    def __init__(self,brazo,broker,timepo_espera_msg=16,pruebas=False) -> None:
        self.brazo=brazo
        self.broker=broker
        self.broker.conectar()
        self.input=False
        self.tipo_mov=1
        self.respuesta=False
        self.movimiento=0
        self.tiempo_espera_msg=timepo_espera_msg
        self.posicion_actual=Posicion(0,brazo.x,brazo.y,brazo.q1,brazo.q2)
        self.registrar_mov(True)
        self.broker.client.on_message=self.on_message
        self.s_msg= threading.Semaphore(1)
        self.msg_recibido=False
        self.pruebas=pruebas
        self.reinicio=False

    def on_message(self,client, userdata, message):
            mensaje=str(message.payload.decode("utf-8"))
            if mensaje=="ok":
                if not self.reinicio:
                    self.posicion_actual=Posicion(self.movimiento+1,
                                                self.brazo.x,
                                                self.brazo.y,
                                                self.brazo.q1,
                                                self.brazo.q2)
                else:
                    self.posicion_actual.indice=self.movimiento+1
                self.msg_recibido=True
                system("clear")
                print(f"Movimiento realizado con éxito.")
                self.registrar_mov()

    def registrar_mov(self,inicial=False):
        """Registra x, y, q1 y q2 del la posición actual en ese orden.
        los registros se guardan uno por linea."""
        modo="a+"
        if inicial:
            modo="w+"
        try:
            with open(f"./Lab_brazo/movimientos_{self.brazo.nombre}.txt",modo) as my_file:
                my_file.write(f"{self.posicion_actual.registro()}\n")
            print(f"Se registró la posición: {self.posicion_actual}\n\n")
            self.movimiento+=1
        except Exception as e:
            print(f"Error al registrar movimiento: {e}")
        
    def esperar_mensaje(self):
        t=0
        p="."
        while t<self.tiempo_espera_msg and not self.msg_recibido:
            system("clear")
            print(f"Esperando confirmación del movimiento.{p*t}\n")
            time.sleep(1)
            t+=1
        #hay que hacer algo que compruebe la confrimación o descarte el movimiento
        self.msg_recibido=False
        time.sleep(1)
        self.s_msg.release()

    def enviar_mov(self,topico,valor):
        """Envía un mensaje al broker con los ángulos q1 y q2 del movimiento"""
        if self.broker.conectado:
            self.broker.enviar_mensaje(topico,f"{valor}")
        else:
            self.s_msg.release()
            system("clear")
            print(f"Se quería enviar {topico},{valor}")
            print("No esta conectado el broker\n")

    def mover(self,x=180,y=0,paralelo=False,posicion=False):
        """Si se valida el movimiento solicitado, se realizan las acciones correspondientes para llevar
        a caboel movimiento solicitado."""
        self.s_msg.acquire()
        if not posicion:
            if self.brazo.validar_mov(x,y):
                self.brazo.x=x
                self.brazo.y=y
                self.brazo.calcular_qs()
            else:
                #el movimiento no es válido
                system("clear")
                print("El movimiento no es válido\n")
                self.s_msg.release()
                return
        if posicion:
            self.enviar_mov("q1",posicion.q1)
            
            self.enviar_mov("q2",posicion.q2)
        elif paralelo:
            print("Movimiento en paralelo\n")
            t1 = threading.Thread(target = self.enviar_mov,args=("q1",self.brazo.q1))
            t2 = threading.Thread(target = self.enviar_mov,args=("q2",self.brazo.q2))
            t1.start()
            t2.start()
        else:
            print("Movimiento serial\n")
            self.enviar_mov("q1",self.brazo.q1)
            self.enviar_mov("q2",self.brazo.q2)
        t_esp_mensaje = threading.Thread(target = self.esperar_mensaje)
        t_esp_mensaje.start()
        
    def leer_mov(self):
        lista=[]
        try:
            with open(f"./Lab_brazo/movimientos_{self.brazo.nombre}.txt","r") as my_file:
                movimientos = my_file.readlines()
                for mov in movimientos:
                    p=mov.split(",")
                    p=Posicion(
                        p[0],p[1],p[2],p[3],p[4].rstrip()
                    )
                    lista.append(p)
            for el in lista:
                print(el.q1)
            return lista
        except Exception as e:
            print(f"Error en registrar mov: {e}")

    def iniciar_loop_control(self):
        system("clear")
        salir=False
        while not self.broker.conectado:
            print("No hay conexión con el broker")
            print("r para reintentar")
            conectar=input()
            if conectar!="r":
                print("Nos vemos en Disney")
                salir=True
                return "r"

        if not salir:
            while self.input!="salir":
                self.s_msg.acquire()
                print("Tipo de movimiento \n 1 en serie \n 2 en paralelo")
                print("s para volver.\n")
                self.tipo_mov=input("->")
                if self.tipo_mov=="s":
                    self.s_msg.release()
                    return "r"
                self.tipo_mov=int(self.tipo_mov)
                paralelo=False
                if self.tipo_mov==2:
                    paralelo=True
                print(f"Coordenada en x: \n valor entre {self.brazo.x_min} y {self.brazo.x_max} (mm):")
                x=float(input("->"))
                print(f"Coordenada en y: \n valor entre {self.brazo.y_min} y {self.brazo.y_max} (mm):")
                y=float(input("->"))
                if not self.pruebas:
                    self.s_msg.release()
                    self.mover(x,y,paralelo)
                else:
                    print("Estamos en pruebas, sin conexión.")

    def iniciar_loop_leer_mov(self):
        pass

    def reiniciar(self):
        self.reinicio=True
        for pos in reversed(self.leer_mov()):
            self.s_msg.acquire()
            print(f"se evvia q {pos.q1}")
            self.s_msg.release()
            self.posicion_actual=pos
            self.mover(posicion=pos)
        self.s_msg.acquire()
        self.s_msg.release()
        self.reinicio=False
        print("Reinicio exitoso\nIniciar un nuevo registro de movimientos? s/n")
        nuevo=input("->")
        if nuevo=="s":
            self.brazo.nombre=f"{self.brazo.nombre}_1"
            self.movimiento=0
            self.posicion_actual.indice=0
            self.registrar_mov(inicial=True)
        return "r"

    def iniciar_loop(self):
        opccion="m"
        system("clear")
        while opccion!="s":
            print("Opciones: \n 1 Mover \n 2 Ver registro de movimientos \n 3 Reinicio")
            print("s para salir.\n")
            opccion=input("->")
            if opccion=="1":
                opccion=self.iniciar_loop_control()
            if opccion=="2":
                opccion=self.iniciar_loop_leer_mov()
            if opccion=="3":
                opccion=self.reiniciar()
            if opccion=="s":
                break
            if opccion=="r":
                pass
            else:
                print("La opción no es válida.")







brazo=Brazo("brazo_1",0,180,0,180,100,80)
broker=Broker(ip)
Control_brzao(brazo,broker).iniciar_loop()
