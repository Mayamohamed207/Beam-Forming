greenColor = "#03efb0"

darkColor = "#2D2D2D"
# darkColor = "#242D5C" #blue
# greenColor = "#2BE7AF" #green

# greenColor="#2BAF7E"
purpleColor="#472B79"
greenColorHover = "#0A6950"

mainStyle = f"""
    QMainWindow, QWidget {{
        background-color: {darkColor};
    }}
    QLabel {{
        color: {greenColor};
        font-weight: bold; /* Optional for emphasis */
    }} 
"""

sliderStyle = f"""
    QSlider::groove:horizontal {{
        background: {greenColor};
        height: 6px;
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: {greenColor};
        border: 1px solid {greenColor};
        width: 12px;
        height: 12px;
        margin: -3px 0;
        border-radius: 6px;
    }}
"""
sliderDisabledStyle = f"""
    QSlider::groove:horizontal {{
        background: lightgray;
        height: 6px;
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: lightgray;
        border: 1px solid lightgray;
        width: 12px;
        height: 12px;
        margin: -3px 0;
        border-radius: 6px;
    }}
"""

groupBoxStyle = f"""
    QGroupBox {{
        border: 2px solid {greenColor};
        border-radius: 10px;
        margin-top: 10px;
        background-color: #d39232;
        padding: 10px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 3px;
        color: {greenColor}; 
        font-weight: bold;
    }}
"""

buttonStyle = f"""
    QPushButton {{
        background-color: {greenColor};
        color: {purpleColor};
        font-weight: bold;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
    }}
    QPushButton:hover {{
        background-color: {greenColorHover};
        color:white;
    }}
"""

spinBoxStyle = f"""
    QSpinBox {{
        background-color: {darkColor};  /* Match the dark color background */
        border: 1px solid {greenColor};  /* Green border */
        border-radius: 5px;
        padding: 2px 6px;
        font-size: 14px;
        color: {greenColor};  /* Green text color */
    }}

    QSpinBox:hover {{
        border: 1px solid {greenColor};  /* Highlight border on hover */
    }}

  

  

"""

comboBoxStyle = f"""
    QComboBox {{
        background-color: {darkColor};  /* Match the dark color background */
        border: 1px solid {greenColor};
        border-radius: 5px;
        padding: 2px 6px;
        font-size: 14px;
        color: {greenColor};  /* Text color matches the green */
    }}
   

    
    QComboBox QAbstractItemView {{
        background-color: {darkColor};  /* Dark background for the dropdown items */
        color: {greenColor};  /* Green text for the dropdown items */
        border: 1px solid {greenColor};  /* Border color for the dropdown list */
    }}

    QComboBox QAbstractItemView::item:hover {{
        background-color: {greenColor};  /* Highlight background when hovering over items */
        color: {darkColor};  /* Change text color to dark on hover */
    }}
"""
