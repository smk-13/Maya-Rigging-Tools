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





class Leg:

    def __init__(self, side, color):
        """ """
        self.side = side
        self.leg_chain = [f'{side}_{i}_jnt' for i in ('hip', 'knee', 'ankle', 'ball', 'toe')]
        self.rev_chain = [f'{side}_{i}' for i in ('revCBank', 'revEBank', 'revPivot', 'revHeel', 'revToe', 'revBall', 'revAnkle')]
        self.master = 'master2_ctl'
        self.pelvis = 'pelvis_jnt'

        self.ctl_dict = {
            'foot': {'base_name': f'{side}_foot', 'shape': 'Asari_foot', 'scale': 1, 'hidden_attrs': ['v', 'sx', 'sy', 'sz'], 'color': color},
            'kneePV': {'base_name': f'{side}_kneePV', 'shape': 'sphere', 'scale': 3, 'hidden_attrs': ['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz'], 'color': color},
            'footRoll': {'base_name': f'{side}_footRoll', 'shape': 'rotate_sphere', 'scale': 6, 'hidden_attrs': ['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz'],'color': color},
            'toeTap': {'base_name': f'{side}_toeTap', 'shape': 'circleZ', 'scale': 4, 'hidden_attrs': ['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz', 'rx', 'ry'], 'color': color},
            'hip': {'base_name': f'{side}_hip_FK', 'shape': 'sphere', 'scale': 7, 'hidden_attrs': ['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz'], 'color': color},
            'knee': {'base_name': f'{side}_knee_FK', 'shape': 'sphere', 'scale': 6, 'hidden_attrs': ['v','sx','sy','sz','tx','ty','tz','rx','ry'], 'color': color},
            'ankle': {'base_name': f'{side}_ankle_FK', 'shape': 'sphere', 'scale': 5, 'hidden_attrs': ['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz'], 'color': color},
            'ball': {'base_name': f'{side}_ball_FK', 'shape': 'sphere', 'scale': 4, 'hidden_attrs': ['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz', 'rx', 'ry'], 'color': color}
        }

        self.main()
        self.add_roll_bones()
        self.add_ik_effects()
        self.add_fk_switch()
        self.add_space_switches()
        self.add_helper_joints()

    def main(self):
        """ """
        self.leg_conn = utils.helper.duplicate_single_joint(joint=self.leg_chain[0], name=f'{self.side}_legConn', parent=self.pelvis)

        # for better outliner organization
        cmds.parent(self.leg_conn, self.master)
        cmds.parentConstraint(self.pelvis, self.leg_conn, mo=True)

        cmds.parent(self.leg_chain[0], self.leg_conn)

        self.ik_chain = utils.helper.duplicate_joint_chain_v3(joint_chain=self.leg_chain, suffix='IK', parent=self.leg_conn)

        self.leg_ikh = utils.helper.ik_handle(start_joint=self.ik_chain[0], end_joint=self.ik_chain[2], base_name=f'{self.side}_leg', solver='ikRPsolver')
        self.foot_ikh = utils.helper.ik_handle(start_joint=self.ik_chain[2], end_joint=self.ik_chain[3], base_name=f'{self.side}_foot', solver='ikSCsolver')
        self.toe_ikh = utils.helper.ik_handle(start_joint=self.ik_chain[3], end_joint=self.ik_chain[4], base_name=f'{self.side}_toe', solver='ikSCsolver')

        self.footCtlObj = ctl.ctrl.Control(target=self.rev_chain[-1], parent=self.master, **self.ctl_dict['foot'])
        self.footCtlObj.mirror_if_right_side()

        self.kneePvCtlObj = ctl.ctrl.Control(parent=self.master, **self.ctl_dict['kneePV'])
        self.kneePvCtlObj.place_along_pole_vector(self.ik_chain[1], 60)
        self.kneePvCtlObj.create_annotation(self.ik_chain[1])
        self.kneePvCtlObj.mirror_if_right_side()

        cmds.poleVectorConstraint(self.kneePvCtlObj.ctrl, self.leg_ikh)

        self.toeTapCtlObj = ctl.ctrl.Control(target=self.leg_chain[3], parent=self.rev_chain[4], **self.ctl_dict['toeTap'])

        cmds.parent(self.toe_ikh, self.toeTapCtlObj.ctrl)
        cmds.parent(self.leg_ikh, self.rev_chain[6])
        cmds.parent(self.foot_ikh, self.rev_chain[5])
        cmds.parent(self.rev_chain[0], self.footCtlObj.ctrl)

        self.footRollCtlObj = ctl.ctrl.Control(target=self.rev_chain[2], parent=self.footCtlObj.ctrl, **self.ctl_dict['footRoll'])
        cmds.xform(self.footRollCtlObj.grp, r=True, os=True, t=[25, self.ctl_dict['footRoll']['scale'], 0])
        self.footRollCtlObj.mirror_if_right_side()

        toe_lift = 'ToeLiftAngle'
        toe_straight = 'ToeStraightAngle'
        cmds.addAttr(self.footRollCtlObj.ctrl, ln=toe_lift, at='double', dv=60, k=True)
        cmds.addAttr(self.footRollCtlObj.ctrl, ln=toe_straight, at='double', dv=75, k=True)

        # roll
        condition_roll = cmds.createNode('condition', name=f'{self.side}_footRoll_COND')
        blend_roll = cmds.createNode('blendColors', name=f'{self.side}_footRoll_BC')
        remap_roll = cmds.createNode('remapValue', name=f'{self.side}_footRoll_REMAP')
        cmds.setAttr(f'{condition_roll}.operation', 2)
        cmds.setAttr(f'{condition_roll}.colorIfFalseR', 0)
        cmds.connectAttr(f'{self.footRollCtlObj.ctrl}.rotateX', f'{condition_roll}.colorIfFalseG')
        cmds.connectAttr(f'{self.footRollCtlObj.ctrl}.rotateX', f'{condition_roll}.colorIfTrueR')
        cmds.connectAttr(f'{self.footRollCtlObj.ctrl}.rotateX', f'{condition_roll}.firstTerm')
        cmds.connectAttr(f'{self.footRollCtlObj.ctrl}.rotateX', f'{remap_roll}.inputValue')
        cmds.connectAttr(f'{self.footRollCtlObj.ctrl}.{toe_lift}', f'{remap_roll}.inputMin')
        cmds.connectAttr(f'{self.footRollCtlObj.ctrl}.{toe_straight}', f'{remap_roll}.inputMax')
        cmds.connectAttr(f'{remap_roll}.outValue', f'{blend_roll}.blender')
        cmds.connectAttr(f'{condition_roll}.outColorR', f'{blend_roll}.color1R')
        cmds.connectAttr(f'{condition_roll}.outColorR', f'{blend_roll}.color2G')
        cmds.connectAttr(f'{condition_roll}.outColorG', f'{self.rev_chain[3]}.rotateX')
        cmds.connectAttr(f'{blend_roll}.outputR', f'{self.rev_chain[4]}.rotateX')
        cmds.connectAttr(f'{blend_roll}.outputG', f'{self.rev_chain[5]}.rotateX')

        # bank
        condition_bank = cmds.createNode('condition', name=f'{self.side}_banking_COND')
        cmds.setAttr(f'{condition_bank}.operation', 2)
        cmds.setAttr(f'{condition_bank}.colorIfFalseR', 0)
        cmds.connectAttr(f'{self.footRollCtlObj.ctrl}.rotateZ', f'{condition_bank}.colorIfFalseG')
        cmds.connectAttr(f'{self.footRollCtlObj.ctrl}.rotateZ', f'{condition_bank}.colorIfTrueR')
        cmds.connectAttr(f'{self.footRollCtlObj.ctrl}.rotateZ', f'{condition_bank}.firstTerm')
        cmds.connectAttr(f'{condition_bank}.outColorR', f'{self.rev_chain[0]}.rotateZ')
        cmds.connectAttr(f'{condition_bank}.outColorG', f'{self.rev_chain[1]}.rotateZ')

        # ball spin
        cmds.connectAttr(f'{self.footRollCtlObj.ctrl}.rotateY', f'{self.rev_chain[2]}.rotateY')

        # hide rev chain
        for i in self.rev_chain: cmds.setAttr(f'{i}.drawStyle', 2)
        


    def add_fk_switch(self):
        self.hipCtlObj = ctl.ctrl.Control(target=self.leg_chain[0], parent=self.leg_conn, **self.ctl_dict['hip'])
        self.kneeCtlObj = ctl.ctrl.Control(target=self.leg_chain[1], parent=self.hipCtlObj.ctrl, **self.ctl_dict['knee'])
        self.ankleCtlObj = ctl.ctrl.Control(target=self.leg_chain[2], parent=self.kneeCtlObj.ctrl, **self.ctl_dict['ankle'])
        self.ballCtlObj = ctl.ctrl.Control(target=self.leg_chain[3], parent=self.ankleCtlObj.ctrl, **self.ctl_dict['ball'])

        utils.switch.IKFKSwitch(base_name=f'{self.side}_leg', bind_chain=self.leg_chain, ik_chain=self.ik_chain, fk_chain=None, ikfk_attr='FK', ikCtlObjs=[self.footCtlObj,
            self.kneePvCtlObj, self.footRollCtlObj, self.toeTapCtlObj], fkCtlObjs=[self.hipCtlObj, self.kneeCtlObj, self.ankleCtlObj, self.ballCtlObj])


    def add_space_switches(self):

        # auto knee
        self.hip_pv_driver = utils.helper.create_match_offset_parent(name=f'{self.side}_leg_autoPV_hipDriver', target=self.leg_chain[0], parent=self.leg_conn)
        self.ankle_pv_driver = utils.helper.create_match_offset_parent(name=f'{self.side}_leg_autoPV_ankleDriver', target=self.leg_chain[2], parent=self.rev_chain[-1])

        self.hip_pv_driver_up = utils.helper.create_match_offset_parent(name=f'{self.side}_leg_autoPV_hipDriverUp', target=self.leg_chain[0], offset=[0,0,10], parent=self.leg_conn)
        self.ankle_pv_driver_up = utils.helper.create_match_offset_parent(name=f'{self.side}_leg_autoPV_ankleDriverUp', target=self.leg_chain[2], offset=[0,0,10],parent=self.rev_chain[-1])

        cmds.aimConstraint(self.rev_chain[-1], self.hip_pv_driver, worldUpType='object', aimVector=[1,0,0], upVector=[0,0,1], worldUpObject=self.hip_pv_driver_up)
        cmds.aimConstraint(self.leg_conn, self.ankle_pv_driver, worldUpType='object', aimVector=[1,0,0], upVector=[0,0,1], worldUpObject=self.ankle_pv_driver_up)

        self.hip_pv_driver_offset = utils.helper.create_match_offset_parent(name=f'{self.side}_leg_autoPV_hipDriverOffset', target=self.kneePvCtlObj.ctrl, parent=self.hip_pv_driver)
        self.ankle_pv_driver_offset = utils.helper.create_match_offset_parent(name=f'{self.side}_leg_autoPV_ankleDriverOffset', target=self.kneePvCtlObj.ctrl, parent=self.ankle_pv_driver)
        self.knee_auto_driver_eff = utils.helper.create_match_offset_parent(name=f'{self.side}_leg_autoPV_effector', target=self.kneePvCtlObj.ctrl, parent=self.master)
        cmds.pointConstraint(self.hip_pv_driver_offset, self.ankle_pv_driver_offset, self.knee_auto_driver_eff)

        utils.switch.SpaceSwitch(base_name=f'{self.side}_kneePV', buffer=self.kneePvCtlObj.grp, ctrl=self.kneePvCtlObj.ctrl,
            space_dict={'World': self.master, 'Automatic': self.knee_auto_driver_eff})
        cmds.setAttr(f'{self.kneePvCtlObj.ctrl}.Space', 1)

        # generic space switch
        utils.switch.SpaceSwitch(base_name=f'{self.side}_foot', buffer=self.footCtlObj.grp, ctrl=self.footCtlObj.ctrl, space_dict={'World': self.master, 'Hip': self.leg_conn})


    def add_roll_bones(self):
        """ """
        utils.roll_joints.RollBoneThigh(side=self.side, pelvis=self.leg_conn, hip=self.leg_chain[0], knee=self.leg_chain[1])
        utils.roll_joints.RollBoneShin(side=self.side, knee=self.leg_chain[1], ankle=self.leg_chain[2])

    def add_ik_effects(self):
        """ """
        self.ikEffectsObj = utils.ik_effects.IKEffects(base_name=f'{self.side}_leg', ik_chain=self.ik_chain, main_ctrl=self.footCtlObj.ctrl, pv_ctrl=self.kneePvCtlObj.ctrl,
            base=self.leg_conn, master=self.master, ikh=self.leg_ikh, effector=self.rev_chain[-1])

    def add_helper_joints(self):
        """ Various helper joints for volume preservation. """
        cmds.select(cl=True)
        self.butt = cmds.joint(name=f'{self.side}_butt_jnt')
        cmds.matchTransform(self.butt, self.leg_conn)
        cmds.makeIdentity(self.butt, apply=True)
        cmds.parent(self.butt, self.leg_conn)
        cnst = cmds.orientConstraint(self.leg_conn, f'{self.side}_thigh_roll_start', self.butt)[0]  # maybe use a variable instead
        cmds.setAttr(f'{cnst}.interpType', 2)












