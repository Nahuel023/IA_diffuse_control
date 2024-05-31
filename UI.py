from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QMainWindow
from PySide6 import QtCharts
from PySide6.QtCore import Qt, QTimer
import sys
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Crear un widget central para la ventana principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Crear un layout vertical
        self.layout = QVBoxLayout(self.central_widget)

        # Crear un botón y añadirlo al layout
        self.button = QPushButton("Haz clic en mí")
        self.layout.addWidget(self.button)

        # Crear una etiqueta y añadirlo al layout
        self.label = QLabel("Esta es una etiqueta")
        self.layout.addWidget(self.label)

        # Crear un gráfico y añadirlo al layout
        self.chart = QtCharts.QChart()
        self.chart_view = QtCharts.QChartView(self.chart)
        self.layout.addWidget(self.chart_view)

        # Crear tres series de datos para los sensores
        self.series1 = QtCharts.QLineSeries()
        self.series2 = QtCharts.QLineSeries()
        self.series3 = QtCharts.QLineSeries()

        # Añadir las series al gráfico
        self.chart.addSeries(self.series1)
        self.chart.addSeries(self.series2)
        self.chart.addSeries(self.series3)

        # Crear un eje para el gráfico y añadirlo al gráfico
        self.axisX = QtCharts.QValueAxis()
        self.axisY = QtCharts.QValueAxis()
        self.axisX.setRange(0, 30)
        self.axisY.setRange(0, 255)
        self.chart.addAxis(self.axisX, Qt.AlignBottom)
        self.chart.addAxis(self.axisY, Qt.AlignLeft)

        # Asociar las series con el eje
        self.series1.attachAxis(self.axisX)
        self.series1.attachAxis(self.axisY)
        self.series2.attachAxis(self.axisX)
        self.series2.attachAxis(self.axisY)
        self.series3.attachAxis(self.axisX)
        self.series3.attachAxis(self.axisY)

        # Crear un QTimer
        self.timer = QTimer()
        self.timer.setInterval(1000)  # 1000 ms = 1 s
        self.timer.timeout.connect(self.update_data)
        self.timer.start()

    def update_data(self):
        # Añadir nuevos datos a las series y eliminar los datos antiguos
        self.series1.append(self.series1.count(), np.random.randint(0, 256))
        self.series2.append(self.series2.count(), np.random.randint(0, 256))
        self.series3.append(self.series3.count(), np.random.randint(0, 256))
        if self.series1.count() > 255:
            self.series1.remove(0)
            self.series2.remove(0)
            self.series3.remove(0)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())
