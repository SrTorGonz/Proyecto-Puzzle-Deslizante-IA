from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QRadioButton, QGroupBox, QGridLayout
from PyQt6.QtGui import QPixmap, QImage
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
        self.puzzle_grid.setSpacing(10)
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
        
        # Botón para definir estado final
        self.setup_final_state_button = QPushButton("Definir Estado Final")

        # Botones para resolver el puzzle en una misma línea
        self.solve_bfs_button = QPushButton("Resolver por Anchura")
        self.solve_dfs_button = QPushButton("Resolver por Profundidad")
        solve_buttons_layout = QHBoxLayout()
        solve_buttons_layout.addWidget(self.solve_bfs_button)
        solve_buttons_layout.addWidget(self.solve_dfs_button)
        
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.setup_final_state_button)
        buttons_layout.addLayout(solve_buttons_layout)
        
        # Añadir elementos al layout
        layout.addWidget(self.puzzle_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.size_label)
        layout.addWidget(self.size_combo)
        layout.addWidget(self.appearance_group)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        self.update_puzzle_display()

    def update_puzzle_display(self):
        """Inicializa la matriz del puzzle y la interfaz gráfica."""
        size = int(self.size_combo.currentText().split('x')[0])
        self.size = size
        self.grid_state = [[(i, j) for j in range(size)] for i in range(size)]
        self.grid_state[size - 1][size - 1] = None  # Última posición vacía

        self.empty_tile = (size - 1, size - 1)  # Última posición vacía

        self.refresh_puzzle_ui()

    def refresh_puzzle_ui(self):
        """Limpia y redibuja la interfaz gráfica del puzzle según `self.grid_state`."""
        # Limpiar el grid anterior
        for i in reversed(range(self.puzzle_grid.count())):
            self.puzzle_grid.itemAt(i).widget().setParent(None)

        self.tiles = {}
        available_width = min(self.width(), self.height()) - 50
        tile_size = (available_width - (self.size - 1) * 10) // self.size if self.size > 0 else 50
        font_size = max(10, tile_size // 3)
        use_numbers = self.numbers_radio.isChecked()

        image = QImage("prueba.png") if not use_numbers else None
        piece_width = image.width() // self.size if image else 0
        piece_height = image.height() // self.size if image else 0

        for i in range(self.size):
            for j in range(self.size):
                if self.grid_state[i][j] is None:
                    continue  # Espacio vacío
                
                label = QLabel()
                label.setFixedSize(QSize(tile_size, tile_size))
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet(f"background-color: gray; border: 2px solid black; font-size: {font_size}px;")

                if use_numbers:
                    label.setText(str(self.grid_state[i][j][0] * self.size + self.grid_state[i][j][1] + 1))
                else:
                    original_x, original_y = self.grid_state[i][j]
                    cropped_piece = image.copy(original_y * piece_width, original_x * piece_height, piece_width, piece_height)
                    pixmap = QPixmap.fromImage(cropped_piece).scaled(tile_size, tile_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    label.setPixmap(pixmap)
                
                label.mousePressEvent = self.create_mouse_press_event(i, j)
                self.tiles[(i, j)] = label
                self.puzzle_grid.addWidget(label, i, j)

    def create_mouse_press_event(self, x, y):
        """Crea un evento de clic para mover la ficha."""
        def handler(event):
            self.move_tile(x, y)
        return handler

    def move_tile(self, x, y):
        """Mueve una ficha si hay un espacio vacío adyacente y actualiza la cuadrícula correctamente."""
        empty_x, empty_y = self.empty_tile
        
        # Verificar si la ficha clicada está adyacente al espacio vacío
        if (abs(x - empty_x) == 1 and y == empty_y) or (abs(y - empty_y) == 1 and x == empty_x):
            # Intercambiar posiciones en `grid_state`
            self.grid_state[empty_x][empty_y], self.grid_state[x][y] = self.grid_state[x][y], None

            # Actualizar la posición del espacio vacío
            self.empty_tile = (x, y)

            # Redibujar la interfaz
            self.refresh_puzzle_ui()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PuzzleConfigGUI()
    window.show()
    sys.exit(app.exec())
