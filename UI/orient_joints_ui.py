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
        self.setMaximumWidth(500)
        self.setMinimumWidth(500)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.show()


    def create_widgets(self):
        """ """

        # widgets for row1
        self.label1 = QtWidgets.QLabel('Aim Axis')

        self.r_btn_aimX = QtWidgets.QRadioButton('X')
        self.r_btn_aimY = QtWidgets.QRadioButton('Y')
        self.r_btn_aimZ = QtWidgets.QRadioButton('Z')
        self.r_btn_aimNX = QtWidgets.QRadioButton('-X')
        self.r_btn_aimNY = QtWidgets.QRadioButton('-Y')
        self.r_btn_aimNZ = QtWidgets.QRadioButton('-Z')

        self.btn_grp = QtWidgets.QButtonGroup()
        self.btn_grp.addButton(self.r_btn_aimX)
        self.btn_grp.addButton(self.r_btn_aimY)
        self.btn_grp.addButton(self.r_btn_aimZ)
        self.btn_grp.addButton(self.r_btn_aimNX)
        self.btn_grp.addButton(self.r_btn_aimNY)
        self.btn_grp.addButton(self.r_btn_aimNZ)
        self.r_btn_aimX.setChecked(True)

        # widgets for row2
        self.label2 = QtWidgets.QLabel('Up Axis')

        self.r_btn_upX = QtWidgets.QRadioButton('X')
        self.r_btn_upY = QtWidgets.QRadioButton('Y')
        self.r_btn_upZ = QtWidgets.QRadioButton('Z')
        self.r_btn_upNX = QtWidgets.QRadioButton('-X')
        self.r_btn_upNY = QtWidgets.QRadioButton('-Y')
        self.r_btn_upNZ = QtWidgets.QRadioButton('-Z')

        self.btn_grp = QtWidgets.QButtonGroup()
        self.btn_grp.addButton(self.r_btn_upX)
        self.btn_grp.addButton(self.r_btn_upY)
        self.btn_grp.addButton(self.r_btn_upZ)
        self.btn_grp.addButton(self.r_btn_upNX)
        self.btn_grp.addButton(self.r_btn_upNY)
        self.btn_grp.addButton(self.r_btn_upNZ)
        self.r_btn_upZ.setChecked(True)

        # widgets for row3
        self.btn1 = QtWidgets.QPushButton('3 joints')
        #self.btn1.setMaximumWidth(150)

        self.btn2 = QtWidgets.QPushButton('1 joint')
        #self.btn2.setMaximumWidth(150)

        self.btn3 = QtWidgets.QPushButton('zero out')
        #self.btn2.setMaximumWidth(150)



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
        row1.addWidget(self.r_btn_aimX)
        row1.addWidget(self.r_btn_aimY)
        row1.addWidget(self.r_btn_aimZ)
        row1.addWidget(self.r_btn_aimNX)
        row1.addWidget(self.r_btn_aimNY)
        row1.addWidget(self.r_btn_aimNZ)

        row2.addWidget(self.label2)
        row2.addWidget(self.r_btn_upX)
        row2.addWidget(self.r_btn_upY)
        row2.addWidget(self.r_btn_upZ)
        row2.addWidget(self.r_btn_upNX)
        row2.addWidget(self.r_btn_upNY)
        row2.addWidget(self.r_btn_upNZ)

        # row3
        row3.addWidget(self.btn1)
        row3.addWidget(self.btn2)
        row3.addWidget(self.btn3)
        #row3.addStretch()


    def create_connections(self):
        """ """
        self.btn1.clicked.connect(self.create_run_cmd1)
        self.btn2.clicked.connect(self.create_run_cmd2)
        self.btn3.clicked.connect(self.create_zero_out_cmd)

    def get_axis(self):

        if self.r_btn_aimX.isChecked():
            aim_axis = [1,0,0]
        elif self.r_btn_aimY.isChecked():
            aim_axis = [0,1,0]
        elif self.r_btn_aimZ.isChecked():
            aim_axis = [0,0,1]
        elif self.r_btn_aimNX.isChecked():
            aim_axis = [-1,0,0]
        elif self.r_btn_aimNY.isChecked():
            aim_axis = [0,-1,0]
        else:
            aim_axis = [0,0,-1]

        if self.r_btn_upX.isChecked():
            up_axis = [1,0,0]
        elif self.r_btn_upY.isChecked():
            up_axis = [0,1,0]
        elif self.r_btn_upZ.isChecked():
            up_axis = [0,0,1]
        elif self.r_btn_upNX.isChecked():
            up_axis = [-1,0,0]
        elif self.r_btn_upNY.isChecked():
            up_axis = [0,-1,0]
        else:
            up_axis = [0,0,-1]

        return aim_axis, up_axis


    def create_run_cmd1(self):
        """ """
        aim_axis, up_axis = self.get_axis()

        utils.orient_joints.orient_three_joints(joint_chain=None, aim_vec=aim_axis, up_vec=up_axis)


    def create_run_cmd2(self):
        """ """
        aim_axis, up_axis = self.get_axis()

        utils.orient_joints.orient_single_joint(aim_vec=aim_axis, up_vec=up_axis)


    def create_zero_out_cmd(self):
        """ """
        joints = cmds.ls(sl=True, type='joint')
        for jnt in joints:
            cmds.joint(jnt, edit=True, orientation=[0,0,0])









