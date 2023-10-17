from maya import cmds
from maya.api import OpenMaya
from maya import OpenMayaUI
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
from importlib import reload

import utils.helper
reload(utils.helper)

import UI.collapsible_wdg
reload(UI.collapsible_wdg)

import UI.deco_lib
reload(UI.deco_lib)

import biped.spine
reload(biped.spine)

import biped.leg
reload(biped.leg)

import biped.arm
reload(biped.arm)

import biped.master
reload(biped.master)



def maya_main_window():
    maya_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(maya_window_ptr), QtWidgets.QWidget)



class BipedDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.setWindowTitle('Biped')
        self.setMaximumWidth(400)
        self.setMinimumWidth(400)

        self.setMaximumSize(400, 400)

        self.create_layouts()
        self.create_connections()

        self.show()




    def create_collapsible_form_layout(self, title, parent_layout, row_dict, expanded=True):
        """ Helper function that creates a collapsibel widget with a form layout and a run button.
            The form layout is filled with rows of edit lines and a preceding label.
            The label corresponds to the keyword of the function
            and the edit line text is the value passed to the function.
        """

        collapsible_wdg = UI.collapsible_wdg.CollapsibleWidget(title)
        collapsible_wdg.setExpanded(expanded)
        parent_layout.addWidget(collapsible_wdg)

        formLayout = QtWidgets.QFormLayout()
        collapsible_wdg.addLayout(formLayout)

        btn = QtWidgets.QPushButton('Run')
        btn.setMaximumWidth(60)
        collapsible_wdg.addWidget(btn)

        edit_lines = []
        for label, obj in row_dict.items():
            el = QtWidgets.QLineEdit(obj)
            formLayout.addRow(label, el)
            edit_lines.append(el)

        return collapsible_wdg, formLayout, btn, edit_lines


    def create_layouts(self):
        """ """

        # main and collapsible widgets
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop)



        # master
        self.master_dict = {
            'masters': 'master_ctl master2_ctl',
            'root': 'root_jnt'
        }
        self.collapsible_wdg6, self.layout6, self.btn6, self.edit_lines6 = self.create_collapsible_form_layout(
            title='Master', parent_layout=main_layout, row_dict=self.master_dict, expanded=False)


        # spine
        self.spine_dict = {
            'pelvis': 'C_pelvis',
            'spine1': 'C_spine_1',
            'chest': 'C_chest',
            'mainSpine': 'C_mainSpine_ctl',
            'pelvisTrans': 'C_pelvisTrans_ctl',
            'pelvisRot': 'C_pelvisRot_ctl',
            'chestTrans': 'C_chestTrans_ctl',
            'chestTwist': 'C_chestTwist_ctl',
            'master': 'master2_ctl'
        }
        self.collapsible_wdg1, self.layout1, self.btn1, self.edit_lines1 = self.create_collapsible_form_layout(
            title='Spine', parent_layout=main_layout, row_dict=self.spine_dict, expanded=False)


        self.neck_dict = {
            'neck': 'C_neck',
            'head': 'C_head',
            'headAim': 'C_headAim_ctl',
            'headTilt': 'C_headTilt_ctl',
            'neckRot': 'C_neck_ctl',
            'chest': 'C_chest',
            'master': 'master2_ctl'
        }
        self.collapsible_wdg2, self.layout2, self.btn2, self.edit_lines2 = self.create_collapsible_form_layout(
            title='Neck', parent_layout=main_layout, row_dict=self.neck_dict, expanded=False)


        self.arm_dict = {
            'ik_chain': 'L_clavicle L_shoulder L_elbow L_wrist',
            'armTrans': 'L_armTrans_ctl',
            'armPV': 'L_armPV_ctl',
            'clavicleCtl': 'L_clavicle_ctl',
            'wristCtl': 'L_wrist_ctl',
            'chest': 'C_chest',
            'master': 'master2_ctl'
        }
        self.collapsible_wdg4, self.layout4, self.btn4, self.edit_lines4 = self.create_collapsible_form_layout(
            title='Arm', parent_layout=main_layout, row_dict=self.arm_dict, expanded=False)


        self.leg_dict = {
            'ik_chain': 'L_hip L_knee L_ankle L_ball L_toe',
            'legTrans': 'L_legTrans_ctl',
            'legPV': 'L_legPV_ctl',
            'footRot': 'L_footRot_ctl',
            'toeRot': 'L_toeRot_ctl',
            'master': 'master2_ctl'
        }
        self.collapsible_wdg3, self.layout3, self.btn3, self.edit_lines3 = self.create_collapsible_form_layout(
            title='Leg Simple', parent_layout=main_layout, row_dict=self.leg_dict, expanded=False)


        self.revLeg_dict = {
            'ik_chain': 'L_hip L_knee L_ankle L_ball L_toe',
            'rev_chain': 'L_revCBank L_revEBank L_revPivot L_revHeel L_revToe L_revBall L_revAnkle',
            'legTrans': 'L_revFoot_ctl',
            'legPV': 'L_revLegPV_ctl',
            'footRoll': 'L_footRoll_ctl',
            'master': 'master2_ctl'
        }
        self.collapsible_wdg5, self.layout5, self.btn5, self.edit_lines5 = self.create_collapsible_form_layout(
            title='Leg Reverse Foot', parent_layout=main_layout, row_dict=self.revLeg_dict, expanded=False)



    def create_connections(self):
        """ """
        self.btn1.clicked.connect(self.spine_cmd)
        self.btn2.clicked.connect(self.neck_cmd)
        self.btn3.clicked.connect(self.leg_cmd)
        self.btn4.clicked.connect(self.arm_cmd)
        self.btn5.clicked.connect(self.rev_leg_cmd)
        self.btn6.clicked.connect(self.master_cmd)


    @UI.deco_lib.d_undoable
    def spine_cmd(self):
        biped.spine.Spine(**{parm: el.text() for parm, el in zip(self.spine_dict.keys(), self.edit_lines1)})

    @UI.deco_lib.d_undoable
    def neck_cmd(self):
        biped.spine.Neck(**{parm: el.text() for parm, el in zip(self.neck_dict.keys(), self.edit_lines2)})

    @UI.deco_lib.d_undoable
    def leg_cmd(self):
        unpack_dict = {parm: el.text() for parm, el in zip(self.leg_dict.keys(), self.edit_lines3)}
        unpack_dict.update({'ik_chain': unpack_dict['ik_chain'].split(' ')})
        biped.leg.ikLeg(**unpack_dict)

    @UI.deco_lib.d_undoable
    def arm_cmd(self):
        unpack_dict = {parm: el.text() for parm, el in zip(self.arm_dict.keys(), self.edit_lines4)}
        unpack_dict.update({'ik_chain': unpack_dict['ik_chain'].split(' ')})
        biped.arm.Arm(**unpack_dict)

    @UI.deco_lib.d_undoable
    def rev_leg_cmd(self):
        unpack_dict = {parm: el.text() for parm, el in zip(self.revLeg_dict.keys(), self.edit_lines5)}
        unpack_dict.update({'ik_chain': unpack_dict['ik_chain'].split(' ')})
        unpack_dict.update({'rev_chain': unpack_dict['rev_chain'].split(' ')})
        biped.leg.rev_ikLeg(**unpack_dict)

    @UI.deco_lib.d_undoable
    def master_cmd(self):
        unpack_dict = {parm: el.text() for parm, el in zip(self.master_dict.keys(), self.edit_lines6)}
        unpack_dict.update({'masters': unpack_dict['masters'].split(' ')})
        biped.master.Master(**unpack_dict)











