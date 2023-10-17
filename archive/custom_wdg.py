from maya import cmds
from maya.api import OpenMaya
from maya import OpenMayaUI
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
from importlib import reload

# https://doc.qt.io/qtforpython-5/PySide2/QtCore/Qt.html#PySide2.QtCore.PySide2.QtCore.Qt.Key

class CustomListWidget(QtWidgets.QListWidget):

    enter_pressed = QtCore.Signal()
    delete_pressed = QtCore.Signal()

    def keyPressEvent(self, e):
        super().keyPressEvent(e)

        if e.key() == QtCore.Qt.Key_Return or e.key() == QtCore.Qt.Key_Enter:
            self.enter_pressed.emit()
        elif e.key() == QtCore.Qt.Key_Delete:
            self.delete_pressed.emit()


class CustomLineEdit(QtWidgets.QLineEdit):

    enter_pressed = QtCore.Signal()

    def keyPressEvent(self, e):
        super().keyPressEvent(e)

        if e.key() == QtCore.Qt.Key_Return or e.key() == QtCore.Qt.Key_Enter:
            self.enter_pressed.emit()