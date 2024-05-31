import sys
import sim
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import threading
import time

#Librerias logica difusa

#Verificacion de comentario

import skfuzzy as fuzz
from skfuzzy import control as ctrl

class WindowsPyQt(QWidget):
    def __init__(self):
        super().__init__()
        self.inicializarUI()

    def inicializarUI(self):
        self.setGeometry(100,100,800,800)
        self.setWindowTitle("IA 2024")

        # Crear un botón
        self.boton = QPushButton('Conectar', self)
        self.boton.setFixedSize(100, 50)

        # Crear labels
        self.label1 = QLabel('', self)
        self.label1.setFixedSize(200, 50)
        self.label2 = QLabel('', self)
        self.label2.setFixedSize(200, 50)

        # Crear un layout vertical y agregar el botón y los labels
        layout = QVBoxLayout()
        layout.addWidget(self.boton)
        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        self.setLayout(layout)

        canvas = FigureCanvasQTAgg(fig)
        layout.addWidget(canvas)

        toolbar = NavigationToolbar2QT(canvas, self)
        layout.addWidget(toolbar)

        # Conectar el evento de clic del botón a la función de inicio de los hilos
        self.boton.clicked.connect(self.iniciarHilos)

        self.show()

    def iniciarHilos(self):
        # Crear los hilos para sim y para imprimir los números
        thread1 = threading.Thread(target=self.run_sim)
        thread1.daemon = True  # Hacer que el hilo sea daemon
        # Iniciar los hilos
        thread1.start()


    def run_sim(self):
        clientID = connect(19999)
        if clientID == 0: 
            print("conectado a", 19999)
            self.label1.setText("conectado a 19999")
        else: 
            print("no se pudo conectar")
            self.label1.setText("no se pudo conectar")
        
        # Obtén los manejadores de los tres sensores de visión
        res1, visionSensorHandle1 = sim.simxGetObjectHandle(clientID, 'Pioneer_p3dx_CenterSensor1', sim.simx_opmode_oneshot_wait)
        res2, visionSensorHandle2 = sim.simxGetObjectHandle(clientID, 'Pioneer_p3dx_LeftSensor2', sim.simx_opmode_oneshot_wait)
        res3, visionSensorHandle3 = sim.simxGetObjectHandle(clientID, 'Pioneer_p3dx_RightSensor3', sim.simx_opmode_oneshot_wait)
        if res1 != sim.simx_return_ok or res2 != sim.simx_return_ok or res3 != sim.simx_return_ok:
            print('No se pudo obtener el manejador de uno o más sensores de visión')
            return

        # Obtén los manejadores de los motores
        res, leftMotorHandle = sim.simxGetObjectHandle(clientID, 'Pioneer_p3dx_leftMotor', sim.simx_opmode_oneshot_wait)
        res, rightMotorHandle = sim.simxGetObjectHandle(clientID, 'Pioneer_p3dx_rightMotor', sim.simx_opmode_oneshot_wait)

        # Inicializa la variable para rastrear el último sensor que vio la línea negra
        last_black_line_sensor = 0

        i = 1
        while True:
            self.label2.setText(str(i))
            time.sleep(0.1)
            i = i % 10 + 1 

            # Obtén la imagen de cada sensor de visión
            sensor_values = []
            for handle, sensor_name in zip([visionSensorHandle1, visionSensorHandle2, visionSensorHandle3], ['Pioneer_p3dx_CenterSensor1', 'Pioneer_p3dx_LeftSensor2', 'Pioneer_p3dx_RightSensor3']):
                res, resolution, image = sim.simxGetVisionSensorImage(clientID, handle, 0, sim.simx_opmode_oneshot_wait)
                if res == sim.simx_return_ok:
                    # Transforma la imagen en una matriz de numpy y obtén los valores RGB
                    image_np = np.array(image, dtype=np.uint8)
                    image_np = np.reshape(image_np, (resolution[1], resolution[0], 3))
                    
                    # Calcular el promedio de los valores de los píxeles RGB
                    avg = np.mean(image_np)
                    
                    # Determinar si el sensor está sobre una línea negra o un fondo blanco
                    if avg < 80:
                        #print(f'El sensor {sensor_name} está sobre una línea negra')
                        sensor_values.append(-1)
                        # Actualiza el último sensor que vio la línea negra
                        last_black_line_sensor = handle
                    else:
                        #print(f'El sensor {sensor_name} está sobre un fondo blanco')
                        sensor_values.append(1)


            # Si todos los sensores están sobre un fondo blanco, gira en la dirección del último sensor que vio la línea negra
            if all(value == 1 for value in sensor_values):
                #print('Todos los sensores están sobre un fondo blanco, girando hacia el último sensor que vio la línea negra...')
                if last_black_line_sensor == visionSensorHandle1 or last_black_line_sensor == visionSensorHandle2:
                    leftSpeed = -0.2
                    rightSpeed = 0.2
                else:
                    leftSpeed = 0.2
                    rightSpeed = -0.2
            else:
                # Aplicar la lógica difusa al error
                if sensor_values[1] < 0 and sensor_values[2] < 0:
                    delta = -0.3
                elif sensor_values[1] > 0 and sensor_values[2] > 0:
                    delta = 0.3
                else:
                    delta = 0

                # Ajustar las velocidades de los motores en función del delta
                leftSpeed = 0.4 + delta
                rightSpeed = 0.4 - delta

            # Establecer las velocidades de los motores
            sim.simxSetJointTargetVelocity(clientID, leftMotorHandle, leftSpeed, sim.simx_opmode_oneshot_wait)
            sim.simxSetJointTargetVelocity(clientID, rightMotorHandle, rightSpeed, sim.simx_opmode_oneshot_wait)

            # Verificar el estado de la conexión
            connection_status = sim.simxGetConnectionId(clientID)
            if connection_status == -1:
                print("La conexión se ha perdido")
                self.label1.setText("La conexión se ha perdido")
                break  # Salir del bucle si la conexión se ha perdido

# Datos de ejemplo
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.tan(x)

fig = Figure()
ax =  fig.add_subplot()
ax.plot(x, y1, label='sin(x)')

 
def connect(port):
    sim.simxFinish(-1) 
    clientID=sim.simxStart('127.0.0.1',port,True,True,2000,5) 
    return clientID

if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open('style.qss', 'r') as f:
        style = f.read()
    app.setStyleSheet(style)
    ventana = WindowsPyQt()
    sys.exit(app.exec())
