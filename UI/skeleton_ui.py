from maya import cmds
from maya.api import OpenMaya
from maya import OpenMayaUI
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
from importlib import reload
import os

import utils.helper
reload(utils.helper)

import skel.skel_utils
reload(skel.skel_utils)

import UI.collapsible_wdg
reload(UI.collapsible_wdg)

import UI.dropdown_config_utils
reload(UI.dropdown_config_utils)

import UI.deco_lib
reload(UI.deco_lib)


def maya_main_window():
    maya_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(maya_window_ptr), QtWidgets.QWidget)



class SkeletonDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.lra_next = 1

        self.setWindowTitle('Skeleton')
        self.setMaximumWidth(450)
        self.setMinimumWidth(450)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.show()

    def create_widgets(self):

        self.skelComboBox = QtWidgets.QComboBox()
        self.skelComboBox.setMaxVisibleItems(30)

        drop_down_dict = UI.dropdown_config_utils.get_lib_data(file_name='skeleton_dropdown')
        for label, file_name in drop_down_dict.items():
            self.skelComboBox.addItem(label, file_name)

        self.customSkelLine = QtWidgets.QLineEdit()
        self.customSkelLine.setPlaceholderText('If not listed in drop down list')

        self.newSkelLine = QtWidgets.QLineEdit()
        self.newSkelLine.setPlaceholderText('select joints and enter a name')

        self.btn_load = QtWidgets.QPushButton('Load')
        self.btn_load.setMaximumWidth(60)

        self.btn_save = QtWidgets.QPushButton('Save')
        self.btn_save.setMaximumWidth(60)

        self.btn_lib = QtWidgets.QPushButton('Library')
        self.btn_lib.setMaximumWidth(60)

        self.btn_config = QtWidgets.QPushButton('Config')
        self.btn_config.setMaximumWidth(60)




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
        save_layout.addWidget(self.btn_lib)
        save_layout.addWidget(self.btn_config)


    

    def create_connections(self):
        """ """
        self.btn_load.clicked.connect(self.load_cmd)
        self.btn_save.clicked.connect(self.save_cmd)
        self.btn_lib.clicked.connect(self.open_lib_folder_cmd)
        self.btn_config.clicked.connect(self.open_dropdown_config_file_cmd)

    @UI.deco_lib.d_undoable
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

        # error checking
        if file_name == '':
            OpenMaya.MGlobal.displayInfo('no name assigned')
            return
        sel = cmds.ls(sl=True)
        if len(sel) == 0:
            OpenMaya.MGlobal.displayInfo('nothing selected')
            return
        else:
            for s in sel:
                if cmds.objectType(s) != 'joint':
                    OpenMaya.MGlobal.displayInfo('at least one selected object is not a joint')
                    return

        skel.skel_utils.save_to_lib(file_name=file_name, joints=None)

    def open_lib_folder_cmd(self):
        """ """
        lib_dir = skel.skel_utils.SKELETON_LIBRARY_PATH
        os.startfile(lib_dir)

    def open_dropdown_config_file_cmd(self):
        """ """
        config_file = UI.dropdown_config_utils.DROPDOWN_CONFIGS_PATH + '\\skeleton_dropdown.json'
        os.startfile(config_file)
