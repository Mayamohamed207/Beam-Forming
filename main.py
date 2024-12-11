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
from mainStyle import mainStyle, sliderStyle, groupBoxStyle , buttonStyle, spinBoxStyle, comboBoxStyle,darkColor,sliderDisabledStyle
from phased_array import set_speed, SPEED_OF_LIGHT, SPEED_OF_SOUND_TISSUE, SPEED_OF_SOUND_AIR, set_frequency,five_g_reciever_frequency



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
            'f': 500,
            'dir': 30,
            'distance': 0.042875,
            'geometry': 'Linear',
            'curvature': 0.0,
            'scenario': 'Default Mode'
        }
        self.createUIElements()
        self.layoutSet()
        self.styleUi()

        # Initialize BeamForming controller
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
        self.distance_slider.setValue(10)
        self.distance_value = QLabel("0.10")
        self.distance_slider.setToolTip("Adjust distance between emitters")

        self.emitters_label = QLabel("Transmitters Number:")
        self.emitters_spinbox = QSpinBox()
        self.emitters_spinbox.setRange(2, 64)
        self.emitters_spinbox.setValue(8)

        self.geometry_label = QLabel("Geometry:")
        self.geometry_dropdown = QComboBox()
        self.geometry_dropdown.addItems(["Linear", "Curved"])

        self.curvature_label = QLabel("Curvature:")
        self.curvature_slider = QSlider(Qt.Horizontal)
        self.curvature_slider.setRange(0, 50)
        self.curvature_slider.setValue(1)
        self.curvature_value = QLabel("0.0")
        self.curvature_slider.setEnabled(False)

        self.scenario_label = QLabel("Select Scenario:")
        self.scenario_dropdown = QComboBox()
        self.scenario_dropdown.addItems(["Default Mode","5G", "Ultrasound", "Tumor Ablation"])
        # self.choose_scenario_button = QPushButton("Load Scenario")
        # self.choose_scenario_button.setStyleSheet("background-color: lightblue; font-weight: bold")

        #Graphs 
        self.constructive_map_canvas = FigureCanvas(plt.figure(figsize=(7, 4)))
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

        self.emitters_widget = self.createSpinBox(self.emitters_label, self.emitters_spinbox)
        self.parameters_box.addWidget(self.emitters_widget) 

        # Geometry
        self.geometry_box = self.createCompactGroupBox("Geometry", [
            self.createSliders(self.curvature_label, self.curvature_value, self.curvature_slider),
            self.createComboBox(self.geometry_label, self.geometry_dropdown)
        ])
        controlBar_layout.addWidget(self.geometry_box)

        # Scenario
        controlBar_layout.addWidget(self.createCompactGroupBox("Scenario", [
            self.scenario_label, self.scenario_dropdown
            # self.choose_scenario_button
        ]))

        controlBar = QWidget()
        controlBar.setLayout(controlBar_layout)
       

        # Graphs Layout
        graphsBar_layout = QVBoxLayout()
        graphsBar_layout.setSpacing(5)  
        graphsBar_layout.setContentsMargins(0, 0, 0, 0)
        graphsBar_layout.addWidget(QLabel("Constructive/Destructive Map"))
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
        self.curvature_slider.setStyleSheet(sliderDisabledStyle)
        self.emitters_spinbox.setStyleSheet(spinBoxStyle)
        self.geometry_dropdown.setStyleSheet(comboBoxStyle)
        self.scenario_dropdown.setStyleSheet(comboBoxStyle)
        # self.choose_scenario_button.setStyleSheet(buttonStyle)
        self.constructive_map_canvas.figure.set_facecolor(darkColor) 
        self.beam_profile_canvas.figure.set_facecolor(darkColor) 

    def connectingUI(self):
        print("Connecting UI")

        self.frequency_slider.valueChanged.connect(
            lambda: self.frequency_value.setText(str(self.frequency_slider.value()))
        )
        self.phase_slider.valueChanged.connect(
            lambda: self.phase_value.setText(str(self.phase_slider.value()))
        )
        self.distance_slider.valueChanged.connect(
            lambda: self.distance_value.setText(f"{self.distance_slider.value() / 100:.3f}")
        )

        self.mode_dropdown.currentTextChanged.connect(self.update_mode)
        

        self.frequency_slider.sliderReleased.connect(self.update_plot)
        self.phase_slider.sliderReleased.connect(self.update_plot)
        self.distance_slider.sliderReleased.connect(self.update_plot)
        self.emitters_spinbox.valueChanged.connect(self.update_plot)
        
        self.geometry_dropdown.currentTextChanged.connect(self.update_geometry)
        self.curvature_slider.sliderReleased.connect(self.update_plot)

        # self.choose_scenario_button.clicked.connect(self.choose_scenario)
        self.scenario_dropdown.currentIndexChanged.connect(self.choose_scenario)

    def update_mode(self, mode):
        if mode == "Receiver":
            # Remove Frequency slider
            self.parameters_box.removeWidget(self.frequency_widget)
            self.frequency_widget.setParent(None)  
            self.distance_label.setText("Receiver Position:")
            self.emitters_label.setText("Receivers Number:")
            self.emitters_spinbox.setRange(1, 64)
            self.geometry_box.setVisible(False)
            
            self.distance_slider.setEnabled(True)
            self.distance_slider.setStyleSheet(sliderStyle)

        else:  # Transmitter mode
            # Add Frequency slider
            self.parameters_box.insertWidget(0, self.frequency_widget)  
            self.distance_label.setText("Transmitter Position:")
            self.emitters_label.setText("Transmitters Number:")
            self.emitters_spinbox.setRange(2, 64)
            self.geometry_box.setVisible(True)
            if self.geometry_dropdown.currentText()== "Curved":
                self.distance_slider.setEnabled(False)
                self.distance_slider.setStyleSheet(sliderDisabledStyle)  
            

        self.update_plot()


    def update_plot(self):
        mode = self.mode_dropdown.currentText()
        self.initial_state['scenario'] = self.scenario_dropdown.currentText()  

        if mode == "Receiver":
            self.controller.update_state(
            mode=mode,
            receiver_count=self.emitters_spinbox.value(),
            receiver_spacing=self.distance_slider.value() / 100,
            dir=self.phase_slider.value()  # Use the phase slider for steering angle
    )

        else:  # Transmitter mode
            self.controller.update_state(
                mode=mode,
                N=self.emitters_spinbox.value(),
                f=self.frequency_slider.value(),
                dir=self.phase_slider.value(),
                distance=self.distance_slider.value() / 100,
                geometry=self.geometry_dropdown.currentText(),
                curvature=self.curvature_slider.value() / 10
            )
        self.constructive_map_canvas.draw()
        self.beam_profile_canvas.draw()

   
    def update_geometry(self):
        selected_geometry = self.geometry_dropdown.currentText()

        if selected_geometry == "Linear":
            self.curvature_slider.setEnabled(False)
            self.curvature_slider.setStyleSheet(sliderDisabledStyle)  
            # Enable distance slider
            self.distance_slider.setEnabled(True)
            self.distance_slider.setStyleSheet(sliderStyle)  
        elif selected_geometry == "Curved":
            # Enable curvature slider
            self.curvature_slider.setEnabled(True)
            self.curvature_slider.setStyleSheet(sliderStyle)  
            # Disable distance slider
            self.distance_slider.setEnabled(False)
            self.distance_slider.setStyleSheet(sliderDisabledStyle)  
        
        self.update_plot()

    def choose_scenario(self):
        scenario = self.scenario_dropdown.currentText()
        print(f"Loaded scenario: {scenario}")
        self.initial_state['scenario'] = scenario
        self.controller.update_state(scenario=scenario)
        if scenario == "5G":
            # Switch to Receiver mode
            set_speed(SPEED_OF_LIGHT)
            set_frequency(five_g_reciever_frequency)
            self.mode_dropdown.setCurrentText("Receiver")
            self.distance_slider.setValue(10)
            self.emitters_spinbox.setValue(8)
            self.phase_slider.setValue(45)  # Steering direction
        elif scenario == "Ultrasound":
            # Switch to Transmitter mode
            set_speed(SPEED_OF_SOUND_TISSUE)

            self.mode_dropdown.setCurrentText("Transmitter")
            self.frequency_slider.setRange(2000000, 5000000)
            self.frequency_slider.setValue(3000000)
            self.phase_slider.setValue(10)
            self.distance_slider.setValue(5)
            self.emitters_spinbox.setValue(16)
            self.geometry_dropdown.setCurrentText("Linear")

        elif scenario == "Tumor Ablation":
            # Switch to Transmitter mode
            set_speed(SPEED_OF_SOUND_TISSUE)

            self.mode_dropdown.setCurrentText("Transmitter")
            self.frequency_slider.setRange(500000, 2000000)
            self.frequency_slider.setValue(600000)
            self.phase_slider.setValue(15)
            self.curvature_slider.setValue(8)
            self.emitters_spinbox.setValue(32)
            self.geometry_dropdown.setCurrentText("Curved")
            
        elif scenario == "Default Mode":
            set_speed(SPEED_OF_SOUND_AIR)
            self.mode_dropdown.setCurrentText("Transmitter")
            self.frequency_slider.setRange(500, 5000)
            self.frequency_slider.setValue(500)
            self.phase_slider.setValue(0)
            self.distance_slider.setValue(10)
            self.emitters_spinbox.setValue(8)
            self.geometry_dropdown.setCurrentText("Linear")

        # Trigger UI updates and redraw
        self.update_mode(self.mode_dropdown.currentText())
        self.update_plot()

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