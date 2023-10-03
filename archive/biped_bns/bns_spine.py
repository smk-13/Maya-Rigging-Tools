from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload


import utils.helper
reload(utils.helper)

import ctl.ctrl 
reload(ctl.ctrl)




class Spine:
    """ """

    def __init__(self):
        """ """
        self.pelvis = 'pelvis_jnt'
        self.spine1 = 'spine1_jnt'
        self.spine2 = 'spine2_jnt'
        self.chest = 'chest_jnt'

        self.master = 'master2_ctl'

        self.ctl_dict = {
            'mainSpine': {'base_name': 'mainSpine', 'shape': 'bracketsX', 'scale': 15, 'color': 22, 'hidden_attrs': ['v', 'sx', 'sy', 'sz']},
            'pelvisTrans': {'base_name': 'pelvisMover', 'shape': 'circle', 'scale': 13, 'color': 14, 'hidden_attrs': ['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz']},
            'pelvisRot': {'base_name': 'pelvisRot', 'shape': 'circle', 'scale': 10, 'color': 18, 'hidden_attrs': ['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz']},
            'chestTrans': {'base_name': 'chestMover', 'shape': 'Asari_chest', 'scale': 10, 'color': 14, 'hidden_attrs':['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz']},
            'chestTwist': {'base_name': 'chestTwist', 'shape': 'circle', 'scale': 10, 'color': 18, 'hidden_attrs':['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz', 'ry', 'rz']}
        }

        self.main()


    def main(self):

        neck_eff = utils.helper.create_match_offset_parent(name='neck_eff', target=self.chest, offset=[16,0,0])

        self.mainCtlObj = ctl.ctrl.Control(target=self.pelvis, parent=self.master, **self.ctl_dict['mainSpine'])
        self.pelvisTransCtlObj = ctl.ctrl.Control(target=self.pelvis, parent=self.mainCtlObj.ctrl, **self.ctl_dict['pelvisTrans'])
        self.pelvisRotCtlObj = ctl.ctrl.Control(target=self.pelvis, parent=self.pelvisTransCtlObj.ctrl, **self.ctl_dict['pelvisRot'])
        self.chestTransCtlObj = ctl.ctrl.Control(target=neck_eff, parent=self.mainCtlObj.ctrl, **self.ctl_dict['chestTrans'])

        chest_root = utils.helper.create_match_offset_parent(name='chest_root', target=self.pelvis, parent=self.pelvisTransCtlObj.ctrl, locator=False)
        chest_twist = utils.helper.create_match_offset_parent(name='chest_twist', target=self.pelvis, parent=chest_root, locator=False)
        chest_eff = utils.helper.create_match_offset_parent(name='chest_eff', target=neck_eff, parent=chest_twist, locator=False)
        chest_up = utils.helper.create_match_offset_parent(name='chest_up', target=self.chest, offset=[0,40,0], parent=chest_twist, locator=False)

        self.chestTwistCtlObj = ctl.ctrl.Control(target=self.chest, parent=chest_root, **self.ctl_dict['chestTwist'])

        pelvis_eff = utils.helper.create_match_offset_parent(name='pelvis_eff', target=neck_eff, parent=self.pelvisRotCtlObj.ctrl, locator=False)
        pelvis_up = utils.helper.create_match_offset_parent(name='pelvis_up', target=self.chest, offset=[0,40,0], parent=self.pelvisRotCtlObj.ctrl, locator=False)

        spine1_eff = utils.helper.create_match_offset_parent(name='spine1_eff', target=neck_eff, parent=self.pelvisTransCtlObj.ctrl, locator=False)
        spine1_up = utils.helper.create_match_offset_parent(name='spine1_up', target=self.chest, offset=[0,40,0], parent=self.pelvisTransCtlObj.ctrl, locator=False)

        cmds.aimConstraint(self.chestTransCtlObj.ctrl, chest_root, worldUpType='none', aimVector=[1,0,0], mo=True)
        cmds.aimConstraint(self.chestTransCtlObj.ctrl, chest_twist, worldUpType='objectrotation', aimVector=[1,0,0], upVector=[0,1,0], worldUpVector=[0,1,0],
            worldUpObject=self.chestTwistCtlObj.ctrl, mo=True)

        cmds.pointConstraint(chest_eff, pelvis_eff, spine1_eff, mo=True)
        cmds.pointConstraint(chest_up, pelvis_up, spine1_up, mo=True)

        cmds.aimConstraint(chest_eff, self.chest, worldUpType='object', aimVector=[1,0,0], upVector=[0,1,0], worldUpObject=chest_up, mo=True)
        cmds.aimConstraint(spine1_eff, self.spine1, worldUpType='object', aimVector=[1,0,0], upVector=[0,1,0], worldUpObject=spine1_up, mo=True)
        cmds.parent(self.pelvis, self.pelvisRotCtlObj.ctrl)

        # new
        spine2_eff = utils.helper.create_match_offset_parent(name='spine2_eff', target=neck_eff, parent=self.pelvisTransCtlObj.ctrl, locator=False)
        spine2_up = utils.helper.create_match_offset_parent(name='spine2_up', target=self.chest, offset=[0,40,0], parent=self.pelvisTransCtlObj.ctrl, locator=False)
        cnst = cmds.pointConstraint(chest_eff, pelvis_eff, spine2_eff, mo=True)[0]
        cmds.setAttr(f'{cnst}.{chest_eff}W0', 3/4)
        cmds.setAttr(f'{cnst}.{pelvis_eff}W1', 1/4)
        cnst = cmds.pointConstraint(chest_up, pelvis_up, spine2_up, mo=True)[0]
        cmds.setAttr(f'{cnst}.{chest_up}W0', 3/4)
        cmds.setAttr(f'{cnst}.{pelvis_up}W1', 1/4)
        cmds.aimConstraint(spine2_eff, self.spine2, worldUpType='object', aimVector=[1,0,0], upVector=[0,1,0], worldUpObject=spine2_up, mo=True)

        cmds.delete(neck_eff)















