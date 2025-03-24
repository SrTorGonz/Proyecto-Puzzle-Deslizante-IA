from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, 
    QRadioButton, QGroupBox, QGridLayout, QMessageBox, QGraphicsView, QGraphicsScene, QGraphicsTextItem
)
from PyQt6.QtGui import QPixmap, QImage, QFont, QPainter
from PyQt6.QtCore import Qt, QSize, QTimer
import sys


# Función para formatear el estado como una matriz
def format_state_as_matrix(state):
    if state is None:
        return "None"
    return "\n".join([" ".join([str(cell) if cell is not None else " " for cell in row]) for row in state])


class TreeViewer(QWidget):
    def __init__(self, tree_data):
        super().__init__()
        self.tree_data = tree_data
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Árbol de Búsqueda")
        self.setGeometry(100, 100, 1200, 800)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

        # Llamar a draw_tree con un espaciado inicial más pequeño
        self.draw_tree(self.tree_data, 600, 50, self.calculate_tree_width(self.tree_data) * 10)  # Reducir x_offset a 50

    def calculate_tree_width(self, node):
        """
        Calcula el ancho necesario para el subárbol de un nodo.
        """
        if node is None or 'children' not in node or not node['children']:
            return 1  # Si no tiene hijos, el ancho es 1

        width = 0
        for child in node['children']:
            width += self.calculate_tree_width(child)
        return width

    def draw_tree(self, node, x, y, x_offset):
        if node is None:
            return

        # Formatear el estado como una matriz
        state_matrix = format_state_as_matrix(node['state'])

        # Dibujar el nodo actual
        rect = QGraphicsTextItem(state_matrix)
        rect.setFont(QFont("Arial", 8))
        rect.setPos(x, y)
        self.scene.addItem(rect)

        # Dibujar las conexiones con los hijos
        if 'children' in node and node['children']:
            total_width = self.calculate_tree_width(node)  # Ancho total del subárbol
            start_x = x - (total_width * x_offset) / 2  # Centrar los hijos debajo del nodo actual

            for child in node['children']:
                child_width = self.calculate_tree_width(child)  # Ancho del subárbol del hijo
                child_x = start_x + (child_width * x_offset) / 2  # Posición horizontal del hijo
                child_y = y + 100  # Espacio vertical entre niveles (reducido a 100)

                # Dibujar una línea desde el nodo actual al hijo
                self.scene.addLine(x + 40, y + 40, child_x + 40, child_y)

                # Dibujar el subárbol del hijo
                self.draw_tree(child, child_x, child_y, x_offset)

                start_x += child_width * x_offset  # Mover la posición para el siguiente hijo


class PuzzleConfigGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.final_state = None  
        self.max_search_depth = 50  
        self.tree_data = None  # Almacenar el árbol de búsqueda
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Puzzle Deslizante")
        self.setGeometry(100, 100, 600, 700)

        layout = QVBoxLayout()

        self.puzzle_widget = QWidget()
        self.puzzle_grid = QGridLayout(self.puzzle_widget)
        self.puzzle_grid.setSpacing(10)
        self.puzzle_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.size_label = QLabel("Selecciona el tamaño del puzzle:")
        self.size_combo = QComboBox()
        self.size_combo.addItems([f"{i}x{i}" for i in range(3, 10)])
        self.size_combo.currentIndexChanged.connect(self.update_puzzle_display)

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

        self.setup_final_state_button = QPushButton("Definir Estado Final")
        self.setup_final_state_button.clicked.connect(self.save_final_state)

        self.solve_bfs_button = QPushButton("Resolver por Anchura")
        self.solve_bfs_button.clicked.connect(self.solve_puzzle_bfs)

        self.solve_dfs_button = QPushButton("Resolver por Profundidad")
        self.solve_dfs_button.clicked.connect(self.solve_puzzle_dfs)

        self.view_tree_button = QPushButton("Ver Árbol")
        self.view_tree_button.clicked.connect(self.view_tree)

        solve_buttons_layout = QHBoxLayout()
        solve_buttons_layout.addWidget(self.solve_bfs_button)
        solve_buttons_layout.addWidget(self.solve_dfs_button)

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.setup_final_state_button)
        buttons_layout.addLayout(solve_buttons_layout)
        buttons_layout.addWidget(self.view_tree_button)  # Agregar el botón "Ver Árbol"

        layout.addWidget(self.puzzle_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.size_label)
        layout.addWidget(self.size_combo)
        layout.addWidget(self.appearance_group)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        self.update_puzzle_display()

    def solve_puzzle_bfs(self):
        self.solve_puzzle("BFS")

    def solve_puzzle_dfs(self):
        self.solve_puzzle("DFS")

    def update_puzzle_display(self):
        size = int(self.size_combo.currentText().split('x')[0])
        self.size = size
        self.grid_state = [[i * size + j + 1 for j in range(size)] for i in range(size)]
        self.grid_state[size - 1][size - 1] = None  
        self.empty_tile = (size - 1, size - 1)
        self.refresh_puzzle_ui()

    def refresh_puzzle_ui(self):
        for i in reversed(range(self.puzzle_grid.count())):
            self.puzzle_grid.itemAt(i).widget().setParent(None)

        self.tiles = {}
        available_width = min(self.width(), self.height()) - 50
        tile_size = (available_width - (self.size - 1) * 10) // self.size
        font_size = max(10, tile_size // 3)
        use_numbers = self.numbers_radio.isChecked()

        image = QImage("prueba.png") if not use_numbers else None
        piece_width = image.width() // self.size if image else 0
        piece_height = image.height() // self.size if image else 0

        for i in range(self.size):
            for j in range(self.size):
                if self.grid_state[i][j] is None:
                    continue  

                label = QLabel()
                label.setFixedSize(QSize(tile_size, tile_size))
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet(f"background-color: gray; border: 2px solid black; font-size: {font_size}px;")
                
                if use_numbers:
                    label.setText(str(self.grid_state[i][j]))  
                else:
                    num = self.grid_state[i][j] - 1  
                    row, col = divmod(num, self.size)
                    cropped_piece = image.copy(col * piece_width, row * piece_height, piece_width, piece_height)
                    pixmap = QPixmap.fromImage(cropped_piece).scaled(tile_size, tile_size)
                    label.setPixmap(pixmap)
                
                label.mousePressEvent = self.create_mouse_press_event(i, j)
                self.tiles[(i, j)] = label
                self.puzzle_grid.addWidget(label, i, j)

    def create_mouse_press_event(self, x, y):
        def handler(event):
            self.move_tile(x, y)
        return handler

    def move_tile(self, x, y):
        empty_x, empty_y = self.empty_tile
        
        if (abs(x - empty_x) == 1 and y == empty_y) or (abs(y - empty_y) == 1 and x == empty_x):
            self.grid_state[empty_x][empty_y], self.grid_state[x][y] = self.grid_state[x][y], None
            self.empty_tile = (x, y)
            self.refresh_puzzle_ui()

    def save_final_state(self):
        self.final_state = [row[:] for row in self.grid_state]  
        QMessageBox.information(self, "Estado Final Guardado", "El estado final ha sido guardado correctamente.")

    def solve_puzzle(self, algorithm):
        if self.final_state is None:
            QMessageBox.warning(self, "Error", "Primero debe guardar un estado final antes de resolver el puzzle.")
            return

        # Guardar el estado inicial actual
        initial_state = [row[:] for row in self.grid_state]

        # Inicializar la cola con el estado inicial y un nodo raíz
        root_node = {'state': initial_state, 'children': [], 'parent': None}
        queue = [[initial_state, [], root_node]]
        visited = set()

        while queue:
            state, path, node = queue.pop(0) if algorithm == "BFS" else queue.pop()

            if len(path) > self.max_search_depth:
                QMessageBox.warning(self, "Límite de profundidad", "No se encontró solución con profundidad 50")
                return

            if str(state) in visited:
                continue

            visited.add(str(state))

            if state == self.final_state:
                self.animate_solution(path)
                self.tree_data = root_node  # Almacenar el árbol completo
                return

            empty_x, empty_y = [(r, c) for r in range(self.size) for c in range(self.size) if state[r][c] is None][0]

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = empty_x + dx, empty_y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    new_state = [row[:] for row in state]
                    new_state[empty_x][empty_y], new_state[nx][ny] = new_state[nx][ny], None

                    # Crear un nuevo nodo hijo
                    child_node = {'state': new_state, 'children': [], 'parent': node}
                    node['children'].append(child_node)  # Agregar el hijo al nodo actual

                    queue.append([new_state, path + [(nx, ny)], child_node])

    def animate_solution(self, path):
        for i, (x, y) in enumerate(path):
            QTimer.singleShot(i * 250, lambda x=x, y=y: self.move_tile(x, y))

    def view_tree(self):
        if self.tree_data is None:
            QMessageBox.warning(self, "Error", "Primero debe resolver el puzzle para ver el árbol.")
            return

        self.tree_viewer = TreeViewer(self.tree_data)
        self.tree_viewer.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PuzzleConfigGUI()
    window.show()
    sys.exit(app.exec())