from maya import cmds
from maya.api import OpenMaya
from importlib import reload

import utils.helper
reload(utils.helper)

import utils.soft_distance
reload(utils.soft_distance)

import utils.switch
reload(utils.switch)


class Arm:
    """ """

    # TO DO: lock for the hands

    def __init__(self, ik_chain, armTrans, armPV, clavicleCtl, wristCtl, chest=None, master=None):
        """ """

        self.ik_chain = ik_chain
        self.armTrans = armTrans
        self.armPV = armPV
        self.clavicleCtl = clavicleCtl
        self.wristCtl = wristCtl

        utils.helper.check_if_objs_exist(objects=list(self.__dict__.values()))

        self.chest = chest
        self.master = master

        self.create_offsets()
        self.main()
        self.set_hidden_attrs()

    def create_offsets(self):
        self.armTrans_offsets = utils.helper.create_offsets(self.armTrans, tokens=['Grp'])
        self.armPV_offsets = utils.helper.create_offsets(self.armPV, tokens=['Grp'])
        self.clavicleCtl_offsets = utils.helper.create_offsets(self.clavicleCtl, tokens=['Grp'])
        self.wristCtl_offsets = utils.helper.create_offsets(self.wristCtl, tokens=['Grp'])

    def set_hidden_attrs(self):
        utils.helper.set_hidden_attrs(ctrl=self.armTrans, hidden_attrs=['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz'])
        utils.helper.set_hidden_attrs(ctrl=self.armPV, hidden_attrs=['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz'])
        utils.helper.set_hidden_attrs(ctrl=self.clavicleCtl, hidden_attrs=['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz'])
        utils.helper.set_hidden_attrs(ctrl=self.wristCtl, hidden_attrs=['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz'])

    def main(self):

        cmds.parentConstraint(self.clavicleCtl, self.ik_chain[0])

        self.arm_ikh = utils.helper.ik_handle(start_joint=self.ik_chain[1], end_joint=self.ik_chain[-1])
        cmds.poleVectorConstraint(self.armPV, self.arm_ikh)
        cmds.parent(self.arm_ikh, self.armTrans)

        wrist_local = cmds.createNode('transform', name=f'{self.wristCtl_offsets[0]}_local')
        cmds.matchTransform(wrist_local, self.ik_chain[-1])
        cmds.pointConstraint(self.ik_chain[3], wrist_local)
        cmds.orientConstraint(self.ik_chain[2], wrist_local, mo=True)

        wrist_world = cmds.createNode('transform', name=f'{self.wristCtl_offsets[0]}_world')
        cmds.matchTransform(wrist_world, self.ik_chain[-1])
        cmds.pointConstraint(self.ik_chain[3], wrist_world)

        utils.switch.blend_switch(ctrl=self.wristCtl, space1=wrist_local, space2=wrist_world,
            transform=self.wristCtl_offsets[0], attr_name='lock')

        cmds.orientConstraint(self.wristCtl, self.ik_chain[3])





        # connect
        if cmds.objExists(self.master):
            cmds.parent(self.armTrans_offsets[0], self.master)
            cmds.parent(self.armPV_offsets[0], self.master)
            cmds.parent(self.clavicleCtl_offsets[0], self.master)
            cmds.parent(self.wristCtl_offsets[0], self.master)
            cmds.parent(wrist_local, self.master)
            cmds.parent(wrist_world, self.master)


        if cmds.objExists(self.chest):
            cmds.parentConstraint(self.chest, self.clavicleCtl_offsets[0], mo=True)







