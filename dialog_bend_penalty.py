from PySide6.QtWidgets import QDialog, QHBoxLayout, QSlider, QPushButton, QLabel
from PySide6.QtCore import Qt

class BendPenaltyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bend Penalty")
        self.setFixedWidth(400)
        
        self.layout = QHBoxLayout()
        
        self.label = QLabel("0.0")
        self.layout.addWidget(self.label)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(40) # 0 to 4 with one decimal place
        self.slider.setTickInterval(1)
        self.slider.setValue(10)
        self.update_label(10)
        self.slider.valueChanged.connect(self.update_label)
        self.layout.addWidget(self.slider)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)

        self.setLayout(self.layout)

    def update_label(self, value):
        self.label.setText(f"{self.get_value()}")

    def get_value(self):
        return self.slider.value() / 10.0