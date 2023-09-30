from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload


import utils.helper
reload(utils.helper)

import ctl.ctrl 
reload(ctl.ctrl)

import utils.switch
reload(utils.switch)

import utils.roll_joints
reload(utils.roll_joints)

import utils.ik_effects
reload(utils.ik_effects)



class Arm:

    def __init__(self, side, color):
        """ """

        self.side = side
        self.shoulder = f'{side}_shoulder_jnt'
        self.arm_chain = [f'{side}_{i}_jnt' for i in ('upperArm', 'forearm', 'wrist')]
        self.master = 'master2_ctl'
        self.chest = 'chest_jnt'

        self.ctl_dict = {
            'shoulder': {'base_name': f'{side}_shoulder', 'shape': 'cube_on_base_X', 'scale': 5, 'hidden_attrs': ['v','sx','sy','sz','tx','ty','tz'], 'color': color},
            'hand': {'base_name': f'{side}_handMover', 'shape': 'cube', 'scale': 4, 'hidden_attrs': ['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz'], 'color': color},
            'hand2': {'base_name': f'{side}_handRot', 'shape': 'cube', 'scale': 2.5, 'hidden_attrs': ['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz'], 'color': color},
            'elbowPV': {'base_name': f'{side}_elbowPV', 'shape': 'sphere', 'scale': 3, 'hidden_attrs': ['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz'], 'color': color},
            'upperArm': {'base_name': f'{side}_upperArm_FK', 'shape': 'sphere', 'scale': 6, 'hidden_attrs': ['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz'], 'color': color},
            'forearm': {'base_name': f'{side}_forearm_FK', 'shape': 'sphere', 'scale': 4, 'hidden_attrs': ['v','sx','sy','sz','tx','ty','tz','rx','rz'], 'color': color},
            'wrist': {'base_name': f'{side}_wrist_FK', 'shape': 'sphere', 'scale': 3, 'hidden_attrs': ['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz'], 'color': color}
        }

        self.main()
        self.add_roll_bones()
        self.add_ik_effects()
        self.add_fk_switch()
        self.add_space_switches()


    def main(self):
        """ """

        self.shoulderCtlObj = ctl.ctrl.Control(target=self.shoulder, parent=self.master, **self.ctl_dict['shoulder'])
        self.shoulderCtlObj.mirror_if_right_side()
        cmds.parentConstraint(self.chest, self.shoulderCtlObj.grp, mo=True)
        cmds.parent(self.shoulder, self.shoulderCtlObj.ctrl)

        self.ik_chain = utils.helper.duplicate_joint_chain_v3(joint_chain=self.arm_chain, suffix='IK', parent=self.shoulder)

        self.handCtlObj = ctl.ctrl.Control(target=self.ik_chain[2], parent=self.master, **self.ctl_dict['hand'], position_only=True)
        self.handCtlObj.mirror_if_right_side()

        self.elbowPvCtlObj = ctl.ctrl.Control(parent=self.master, **self.ctl_dict['elbowPV'])
        self.elbowPvCtlObj.place_along_pole_vector(self.ik_chain[1], 40)
        self.elbowPvCtlObj.create_annotation(self.ik_chain[1])
        self.elbowPvCtlObj.mirror_if_right_side()

        self.arm_ikh = utils.helper.ik_handle(start_joint=self.ik_chain[0], end_joint=self.ik_chain[2], base_name=f'{self.side}_arm', solver='ikRPsolver')
        cmds.poleVectorConstraint(self.elbowPvCtlObj.ctrl, self.arm_ikh)
        cmds.parent(self.arm_ikh, self.handCtlObj.ctrl)

        self.hand2CtlObj = ctl.ctrl.Control(target=self.ik_chain[2], parent=self.master, **self.ctl_dict['hand2'])
        self.hand2CtlObj.mirror_if_right_side()
        cmds.pointConstraint(self.ik_chain[2], self.hand2CtlObj.grp)
        cmds.orientConstraint(self.ik_chain[1], self.hand2CtlObj.grp, mo=True)  # MAINTAIN OFFSET FOR THE RIGHT SIDE!
        cmds.orientConstraint(self.hand2CtlObj.ctrl, self.ik_chain[2])


    def add_fk_switch(self):
        self.upperArmCtlObj = ctl.ctrl.Control(target=self.arm_chain[0], parent=self.shoulderCtlObj.ctrl, **self.ctl_dict['upperArm'])
        self.forearmCtlObj = ctl.ctrl.Control(target=self.arm_chain[1], parent=self.upperArmCtlObj.ctrl, **self.ctl_dict['forearm'])
        self.wristCtlObj = ctl.ctrl.Control(target=self.arm_chain[2], parent=self.forearmCtlObj.ctrl, **self.ctl_dict['wrist'])

        utils.switch.IKFKSwitch(base_name=f'{self.side}_arm', bind_chain=self.arm_chain, ik_chain=self.ik_chain, fk_chain=None, ikfk_attr='FK',
            ikCtlObjs=[self.handCtlObj, self.elbowPvCtlObj, self.hand2CtlObj], fkCtlObjs=[self.upperArmCtlObj, self.forearmCtlObj, self.wristCtlObj], additionalCtlObjs=self.shoulderCtlObj)

    def add_space_switches(self):
        utils.switch.SpaceSwitch(base_name=f'{self.side}_hand', buffer=self.handCtlObj.grp, ctrl=self.handCtlObj.ctrl,
            space_dict={'World': self.master, 'Chest': self.chest, 'Shoulder': self.shoulder})
        utils.switch.SpaceSwitch(base_name=f'{self.side}_elbowPV', buffer=self.elbowPvCtlObj.grp, ctrl=self.elbowPvCtlObj.ctrl,
            space_dict={'World': self.master, 'Chest': self.chest, 'Shoulder': self.shoulder})
        utils.switch.RotationSpaceSwitch(base_name=f'{self.side}_upperArm_FK', buffer=self.upperArmCtlObj.grp, ctrl=self.upperArmCtlObj.ctrl,
            space_dict={'Shoulder': self.shoulder, 'World': self.master})

    def add_roll_bones(self):
        """ """
        utils.roll_joints.RollBoneUpperArm(side=self.side, shoulder=self.shoulder, upperArm=self.arm_chain[0], forearm=self.arm_chain[1])
        utils.roll_joints.RollBoneForearm(side=self.side, forearm=self.arm_chain[1], wrist=self.arm_chain[2])

    def add_ik_effects(self):
        """ """
        utils.ik_effects.IKEffects(base_name=f'{self.side}_arm', ik_chain=self.ik_chain, main_ctrl=self.handCtlObj.ctrl, pv_ctrl=self.elbowPvCtlObj.ctrl,
            base=self.shoulder, master=self.master, ikh=self.arm_ikh, effector=self.handCtlObj.ctrl)






