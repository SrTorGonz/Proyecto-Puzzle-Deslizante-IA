from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QRadioButton, QGroupBox, QGridLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize
import sys

class PuzzleConfigGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Puzzle Deslizante")
        self.setGeometry(100, 100, 600, 700)

        layout = QVBoxLayout()

        # Mostrar el puzzle con un layout fijo
        self.puzzle_widget = QWidget()
        self.puzzle_grid = QGridLayout(self.puzzle_widget)
        self.puzzle_grid.setSpacing(10)  # Espaciado fijo entre celdas
        self.puzzle_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Selección del tamaño del puzzle
        self.size_label = QLabel("Selecciona el tamaño del puzzle:")
        self.size_combo = QComboBox()
        self.size_combo.addItems([f"{i}x{i}" for i in range(3, 10)])
        self.size_combo.currentIndexChanged.connect(self.update_puzzle_display)

        # Selección de tipo de ficha
        self.appearance_group = QGroupBox("Apariencia de las fichas")
        appearance_layout = QVBoxLayout()
        self.numbers_radio = QRadioButton("Números")
        self.image_radio = QRadioButton("Imagen")
        self.numbers_radio.setChecked(True)

        appearance_layout.addWidget(self.numbers_radio)
        appearance_layout.addWidget(self.image_radio)
        self.appearance_group.setLayout(appearance_layout)

        self.numbers_radio.toggled.connect(self.update_puzzle_display)
        self.image_radio.toggled.connect(self.update_puzzle_display)
        
        # Botones para definir estados
        self.setup_initial_state_button = QPushButton("Definir Estado Inicial")
        self.setup_final_state_button = QPushButton("Definir Estado Final")

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.setup_initial_state_button)
        buttons_layout.addWidget(self.setup_final_state_button)
        
        # Añadir elementos al layout
        layout.addWidget(self.puzzle_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.size_label)
        layout.addWidget(self.size_combo)
        layout.addWidget(self.appearance_group)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        self.update_puzzle_display()

    def update_puzzle_display(self):
        """Actualiza la visualización del puzzle manteniendo proporciones y dejando un hueco."""
        for i in reversed(range(self.puzzle_grid.count())):
            self.puzzle_grid.itemAt(i).widget().setParent(None)
        
        size = int(self.size_combo.currentText().split('x')[0])
        use_numbers = self.numbers_radio.isChecked()
        available_width = min(self.width(), self.height()) - 50  # Asegurar cuadrícula dentro de la ventana
        tile_size = (available_width - (size - 1) * 10) // size if size > 0 else 50  # Ajustar tamaño dinámico
        font_size = max(10, tile_size // 3)  # Ajustar tamaño del número según el tile
        
        for i in range(size):
            for j in range(size):
                if i == size - 1 and j == size - 1:
                    continue  # Dejar la última posición vacía
                
                label = QLabel()
                label.setFixedSize(QSize(tile_size, tile_size))
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet(f"background-color: gray; border: 2px solid black; font-size: {font_size}px;")
                
                if use_numbers:
                    label.setText(str(i * size + j + 1))
                else:
                    image = QPixmap("prueba.png").scaled(tile_size, tile_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    label.setPixmap(image)
                
                self.puzzle_grid.addWidget(label, i, j)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PuzzleConfigGUI()
    window.show()
    sys.exit(app.exec())