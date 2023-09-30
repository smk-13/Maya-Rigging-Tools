from maya import cmds
from maya.api import OpenMaya
from maya import OpenMayaUI
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
from importlib import reload

import ctl.ctrl
reload(ctl.ctrl)

import UI.collapsible_wdg
reload(UI.collapsible_wdg)




def maya_main_window():
    maya_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(maya_window_ptr), QtWidgets.QWidget)

def create_unique_name(base_name):
    count = 1
    new_name = base_name
    while cmds.objExists(new_name):
        new_name = "{}_{}".format(base_name, count)
        count += 1
    return new_name


class ControlDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.setWindowTitle('Control')
        self.setMaximumWidth(380)
        self.setMinimumWidth(380)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.show()

    def create_widgets(self):

        self.shapesComboBox = QtWidgets.QComboBox()
        self.shapesComboBox.setMaxVisibleItems(30)
        self.shapesComboBox.addItem('sphere', 'sphere')
        self.shapesComboBox.addItem('box', 'cube')
        self.shapesComboBox.addItem('box on ground', 'cube_on_base')
        self.shapesComboBox.addItem('diamond', 'diamond')
        self.shapesComboBox.addItem('brackets', 'brackets')
        self.shapesComboBox.addItem('circle', 'circle')
        self.shapesComboBox.addItem('circle pointer', 'circle_pointer')
        self.shapesComboBox.addItem('square', 'square')
        self.shapesComboBox.addItem('rectangle', 'rectangle')
        self.shapesComboBox.addItem('circle cross arrow', 'circle_cross_arrow')
        self.shapesComboBox.addItem('arrow', 'arrow')
        self.shapesComboBox.addItem('double arrow', 'double_arrow')
        self.shapesComboBox.addItem('locator', 'locator')
        self.shapesComboBox.addItem('pin', 'pin')
        self.shapesComboBox.addItem('rotate sphere', 'rotate_sphere')
        self.shapesComboBox.addItem('sledgehammer', 'sledgehammer')
        self.shapesComboBox.addItem('star', 'star')
        self.shapesComboBox.addItem('emblem', 'emblem')
        self.shapesComboBox.addItem('four sided pyramide', 'four_sided_pyramide')
        self.shapesComboBox.addItem('three sided pyramide', 'three_sided_pyramide')

        self.scaleSpinBox = QtWidgets.QDoubleSpinBox()
        self.scaleSpinBox.setValue(1.0)
        self.scaleSpinBox.setRange(-99, 99)
        self.scaleSpinBox.setSingleStep(1.0)
        self.scaleSpinBox.setValue(20)

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

        self.red_btn = QtWidgets.QPushButton('Red')
        self.blue_btn = QtWidgets.QPushButton('Blue')
        self.green_btn = QtWidgets.QPushButton('Green')
        self.yellow_btn = QtWidgets.QPushButton('Yellow')
        self.cyan_btn = QtWidgets.QPushButton('Cyan')

        self.combine_btn = QtWidgets.QPushButton('Combine selected curves under the first selected')

    def create_layouts(self):
        
        main_layout = QtWidgets.QVBoxLayout(self)

        collapsible_wdg_create = UI.collapsible_wdg.CollapsibleWidget('Create new curve')
        collapsible_wdg_save = UI.collapsible_wdg.CollapsibleWidget('Save to Library')
        collapsible_wdg_modify = UI.collapsible_wdg.CollapsibleWidget('Modify curve')
        collapsible_wdg_create.setExpanded(True)
        collapsible_wdg_save.setExpanded(True)
        collapsible_wdg_modify.setExpanded(True)

        main_layout.addWidget(collapsible_wdg_create)
        main_layout.addWidget(collapsible_wdg_save)
        main_layout.addWidget(collapsible_wdg_modify)
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow('Shape', self.shapesComboBox)
        form_layout.addRow('Custom Shape', self.customShapeLine)
        form_layout.addRow('Scale', self.scaleSpinBox)
        form_layout.addRow('Color Index', self.colorSpinBox)

        btn_run_layout = QtWidgets.QHBoxLayout()
        btn_run_layout.addWidget(self.btn_run)
        btn_run_layout.addStretch()

        new_curve_layout = QtWidgets.QHBoxLayout()
        new_curve_layout.addWidget(self.newShapeLine)
        new_curve_layout.addWidget(self.btn_save)

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
        self.btn_save.clicked.connect(self.save_to_library)

        self.red_btn.clicked.connect(lambda: self.color_curve_cmd(13))
        self.blue_btn.clicked.connect(lambda: self.color_curve_cmd(6))
        self.yellow_btn.clicked.connect(lambda: self.color_curve_cmd(22))
        self.cyan_btn.clicked.connect(lambda: self.color_curve_cmd(18))
        self.green_btn.clicked.connect(lambda: self.color_curve_cmd(14))

        self.combine_btn.clicked.connect(self.combine_curves)


    def create_control_cmd(self):
        """ """
        new_name = create_unique_name(base_name='new_curve')

        shape = self.shapesComboBox.currentData()
        custom_shape = self.customShapeLine.text()
        if custom_shape != '':
            shape = custom_shape

        scale = self.scaleSpinBox.value()
        color = self.colorSpinBox.value()

        crv = ctl.ctrl.initialize_new_curve(name=new_name, shape=shape)

        cmds.xform(f'{crv}.cv[*]', os=True, r=True, scale=(scale, scale, scale))

        for shp in cmds.listRelatives(crv, shapes=True):
            cmds.setAttr(f'{shp}.overrideEnabled', 1)
            cmds.setAttr(f'{shp}.overrideColor', color)

    def save_to_library(self):
        crv = cmds.ls(sl=True)[0]
        if not cmds.objectType(cmds.listRelatives(crv, shapes=True)[0], isType='nurbsCurve'):
            raise RuntimeError('Not a curve.')
        name = self.newShapeLine.text()
        ctl.ctrl.save_to_lib(crv=crv, shape_name=name)

    def color_curve_cmd(self, color):
        """ """
        crv = cmds.ls(sl=True)[0]
        for shp in cmds.listRelatives(crv, shapes=True):
            cmds.setAttr(f'{shp}.overrideEnabled', 1)
            cmds.setAttr(f'{shp}.overrideColor', color)

    def combine_curves(self):
        sel = cmds.ls(sl=True, type='transform')

        for crv in sel[1:]:
            cmds.makeIdentity(crv, apply=True)
            for shp in cmds.listRelatives(crv, shapes=True):
                cmds.parent(shp, sel[0], r=True, shape=True)
            cmds.delete(crv)



if __name__ == "__main__":

    try:
        d.close()
        d.deleteLater()
    except:
        pass

    d = UI.control_ui.ControlDialog()
    d.show()





# TO DO: Button to print a list of all shapes of library
# TO DO: Add control class functionality like offset groups and tag as controller