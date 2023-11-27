import math 
import numpy as np

class Brazo():
    def __init__(self,nombre,x_min,x_max,y_min,y_max,l1,l2) -> None:
        """Crea el objeto brazo, inicializa las variables necesarias por defecto.
        l1 y l2 deben proporcionarse en mm. q1 y q2 deben proporcionarse en grados."""
        self.nombre=nombre
        self.x_min=x_min
        self.x_max=x_max
        self.y_min=y_min
        self.y_max=y_max
        self.l12=pow(l1, 2)
        self.l22=pow(l2,2)
        self.x=x_max
        self.y=0
        self.q1=0
        self.q2=0
        self.l1=l1
        self.l2=l2
        self.error=False

    def validar_mov(self,x,y):
        """Valida el movimiento solicitado en funcion de los valores máximos posibles para x e y."""
        if not (self.x_min<=x<=self.x_max and self.y_min<=y<=self.y_max):
            self.error="Las coordenadas no son válidas"
            return False
        h=x**2 +y**2
        arg=(h-(self.l12+self.l22))/(2*self.l1*self.l2)
        print(f"El argumento de cos q2 : {arg}")
        if arg<-1: 
            self.error="Las coordenadas no son válidas_inf"
            return False
        if 1<arg:
            self.error="Las coordenadas no son válidas_sup"
            return False
        if -1<arg<1:
            self.arg=arg
            self.caso=1
        elif arg==1:
            self.caso=2
        elif arg==-1:
            self.caso=3
        return True
        
    def calcular_qs(self):
        """Se calculan los valores de q1 y q2 """
        self.x2=pow(self.x, 2)
        self.y2=pow(self.y, 2)
        if self.caso==1:
            self.q2=np.arccos(self.arg)
            if self.x==0:
                self.x=0.01
            arg_1=self.y/self.x
            atan_1=np.arctan(arg_1)
            arg_2=((self.l2*np.sin(self.q2))/(self.l1+self.l2*np.cos(self.q2)))
            atan_2=np.arctan(arg_2)
            self.q1=(atan_1-atan_2)
        elif self.caso==2:
            self.q2=0
            if self.x==0:
                self.q1=np.pi/2
            else:
                self.q1=np.arctan(self.y/self.x)
        elif self.caso==3:
            self.q2=np.pi
            if self.x==0:
                self.q1=np.pi/2
            else:
                self.q1=np.arctan(self.y/self.x)
        self.q1=round(math.degrees(self.q1),2)
        self.q2=round(math.degrees(self.q2),2)