from maya import cmds
from maya.api import OpenMaya
from maya import OpenMayaUI
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance
from importlib import reload




def maya_main_window():
    maya_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(maya_window_ptr), QtWidgets.QWidget)


class CollapsibleHeader(QtWidgets.QWidget):

    COLLAPSED_PIXMAP = QtGui.QPixmap(':teRightArrow.png')
    EXPANDED_PIXMAP = QtGui.QPixmap(':teDownArrow.png')

    clicked = QtCore.Signal()

    def __init__(self, text, parent=None):
        super().__init__(parent)

        self.setAutoFillBackground(True)
        self.setBackgroundColor(None)

        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedWidth(self.COLLAPSED_PIXMAP.width())

        self.text_label = QtWidgets.QLabel()
        self.text_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(4,4,4,4)
        self.main_layout.addWidget(self.icon_label)
        self.main_layout.addWidget(self.text_label)

        self.setText(text)
        self.setExpanded(False)

    def setText(self, text):
        self.text_label.setText(f'<b>{text}</b>')

    def setBackgroundColor(self, color):
        if color is None:
            color = QtWidgets.QPushButton().palette().color(QtGui.QPalette.Button)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, color)
        self.setPalette(palette)

    def isExpanded(self):
        return self._expanded

    def setExpanded(self, expanded):
        self._expanded = expanded
        self.icon_label.setPixmap(self.EXPANDED_PIXMAP) if self._expanded else self.icon_label.setPixmap(self.COLLAPSED_PIXMAP)

    def mouseReleaseEvent(self, event):
        self.clicked.emit()


class CollapsibleWidget(QtWidgets.QWidget):

    def __init__(self, text, parent=None):
        super().__init__(parent)

        self.header_wdg = CollapsibleHeader(text)
        self.header_wdg.setFixedHeight(20)
        self.header_wdg.clicked.connect(self.on_header_clicked)

        self.body_wdg = QtWidgets.QWidget()

        self.body_layout = QtWidgets.QVBoxLayout(self.body_wdg)
        self.body_layout.setContentsMargins(2,2,2,2)
        self.body_layout.setSpacing(6)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.addWidget(self.header_wdg)
        self.main_layout.addWidget(self.body_wdg)

        self.setExpanded(False)

    def setHeaderBackgroundColor(self, color):
        self.header_wdg.setBackgroundColor(color)

    def addWidget(self, widget):  # to comply with the regular Qt notation
        self.body_layout.addWidget(widget)

    def addLayout(self, layout):
        self.body_layout.addLayout(layout)

    def setExpanded(self, expanded):
        self.header_wdg.setExpanded(expanded)
        self.body_wdg.setVisible(expanded)

    def on_header_clicked(self):
        self.setExpanded(not self.header_wdg.isExpanded())


class TestDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.setWindowTitle('Test')
        # self.setMinimumWidth(300)
        self.setMinimumSize(200, 200)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.collapsible_wdg1 = CollapsibleWidget('Section A')
        self.collapsible_wdg2 = CollapsibleWidget('Section B')

        for i in range(5):
            self.collapsible_wdg1.addWidget(QtWidgets.QPushButton(f'{i}'))

        for i in range(5):
            self.collapsible_wdg2.addWidget(QtWidgets.QCheckBox(f'{i}'))

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.collapsible_wdg1)
        self.main_layout.addWidget(self.collapsible_wdg2)
        self.main_layout.setAlignment(QtCore.Qt.AlignTop) ###

        # self.body_scroll_area = QtWidgets.QScrollArea()
        # self.body_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        # self.body_scroll_area.setWidgetResizeable(True)
        # self.body_scroll_area.setWidget(self.body_wdg)

    def create_connections(self):
        pass