from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, 
    QRadioButton, QGroupBox, QGridLayout, QMessageBox, QGraphicsView, QGraphicsScene, QGraphicsTextItem
)
from PyQt6.QtGui import QPixmap, QImage, QFont, QPainter
from PyQt6.QtGui import QPen, QBrush, QPainterPath, QColor
from PyQt6.QtCore import Qt, QSize, QTimer
import sys
import os

# Función para formatear el estado como una matriz
def format_state_as_matrix(state):
    if state is None:
        return "None"
    return "\n".join([" ".join([str(cell) if cell is not None else " " for cell in row]) for row in state])

    

from PyQt6.QtGui import QColor  # Añade esto al inicio con las otras importaciones

class TreeViewer(QWidget):
    def __init__(self, tree_data, puzzle_size, final_state):
        super().__init__()
        self.tree_data = tree_data
        self.puzzle_size = puzzle_size
        self.final_state = final_state
        
        # Configuración de tamaños ajustada
        self.base_cell_size = 30  # Aumentamos el tamaño base
        self.cell_size = max(20, self.base_cell_size - (self.puzzle_size - 3) * 2)  # Reducción más gradual
        self.node_width = self.cell_size * (self.puzzle_size + 2)  # Más espacio horizontal
        self.node_height = self.cell_size * (self.puzzle_size + 1)  # Más espacio vertical
        self.horizontal_spacing = self.node_width * 0.8
        self.vertical_spacing = self.node_height * 2.0
        
        # Variables para panning
        self.pan_start = None
        self.panning = False
        
        self.node_info = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Árbol de Búsqueda (Arrastrar con clic izquierdo)")
        self.setGeometry(100, 100, 1200, 900)
        
        self.scene = QGraphicsScene()
        self.view = CustomGraphicsView(self.scene, self)
        self.view.setRenderHints(QPainter.RenderHint.Antialiasing | 
                               QPainter.RenderHint.TextAntialiasing |
                               QPainter.RenderHint.SmoothPixmapTransform)
        
        # Configuración de scroll
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
        
        self.draw_tree()
        
        # Ajuste inicial de la vista
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event):
        """Zoom con la rueda del mouse"""
        zoom_factor = 1.2
        if event.angleDelta().y() > 0:
            self.view.scale(zoom_factor, zoom_factor)
        else:
            self.view.scale(1/zoom_factor, 1/zoom_factor)

    def mousePressEvent(self, event):
        """Iniciar panning"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.pan_start = event.pos()
            self.panning = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Mover la vista durante panning"""
        if self.panning and self.pan_start:
            delta = event.pos() - self.pan_start
            self.pan_start = event.pos()
            
            # Mover la barra de scroll
            h_bar = self.view.horizontalScrollBar()
            v_bar = self.view.verticalScrollBar()
            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Finalizar panning"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)

    def draw_tree(self):
        if not self.tree_data:
            return
            
        # Calcular estructura del árbol
        levels = {}
        max_level_width = 0
        queue = [(self.tree_data, 0)]
        
        while queue:
            node, level = queue.pop(0)
            if level not in levels:
                levels[level] = []
            levels[level].append(node)
            
            for child in node.get('children', []):
                queue.append((child, level + 1))
        
        # Calcular dimensiones totales con más margen
        max_level_width = max(len(nodes) for nodes in levels.values())
        total_height = len(levels) * self.vertical_spacing + 200
        total_width = max_level_width * (self.node_width + self.horizontal_spacing) + 200
        
        self.scene.setSceneRect(-50, -50, total_width, total_height)
        
        # Dibujar nodos con espaciado vertical aumentado
        for level, nodes in levels.items():
            y = 50 + level * self.vertical_spacing
            level_width = len(nodes) * self.node_width + (len(nodes) - 1) * self.horizontal_spacing
            start_x = (total_width - level_width) / 2
            
            for i, node in enumerate(nodes):
                x = start_x + i * (self.node_width + self.horizontal_spacing)
                self.draw_node(node, x, y)
                self.node_info[id(node)] = {
                    'x': x,
                    'y': y,
                    'width': self.node_width,
                    'height': self.node_height
                }
        
        # Dibujar conexiones más largas
        for level, nodes in levels.items():
            for node in nodes:
                if 'children' in node:
                    for child in node['children']:
                        if id(child) in self.node_info:
                            self.draw_connection(node, child)

    def draw_node(self, node, x, y):
        state = node.get('state', [])
        is_final = state == self.final_state
        
        # Colores mejorados
        node_color = QColor(180, 255, 180) if is_final else QColor(240, 240, 240)
        border_color = QColor(0, 100, 0) if is_final else QColor(80, 80, 80)
        
        # Rectángulo con bordes redondeados
        path = QPainterPath()
        radius = 5
        path.addRoundedRect(x, y, self.node_width, self.node_height, radius, radius)
        self.scene.addPath(
            path,
            QPen(border_color, 1.2),
            QBrush(node_color)
        )
        
        if state:
            # Texto mejorado
            font_size = max(8, 12 - int(self.puzzle_size/2))
            font = QFont("Courier New", font_size)
            font.setStyleHint(QFont.StyleHint.Monospace)
            
            # Formato compacto
            max_num = self.puzzle_size * self.puzzle_size
            cell_width = len(str(max_num))
            matrix_text = "\n".join(
                " ".join(f"{cell:>{cell_width}}" if cell is not None else " " * cell_width 
                        for cell in row)
                for row in state
            )
            
            text_item = QGraphicsTextItem(matrix_text)
            text_item.setFont(font)
            text_item.setDefaultTextColor(Qt.GlobalColor.black)
            
            # Centrado mejorado
            text_rect = text_item.boundingRect()
            text_x = x + (self.node_width - text_rect.width()) / 2
            text_y = y + (self.node_height - text_rect.height()) / 2
            
            text_item.setPos(text_x, text_y)
            self.scene.addItem(text_item)

    def draw_connection(self, parent_node, child_node):
        parent_info = self.node_info[id(parent_node)]
        child_info = self.node_info[id(child_node)]
        
        x1 = parent_info['x'] + parent_info['width'] / 2
        y1 = parent_info['y'] + parent_info['height']
        x2 = child_info['x'] + child_info['width'] / 2
        y2 = child_info['y']
        
        # Línea de conexión más visible
        line = self.scene.addLine(x1, y1, x2, y2, QPen(Qt.GlobalColor.white, 1.2))


