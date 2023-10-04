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




def maya_main_window():
    maya_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(maya_window_ptr), QtWidgets.QWidget)



class SkeletonDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.lra_next = 1

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
        self.skelComboBox.addItem('Ahsoka', 'Ahsoka')

        self.customSkelLine = QtWidgets.QLineEdit()
        self.customSkelLine.setPlaceholderText('If not listed in drop down list')

        self.newSkelLine = QtWidgets.QLineEdit()
        self.newSkelLine.setPlaceholderText('select joints and enter a name')

        self.btn_load = QtWidgets.QPushButton('Load')
        self.btn_load.setMaximumWidth(60)

        self.btn_save = QtWidgets.QPushButton('Save')
        self.btn_save.setMaximumWidth(60)

        self.btn_lra = QtWidgets.QPushButton('LRA')
        self.btn_lra.setMaximumWidth(40)

        self.btn_jnt = QtWidgets.QPushButton('JNT')
        self.btn_jnt.setMaximumWidth(40)

        self.btn_loc = QtWidgets.QPushButton('LOC')
        self.btn_loc.setMaximumWidth(40)

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

        #
        collapsible_wdg3 = UI.collapsible_wdg.CollapsibleWidget('Skeleton Creation Tools')
        collapsible_wdg3.setExpanded(True)
        main_layout.addWidget(collapsible_wdg3)

        tools_layout = QtWidgets.QHBoxLayout()
        collapsible_wdg3.addLayout(tools_layout)
        tools_layout.addWidget(self.btn_lra)
        tools_layout.addWidget(self.btn_jnt)
        tools_layout.addWidget(self.btn_loc)
        tools_layout.addWidget(self.btn_measure)
        tools_layout.addStretch()
        tools_layout.addWidget(self.label1)
        tools_layout.addWidget(self.spinBox1)
        tools_layout.addWidget(self.btn_chain)
        


    def create_connections(self):
        """ """
        self.btn_load.clicked.connect(self.load_cmd)
        self.btn_save.clicked.connect(self.save_cmd)
        self.btn_lra.clicked.connect(self.lra_cmd)
        self.btn_jnt.clicked.connect(self.jnt_cmd)
        self.btn_loc.clicked.connect(self.loc_cmd)
        self.btn_measure.clicked.connect(self.measure_cmd)
        self.btn_chain.clicked.connect(self.chain_cmd)

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
        cmds.select(cl=True)
        cmds.joint()
        cmds.select(cl=True)

    def loc_cmd(self):
        """ """
        cmds.spaceLocator()

    def measure_cmd(self):
        """ """
        print(utils.helper.measure_distance())

    def chain_cmd(self):
        """ """
        sel = cmds.ls(sl=True)

        if len(sel) != 2:
            cmds.error('select two objects. This function creates a joint chain with joints at equal distances between the selected objects.')

        utils.helper.create_equidistant_joint_chain(joints=None, joint_count=self.spinBox1.value())
