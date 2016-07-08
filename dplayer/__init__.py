import sys
from PyQt5.QtWidgets import QApplication
from ui import DPlayerUI

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = DPlayerUI()
    sys.exit(app.exec_())
