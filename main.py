import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QGroupBox,
    QWidget, QLabel, QSlider, QPushButton, QComboBox, QSpinBox
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from BeamFormingSystem import BeamForming
import numpy as np
from mainStyle import sliderStyle
from mainStyle import  sliderStyle, groupBoxStyle , buttonStyle, spinBoxStyle, comboBoxStyle


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        print(f"{self} initialized")
        self.initializeUI()
        self.connectingUI()

    def initializeUI(self):
        print("UI initialized")
        self.setWindowTitle("2D Beamforming Simulator")
        self.setGeometry(100, 100, 1200, 800)        
        self.initial_state = {
            'N': 8,
            'f': 2000,
            'dir': 30,
            'distance': 0.042875
        }
        self.createUIElements()
        self.layoutSet()
        self.styleUi()

        # Initialize BeamForming controller
        self.controller = BeamForming(self.beam_profile_canvas.figure, self.beam_profile_canvas.figure.gca(), self.initial_state)
        self.update_plot()

    def createUIElements(self):
        # Left controlBar Elements
        self.frequency_label = QLabel("Frequency (Hz):")
        self.frequency_slider = QSlider(Qt.Horizontal)
        self.frequency_slider.setRange(500, 5000)
        self.frequency_slider.setValue(2000)
        self.frequency_value = QLabel("2000")
        self.frequency_slider.setToolTip("Adjust frequency between 500Hz and 5000Hz")

        self.phase_label = QLabel("Phase Shift (°):")
        self.phase_slider = QSlider(Qt.Horizontal)
        self.phase_slider.setRange(-180, 180)
        self.phase_slider.setValue(0)
        self.phase_value = QLabel("0")
        self.phase_slider.setToolTip("Adjust phase shift between -180° and 180°")

        self.distance_label = QLabel("Position of Emitters:")
        self.distance_slider = QSlider(Qt.Horizontal)
        self.distance_slider.setRange(1, 50)
        self.distance_slider.setValue(10)
        self.distance_value = QLabel("0.10")
        self.distance_slider.setToolTip("Adjust distance between emitters")

        self.emitters_label = QLabel("Emitters Number:")
        self.emitters_spinbox = QSpinBox()
        self.emitters_spinbox.setRange(2, 16)
        self.emitters_spinbox.setValue(8)

        self.geometry_label = QLabel("Geometry:")
        self.geometry_dropdown = QComboBox()
        self.geometry_dropdown.addItems(["Linear", "Curved"])

        self.curvature_label = QLabel("Curvature:")
        self.curvature_slider = QSlider(Qt.Horizontal)
        self.curvature_slider.setRange(-50, 50)
        self.curvature_slider.setValue(0)
        self.curvature_value = QLabel("0.0")

        self.scenario_label = QLabel("Select Scenario:")
        self.scenario_dropdown = QComboBox()
        self.scenario_dropdown.addItems(["5G", "Ultrasound", "Tumor Ablation"])
        self.load_scenario_button = QPushButton("Load Scenario")
        self.load_scenario_button.setStyleSheet("background-color: lightblue; font-weight: bold")
   
        self.beam_profile_canvas = FigureCanvas(plt.figure(figsize=(7, 4)))  # Larger canvas for Beam Profile
        self.second_graph_canvas = FigureCanvas(plt.figure(figsize=(7, 2)))  # Smaller canvas for secondary graph

    def layoutSet(self):
        controlBar_layout = QVBoxLayout()

        # beamforming parameters
        controlBar_layout.addWidget(self.createGroupBox("Beamforming Parameters", [
            self.createSliders(self.frequency_label, self.frequency_value, self.frequency_slider),
            self.createSliders(self.phase_label, self.phase_value, self.phase_slider),
            self.createSliders(self.distance_label, self.distance_value, self.distance_slider),
            self.createSpinBox(self.emitters_label, self.emitters_spinbox)
        ]))

        # Geometry 
        controlBar_layout.addWidget(self.createCompactGroupBox("Geometry", [
            self.createSliders(self.curvature_label, self.curvature_value, self.curvature_slider),
            self.createComboBox(self.geometry_label, self.geometry_dropdown)
        ]))

        # Scenario
        controlBar_layout.addWidget(self.createCompactGroupBox("Scenario", [
            self.scenario_label, self.scenario_dropdown,
            self.load_scenario_button
        ]))

        controlBar = QWidget()
        controlBar.setLayout(controlBar_layout)

       # Graphs Layout
        graphsBar_layout = QVBoxLayout()
        graphsBar_layout.addWidget(QLabel("Beam Profile Viewer"))
        graphsBar_layout.addWidget(self.beam_profile_canvas)
        graphsBar_layout.addWidget(QLabel("Constructive/Destructive Map"))
        graphsBar_layout.addWidget(self.second_graph_canvas)

        # graphsBar_layout.addStretch(1)

        graphsBar = QWidget()
        graphsBar.setLayout(graphsBar_layout)

        
        # Main Layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(controlBar, 1)  
        main_layout.addWidget(graphsBar, 4)  

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)


    def styleUi(self):
        self.setStyleSheet(groupBoxStyle)  
        self.frequency_slider.setStyleSheet(sliderStyle)
        self.phase_slider.setStyleSheet(sliderStyle)
        self.distance_slider.setStyleSheet(sliderStyle)
        self.curvature_slider.setStyleSheet(sliderStyle)
        self.emitters_spinbox.setStyleSheet(spinBoxStyle)
        self.geometry_dropdown.setStyleSheet(comboBoxStyle)
        self.scenario_dropdown.setStyleSheet(comboBoxStyle)
        # self.load_scenario_button.setStyleSheet(buttonStyle)

    def createGroupBox(self, title, widgets):
        groupbox = QGroupBox(title)
        layout = QVBoxLayout()
        for widget in widgets:
            layout.addWidget(widget)
        groupbox.setLayout(layout)
        return groupbox

    def createCompactGroupBox(self, title, widgets):
        groupbox = QGroupBox(title)
        layout = QVBoxLayout()
        for widget in widgets:
            layout.addWidget(widget)
        groupbox.setLayout(layout)
        groupbox.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        groupbox.adjustSize()  
        return groupbox

    def createSliders(self, label, value_label, slider):
    
        widget = QWidget()
        main_layout = QVBoxLayout()
        
        label_layout = QHBoxLayout()
        label_layout.addWidget(label)
        label_layout.addStretch() 
        label_layout.addWidget(value_label)
        
        main_layout.addLayout(label_layout)
        main_layout.addWidget(slider)
        
        widget.setLayout(main_layout)
        
        slider.valueChanged.connect(
            lambda: value_label.setText(str(slider.value()) if label.text().startswith("Phase") else
                                        f"{slider.value() / 100:.2f}" if label.text().startswith("Distance") else
                                        f"{slider.value() / 10:.1f}" if label.text().startswith("Curvature") else
                                        str(slider.value()))
        )
        return widget

    def createSpinBox(self, label, spinbox):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(spinbox)
        widget.setLayout(layout)
        return widget

    def createComboBox(self, label, combobox):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(combobox)
        widget.setLayout(layout)
        return widget


    def connectingUI(self):
        print("Connecting UI")

        # Update slider values dynamically
        self.frequency_slider.valueChanged.connect(
            lambda: self.frequency_value.setText(str(self.frequency_slider.value()))
        )
        self.phase_slider.valueChanged.connect(
            lambda: self.phase_value.setText(str(self.phase_slider.value()))
        )
        self.distance_slider.valueChanged.connect(
            lambda: self.distance_value.setText(f"{self.distance_slider.value() / 100:.3f}")
        )

        # Update beamforming simulation when sliders or spinbox change
        self.frequency_slider.sliderReleased.connect(self.update_plot)
        self.phase_slider.sliderReleased.connect(self.update_plot)
        self.distance_slider.sliderReleased.connect(self.update_plot)
        self.emitters_spinbox.valueChanged.connect(self.update_plot)

        # Reset button
        # self.reset_button.clicked.connect(self.reset_parameters)

        # Load Scenario button
        self.load_scenario_button.clicked.connect(self.load_scenario)

    
    def update_plot(self):
        print("Updating simulation...")
        self.controller.update_state(
            N=self.emitters_spinbox.value(),
            f=self.frequency_slider.value(),
            dir=self.phase_slider.value(),
            distance=self.distance_slider.value() / 100
        )
        self.beam_profile_canvas.draw()
        


       

    def reset_parameters(self):
        print("Resetting parameters to default...")
        self.frequency_slider.setValue(self.initial_state['f'])
        self.phase_slider.setValue(self.initial_state['dir'])
        self.distance_slider.setValue(int(self.initial_state['distance'] * 100))
        self.emitters_spinbox.setValue(self.initial_state['N'])
        self.update_plot()

    def load_scenario(self):
        scenario = self.scenario_dropdown.currentText()
        print(f"Loaded scenario: {scenario}")
        if scenario == "5G":
            self.frequency_slider.setValue(28000)
            self.phase_slider.setValue(45)
            self.distance_slider.setValue(15)
            self.emitters_spinbox.setValue(16)
        elif scenario == "Ultrasound":
            self.frequency_slider.setValue(2000000)
            self.phase_slider.setValue(30)
            self.distance_slider.setValue(25)
            self.emitters_spinbox.setValue(32)
        elif scenario == "Tumor Ablation":
            self.frequency_slider.setValue(1500000)
            self.phase_slider.setValue(0)
            self.distance_slider.setValue(10)
            self.emitters_spinbox.setValue(24)
        self.update_plot()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())
