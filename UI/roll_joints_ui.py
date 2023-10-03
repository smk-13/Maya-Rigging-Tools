from maya import cmds
from maya.api import OpenMaya
from maya import OpenMayaUI
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
from importlib import reload

import utils.helper
reload(utils.helper)

import utils.roll_joints
reload(utils.roll_joints)

import UI.collapsible_wdg
reload(UI.collapsible_wdg)





def maya_main_window():
    maya_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(maya_window_ptr), QtWidgets.QWidget)


class RollJointsDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.lra_next = 1

        self.setWindowTitle('No Flip Roll Joints')
        self.setMaximumWidth(400)
        self.setMinimumWidth(400)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.show()


    def create_widgets(self):
        """ """
        # run buttons
        self.btn_run1 = QtWidgets.QPushButton('forearm/lowerLeg')
        self.btn_run2 = QtWidgets.QPushButton('upperArm/upperLeg')

        # aim axis
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

        # inbetweens
        self.spinBox1 = QtWidgets.QSpinBox()
        self.spinBox1.setValue(3)

        # base_name
        self.lineEdit1 = QtWidgets.QLineEdit()
        self.lineEdit1.setText('L_upperArm')

        # instructions
        self.label1 = QtWidgets.QLabel('''For the forearm/lowerLeg the aim axis is inverted.
However, if the skeleton has been mirrored to the right side, the aim axis is inverted again.''')
        self.label1.setWordWrap(True)
        self.label2 = QtWidgets.QLabel('''For the forearm/lowerLeg select the wrist/ankle, then elbow/knee.''')
        self.label2.setWordWrap(True)
        self.label3 = QtWidgets.QLabel('''For the upperArm/upperLeg select the clavicle/pelvis,
then the shoulder/hip, and then the elbow/knee.''')
        self.label3.setWordWrap(True)

    def create_layouts(self):
        """ """

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        #
        collapsible_wdg1 = UI.collapsible_wdg.CollapsibleWidget('Create Roll Joints')
        main_layout.addWidget(collapsible_wdg1)

        # parent layout of row1, row2, and row3
        formLayout1 = QtWidgets.QFormLayout()
        collapsible_wdg1.addLayout(formLayout1)
        collapsible_wdg1.setExpanded(True)

        # row1
        row1 = QtWidgets.QHBoxLayout()
        row1.addWidget(self.r_btn_aimX)
        row1.addWidget(self.r_btn_aimY)
        row1.addWidget(self.r_btn_aimZ)
        row1.addWidget(self.r_btn_aimNX)
        row1.addWidget(self.r_btn_aimNY)
        row1.addWidget(self.r_btn_aimNZ)
        formLayout1.addRow('Aim Axis', row1)

        # row2
        formLayout1.addRow('Inbetweens', self.spinBox1)

        # row3
        formLayout1.addRow('Basename', self.lineEdit1)

        # run buttons
        layout2 = QtWidgets.QHBoxLayout()
        collapsible_wdg1.addLayout(layout2)
        layout2.addWidget(self.btn_run1)
        layout2.addWidget(self.btn_run2)

        # instruction text
        collapsible_wdg2 = UI.collapsible_wdg.CollapsibleWidget('Instructions')
        main_layout.addWidget(collapsible_wdg2)
        collapsible_wdg2.setExpanded(False)
        collapsible_wdg2.addWidget(self.label1)
        collapsible_wdg2.addWidget(self.label2)
        collapsible_wdg2.addWidget(self.label3)


    def create_connections(self):
        """ """
        self.btn_run1.clicked.connect(self.roll_joint_cmd1)
        self.btn_run2.clicked.connect(self.roll_joint_cmd2)


    def roll_joint_cmd1(self):
        sel = cmds.ls(sl=True, type='joint')

        aim_axis = self.get_axis()
        inbetweens = self.spinBox1.value()
        base_name = self.lineEdit1.text()

        utils.roll_joints.RollBoneInverse(aim_vec=aim_axis, inbetweens=inbetweens,
            base_name=base_name, wrist=sel[0], elbow=sel[1])


    def roll_joint_cmd2(self):
        sel = cmds.ls(sl=True, type='joint')

        aim_axis = self.get_axis()
        inbetweens = self.spinBox1.value()
        base_name = self.lineEdit1.text()

        utils.roll_joints.RollBoneAnchor(aim_vec=aim_axis, inbetweens=inbetweens,
            base_name=base_name, pelvis=sel[0], hip=sel[1], knee=sel[2])



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

        return aim_axis