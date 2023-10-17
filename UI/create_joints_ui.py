from maya import cmds
from maya.api import OpenMaya
from maya import OpenMayaUI
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
from importlib import reload

import utils.helper
reload(utils.helper)

import skel.skel_utils
reload(skel.skel_utils)

import UI.collapsible_wdg
reload(UI.collapsible_wdg)

import UI.deco_lib
reload(UI.deco_lib)




def maya_main_window():
    maya_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(maya_window_ptr), QtWidgets.QWidget)



class CreateJointsDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.lra_next = 1

        self.setWindowTitle('Skeleton Creation Tools')
        self.setMaximumWidth(400)
        self.setMinimumWidth(400)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.show()


    def create_widgets(self):
        self.btn_lra = QtWidgets.QPushButton('LRA')
        self.btn_lra.setMaximumWidth(40)

        self.btn_jnt = QtWidgets.QPushButton('JNT')
        self.btn_jnt.setMaximumWidth(40)

        self.btn_measure = QtWidgets.QPushButton('DIST')
        self.btn_measure.setMaximumWidth(40)

        self.label1 = QtWidgets.QLabel('Joints')
        self.spinBox1 = QtWidgets.QSpinBox()
        self.spinBox1.setValue(5)
        self.btn_chain = QtWidgets.QPushButton('Chain')
        self.btn_chain.setMaximumWidth(60)


    def create_layouts(self):
        
        #
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        #
        collapsible_wdg1 = UI.collapsible_wdg.CollapsibleWidget('Skeleton Creation Tools')
        collapsible_wdg1.setExpanded(True)
        main_layout.addWidget(collapsible_wdg1)

        tools_layout = QtWidgets.QHBoxLayout()
        collapsible_wdg1.addLayout(tools_layout)
        tools_layout.addWidget(self.btn_lra)
        tools_layout.addWidget(self.btn_jnt)
        tools_layout.addWidget(self.btn_measure)
        tools_layout.addStretch()
        tools_layout.addWidget(self.label1)
        tools_layout.addWidget(self.spinBox1)
        tools_layout.addWidget(self.btn_chain)
        


    def create_connections(self):
        """ """
        self.btn_lra.clicked.connect(self.lra_cmd)
        self.btn_jnt.clicked.connect(self.jnt_cmd)
        self.btn_measure.clicked.connect(self.measure_cmd)
        self.btn_chain.clicked.connect(self.chain_cmd)

    @UI.deco_lib.d_undoable
    def lra_cmd(self):
        """ """
        sel = cmds.ls(sl=True, type='transform')
        if len(sel) > 0:
            joints = sel
        else:
            joints = cmds.ls(type='joint')

        for jnt in joints:
            cmds.setAttr(f'{jnt}.displayLocalAxis', self.lra_next)
        if self.lra_next == 1:
            self.lra_next = 0
        else:
            self.lra_next = 1

    def jnt_cmd(self):
        """ """
        pos = utils.helper.calculate_mid_position() if cmds.ls(sl=True) else [0,0,0]
        cmds.select(cl=True)
        jnt = cmds.joint(radius=5)
        cmds.xform(jnt, ws=True, translation=pos)

    def measure_cmd(self):
        """ """
        print(utils.helper.measure_distance())


    @UI.deco_lib.d_undoable
    def chain_cmd(self):
        """ """
        sel = cmds.ls(sl=True)

        if len(sel) != 2:
            OpenMaya.MGlobal.displayInfo('Select two objects. This function creates a joint chain with joints at equal distances between the selected objects.')
            OpenMaya.MGlobal.displayInfo('The orientation of these new joints will be equal to the first selected object.')

            cmds.error()


        utils.helper.create_equidistant_joint_chain(joints=None, joint_count=self.spinBox1.value())
