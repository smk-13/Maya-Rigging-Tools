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

import ctl.crv
reload(ctl.crv)

import UI.collapsible_wdg
reload(UI.collapsible_wdg)

import UI.dropdown_config_utils
reload(UI.dropdown_config_utils)

import UI.deco_lib
reload(UI.deco_lib)




def maya_main_window():
    maya_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(maya_window_ptr), QtWidgets.QWidget)



class CurveDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.setWindowTitle('Curve Designer')
        self.setMaximumWidth(450)
        self.setMinimumWidth(450)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.show()


    def create_widgets(self):

        self.shapesComboBox = QtWidgets.QComboBox()
        self.shapesComboBox.setMaxVisibleItems(30)

        drop_down_dict = UI.dropdown_config_utils.get_lib_data(file_name='curves_dropdown')
        for label, file_name in drop_down_dict.items():
            self.shapesComboBox.addItem(label, file_name)


        # scale
        self.scaleSpinBox = QtWidgets.QDoubleSpinBox()
        self.scaleSpinBox.setValue(1.0)
        self.scaleSpinBox.setRange(-99, 99)
        self.scaleSpinBox.setSingleStep(1.0)
        self.scaleSpinBox.setValue(1)

        # color
        self.colorSpinBox = QtWidgets.QSpinBox()
        self.colorSpinBox.setRange(0, 31)
        self.colorSpinBox.setValue(13)

        self.customShapeLine = QtWidgets.QLineEdit()
        self.customShapeLine.setPlaceholderText('If not listed in drop down list')

        self.newShapeLine = QtWidgets.QLineEdit()
        self.newShapeLine.setPlaceholderText('Select curve and enter a name')

        self.btn_run = QtWidgets.QPushButton('Create')
        self.btn_run.setMaximumWidth(60)

        self.btn_save = QtWidgets.QPushButton('Save')
        self.btn_save.setMaximumWidth(60)

        self.btn_lib = QtWidgets.QPushButton('Library')
        self.btn_lib.setMaximumWidth(60)

        self.btn_config = QtWidgets.QPushButton('Config')
        self.btn_config.setMaximumWidth(60)

        self.red_btn = QtWidgets.QPushButton('Red')
        self.blue_btn = QtWidgets.QPushButton('Blue')
        self.green_btn = QtWidgets.QPushButton('Green')
        self.yellow_btn = QtWidgets.QPushButton('Yellow')
        self.cyan_btn = QtWidgets.QPushButton('Cyan')

        self.combine_btn = QtWidgets.QPushButton('combine selected curves under the first selected')


    def create_layouts(self):
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        collapsible_wdg_create = UI.collapsible_wdg.CollapsibleWidget('Create new curve')
        collapsible_wdg_save = UI.collapsible_wdg.CollapsibleWidget('Save to Library')
        collapsible_wdg_modify = UI.collapsible_wdg.CollapsibleWidget('Modify curve')
        collapsible_wdg_create.setExpanded(True)
        collapsible_wdg_save.setExpanded(True)
        collapsible_wdg_modify.setExpanded(True)

        main_layout.addWidget(collapsible_wdg_create)
        main_layout.addWidget(collapsible_wdg_save)
        main_layout.addWidget(collapsible_wdg_modify)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow('Shape', self.shapesComboBox)
        form_layout.addRow('Quick Search', self.customShapeLine)
        form_layout.addRow('Scale', self.scaleSpinBox)
        form_layout.addRow('Color Index', self.colorSpinBox)

        btn_run_layout = QtWidgets.QHBoxLayout()
        btn_run_layout.addWidget(self.btn_run)
        btn_run_layout.addStretch()

        new_curve_layout = QtWidgets.QHBoxLayout()
        new_curve_layout.addWidget(self.newShapeLine)
        new_curve_layout.addWidget(self.btn_save)

        new_curve_layout.addWidget(self.btn_lib)
        new_curve_layout.addWidget(self.btn_config)

        color_layout = QtWidgets.QHBoxLayout()
        color_layout.addWidget(self.red_btn)
        color_layout.addWidget(self.blue_btn)
        color_layout.addWidget(self.green_btn)
        color_layout.addWidget(self.yellow_btn)
        color_layout.addWidget(self.cyan_btn)

        btn_combine_layout = QtWidgets.QHBoxLayout()
        btn_combine_layout.addWidget(self.combine_btn)

        collapsible_wdg_create.addLayout(form_layout)
        collapsible_wdg_create.addLayout(btn_run_layout)
        collapsible_wdg_save.addLayout(new_curve_layout)
        collapsible_wdg_modify.addLayout(color_layout)
        collapsible_wdg_modify.addLayout(btn_combine_layout)




    def create_connections(self):
        """ """
        self.btn_run.clicked.connect(self.create_control_cmd)
        self.btn_save.clicked.connect(self.save_to_library_cmd)
        self.btn_lib.clicked.connect(self.open_lib_folder_cmd)
        self.btn_config.clicked.connect(self.open_dropdown_config_file_cmd)

        self.red_btn.clicked.connect(lambda: self.color_curve_cmd(13))
        self.blue_btn.clicked.connect(lambda: self.color_curve_cmd(6))
        self.yellow_btn.clicked.connect(lambda: self.color_curve_cmd(22))
        self.cyan_btn.clicked.connect(lambda: self.color_curve_cmd(18))
        self.green_btn.clicked.connect(lambda: self.color_curve_cmd(14))

        self.combine_btn.clicked.connect(self.combine_curves_cmd)


    @UI.deco_lib.d_undoable
    def create_control_cmd(self):
        """ """
        orig_sel = cmds.ls(sl=True, type='transform')

        new_name = utils.helper.create_unique_name(base_name='new_curve')

        shape = self.shapesComboBox.currentData()
        custom_shape = self.customShapeLine.text()
        if custom_shape != '':
            shape = custom_shape

        crv = ctl.crv.create_new_curve_from_lib(name=new_name, file_name=shape)

        # scale
        scale = self.scaleSpinBox.value()
        cmds.xform(f'{crv}.cv[*]', os=True, r=True, scale=(scale, scale, scale))

        # color
        color = self.colorSpinBox.value()
        for shp in cmds.listRelatives(crv, shapes=True):
            cmds.setAttr(f'{shp}.overrideEnabled', 1)
            cmds.setAttr(f'{shp}.overrideColor', color)

        # match transform
        if orig_sel:
            cmds.matchTransform(new_name, orig_sel[0])



    def save_to_library_cmd(self):

        sel = cmds.ls(sl=True)

        file_name = self.newShapeLine.text()

        # error checking
        if file_name == '':
            OpenMaya.MGlobal.displayInfo('no name assigned')
            return
        if len(sel) == 0:
            OpenMaya.MGlobal.displayInfo('nothing selected')
            return
        else:
            for s in sel:
                if cmds.listRelatives(s, shapes=True) is None:
                    OpenMaya.MGlobal.displayInfo('selected object is not a curve')
                    return

        ctl.crv.save_to_lib(crv=sel[0], shape_name=file_name)


    @UI.deco_lib.d_undoable
    def color_curve_cmd(self, color):
        """ """
        crvs = cmds.ls(sl=True)
        for crv in crvs:
            for shp in cmds.listRelatives(crv, shapes=True):
                cmds.setAttr(f'{shp}.overrideEnabled', 1)
                cmds.setAttr(f'{shp}.overrideColor', color)

    @UI.deco_lib.d_undoable
    def combine_curves_cmd(self):
        sel = cmds.ls(sl=True, type='transform')

        for crv in sel[1:]:
            cmds.makeIdentity(crv, apply=True)
            for shp in cmds.listRelatives(crv, shapes=True):
                cmds.parent(shp, sel[0], r=True, shape=True)
            cmds.delete(crv)

    def open_lib_folder_cmd(self):
        lib_dir = ctl.crv.SHAPE_LIBRARY_PATH
        os.startfile(lib_dir)

    def open_dropdown_config_file_cmd(self):
        """ """
        config_file = UI.dropdown_config_utils.DROPDOWN_CONFIGS_PATH + '\\curves_dropdown.json'
        # open(config_file, 'r')
        os.startfile(config_file)









