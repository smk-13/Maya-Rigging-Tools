from maya import cmds
from maya.api import OpenMaya
from maya import OpenMayaUI
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
from importlib import reload

import ctl.crv
reload(ctl.crv)

import UI.collapsible_wdg
reload(UI.collapsible_wdg)



def maya_main_window():
    maya_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(maya_window_ptr), QtWidgets.QWidget)



class CurveSetDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.setWindowTitle('Curve Sets')
        self.setMaximumWidth(400)
        self.setMinimumWidth(400)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.show()

    def create_widgets(self):
        """ """
        self.comboBox1 = QtWidgets.QComboBox()
        self.comboBox1.setMaxVisibleItems(30)
        self.comboBox1.addItem('Ahsoka Leg', 'ahsoka_leg')
        self.comboBox1.addItem('Ahsoka Arm', 'ahsoka_arm')

        self.editLine1 = QtWidgets.QLineEdit()
        self.editLine1.setPlaceholderText('If not listed in drop down list')

        self.editLine2 = QtWidgets.QLineEdit()
        self.editLine2.setPlaceholderText('select curves and enter a name')

        self.btn_load = QtWidgets.QPushButton('Load')
        self.btn_load.setMaximumWidth(60)

        self.btn_save = QtWidgets.QPushButton('Save')
        self.btn_save.setMaximumWidth(60)

    def create_layouts(self):
        """ """
                #
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        #
        collapsible_wdg1 = UI.collapsible_wdg.CollapsibleWidget('Load Curve Set')
        collapsible_wdg1.setExpanded(True)
        main_layout.addWidget(collapsible_wdg1)

        form_layout = QtWidgets.QFormLayout()
        collapsible_wdg1.addLayout(form_layout)
        form_layout.addRow('Skeleton', self.comboBox1)
        form_layout.addRow('Quick Search', self.editLine1)
        collapsible_wdg1.addWidget(self.btn_load)

        #
        collapsible_wdg2 = UI.collapsible_wdg.CollapsibleWidget('Save Curve Set')
        collapsible_wdg2.setExpanded(True)
        main_layout.addWidget(collapsible_wdg2)

        save_layout = QtWidgets.QHBoxLayout()
        collapsible_wdg2.addLayout(save_layout)
        save_layout.addWidget(self.editLine2)
        save_layout.addWidget(self.btn_save)

    def create_connections(self):
        """ """
        self.btn_load.clicked.connect(self.load_cmd)
        self.btn_save.clicked.connect(self.save_cmd)


    def load_cmd(self):
        """ """
        file_name = self.comboBox1.currentData()
        quick_search = self.editLine1.text()
        if quick_search != '':
            file_name = quick_search

        ctl.crv.create_shape_set_from_lib(file_name=file_name)

    def save_cmd(self):
        """ """
        file_name = self.editLine2.text()
        ctl.crv.save_shape_set_to_lib(file_name=file_name)