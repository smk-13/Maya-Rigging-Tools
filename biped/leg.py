from maya import cmds
from maya.api import OpenMaya
from importlib import reload

import utils.helper
reload(utils.helper)




# This time, I don't create the ctrls here, but I use an already existing set of ctrls
# I could create the offset groups here

class Leg:
    """ """

    def __init__(self, side):
        """ """

        self.side = side
        self.offset_tokens = ['Grp']

        self.leg_chain = [f'{side}_{i}' for i in ('hip', 'knee', 'ankle', 'ball', 'toe')]
        self.rev_chain = [f'{side}_{i}' for i in ('revCBank', 'revEBank', 'revPivot', 'revHeel', 'revToe', 'revBall', 'revAnkle')]

        self.legTrans = f'{side}_legTrans_ctl'
        self.legPV = f'{side}_legPV_ctl'
        self.footRoll = f'{side}_footRoll_ctl'
        self.footRot = f'{side}_footRot_ctl'
        self.toeRot = f'{side}_toeRot_ctl'

        self.create_offsets()
        self.main()
        self.set_hidden_attrs()

    def create_offsets(self):
        self.legTrans_offsets = utils.helper.create_offsets(self.legTrans, tokens=self.offset_tokens)
        self.legPV_offsets = utils.helper.create_offsets(self.legPV, tokens=self.offset_tokens)
        self.footRoll_offsets = utils.helper.create_offsets(self.footRoll, tokens=self.offset_tokens)
        self.footRot_offsets = utils.helper.create_offsets(self.footRot, tokens=self.offset_tokens)
        self.toeRot_offsets = utils.helper.create_offsets(self.toeRot, tokens=self.offset_tokens)

    def set_hidden_attrs(self):
        utils.helper.set_hidden_attrs(ctrl=self.legTrans, hidden_attrs=['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz'])
        utils.helper.set_hidden_attrs(ctrl=self.legPV, hidden_attrs=['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz'])
        utils.helper.set_hidden_attrs(ctrl=self.footRoll, hidden_attrs=['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz'])
        utils.helper.set_hidden_attrs(ctrl=self.footRot, hidden_attrs=['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz', 'rz'])
        utils.helper.set_hidden_attrs(ctrl=self.toeRot, hidden_attrs=['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz', 'rx', 'rz'])


    def main(self):
        """ """
        self.leg_conn = utils.helper.duplicate_single_joint(joint=self.leg_chain[0],
            name=f'{self.side}_legRig')

        cmds.parent(self.leg_chain[0], self.leg_conn)

        #self.ik_chain = utils.helper.duplicate_joint_chain_v3(joint_chain=self.leg_chain, suffix='IK', parent=self.leg_conn)
        self.ik_chain = self.leg_chain

        self.leg_ikh = utils.helper.ik_handle(start_joint=self.ik_chain[0], end_joint=self.ik_chain[2], base_name=f'{self.side}_leg', solver='ikRPsolver')
        self.foot_ikh = utils.helper.ik_handle(start_joint=self.ik_chain[2], end_joint=self.ik_chain[3], base_name=f'{self.side}_foot', solver='ikSCsolver')
        self.toe_ikh = utils.helper.ik_handle(start_joint=self.ik_chain[3], end_joint=self.ik_chain[4], base_name=f'{self.side}_toe', solver='ikSCsolver')

        cmds.poleVectorConstraint(self.legPV, self.leg_ikh)

        cmds.parent(self.toe_ikh, self.toeRot)
        cmds.parent(self.leg_ikh, self.rev_chain[6])
        cmds.parent(self.foot_ikh, self.rev_chain[5])
        cmds.parent(self.rev_chain[0], self.footRot)

        toe_lift = 'ToeLiftAngle'
        toe_straight = 'ToeStraightAngle'
        cmds.addAttr(self.footRoll, ln=toe_lift, at='double', dv=60, k=True)
        cmds.addAttr(self.footRoll, ln=toe_straight, at='double', dv=75, k=True)

        # roll
        condition_roll = cmds.createNode('condition', name=f'{self.side}_footRoll_COND')
        blend_roll = cmds.createNode('blendColors', name=f'{self.side}_footRoll_BC')
        remap_roll = cmds.createNode('remapValue', name=f'{self.side}_footRoll_REMAP')
        cmds.setAttr(f'{condition_roll}.operation', 2)
        cmds.setAttr(f'{condition_roll}.colorIfFalseR', 0)
        cmds.connectAttr(f'{self.footRoll}.rotateX', f'{condition_roll}.colorIfFalseG')
        cmds.connectAttr(f'{self.footRoll}.rotateX', f'{condition_roll}.colorIfTrueR')
        cmds.connectAttr(f'{self.footRoll}.rotateX', f'{condition_roll}.firstTerm')
        cmds.connectAttr(f'{self.footRoll}.rotateX', f'{remap_roll}.inputValue')
        cmds.connectAttr(f'{self.footRoll}.{toe_lift}', f'{remap_roll}.inputMin')
        cmds.connectAttr(f'{self.footRoll}.{toe_straight}', f'{remap_roll}.inputMax')
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
        cmds.connectAttr(f'{self.footRoll}.rotateZ', f'{condition_bank}.colorIfFalseG')
        cmds.connectAttr(f'{self.footRoll}.rotateZ', f'{condition_bank}.colorIfTrueR')
        cmds.connectAttr(f'{self.footRoll}.rotateZ', f'{condition_bank}.firstTerm')
        cmds.connectAttr(f'{condition_bank}.outColorR', f'{self.rev_chain[0]}.rotateZ')
        cmds.connectAttr(f'{condition_bank}.outColorG', f'{self.rev_chain[1]}.rotateZ')

        # ball spin
        cmds.connectAttr(f'{self.footRoll}.rotateY', f'{self.rev_chain[2]}.rotateY')

        # hide rev chain
        for i in self.rev_chain: cmds.setAttr(f'{i}.drawStyle', 2)

        # parenting
        cmds.parent(self.footRoll_offsets[0], self.legTrans)
        cmds.parent(self.footRot_offsets[0], self.legTrans)
        cmds.parent(self.toeRot_offsets[0], self.rev_chain[4])
        cmds.parent(self.legTrans_offsets[0], self.leg_conn)
        cmds.parent(self.legPV_offsets[0], self.leg_conn)







        


