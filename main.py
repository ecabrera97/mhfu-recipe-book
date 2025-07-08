
from PySide6.QtWidgets import QApplication
from core.gui import TransparentCaptureWindow
import pytesseract
import sys


if __name__ == "__main__":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    app = QApplication(sys.argv)
    win = TransparentCaptureWindow()
    win.show()
    sys.exit(app.exec())