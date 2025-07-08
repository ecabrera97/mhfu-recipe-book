from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen
from PIL import Image
from core.extraction import extract_recipes_from_images
from config import logger
from typing import Dict, List
import mss
import json


class RecipesWindow(QWidget):
    def __init__(self, recipes: List[Dict[str, str]]):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setWindowTitle("Detected Recipes")
        self.setGeometry(300, 300, 350, 300)
        self.setMinimumSize(250, 150)

        layout = QVBoxLayout()
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        if not recipes:
            content_layout.addWidget(QLabel("No recipes detected."))
        else:
            for recipe in recipes:
                text = f"<b>{recipe['ingredient1']}</b> + <b>{recipe['ingredient2']}</b> → <span style='color:green'>{recipe['effect']}</span>"
                label = QLabel(text)
                label.setStyleSheet("font-size: 14px; margin: 6px;")
                content_layout.addWidget(label)
        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.setLayout(layout)
        self.show()


class TransparentCaptureWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(200, 200, 400, 300)
        self.setMinimumSize(100, 100)  # Optional: set a minimum size
        self.setMouseTracking(True)
        
        self.resizing = False
        self.resize_direction = None
        self.resize_margin = 8  # Margin in pixels for resize area
        self.counter = 1
        self.counter_min = 1
        self.counter_max = 5
        self.images = list()
        self.drag_pos = None

        self.add_capture_button()
        self.add_empty_images_button()
        self.add_counter_buttons()
        self.add_recipes_button()
        self.add_close_button()

        self.show()

    def add_capture_button(self):
        self.capture_button = QPushButton(f"add (0)", self)
        self.capture_button.setFixedSize(50, 24)
        self.capture_button.move(10, 10)
        self.capture_button.clicked.connect(self.update_capture)

    def add_empty_images_button(self):
        self.empty_images_button = QPushButton("\u2672", self)
        self.empty_images_button.move(60, 10)
        self.empty_images_button.setFixedSize(24, 24)
        self.empty_images_button.clicked.connect(self.empty_images)
        self.empty_images_button.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                color: blue;
                border: none;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: cyan;
            }
        """ )

    def add_recipes_button(self):
        self.recipies_button = QPushButton("recipes", self)
        self.recipies_button.setFixedSize(50, 24)
        self.recipies_button.move(self.width() - 80, 5)
        self.recipies_button.clicked.connect(self.detect_recipes)

    def add_counter_buttons(self):
        self.left_arrow_button = QPushButton("<", self)
        self.left_arrow_button.setFixedSize(24, 24)
        self.left_arrow_button.move(100, 10)
        self.left_arrow_button.setStyleSheet("""
            QPushButton {
                background-color: lightgreen;
                color: green;
                border: none;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: lime;
            }
        """)
        self.left_arrow_button.clicked.connect(self.decrement_counter)

        self.counter_label = QPushButton(str(self.counter), self)
        self.counter_label.setFixedSize(24, 24)
        self.counter_label.move(130, 10)
        self.counter_label.setEnabled(False)
        self.counter_label.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border: 1px solid #008000;
                font-weight: bold;
                border-radius: 5px;
            }
        """)

        self.right_arrow_button = QPushButton(">", self)
        self.right_arrow_button.setFixedSize(24, 24)
        self.right_arrow_button.move(160, 10)
        self.right_arrow_button.setStyleSheet("""
            QPushButton {
                background-color: lightgreen;
                color: green;
                border: none;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: lime;
            }
        """)
        self.right_arrow_button.clicked.connect(self.increment_counter)


    def add_close_button(self):
        self.close_button = QPushButton("X", self)
        self.close_button.setFixedSize(24, 24)
        self.close_button.move(self.width() - 30, 5)
        self.close_button.clicked.connect(QApplication.quit)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                border: none;
                font-weight: bold;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)


    def decrement_counter(self):
        if self.counter > self.counter_min:
            self.counter -= 1
            self.counter_label.setText(str(self.counter))

    def increment_counter(self):
        if self.counter < self.counter_max:
            self.counter += 1
            self.counter_label.setText(str(self.counter))

    def detect_recipes(self):
        if not len(self.images):
            return
        
        recipes = extract_recipes_from_images(self.images, n_chefs=self.counter)
        self.empty_images()
        logger.debug(f"Recipes detected: {json.dumps(recipes, indent=2)}")
        self.w = RecipesWindow(recipes)
        self.w.show()


    def update_capture(self):
        geo = self.geometry()
        x, y, w, h = geo.x(), geo.y(), geo.width(), geo.height()
        with mss.mss() as sct:
            monitor = {"top": y, "left": x, "width": w, "height": h}
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
            self.images.append(img)
        self.capture_button.setText(f"add ({len(self.images)})")

        logger.debug(f"Image capture, there are {len(self.images)} in cache")
        self.update()

    def empty_images(self):
        self.images.clear()
        self.capture_button.setText(f"add (0)")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))
        pen = QPen(QColor(0, 120, 215), 4)
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))

    def resizeEvent(self, event):
        self.recipies_button.move(self.width() - 80, 5)
        self.close_button.move(self.width() - 30, 5)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            direction = self.get_resize_direction(event.pos())
            if direction:
                self.resizing = True
                self.resize_direction = direction
                self.resize_start_pos = event.globalPosition().toPoint()
                self.resize_start_geom = self.geometry()
                event.accept()
            else:
                self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
        else:
            event.accept()

    def mouseMoveEvent(self, event):
        if self.resizing and self.resize_direction:
            diff = event.globalPosition().toPoint() - self.resize_start_pos
            geom = self.resize_start_geom
            min_w, min_h = self.minimumWidth(), self.minimumHeight()
            x, y, w, h = geom.x(), geom.y(), geom.width(), geom.height()
            dx, dy = diff.x(), diff.y()
            direction = self.resize_direction
            if 'right' in direction:
                w = max(geom.width() + dx, min_w)
            if 'bottom' in direction:
                h = max(geom.height() + dy, min_h)
            if 'left' in direction:
                new_w = max(geom.width() - dx, min_w)
                x = geom.x() + (geom.width() - new_w)
                w = new_w
            if 'top' in direction:
                new_h = max(geom.height() - dy, min_h)
                y = geom.y() + (geom.height() - new_h)
                h = new_h
            self.setGeometry(x, y, w, h)
            event.accept()
        elif event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()
        else:
            direction = self.get_resize_direction(event.pos())
            cursor = Qt.ArrowCursor
            if direction == 'right' or direction == 'left':
                cursor = Qt.SizeHorCursor
            elif direction == 'bottom' or direction == 'top':
                cursor = Qt.SizeVerCursor
            elif direction in ('bottomright', 'topleft'):
                cursor = Qt.SizeFDiagCursor
            elif direction in ('bottomleft', 'topright'):
                cursor = Qt.SizeBDiagCursor
            self.setCursor(cursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.resizing:
            self.resizing = False
            self.resize_direction = None
            self.setCursor(Qt.ArrowCursor)
            event.accept()

    def get_resize_direction(self, pos):
        margin = self.resize_margin
        right = pos.x() >= self.width() - margin
        left = pos.x() <= margin
        bottom = pos.y() >= self.height() - margin
        top = pos.y() <= margin
        if left and top:
            return 'topleft'
        if right and bottom:
            return 'bottomright'
        if left and bottom:
            return 'bottomleft'
        if right and top:
            return 'topright'
        if left:
            return 'left'
        if right:
            return 'right'
        if top:
            return 'top'
        if bottom:
            return 'bottom'
        return None


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = TransparentCaptureWindow()
    sys.exit(app.exec())