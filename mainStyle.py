# sliderStyle = """
#     QSlider::groove:horizontal {
#         background: #B83777;
#         height: 6px;
#         border-radius: 3px;
#     }
#     QSlider::handle:horizontal {
#         background: #F7775E;
#         border: 1px solid #B83777;
#         width: 12px;
#         height: 12px;
#         margin: -3px 0;
#         border-radius: 6px;
#     }
# """

sliderStyle = """
    QSlider::groove:horizontal {
        background: #ddd;
        height: 6px;
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        background: #ddd;
        border: 1px solid #ddd;
        width: 12px;
        height: 12px;
        margin: -3px 0;
        border-radius: 6px;
    }
"""

groupBoxStyle = """
    QGroupBox {
        border: 2px solid #a0a0a0;
        border-radius: 10px;
        margin-top: 10px;
        background-color: #f5f5f5;
        padding: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 3px;
        color: #333; /* Darker title color for better visibility */
        font-weight: bold;
    }
"""

buttonStyle = """
    QPushButton {
        background-color: #0078d7;
        color: white;
        font-weight: bold;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
    }
    QPushButton:hover {
        background-color: #0053a4;
    }
"""

# Style for spin boxes
spinBoxStyle = """
    QSpinBox {
        background-color: #ffffff;
        border: 1px solid #a0a0a0;
        border-radius: 5px;
        padding: 2px 6px;
        font-size: 14px;
    }
  
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {
        background-color: #d0d0d0;
    }
"""

# Style for combo boxes
comboBoxStyle = """
    QComboBox {
        background-color: #ffffff;
        border: 1px solid #a0a0a0;
        border-radius: 5px;
        padding: 2px 6px;
        font-size: 14px;
    }
   
    QComboBox:hover {
        border: 1px solid #0053a4;
    }
"""
