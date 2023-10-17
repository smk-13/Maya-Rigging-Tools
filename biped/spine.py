from maya import cmds
from maya.api import OpenMaya
from importlib import reload

import utils.helper
reload(utils.helper)




class Spine:

    def __init__(self, pelvis='C_pelvis', spine1='C_spine_1', chest='C_chest', mainSpine='C_mainSpine_ctl',
        pelvisTrans='C_pelvisTrans_ctl', pelvisRot='C_pelvisRot_ctl', chestTrans='C_chestTrans_ctl',
        chestTwist='C_chestTwist_ctl', master=None):

        self.pelvis = pelvis
        self.spine1 = spine1
        self.chest = chest

        self.mainSpine = mainSpine
        self.pelvisTrans = pelvisTrans
        self.pelvisRot = pelvisRot
        self.chestTrans = chestTrans
        self.chestTwist = chestTwist

        utils.helper.check_if_objs_exist(objects=list(self.__dict__.values()))

        self.master = master

        self.create_offsets()
        self.main()
        self.set_hidden_attrs()


    def create_offsets(self):
        self.mainSpine_offsets = utils.helper.create_offsets(self.mainSpine, tokens=['Grp'])
        self.pelvisTrans_offsets = utils.helper.create_offsets(self.pelvisTrans, tokens=['Grp'])
        self.pelvisRot_offsets = utils.helper.create_offsets(self.pelvisRot, tokens=['Grp'])
        self.chestTrans_offsets = utils.helper.create_offsets(self.chestTrans, tokens=['Grp'])
        self.chestTwist_offsets = utils.helper.create_offsets(self.chestTwist, tokens=['Grp'])

    def set_hidden_attrs(self):
        utils.helper.set_hidden_attrs(ctrl=self.mainSpine, hidden_attrs=['v', 'sx', 'sy', 'sz'])
        utils.helper.set_hidden_attrs(ctrl=self.pelvisTrans, hidden_attrs=['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz'])
        utils.helper.set_hidden_attrs(ctrl=self.pelvisRot, hidden_attrs=['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz'])
        utils.helper.set_hidden_attrs(ctrl=self.chestTrans, hidden_attrs=['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz'])
        utils.helper.set_hidden_attrs(ctrl=self.chestTwist, hidden_attrs=['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz', 'ry', 'rz'])


    def main(self):
        """ """
        cmds.parent(self.pelvisTrans_offsets[0], self.mainSpine)
        cmds.parent(self.pelvisRot_offsets[0], self.pelvisTrans)

        cmds.parent(self.chestTrans_offsets[0], self.mainSpine)

        chest_root_buffer = utils.helper.create_match_offset_parent(name='chest_rootBuffer', target=self.pelvis, parent=self.pelvisTrans)
        chest_root = utils.helper.create_match_offset_parent(name='chest_root', target=self.pelvis, parent=chest_root_buffer)
        chest_twist = utils.helper.create_match_offset_parent(name='chest_twist', target=self.pelvis, parent=chest_root)
        chest_eff = utils.helper.create_match_offset_parent(name='chest_eff', target=self.chestTrans, parent=chest_twist)
        chest_up = utils.helper.create_match_offset_parent(name='chest_up', target=self.chest, offset=[0,40,0], parent=chest_twist)

        cmds.parent(self.chestTwist_offsets[0], chest_root)

        pelvis_eff = utils.helper.create_match_offset_parent(name='pelvis_eff', target=self.chestTrans, parent=self.pelvisRot)
        pelvis_up = utils.helper.create_match_offset_parent(name='pelvis_up', target=self.chest, offset=[0,40,0], parent=self.pelvisRot)

        spine1_eff = utils.helper.create_match_offset_parent(name='spine1_eff', target=self.chestTrans, parent=self.pelvisTrans)
        spine1_up = utils.helper.create_match_offset_parent(name='spine1_up', target=self.chest, offset=[0,40,0], parent=self.pelvisTrans)

        cmds.aimConstraint(self.chestTrans, chest_root, worldUpType='none', aimVector=[1,0,0], mo=True)
        cmds.aimConstraint(self.chestTrans, chest_twist, worldUpType='objectrotation', aimVector=[1,0,0], upVector=[0,1,0], worldUpVector=[0,1,0],
            worldUpObject=self.chestTwist, mo=True)

        cmds.pointConstraint(chest_eff, pelvis_eff, spine1_eff, mo=True)
        cmds.pointConstraint(chest_up, pelvis_up, spine1_up, mo=True)

        cmds.aimConstraint(chest_eff, self.chest, worldUpType='object', aimVector=[1,0,0], upVector=[0,1,0], worldUpObject=chest_up, mo=True)
        cmds.aimConstraint(spine1_eff, self.spine1, worldUpType='object', aimVector=[1,0,0], upVector=[0,1,0], worldUpObject=spine1_up, mo=True)
        cmds.parentConstraint(self.pelvisRot, self.pelvis)

        # helper joint for easier skinning; this could even be an ik spline with multiple joints
        # cmds.select(cl=True)
        # spine2_jnt = cmds.joint(name='C_spine_2', radius=3)
        # cmds.makeIdentity(spine2_jnt, apply=True)  # why is this not working?!
        # cnst = cmds.parentConstraint(self.spine1, self.chest, spine2_jnt)[0]
        # cmds.setAttr(f'{cnst}.interpType', 2)

        # connect
        if cmds.objExists(self.master):
            cmds.parent(self.mainSpine_offsets[0], self.master)

