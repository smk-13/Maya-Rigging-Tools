from maya import cmds
from maya.api import OpenMaya
from maya import OpenMayaUI
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
from importlib import reload

import utils.orient_joints
reload(utils.orient_joints)

import utils.helper
reload(utils.helper)

# https://doc.qt.io/qtforpython-5/PySide2/QtCore/Qt.html#PySide2.QtCore.PySide2.QtCore.Qt.Key

def maya_main_window():
    maya_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(maya_window_ptr), QtWidgets.QWidget)


class OrientJointsDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.setWindowTitle('Orient Joints')
        self.setMaximumWidth(380)
        self.setMinimumWidth(380)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.show()


    def create_widgets(self):
        """ """

        # widgets for row1
        self.label1 = QtWidgets.QLabel('Aim Axis')

        self.r_btn1 = QtWidgets.QRadioButton('X')
        self.r_btn2 = QtWidgets.QRadioButton('Y')
        self.r_btn3 = QtWidgets.QRadioButton('Z')

        self.btn_grp = QtWidgets.QButtonGroup()
        self.btn_grp.addButton(self.r_btn1)
        self.btn_grp.addButton(self.r_btn2)
        self.btn_grp.addButton(self.r_btn3)
        self.r_btn1.setChecked(True)

        # widgets for row2
        self.label2 = QtWidgets.QLabel('Up Axis')

        self.r_btn4 = QtWidgets.QRadioButton('X')
        self.r_btn5 = QtWidgets.QRadioButton('Y')
        self.r_btn6 = QtWidgets.QRadioButton('Z')

        self.btn_grp = QtWidgets.QButtonGroup()
        self.btn_grp.addButton(self.r_btn4)
        self.btn_grp.addButton(self.r_btn5)
        self.btn_grp.addButton(self.r_btn6)
        self.r_btn6.setChecked(True)

        # widgets for row3
        self.btn1 = QtWidgets.QPushButton('Orient 3 joints')
        self.btn1.setMaximumWidth(150)

        self.btn2 = QtWidgets.QPushButton('Orient 1 joint')
        self.btn2.setMaximumWidth(150)


    def create_layouts(self):
        """ """
        main_layout = QtWidgets.QVBoxLayout(self)
        row1 = QtWidgets.QHBoxLayout()
        row2 = QtWidgets.QHBoxLayout()
        row3 = QtWidgets.QHBoxLayout()
        main_layout.addLayout(row1)
        main_layout.addLayout(row2)
        main_layout.addLayout(row3)

        row1.addWidget(self.label1)
        row1.addWidget(self.r_btn1)
        row1.addWidget(self.r_btn2)
        row1.addWidget(self.r_btn3)

        row2.addWidget(self.label2)
        row2.addWidget(self.r_btn4)
        row2.addWidget(self.r_btn5)
        row2.addWidget(self.r_btn6)

        # row3
        row3.addWidget(self.btn1)
        row3.addWidget(self.btn2)
        row3.addStretch()


    def create_connections(self):
        """ """
        self.btn1.clicked.connect(self.create_run_cmd1)
        self.btn2.clicked.connect(self.create_run_cmd2)


    def create_run_cmd1(self):
        """ """
        if self.r_btn1.isChecked():
            aim_axis = [1,0,0]
        elif self.r_btn2.isChecked():
            aim_axis = [0,1,0]
        else:
            aim_axis = [0,0,1]

        if self.r_btn4.isChecked():
            up_axis = [1,0,0]
        elif self.r_btn5.isChecked():
            up_axis = [0,1,0]
        else:
            up_axis = [0,0,1]

        utils.orient_joints.orient_joint_chain(joint_chain=None,
            aim_vec=aim_axis, up_vec=up_axis)


    def create_run_cmd2(self):
        """ """
        if self.r_btn1.isChecked():
            aim_axis = [1,0,0]
        elif self.r_btn2.isChecked():
            aim_axis = [0,1,0]
        else:
            aim_axis = [0,0,1]

        if self.r_btn4.isChecked():
            up_axis = [1,0,0]
        elif self.r_btn5.isChecked():
            up_axis = [0,1,0]
        else:
            up_axis = [0,0,1]

        utils.orient_joints.orient_single_joint(aim_vec=aim_axis, up_vec=up_axis)








