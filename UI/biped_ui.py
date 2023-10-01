from maya import cmds
from maya.api import OpenMaya
from maya import OpenMayaUI
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
from importlib import reload

import utils.helper
reload(utils.helper)

import ctl.ctrl
reload(ctl.ctrl)

import UI.collapsible_wdg
reload(UI.collapsible_wdg)

import biped.master
reload(biped.master)


def maya_main_window():
    maya_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(maya_window_ptr), QtWidgets.QWidget)



class BipedDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.setWindowTitle('Biped')
        self.setMaximumWidth(400)
        self.setMinimumWidth(400)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.show()


    def create_widgets(self):
        """ """
        self.master_btn = QtWidgets.QPushButton('Create Master')

    def create_layouts(self):
        """ """

        # main and collapsible widgets
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        collapsible_wdg1 = UI.collapsible_wdg.CollapsibleWidget('Master')
        collapsible_wdg2 = UI.collapsible_wdg.CollapsibleWidget('Leg')
        collapsible_wdg3 = UI.collapsible_wdg.CollapsibleWidget('Arm')
        collapsible_wdg4 = UI.collapsible_wdg.CollapsibleWidget('Spine')
        collapsible_wdg1.setExpanded(True)
        collapsible_wdg2.setExpanded(False)
        collapsible_wdg3.setExpanded(False)
        collapsible_wdg4.setExpanded(False)

        main_layout.addWidget(collapsible_wdg1)
        main_layout.addWidget(collapsible_wdg2)
        main_layout.addWidget(collapsible_wdg3)
        main_layout.addWidget(collapsible_wdg4)

        # add widgets
        collapsible_wdg1.addWidget(self.master_btn)


    def create_connections(self):
        """ """
        self.master_btn.clicked.connect(biped.master.Master)