class Spine_simple:

    def __init__(self):
        """ """
        self.pelvis = 'pelvis_jnt'
        self.spine1 = 'spine1_jnt'
        self.chest = 'chest_jnt'

        self.master = 'master2_ctl'

        self.ctl_dict = {
            'mainSpine': {'base_name': 'mainSpine', 'shape': 'bracketsX', 'scale': 15, 'color': 22, 'hidden_attrs': ['v', 'sx', 'sy', 'sz']},
            'pelvisTrans': {'base_name': 'hipMover', 'shape': 'circle', 'scale': 13, 'color': 14, 'hidden_attrs': ['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz']},
            'pelvisRot': {'base_name': 'hipSwing', 'shape': 'circle', 'scale': 10, 'color': 18, 'hidden_attrs': ['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz']},
            'chestTrans': {'base_name': 'upperBodyMover', 'shape': 'circle', 'scale': 10, 'color': 14, 'hidden_attrs':['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz']},
            'chestTwist': {'base_name': 'upperBodyTwist', 'shape': 'circle', 'scale': 10, 'color': 18, 'hidden_attrs':['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz', 'ry', 'rz']}
        }

        self.main()


    def main(self):

        neck_eff = utils.helper.create_match_offset_parent(name='chest_eff_temp', target=self.chest, offset=[16,0,0])

        self.mainCtlObj = ctl.ctrl.Control(target=self.pelvis, parent=self.master, **self.ctl_dict['mainSpine'])
        self.pelvisTransCtlObj = ctl.ctrl.Control(target=self.pelvis, parent=self.mainCtlObj.ctrl, **self.ctl_dict['pelvisTrans'])
        self.pelvisRotCtlObj = ctl.ctrl.Control(target=self.pelvis, parent=self.pelvisTransCtlObj.ctrl, **self.ctl_dict['pelvisRot'])
        self.chestTransCtlObj = ctl.ctrl.Control(target=neck_eff, parent=self.mainCtlObj.ctrl, **self.ctl_dict['chestTrans'])

        chest_root = utils.helper.create_match_offset_parent(name='chest_root', target=self.pelvis, parent=self.pelvisTransCtlObj.ctrl, locator=False)
        chest_twist = utils.helper.create_match_offset_parent(name='chest_twist', target=self.pelvis, parent=chest_root, locator=False)
        chest_eff = utils.helper.create_match_offset_parent(name='chest_eff', target=neck_eff, parent=chest_twist, locator=False)
        chest_up = utils.helper.create_match_offset_parent(name='chest_up', target=self.chest, offset=[0,40,0], parent=chest_twist, locator=False)  # why the chest and not the pelvis?

        self.chestTwistCtlObj = ctl.ctrl.Control(target=self.chest, parent=chest_root, **self.ctl_dict['chestTwist'])

        pelvis_eff = utils.helper.create_match_offset_parent(name='pelvis_eff', target=neck_eff, parent=self.pelvisRotCtlObj.ctrl, locator=False)
        pelvis_up = utils.helper.create_match_offset_parent(name='pelvis_up', target=self.chest, offset=[0,40,0], parent=self.pelvisRotCtlObj.ctrl, locator=False)

        spine1_eff = utils.helper.create_match_offset_parent(name='spine1_eff', target=neck_eff, parent=self.pelvisTransCtlObj.ctrl, locator=False)
        spine1_up = utils.helper.create_match_offset_parent(name='spine1_up', target=self.chest, offset=[0,40,0], parent=self.pelvisTransCtlObj.ctrl, locator=False)

        cmds.aimConstraint(self.chestTransCtlObj.ctrl, chest_root, worldUpType='none', aimVector=[1,0,0], mo=True)
        cmds.aimConstraint(self.chestTransCtlObj.ctrl, chest_twist, worldUpType='objectrotation', aimVector=[1,0,0], upVector=[0,1,0], worldUpVector=[0,1,0],
            worldUpObject=self.chestTwistCtlObj.ctrl, mo=True)

        cmds.pointConstraint(chest_eff, pelvis_eff, spine1_eff, mo=True)
        cmds.pointConstraint(chest_up, pelvis_up, spine1_up, mo=True)

        cmds.aimConstraint(chest_eff, self.chest, worldUpType='object', aimVector=[1,0,0], upVector=[0,1,0], worldUpObject=chest_up, mo=True)
        cmds.aimConstraint(spine1_eff, self.spine1, worldUpType='object', aimVector=[1,0,0], upVector=[0,1,0], worldUpObject=spine1_up, mo=True)
        cmds.parent(self.pelvis, self.pelvisRotCtlObj.ctrl)

        cmds.delete(neck_eff)

