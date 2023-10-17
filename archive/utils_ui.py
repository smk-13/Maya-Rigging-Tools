from maya import cmds
from maya.api import OpenMaya
from maya import OpenMayaUI
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
from importlib import reload

import utils.helper
import utils.rename
import UI.collapsible_wdg
import UI.custom_wdg
reload(utils.helper)
reload(utils.rename)
reload(UI.collapsible_wdg)
reload(UI.custom_wdg)

def maya_main_window():
    maya_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(maya_window_ptr), QtWidgets.QWidget)


class UtilsDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.setWindowTitle('Utility')
        self.setMinimumSize(300, 250)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.collapsible_wdg1 = UI.collapsible_wdg.CollapsibleWidget('Create Joint Chain')
        self.collapsible_wdg2 = UI.collapsible_wdg.CollapsibleWidget('Add Suffix')
        self.collapsible_wdg3 = UI.collapsible_wdg.CollapsibleWidget('Duplicate Selected Joint Chain')
        self.collapsible_wdg1.setExpanded(True)
        self.collapsible_wdg2.setExpanded(True)
        self.collapsible_wdg3.setExpanded(True)

        # create inbetween joints
        self.spinbox1 = QtWidgets.QSpinBox()
        self.spinbox1.setValue(5)
        self.cb1 = QtWidgets.QCheckBox()
        self.cb2 = QtWidgets.QCheckBox()
        self.btn1 = QtWidgets.QPushButton('Run')

        # rename
        self.line1 = UI.custom_wdg.CustomLineEdit()
        self.line1.setPlaceholderText('Add a suffix and hit enter')
        self.line1.setMaximumWidth(150)

        # duplicate selected joint chain
        self.line2 = UI.custom_wdg.CustomLineEdit()
        self.line2.setPlaceholderText('Add a suffix and hit enter')
        self.line2.setMaximumWidth(150)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.collapsible_wdg1)
        self.main_layout.addWidget(self.collapsible_wdg2)
        self.main_layout.addWidget(self.collapsible_wdg3)
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        
        # create inbetween joints
        self.form_layout1 = QtWidgets.QFormLayout()
        self.form_layout1.addRow('Number of Joints', self.spinbox1)
        self.form_layout1.addRow('Disconnected Joints', self.cb1)
        self.form_layout1.addRow('Delete old Joints', self.cb2)
        self.btn_layout1 = QtWidgets.QHBoxLayout()
        self.btn_layout1.addWidget(self.btn1)
        self.btn_layout1.addStretch()
        self.collapsible_wdg1.addLayout(self.form_layout1)
        self.collapsible_wdg1.addLayout(self.btn_layout1)

        # rename
        self.collapsible_wdg2.addWidget(self.line1)

        # duplicate selected joint chain
        self.collapsible_wdg3.addWidget(self.line2)


    def create_connections(self):
        self.btn1.clicked.connect(self.create_inbetween_joints_slot)
        self.line1.enter_pressed.connect(self.add_suffix_slot)
        self.line2.enter_pressed.connect(self.duplicate_selected_joint_chain_slot)

    def create_inbetween_joints_slot(self):
        joint_count = self.spinbox1.value()
        disconnected = self.cb1.isChecked()
        delete_old_joints = self.cb2.isChecked()
        joints = None  # triggers selection mode
        utils.helper.create_inbetween_joints(joints, joint_count, disconnected, delete_old_joints)

    def add_suffix_slot(self):
        suffix = self.line1.text()
        utils.rename.add_suffix(suffix, objs=None, separator='_')

    def duplicate_selected_joint_chain_slot(self):
        suffix = self.line2.text()
        utils.helper.duplicate_selected_joint_chain(suffix, joints=None)



class PoleVectorLocatorDialog(QtWidgets.QDialog):


    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.setWindowTitle('Pole Vector')
        self.setMinimumWidth(200)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.spinbox1 = QtWidgets.QDoubleSpinBox()
        self.spinbox1.setValue(50)
        self.spinbox1.setRange(0,200)
        self.spinbox1.setSingleStep(10)
        self.spinbox1.setSuffix(' cm')

        self.spinbox2 = QtWidgets.QDoubleSpinBox()
        self.spinbox2.setValue(10)

        self.btn1 = QtWidgets.QPushButton('Run')
        self.btn1.setMaximumWidth(60)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.form_layout1 = QtWidgets.QFormLayout()
        self.form_layout1.addRow('distance', self.spinbox1)
        self.form_layout1.addRow('scale', self.spinbox2)

        self.main_layout.addLayout(self.form_layout1)
        self.main_layout.addWidget(self.btn1)

    def create_connections(self):
        self.btn1.clicked.connect(self.create_locator)

    def create_locator(self):
        distance = self.spinbox1.value()
        scale = self.spinbox2.value()
        joints = None  # triggers selection mode
        utils.helper.place_locator_at_pv_pos(joints, distance, scale)
