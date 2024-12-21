import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QGroupBox,
    QWidget, QLabel, QSlider, QPushButton, QComboBox, QSpinBox
)
import os 
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from BeamFormingSystem import BeamForming
import numpy as np
from mainStyle import sliderStyle
from mainStyle import mainStyle, sliderStyle, groupBoxStyle , buttonStyle, spinBoxStyle, comboBoxStyle,darkColor,sliderDisabledStyle
from phased_array import set_speed, SPEED_OF_LIGHT, SPEED_OF_SOUND_TISSUE, SPEED_OF_SOUND_AIR, RESOLUTION_FACTOR,SPEED_OF_RECEIVER,initialize_simulation_grid
from PyQt5.QtGui import QIcon
import logging
for handler in logging.getLogger().handlers[:]:
    logging.getLogger().removeHandler(handler)

logging.basicConfig(
    filename="Logging.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        logging.info("initialized")
        self.initializeUI()
        self.connectingUI()

    def initializeUI(self):
        logging.info("UI initialized")
        self.setWindowTitle("2D Beamforming Simulator")
        self.setGeometry(100, 100, 1200, 800)
        self.initial_state = {
            'N': 2,'f': 500,'dir': 30,'distance': 0.042875,'geometry': 'Linear','curvature': 0.0,'scenario': 'Default Mode','sizeX': 5,'sizeY': 7}
        
        self.ULTRASOUND_FREQ_RANGE = (20000, 50000)
        self.ULTRASOUND_FREQ_DEFAULT =30000
        self.TUMOR_FREQ_RANGE = (1000, 20000)
        self.TUMOR_FREQ_DEFAULT =3000
        self.RECEIVER_FREQ_RANGE=(10,1500)
        self.RECEIVER_FREQ_DEFAULT=500

        self.createUIElements()
        self.layoutSet()
        self.styleUi()

        self.controller = BeamForming(self.beam_profile_canvas.figure,
                                      [self.constructive_map_canvas.figure.gca(), self.beam_profile_canvas.figure.gca()],
                                      self.initial_state)
        self.update_plot()

    def createUIElements(self):
        # controlBar 
        self.mode_label = QLabel("Mode:")
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(["Transmitter", "Receiver"])


        self.frequency_label = QLabel("Frequency (Hz):")
        self.frequency_slider = QSlider(Qt.Horizontal)
        self.frequency_slider.setRange(500, 5000)
        self.frequency_slider.setValue(500)
        self.frequency_value = QLabel("500")
        self.frequency_slider.setToolTip("Adjust frequency between 500Hz and 5MHz")

        self.phase_label = QLabel("Phase Shift (°):")
        self.phase_slider = QSlider(Qt.Horizontal)
        self.phase_slider.setRange(-180, 180)
        self.phase_slider.setValue(0)
        self.phase_value = QLabel("0")
        self.phase_slider.setToolTip("Adjust phase shift between -180° and 180°")

        self.distance_label = QLabel("Transmitter Position:")
        self.distance_slider = QSlider(Qt.Horizontal)
        self.distance_slider.setRange(1,100)
        self.distance_slider.setValue(50)
        self.distance_value = QLabel("0.10")
        self.distance_slider.setToolTip("Adjust distance between emitters")

        self.emitters_label = QLabel("Transmitters Number:")
        self.emitters_spinbox = QSpinBox()
        self.emitters_spinbox.setRange(2, 64)
        self.emitters_spinbox.setValue(2)

        self.geometry_label = QLabel("Geometry:")
        self.geometry_dropdown = QComboBox()
        self.geometry_dropdown.addItems(["Linear", "Curved"])

        self.curvature_label = QLabel("Curvature:")
        self.curvature_slider = QSlider(Qt.Horizontal)
        self.curvature_slider.setRange(0, 50)
        self.curvature_slider.setValue(1)
        self.curvature_value = QLabel("0.0")
        # self.curvature_slider.setEnabled(False)

        self.scenario_label = QLabel("Select Scenario:")
        self.scenario_dropdown = QComboBox()
        self.scenario_dropdown.addItems(["Default Mode","5G_Receiver Mode", "Ultrasound", "Tumor Ablation","5G_Transmitter Mode"])

        #Graphs 
        self.constructive_map_canvas = FigureCanvas(plt.figure(figsize=(7, 4)))
        self.constructive_map_toolbar = NavigationToolbar(self.constructive_map_canvas, self)
       
        for action in self.constructive_map_toolbar.actions():
            action.setVisible(False)  

        for index in [1, 2, 3,5]:
            if index < len(self.constructive_map_toolbar.actions()):
                action = self.constructive_map_toolbar.actions()[index]
                action.setVisible(True) 

                icon = QIcon(f"photos/toolbar_{index}.png")  
                action.setIcon(icon)

        self.beam_profile_canvas = FigureCanvas(plt.figure(figsize=(7, 4)))
        self.beam_profile_canvas.figure.add_subplot(111, polar=True) 

    def layoutSet(self):
        controlBar_layout = QVBoxLayout()

        controlBar_layout.addWidget(self.createCompactGroupBox("Select a Mode", [
        self.createComboBox(self.mode_label, self.mode_dropdown)
         ]))
        
        # beamforming parameters
        self.parameters_box = QVBoxLayout()  
        parameters_group = self.createGroupBox("Beamforming Parameters", self.parameters_box)
        controlBar_layout.addWidget(parameters_group)

        self.frequency_widget = self.createSliders(self.frequency_label, self.frequency_value, self.frequency_slider)
        self.parameters_box.addWidget(self.frequency_widget) 

        self.phase_widget = self.createSliders(self.phase_label, self.phase_value, self.phase_slider)
        self.parameters_box.addWidget(self.phase_widget)  

        self.distance_widget = self.createSliders(self.distance_label, self.distance_value, self.distance_slider)
        self.parameters_box.addWidget(self.distance_widget)  

        self.curvature_widget = self.createSliders(self.curvature_label, self.curvature_value, self.curvature_slider)
        self.parameters_box.addWidget(self.curvature_widget)

        self.emitters_widget = self.createSpinBox(self.emitters_label, self.emitters_spinbox)
        self.parameters_box.addWidget(self.emitters_widget) 

        # Scenario
        controlBar_layout.addWidget(self.createCompactGroupBox("Scenario", [
            self.scenario_label, self.scenario_dropdown
        ]))

        controlBar = QWidget()
        controlBar.setLayout(controlBar_layout)
       
        
        # Graphs Layout
        graphsBar_layout = QVBoxLayout()
        graphsBar_layout.setSpacing(0)  
        graphsBar_layout.setContentsMargins(0, 0, 0, 0)

        map_toolbar_layout = QHBoxLayout()
        map_toolbar_layout.addWidget(QLabel("Constructive/Destructive Map"))
        map_toolbar_layout.addSpacing(170)
        map_toolbar_layout.addWidget(self.constructive_map_toolbar)
        graphsBar_layout.addLayout(map_toolbar_layout)

        graphsBar_layout.addWidget(self.constructive_map_canvas)
        graphsBar_layout.addWidget(QLabel("Beam Profile Viewer"))
        graphsBar_layout.addWidget(self.beam_profile_canvas)

        graphsBar = QWidget()
        graphsBar.setLayout(graphsBar_layout)

        main_layout = QHBoxLayout()
        main_layout.addWidget(controlBar, 1)
        main_layout.addWidget(graphsBar, 4)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def styleUi(self):
        self.centralWidget().setStyleSheet(mainStyle)
        self.setStyleSheet(groupBoxStyle)  
        self.mode_dropdown.setStyleSheet(comboBoxStyle)
        self.frequency_slider.setStyleSheet(sliderStyle)
        self.phase_slider.setStyleSheet(sliderStyle)
        self.distance_slider.setStyleSheet(sliderStyle)
        self.curvature_slider.setStyleSheet(sliderStyle)
        self.emitters_spinbox.setStyleSheet(spinBoxStyle)
        self.scenario_dropdown.setStyleSheet(comboBoxStyle)
        self.constructive_map_canvas.figure.set_facecolor(darkColor) 
        self.beam_profile_canvas.figure.set_facecolor(darkColor) 

    def connectingUI(self):
        logging.info("Connecting UI")

        self.frequency_slider.valueChanged.connect(
            lambda: self.frequency_value.setText(str(self.frequency_slider.value()))
        )
        self.phase_slider.valueChanged.connect(
            lambda: self.phase_value.setText(str(self.phase_slider.value()))
        )
        self.distance_slider.valueChanged.connect(
            lambda: self.update_distance_and_geometry()
        )
        self.curvature_slider.valueChanged.connect(
            lambda: self.update_curvature_and_geometry()
        )
        self.mode_dropdown.currentTextChanged.connect(self.update_mode)
        

        self.frequency_slider.sliderReleased.connect(self.update_plot)
        self.phase_slider.sliderReleased.connect(self.update_plot)
        self.distance_slider.sliderReleased.connect(self.update_plot)
        self.emitters_spinbox.valueChanged.connect(self.update_plot)
        
        self.curvature_slider.sliderReleased.connect(self.update_plot)

        self.scenario_dropdown.currentIndexChanged.connect(self.choose_scenario)

    def update_mode(self, mode):
        if mode == "Receiver":
            self.reset_to_receiver_mode()
            self.frequency_value.setText(str(self.frequency_slider.value()/RESOLUTION_FACTOR))
            self.distance_label.setText("Receiver Position:")
            self.emitters_label.setText("Receivers Number:")
            self.emitters_spinbox.setRange(1, 64)
            self.emitters_spinbox.setValue(4)
            self.curvature_widget.setParent(None)              
            self.distance_slider.setStyleSheet(sliderStyle)

        else:  # Transmitter mode
            if self.scenario_dropdown.currentText()=="Default Mode" or self.scenario_dropdown.currentText()=="5G_Receiver Mode" :
                self.reset_to_default_mode()
            self.parameters_box.insertWidget(3, self.curvature_widget)  
            self.distance_label.setText("Transmitter Position:")
            self.emitters_label.setText("Transmitters Number:")
            self.emitters_spinbox.setRange(2, 64)
            self.curvature_slider.setEnabled(True)
        logging.info("Mode changed to: %s", mode)
        self.update_plot()

    def set_geometry(self, geometry):
        self.initial_state['geometry'] = geometry
        if geometry == "Linear":
            self.curvature_slider.setValue(0)  
        elif geometry == "Curved":
            self.distance_slider.setValue(10) 

        self.update_plot()

    def update_plot(self):
        mode = self.mode_dropdown.currentText()
        self.initial_state['scenario'] = self.scenario_dropdown.currentText()  

        if mode == "Receiver":
            self.controller.update_state(
            mode=mode,
            receiver_count=self.emitters_spinbox.value(),
            receiver_spacing=self.distance_slider.value() / 100,
            f=self.frequency_slider.value(),
            dir=self.phase_slider.value() 
    )

        else: 
            self.controller.update_state(
                mode=mode,
                N=self.emitters_spinbox.value(),
                f=self.frequency_slider.value(),
                dir=self.phase_slider.value(),
                distance=self.distance_slider.value() / 100,
                geometry=self.initial_state['geometry'], 
                curvature=self.curvature_slider.value() / 10
            )
        self.constructive_map_canvas.draw()
        self.beam_profile_canvas.draw()

    def update_distance_and_geometry(self):
        self.distance_value.setText(f"{self.distance_slider.value() / 100:.3f}")
        self.initial_state['geometry'] ="Linear"
        self.update_plot()



    def update_curvature_and_geometry(self):
        self.curvature_value.setText(f"{self.curvature_slider.value() / 10:.1f}")
        self.initial_state['geometry'] ="Curved"
        self.update_plot()

    def choose_scenario(self):
        scenario = self.scenario_dropdown.currentText()
        logging.info(f"Loaded scenario: {scenario}")
        self.initial_state['scenario'] = scenario
        self.controller.update_state(scenario=scenario)
        sizeY=7
        if scenario == "5G_Transmitter Mode":
            # Switch to Receiver mode
            set_speed(SPEED_OF_LIGHT)
            self.mode_dropdown.setCurrentText("Transmitter")
            self.frequency_slider.setRange(200000000, 600000000)
            self.frequency_slider.setValue(40000000)
            self.phase_slider.setValue(0)
            self.distance_slider.setValue(10)
            self.emitters_spinbox.setValue(16)
            self.curvature_slider.setValue(0)
            self.initial_state['geometry'] = "Linear"
            sizeX=5
            sizeY = 3
            max_points=1000000
        elif scenario == "Ultrasound":
            set_speed(SPEED_OF_SOUND_TISSUE)

            self.mode_dropdown.setCurrentText("Transmitter")
            self.frequency_slider.setRange(self.ULTRASOUND_FREQ_RANGE[0], self.ULTRASOUND_FREQ_RANGE[1])
            self.frequency_slider.setValue(self.ULTRASOUND_FREQ_DEFAULT)
            self.frequency_value.setText(str(self.ULTRASOUND_FREQ_DEFAULT*RESOLUTION_FACTOR))
            self.phase_slider.setValue(0)
            self.distance_slider.setValue(2)
            self.emitters_spinbox.setValue(4)
            self.curvature_slider.setValue(0)
            self.initial_state['geometry'] = "Linear"
            sizeY = 1.5
            sizeX=2
            max_points=1000
            self.frequency_slider.valueChanged.connect(
            lambda: self.frequency_value.setText(str(self.frequency_slider.value() * RESOLUTION_FACTOR)))
            
        elif scenario == "Tumor Ablation":
            set_speed(SPEED_OF_SOUND_TISSUE)

            self.mode_dropdown.setCurrentText("Transmitter")
            self.frequency_slider.setRange(self.TUMOR_FREQ_RANGE[0], self.TUMOR_FREQ_RANGE[1])
            self.frequency_slider.setValue(self.TUMOR_FREQ_DEFAULT)
            self.frequency_value.setText(str(self.TUMOR_FREQ_DEFAULT*RESOLUTION_FACTOR))
            self.phase_slider.setValue(0)
            self.distance_slider.setValue(0)

            self.curvature_slider.setValue(40)
            self.emitters_spinbox.setValue(20)
            self.initial_state['geometry'] = "Curved"
            self.frequency_slider.valueChanged.connect(
            lambda: self.frequency_value.setText(str(self.frequency_slider.value() * RESOLUTION_FACTOR)))
            sizeY = 5
            sizeX=5
            max_points=2000

        elif scenario == "Default Mode":
            self.reset_to_default_mode()
            sizeY = 7
            sizeX=5
            max_points=1000

        else:
            self.reset_to_receiver_mode()
            sizeY = 7
            sizeX=5
            max_points=1000
            
        
        self.controller.grid, self.controller.wavelength = initialize_simulation_grid(
        self.controller.state['N'],
        self.controller.state['f'],
        self.controller.state['distance'],
        sizeX=sizeX,
        sizeY=sizeY,
        max_points=max_points,
        geometry=self.initial_state['geometry']
    )
        self.update_mode(self.mode_dropdown.currentText())
        self.update_plot()

    def reset_to_default_mode(self):
        set_speed(SPEED_OF_SOUND_AIR)
        self.mode_dropdown.setCurrentText("Transmitter")
        self.scenario_dropdown.setCurrentText("Default Mode")
        self.frequency_slider.setRange(500, 5000)
        self.frequency_slider.setValue(500)
        self.phase_slider.setValue(0)
        self.distance_slider.setValue(50)
        self.emitters_spinbox.setValue(2)
        self.initial_state['geometry'] = "Linear"

    def reset_to_receiver_mode(self):
        self.scenario_dropdown.setCurrentText("5G_Receiver Mode")
        set_speed(SPEED_OF_RECEIVER)
        self.frequency_slider.setRange(self.RECEIVER_FREQ_RANGE[0], self.RECEIVER_FREQ_RANGE[1])
        
        self.frequency_slider.setValue(self.RECEIVER_FREQ_DEFAULT)
        
        self.frequency_slider.valueChanged.connect(
            lambda: self.frequency_value.setText(str(self.frequency_slider.value()/RESOLUTION_FACTOR)))
        self.frequency_label.setText("Frequency (GHz):")
        self.mode_dropdown.setCurrentText("Receiver")
        self.phase_slider.setValue(0)
        self.distance_slider.setValue(28)
        self.curvature_slider.setValue(0)
        self.emitters_spinbox.setValue(4)
        self.initial_state['geometry'] = "Linear"
    

    def createGroupBox(self, title, layout):
        groupbox = QGroupBox(title)
        groupbox_layout = QVBoxLayout()
        groupbox_layout.addLayout(layout)  
        groupbox.setLayout(groupbox_layout)
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())