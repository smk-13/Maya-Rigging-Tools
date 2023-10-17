from maya import cmds
from maya.api import OpenMaya
from importlib import reload

import utils.helper
reload(utils.helper)

import utils.soft_distance
reload(utils.soft_distance)



class ikLeg:
    """ non reverse foot """

    def __init__(self, ik_chain, legTrans, legPV, footRot, toeRot, master=None):

        self.ik_chain = ik_chain
        self.legTrans = legTrans
        self.legPV = legPV
        self.footRot = footRot
        self.toeRot = toeRot

        utils.helper.check_if_objs_exist(objects=list(self.__dict__.values()))

        self.master = master

        self.create_offsets()
        self.main()
        self.set_hidden_attrs()


    def create_offsets(self):
        self.legTrans_offsets = utils.helper.create_offsets(self.legTrans, tokens=['Grp'])
        self.legPV_offsets = utils.helper.create_offsets(self.legPV, tokens=['Grp'])
        self.footRot_offsets = utils.helper.create_offsets(self.footRot, tokens=['Grp'])
        self.toeRot_offsets = utils.helper.create_offsets(self.toeRot, tokens=['Grp'])

    def set_hidden_attrs(self):
        utils.helper.set_hidden_attrs(ctrl=self.legTrans, hidden_attrs=['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz'])
        utils.helper.set_hidden_attrs(ctrl=self.legPV, hidden_attrs=['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz'])
        utils.helper.set_hidden_attrs(ctrl=self.footRot, hidden_attrs=['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz'])
        utils.helper.set_hidden_attrs(ctrl=self.toeRot, hidden_attrs=['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz', 'rx', 'rz'])

    def main(self):

        self.leg_ikh = utils.helper.ik_handle(start_joint=self.ik_chain[0], end_joint=self.ik_chain[2])

        cmds.parent(self.leg_ikh, self.legTrans)
        cmds.poleVectorConstraint(self.legPV, self.leg_ikh)

        cmds.parent(self.toeRot_offsets[0], self.footRot)

        cmds.orientConstraint(self.footRot, self.ik_chain[2])
        cmds.orientConstraint(self.toeRot, self.ik_chain[3])
        cmds.pointConstraint(self.ik_chain[2], self.footRot_offsets[0])

        # connect
        if cmds.objExists(self.master):
            cmds.parent(self.legTrans_offsets[0], self.master)
            cmds.parent(self.legPV_offsets[0], self.master)
            cmds.parent(self.footRot_offsets[0], self.master)



    # def add_soft_distance(self):
    #     utils.soft_distance.SoftIK(base_name=self.ik_chain[2], ctrl=self.legTrans,
    #         ik_chain=self.ik_chain, start=self.leg_conn, end=self.legTrans, master=self.leg_conn,
    #         ikh=self.leg_ikh)




class rev_ikLeg:
    """ """

    def __init__(self, ik_chain, rev_chain, legTrans, legPV, footRoll, master):

        # TO DO: Add toe tap

        self.ik_chain = ik_chain
        self.rev_chain = rev_chain
        self.legTrans = legTrans
        self.legPV = legPV
        self.footRoll = footRoll

        utils.helper.check_if_objs_exist(objects=list(self.__dict__.values()))
        utils.helper.check_chain_length(chain=self.ik_chain, length=5)
        utils.helper.check_chain_length(chain=self.rev_chain, length=7)

        self.master = master

        self.create_offsets()
        self.main()
        self.set_hidden_attrs()


    def create_offsets(self):
        self.legTrans_offsets = utils.helper.create_offsets(self.legTrans, tokens=['Grp'])
        self.legPV_offsets = utils.helper.create_offsets(self.legPV, tokens=['Grp'])
        self.footRoll_offsets = utils.helper.create_offsets(self.footRoll, tokens=['Grp'])

    def set_hidden_attrs(self):
        utils.helper.set_hidden_attrs(ctrl=self.legTrans, hidden_attrs=['v', 'sx', 'sy', 'sz'])
        utils.helper.set_hidden_attrs(ctrl=self.legPV, hidden_attrs=['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz'])
        utils.helper.set_hidden_attrs(ctrl=self.footRoll, hidden_attrs=['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz'])

    def main(self):
        """ """

        self.leg_ikh = utils.helper.ik_handle(start_joint=self.ik_chain[0], end_joint=self.ik_chain[2], solver='ikRPsolver')
        self.foot_ikh = utils.helper.ik_handle(start_joint=self.ik_chain[2], end_joint=self.ik_chain[3], solver='ikSCsolver')
        self.toe_ikh = utils.helper.ik_handle(start_joint=self.ik_chain[3], end_joint=self.ik_chain[4], solver='ikSCsolver')

        cmds.poleVectorConstraint(self.legPV, self.leg_ikh)

        cmds.parent(self.toe_ikh, self.rev_chain[4])
        cmds.parent(self.leg_ikh, self.rev_chain[6])
        cmds.parent(self.foot_ikh, self.rev_chain[5])
        cmds.parent(self.rev_chain[0], self.legTrans)
        cmds.parent(self.footRoll_offsets[0], self.legTrans)

        toe_lift = 'ToeLiftAngle'
        toe_straight = 'ToeStraightAngle'
        cmds.addAttr(self.footRoll, ln=toe_lift, at='double', dv=60, k=True)
        cmds.addAttr(self.footRoll, ln=toe_straight, at='double', dv=75, k=True)

        # roll
        condition_roll = cmds.createNode('condition', name=f'{self.footRoll}_roll_COND')
        blend_roll = cmds.createNode('blendColors', name=f'{self.footRoll}_roll_BC')
        remap_roll = cmds.createNode('remapValue', name=f'{self.footRoll}_roll_REMAP')
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
        condition_bank = cmds.createNode('condition', name=f'{self.footRoll}_banking_COND')
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

        # connect
        if cmds.objExists(self.master):
            cmds.parent(self.legTrans_offsets[0], self.master)
            cmds.parent(self.legPV_offsets[0], self.master)






        


