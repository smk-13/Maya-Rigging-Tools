from maya import cmds
from maya.api import OpenMaya
from maya import OpenMayaUI
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

from importlib import reload

import utils.orient_joints 
import utils.helper
reload(utils.orient_joints)
reload(utils.helper)


def maya_main_window():
    maya_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(maya_window_ptr), QtWidgets.QWidget)


class OrientJointsDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.setWindowTitle('Orient Joints')
        self.setMinimumWidth(200)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):

        self.label1 = QtWidgets.QLabel('Pick 3 joints by index for CS-Plane:')

        self.spinbox1 = QtWidgets.QSpinBox()
        self.spinbox2 = QtWidgets.QSpinBox()
        self.spinbox3 = QtWidgets.QSpinBox()
        self.spinbox1.setValue(0)
        self.spinbox2.setValue(1)
        self.spinbox3.setValue(2)

        self.checkbox1 = QtWidgets.QCheckBox('Negative Aim Vector')
        self.checkbox2 = QtWidgets.QCheckBox('Negative Up Vector')

        self.comboBox1 = QtWidgets.QComboBox()
        self.comboBox1.addItem('X Z', 0)
        self.comboBox1.addItem('X Y', 1)
        self.comboBox1.addItem('Y Z', 2)
        self.comboBox1.addItem('Z Y', 3)
        self.comboBox1.addItem('Y X', 4)
        self.comboBox1.addItem('Z X', 5)

        self.button1 = QtWidgets.QPushButton('Run')

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(6,6,6,6)

        form_layout1 = QtWidgets.QFormLayout()
        form_layout1.addRow(self.label1)
        form_layout1.addRow('Joint 1', self.spinbox1)
        form_layout1.addRow('Joint 2', self.spinbox2)
        form_layout1.addRow('Joint 3', self.spinbox3)

        form_layout2 = QtWidgets.QFormLayout()
        form_layout2.addRow('Aim Up Combination', self.comboBox1)

        button_layout1 = QtWidgets.QHBoxLayout()
        button_layout1.addWidget(self.button1)
        button_layout1.addStretch()

        main_layout.addLayout(form_layout1)
        main_layout.addLayout(form_layout2)
        main_layout.addWidget(self.checkbox1)
        main_layout.addWidget(self.checkbox2)
        main_layout.addLayout(button_layout1)

    def create_connections(self):
        self.button1.clicked.connect(self.orient_joints_command)

    def orient_joints_command(self):

        joint_chain = utils.helper.select_by_root_joint()

        indices = [sb.value() for sb in (self.spinbox1, self.spinbox2, self.spinbox3)]
        axis_combo = self.comboBox1.currentData()
        positive_aim = True if not self.checkbox1.isChecked() else False
        positive_up = True if not self.checkbox2.isChecked() else False

        utils.orient_joints.orient_joint_chain_and_snap(joint_chain=joint_chain, indices=indices,
            positive_aim=positive_aim, positive_up=positive_up, enum=axis_combo)




class OrientSingleJointDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.setWindowTitle('Orient Single Joint')
        self.setMinimumWidth(200)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.cb1 = QtWidgets.QCheckBox('Negative Aim Vector')
        self.cb2 = QtWidgets.QCheckBox('Negative Up Vector')

        self.comboBox1 = QtWidgets.QComboBox()
        self.comboBox1.addItem('X Z', 0)
        self.comboBox1.addItem('X Y', 1)
        self.comboBox1.addItem('Y Z', 2)
        self.comboBox1.addItem('Z Y', 3)
        self.comboBox1.addItem('Y X', 4)
        self.comboBox1.addItem('Z X', 5)

        self.btn1 = QtWidgets.QPushButton('Run')

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setMargin(6)

        form_layout1 = QtWidgets.QFormLayout()
        form_layout1.addRow('Aim Up Combination', self.comboBox1)

        btn_layout1 = QtWidgets.QHBoxLayout()
        btn_layout1.addWidget(self.btn1)
        btn_layout1.addStretch()

        main_layout.addLayout(form_layout1)
        main_layout.addWidget(self.cb1)
        main_layout.addWidget(self.cb2)
        main_layout.addLayout(btn_layout1)

    def create_connections(self):
        self.btn1.clicked.connect(self.orient_joints_command)

    def orient_joints_command(self):
        """ This needs a revision! """

        joint = cmds.ls(sl=True, type='joint')[0]  # right now only joints, because freeze transforms negates all work on normal transforms

        axis_combo = self.comboBox1.currentData()
        positive_aim = True if not self.cb1.isChecked() else False
        positive_up = True if not self.cb2.isChecked() else False

        utils.orient_joints.orient_with_selection(positive_aim=positive_aim, positive_up=positive_up, enum=axis_combo)





class OrientFirstThreeJointsDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.setWindowTitle('Orient Joints')
        self.setMinimumWidth(200)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        pass

    def create_layouts(self):
        pass

    def create_connections(self):
        pass