class CustomGraphicsView(QGraphicsView):
    """Clase personalizada para mejor manejo de eventos"""
    def __init__(self, scene, parent):
        super().__init__(scene)
        self.parent_viewer = parent
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent_viewer.mousePressEvent(event)
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        if self.parent_viewer.panning:
            self.parent_viewer.mouseMoveEvent(event)
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent_viewer.mouseReleaseEvent(event)
        super().mouseReleaseEvent(event)
        


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

        if not use_numbers:
        # Ruta compatible con PyInstaller y desarrollo
            if getattr(sys, 'frozen', False):
                # Si está empaquetado (.exe), la imagen está en la carpeta temporal
                base_path = sys._MEIPASS
            else:
                # Si es el script .py, usa la ruta local
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            image_path = os.path.join(base_path, "prueba.png")
            
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"No se encontró la imagen en: {image_path}")
            
            image = QImage(image_path)
        else:
            image = None

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

        initial_state = [row[:] for row in self.grid_state]
        root_node = {'state': initial_state, 'children': [], 'parent': None, 'depth': 0}
        queue = [[initial_state, [], root_node]]
        visited = set()
        solution_depth = None  # Almacenará la profundidad donde se encontró la solución

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
                solution_depth = node['depth']
                self.tree_data = root_node
                break  # Salir del bucle cuando se encuentra la solución

            empty_x, empty_y = [(r, c) for r in range(self.size) for c in range(self.size) if state[r][c] is None][0]

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = empty_x + dx, empty_y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    new_state = [row[:] for row in state]
                    new_state[empty_x][empty_y], new_state[nx][ny] = new_state[nx][ny], None

                    child_node = {
                        'state': new_state, 
                        'children': [], 
                        'parent': node,
                        'depth': node['depth'] + 1
                    }
                    node['children'].append(child_node)
                    queue.append([new_state, path + [(nx, ny)], child_node])

        # Solo para BFS: eliminar nodos un nivel después de la solución
        if algorithm == "BFS" and solution_depth is not None:
            self.prune_bfs_tree(root_node, solution_depth)



    def prune_bfs_tree(self, root_node, solution_depth):
        """Elimina solo los nodos que están exactamente un nivel después del nivel de solución"""
        from collections import deque
        
        queue = deque()
        queue.append(root_node)
        
        while queue:
            current_node = queue.popleft()
            
            # Si estamos en el nivel de solución, eliminamos todos sus hijos
            if current_node['depth'] == solution_depth:
                current_node['children'] = []
            else:
                # Si no, seguimos explorando los hijos
                for child in current_node['children']:
                    queue.append(child)


    def animate_solution(self, path):
        for i, (x, y) in enumerate(path):
            QTimer.singleShot(i * 250, lambda x=x, y=y: self.move_tile(x, y))

    def view_tree(self):
        if self.tree_data is None:
            QMessageBox.warning(self, "Error", "Primero debe resolver el puzzle para ver el árbol.")
            return

        puzzle_size = int(self.size_combo.currentText().split('x')[0])
        self.tree_viewer = TreeViewer(self.tree_data, puzzle_size, self.final_state)
        self.tree_viewer.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PuzzleConfigGUI()
    window.show()
    sys.exit(app.exec())