class Neck:

    def __init__(self, neck='C_neck', head='C_head', headAim='C_headAim_ctl', headTilt='C_headTilt_ctl',
        neckRot='C_neck_ctl', chest=None, master=None):
        """ """

        self.neck = neck
        self.head = head
        self.headAim = headAim
        self.headTilt = headTilt
        self.neckRot = neckRot

        utils.helper.check_if_objs_exist(objects=list(self.__dict__.values()))

        self.chest = chest
        self.master = master

        self.create_offsets()
        self.set_hidden_attrs()
        self.main()


    def create_offsets(self):
        self.headAim_offsets = utils.helper.create_offsets(self.headAim, tokens=['Grp'])
        self.headTilt_offsets = utils.helper.create_offsets(self.headTilt, tokens=['Grp'])
        self.neckRot_offsets = utils.helper.create_offsets(self.neckRot, tokens=['Grp'])

    def set_hidden_attrs(self):
        utils.helper.set_hidden_attrs(ctrl=self.headAim, hidden_attrs=['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz'])
        utils.helper.set_hidden_attrs(ctrl=self.headTilt, hidden_attrs=['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz', 'rx', 'rz'])
        utils.helper.set_hidden_attrs(ctrl=self.neckRot, hidden_attrs=['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz', 'rx'])

    def main(self):
        """ """

        cmds.parent(self.headTilt_offsets[0], self.neckRot)

        head_driver = utils.helper.create_match_offset_parent(name='head_driver', target=self.headTilt, parent=self.headTilt)

        cmds.aimConstraint(self.headAim, head_driver, worldUpType='objectrotation', aimVector=[0,1,0], upVector=[1,0,0], worldUpVector=[1,0,0],
            worldUpObject=self.headTilt)

        neckFollow_buffer = utils.helper.create_match_offset_parent(name='neckFollow_buffer', target=self.neck, parent=self.neckRot)

        neckFollow_mdl = cmds.createNode('multDoubleLinear', name='neck_follow_MDL')
        cmds.connectAttr(f'{head_driver}.rx', f'{neckFollow_mdl}.input1')
        cmds.setAttr(f'{neckFollow_mdl}.input2', 0.4)
        cmds.connectAttr(f'{neckFollow_mdl}.output', f'{neckFollow_buffer}.rx')

        cmds.parentConstraint(neckFollow_buffer, self.neck)

        # v1: with orient constraint
        cmds.orientConstraint(head_driver, self.head)

        # connect to spine and master
        if cmds.objExists(self.chest):
            cmds.parentConstraint(self.chest, self.neckRot_offsets[0], mo=True)

        if cmds.objExists(self.master):
            cmds.parent(self.headAim_offsets[0], self.master)
            cmds.parent(self.neckRot_offsets[0], self.master)


