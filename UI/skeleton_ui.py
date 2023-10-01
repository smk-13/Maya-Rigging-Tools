from maya import cmds
from maya.api import OpenMaya
from maya import OpenMayaUI
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
from importlib import reload

import skel.skel_utils
reload(skel.skel_utils)

import UI.collapsible_wdg
reload(UI.collapsible_wdg)




def maya_main_window():
    maya_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(maya_window_ptr), QtWidgets.QWidget)



class SkeletonDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.setWindowTitle('Skeleton')
        self.setMaximumWidth(400)
        self.setMinimumWidth(400)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.show()

    def create_widgets(self):

        self.skelComboBox = QtWidgets.QComboBox()
        self.skelComboBox.setMaxVisibleItems(30)
        self.skelComboBox.addItem('test1', 'test1')
        self.skelComboBox.addItem('test2', 'test2')

        self.customSkelLine = QtWidgets.QLineEdit()
        self.customSkelLine.setPlaceholderText('If not listed in drop down list')

        self.newSkelLine = QtWidgets.QLineEdit()
        self.newSkelLine.setPlaceholderText('select joints and give a name')

        self.btn_load = QtWidgets.QPushButton('Load')
        self.btn_load.setMaximumWidth(60)

        self.btn_save = QtWidgets.QPushButton('Save')
        self.btn_save.setMaximumWidth(60)


    def create_layouts(self):
        
        #
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        #
        collapsible_wdg1 = UI.collapsible_wdg.CollapsibleWidget('Load Skeleton')
        collapsible_wdg1.setExpanded(True)
        main_layout.addWidget(collapsible_wdg1)

        form_layout = QtWidgets.QFormLayout()
        collapsible_wdg1.addLayout(form_layout)
        form_layout.addRow('Skeleton', self.skelComboBox)
        form_layout.addRow('Quick Search', self.customSkelLine)
        collapsible_wdg1.addWidget(self.btn_load)

        #
        collapsible_wdg2 = UI.collapsible_wdg.CollapsibleWidget('Save Skeleton')
        collapsible_wdg2.setExpanded(True)
        main_layout.addWidget(collapsible_wdg2)

        save_layout = QtWidgets.QHBoxLayout()
        collapsible_wdg2.addLayout(save_layout)
        save_layout.addWidget(self.newSkelLine)
        save_layout.addWidget(self.btn_save)


    def create_connections(self):
        """ """
        self.btn_load.clicked.connect(self.load_cmd)
        self.btn_save.clicked.connect(self.save_cmd)

    def load_cmd(self):
        """ """
        skel_name = self.skelComboBox.currentData()
        custom_skel = self.customSkelLine.text()
        if custom_skel != '':
            skel_name = custom_skel

        skeleton_data = skel.skel_utils.create_skeleton_from_lib(file_name=skel_name)

    def save_cmd(self):
        """ """
        file_name = self.newSkelLine.text()
        skel.skel_utils.save_to_lib(file_name=file_name, joints=None)